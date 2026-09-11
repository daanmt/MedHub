"""test_vocab_memoria.py -- F66: a memoria de fraquezas para de ser orfa por ABREVIACAO (s176, 1.3).

O defeito medido: o vocabulario canonico usa forma CURTA (`Infecto`, `Gastro`, `Hepato`) e o
modelo que consolida a memoria escreve a forma LONGA. `_norm` faz casefold + remocao de acento e
declara na propria docstring que **nao faz substring** -- logo `Infectologia` nunca casava
`Infecto`. O dado estava certo e era descartado.

Duas consequencias, ambas medidas: (1) area orfa nunca casa `error_count`, entao **nunca sobe no
ranking de fraquezas que o agente le no PRIMEIRO turno de toda sessao**; (2) o log crescia
~111-139 linhas por consolidacao, para sempre, tornando a linha "memory_errors.log: N" do painel
estritamente sem significado (media quantas vezes o sensor rodou, nao quanta divida existe).

Medicao desta sessao (10/09/2026, store real):
  ANTES  299 WeakAreas · 140 fora do vocabulario (47%) · 91 rotulos distintos
  DEPOIS 290 WeakAreas (9 duplicatas colapsadas) · 100 fora (34%) · 75 normalizadas
"""
import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import app.utils.areas as areas               # noqa: E402
import app.memory.manager as manager          # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --- (a) alias explicito, medido no store, num portador versionado -------------------

def test_as_8_areas_orfas_mais_frequentes_resolvem():
    """Os rotulos e as contagens sao os MEDIDOS, nao exemplos inventados."""
    for rotulo, canonico in (("Infectologia", "Infecto"),        # 11x
                             ("Dermatologia", "Dermato"),        # 8x
                             ("Hepatologia", "Hepato"),          # 6x
                             ("Cirurgia Geral", "Cirurgia"),     # 4x
                             ("Pneumologia", "Pneumo"),          # 3x
                             ("Gastroenterologia", "Gastro"),    # 3x
                             ("Atenção Primária", "Preventiva"),  # 3x
                             ("Endocrinologia", "Endocrino")):   # 3x
        assert areas.resolver_area(rotulo) == canonico, f"{rotulo} deveria resolver"


def test_forma_canonica_e_variacoes_de_caixa_acento_resolvem():
    assert areas.resolver_area("Infecto") == "Infecto"
    assert areas.resolver_area("  obstetricia  ") == "Obstetrícia", "sem acento resolve"
    assert areas.resolver_area("OBSTETRÍCIA") == "Obstetrícia"
    assert areas.resolver_area("Endocrinology") == "Endocrino", "ingles medido no store"


def test_composto_resolve_pelo_prefixo():
    """O modelo escreve `area - tema` dentro do campo `area` -- medido 8x no store."""
    assert areas.resolver_area("Pediatria - Sepse Neonatal") == "Pediatria"
    assert areas.resolver_area("Pediatria - Icterícia Neonatal") == "Pediatria"
    assert areas.resolver_area("Infectologia - Arboviroses") == "Infecto", "prefixo + alias"


# --- o que NAO resolve, e por que isso e correto ------------------------------------

def test_rotulo_ambiguo_NAO_resolve():
    """Chutar repetiria o erro da s110 (3 linhas de `Clinica Medica` eram Infecto,
    Hemato e Oftalmo). Ambiguo vira divida DECLARADA, nao palpite."""
    for rotulo in ("Ginecologia-Obstetrícia - Pré-Natal", "Clínica Médica", "Clinica Geral",
                   "GO"):
        assert areas.resolver_area(rotulo) is None, f"{rotulo} nao pode resolver: e ambiguo"


def test_rotulo_que_nao_e_area_NAO_resolve():
    """`Conhecimento Desatualizado` e habilidade, `Interpretação de Exames` e tema.
    Forcar um casamento aqui corromperia o ranking com dado errado."""
    for rotulo in ("Conhecimento Desatualizado", "Interpretação de Exames", "Todas",
                   "Hemostasia", "DM2 Management"):
        assert areas.resolver_area(rotulo) is None


def test_especialidade_legitima_SEM_area_canonica_fica_como_divida():
    """`Oncologia`, `Urologia`, `Radiologia` sao especialidades reais e NAO estao na lista
    canonica. O sink as torna contaveis -- acrescentar area e decisao do OPERADOR."""
    for rotulo in ("Oncologia", "Urologia", "Radiologia", "Medicina de Emergência"):
        assert areas.resolver_area(rotulo) is None, \
            f"{rotulo}: resolver isto seria inventar area que a lista nao tem"


def test_resolver_nunca_levanta_nem_inventa():
    for ruim in (None, "", "   ", 123, "xpto-inexistente"):
        assert areas.resolver_area(ruim) is None


# --- a fronteira leitura x escrita -------------------------------------------------

def test_o_gate_de_ESCRITA_nao_herda_a_tolerancia_da_LEITURA():
    """`resolver_area` e para rotulo livre (memoria). `validar_area` continua exigindo a
    forma canonica exata -- na escrita, adivinhar e o defeito (F89)."""
    assert areas.resolver_area("Infectologia") == "Infecto"
    try:
        areas.validar_area("Infectologia")
        assert False, "o gate de escrita nao pode aceitar a forma longa"
    except areas.AreaInvalida:
        pass


# --- (b) o vocabulario deixou de vir da taxonomia poluida ---------------------------

def test_vocabulario_vem_do_canonico_e_nao_da_taxonomia():
    """A taxonomia carregava `GO`, `Clinica Medica`, `Clínica Médica` e
    `Clinica Medica/Cardiologia` como 'areas canonicas' -- o vocabulario que validava a
    memoria era ele mesmo poluido (F89). Agora nao ha o que sanear."""
    vocab = manager._vocabulario_taxonomia(manager._IPUB_PATH)
    canonicos = set(vocab.values())
    assert canonicos == set(areas.AREAS_VALIDAS)
    for fantasma in ("GO", "Clinica Medica", "Clínica Médica", "Clinica Medica/Cardiologia"):
        assert fantasma not in canonicos, f"fantasma {fantasma!r} de volta no vocabulario"


# --- (c) o sink e IDEMPOTENTE: conta item aberto, nao vezes que o sensor rodou -------

def test_sink_conta_item_aberto_e_nao_acumula():
    with tempfile.TemporaryDirectory() as d:
        alvo = os.path.join(d, "pend.json")
        manager._gravar_pendentes_vocab({"k1": {"area": "Oncologia"},
                                         "k2": {"area": "Todas"}}, path=alvo)
        d1 = json.load(io.open(alvo, encoding="utf-8"))
        assert d1["total"] == 2
        # segunda passagem com os MESMOS itens -> continua 2 (o log antigo diria 4)
        manager._gravar_pendentes_vocab({"k1": {"area": "Oncologia"},
                                         "k2": {"area": "Todas"}}, path=alvo)
        assert json.load(io.open(alvo, encoding="utf-8"))["total"] == 2, \
            "sink que acumula mede o sensor, nao a divida"
        # item resolvido -> o numero CAI, que e o que o painel precisava
        manager._gravar_pendentes_vocab({"k2": {"area": "Todas"}}, path=alvo)
        assert json.load(io.open(alvo, encoding="utf-8"))["total"] == 1


def test_sink_nunca_derruba_a_consolidacao():
    """Falha ao gravar o sink e registrada, nunca propagada."""
    assert manager._gravar_pendentes_vocab({"k": {}}, path=os.path.join(
        "Z:", "caminho", "que", "nao", "existe", "p.json")) == 1


def test_painel_cita_o_sink_e_rotula_o_log_como_falha():
    with open(os.path.join(ROOT, "tools", "ledger_self.py"), encoding="utf-8") as fh:
        fonte = fh.read()
    assert "wa_vocab_pendentes.json" in fonte, "o painel tem que citar o sink"
    assert "log de FALHA, nao de divida" in fonte, \
        "o contador de linhas do log precisa vir rotulado pelo que ele realmente mede"


if __name__ == "__main__":
    falhas = 0
    for nome, fn in sorted(list(globals().items())):
        if nome.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  OK   {nome}")
            except AssertionError as e:
                falhas += 1
                print(f"  FALHA {nome}: {e}")
    print(f"\n{'FALHOU' if falhas else 'PASSOU'} -- {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
