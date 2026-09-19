"""test_trilha.py -- o gerador da trilha da Fase 1 dentro do repo (s189, spec
`trilha-autoridade-unica`, decisao do /ai-eng).

Ate a s188 o gerador vivia em `scratch/` (gitignored) e o `_doc` do arquivo gerado prometia
"editavel a mao" enquanto o `--gravar` o sobrescrevia. Estes testes protegem, em ordem de dano:

  1. GOLDEN -- o `plano_trilha.json` gravado E a saida do gerador sobre a entrada fixada +
     parametros + camada manual. Edicao a mao no arquivo gerado, ou parametro mudado sem
     `--gravar`, derruba aqui.
  2. PROPRIEDADE -- a saida respeita o que os parametros declaram (piso/teto por bloco,
     calendario, uma prova UERJ inteira por semana declarada, marca de gerado). A MESMA funcao
     roda no `--gravar` antes de escrever. ⚠️ O piso/teto e medido na regua do PROPRIO
     gerador (bloco em que a UERJ cobra o tema): auto-consistencia, nao independencia -- limite
     (c) do modulo.
  3. A camada manual VENCE o gerado por chave, sem duplicar, e exige `racional`.

Le os JSON versionados e o mapa UERJ; nao abre banco. Nada de conteudo de questao e impresso.
"""
import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import plano  # noqa: E402
import trilha  # noqa: E402


@pytest.fixture(scope="module")
def real():
    params = trilha.carregar_parametros()
    entrada = trilha.carregar_entrada(params)
    custom = trilha.carregar_custom()
    return params, entrada, custom, trilha.gerar(params, entrada, custom)


def _gravado():
    with open(trilha.P_SAIDA, encoding="utf-8") as fh:
        return json.load(fh)


def test_golden_o_arquivo_gravado_e_a_saida_do_gerador(real):
    params, _entrada, _custom, r = real
    doc = trilha.documento(params, r["overrides"])
    gravado = _gravado()
    assert gravado["overrides"] == doc["overrides"], (
        "plano_trilha.json != saida do gerador: edicao a mao no arquivo GERADO, ou "
        "parametros/custom/entrada mudaram sem `python tools/trilha.py --gravar`")
    assert gravado == doc, "metadado divergente (_doc/gerado_por/versao/calendario)"


def test_propriedades_da_trilha_gravada(real):
    params, entrada, _custom, r = real
    assert trilha.verificar_propriedades(_gravado(), params, entrada, r["blocos"]) == []


def test_propriedade_pega_saida_adulterada(real):
    """Cada invariante declarado derruba a sua adulteracao -- e o que faz o `--gravar` recusar."""
    params, entrada, _custom, r = real
    doc = trilha.documento(params, r["overrides"])
    verif = lambda d, p=params: trilha.verificar_propriedades(d, p, entrada, r["blocos"])  # noqa: E731

    semana_zero = copy.deepcopy(doc)
    semana_zero["overrides"][0]["semana_plano"] = 0
    assert any("semana invalida" in e for e in verif(semana_zero))

    sem_s7 = copy.deepcopy(params)
    del sem_s7["calendario"]["7"]
    assert any("fora do calendario" in e for e in verif(doc, sem_s7))

    provas = copy.deepcopy(doc)
    por_custom = {t["tarefa_fonte"]: t for t in entrada["plano_custom"]}
    uerj = [o for o in provas["overrides"] if o["fonte"] == "custom"
            and trilha.RX_PROVA_UERJ.match(por_custom[o["tarefa_fonte"]]["tema"])]
    uerj[0]["semana_plano"], uerj[1]["semana_plano"] = uerj[1]["semana_plano"], uerj[0]["semana_plano"]
    assert any("provas UERJ por semana" in e for e in verif(provas))

    teto_baixo = dict(params, teto=0.20)
    assert any("fora de 19-20%" in e for e in verif(doc, teto_baixo))

    sem_marca = dict(doc, gerado_por=None)
    assert any("marca de gerado" in e for e in verif(sem_marca))


def test_camada_manual_vence_o_gerado_e_exige_racional(real):
    params, entrada, custom, r = real
    alvo = next(o for o in r["overrides"] if o["fonte"] == "rf")
    chave = trilha._chave(alvo)
    manual = custom + [dict(fonte="rf", ref_semana_fonte=chave[1], tarefa_fonte=chave[2],
                            semana_plano=6, ordem=99, racional="teste: operador adia a lista")]
    r2 = trilha.gerar(params, entrada, manual)
    chaves = [trilha._chave(o) for o in r2["overrides"]]
    assert len(chaves) == len(set(chaves)) == len(r["overrides"]), "substitui, nunca duplica"
    novo = next(o for o in r2["overrides"] if trilha._chave(o) == chave)
    assert (novo["semana_plano"], novo["ordem"]) == (6, 99)
    for ruim in (dict(manual[-1], racional=""), manual[-1]):
        lote = manual if ruim is manual[-1] else custom + [ruim]
        if ruim is manual[-1]:
            lote = manual + [dict(manual[-1])]          # chave repetida na camada manual
        with pytest.raises(ValueError):
            trilha.gerar(params, entrada, lote)


def test_gravar_recusa_saida_que_viola_propriedade(tmp_path, monkeypatch, capsys):
    """O `--gravar` roda a MESMA verificacao do teste e nao escreve nada se ela falhar."""
    params = json.load(open(trilha.P_PARAMETROS, encoding="utf-8"))
    params["teto"] = 0.20
    p_params = tmp_path / "parametros.json"
    p_params.write_text(json.dumps(params, ensure_ascii=False), encoding="utf-8")
    p_saida = tmp_path / "plano_trilha.json"
    monkeypatch.setattr(trilha, "P_PARAMETROS", str(p_params))
    monkeypatch.setattr(trilha, "P_SAIDA", str(p_saida))
    assert trilha.main(["--gravar"]) == 2
    assert not p_saida.exists(), "recusa nao pode gravar"
    assert "RECUSADO" in capsys.readouterr().out


def test_agendamento_termina_quando_nada_mais_cabe():
    """s189 -- regressao do loop infinito herdado da s188 (achado no porte). Dois blocos com a
    proxima linha maior que a folga da semana: o laco antigo zerava `vazio` antes do teste de
    capacidade e girava para sempre -- com teto 20%, o `--gravar` travava. Roda em thread com
    prazo: regressao FALHA em 10 s, em vez de travar a suite."""
    import collections
    import threading

    def linha(q):
        return {"p": {"q_previstas": q}, "V": 1.0}
    filas = collections.defaultdict(list)
    filas["CIR"] = [[linha(10)], [linha(200)]]
    filas["GO"] = [[linha(200)]]
    saida = {}
    th = threading.Thread(daemon=True, target=lambda: saida.update(
        r=trilha.agendar_series(filas, {s: 30 for s in range(1, 7)})))
    th.start()
    th.join(10)
    assert not th.is_alive(), "agendar_series nao terminou: o loop infinito da s188 voltou"
    semana_de, carga = saida["r"]
    assert dict(carga) == {1: 10} and len(semana_de) == 1, "so a linha que cabe e agendada"


def test_parametro_invalido_e_recusado_na_carga(tmp_path):
    """Erro de digitacao nos parametros vira RECUSA com nome do campo -- bloco fora do
    rodizio travava a intercalacao; piso > teto invertia a escolha em silencio."""
    base = json.load(open(trilha.P_PARAMETROS, encoding="utf-8"))
    for campo, valor, trecho in (("bloco_de_area", {"Pediatria": "PEDS"}, "bloco_de_area"),
                                 ("piso", 0.30, "piso <= teto"),
                                 ("cap_listas", dict(base["cap_listas"], **{"8": 10}),
                                  "semana sem calendario")):
        ruim = dict(base, **{campo: valor})
        p = tmp_path / ("p_%s.json" % campo)
        p.write_text(json.dumps(ruim, ensure_ascii=False), encoding="utf-8")
        with pytest.raises(ValueError, match=trecho):
            trilha.carregar_parametros(str(p))


def test_fronteira_de_fase_nao_diverge_de_plano_py():
    assert trilha.PRIMEIRA_SEMANA_FASE2 == plano.semana_fase2(21)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
