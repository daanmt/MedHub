"""test_sem_caracter_de_controle.py -- nenhum fonte carrega caracter de controle (s187).

🔴 **Este repo ja foi mordido DUAS vezes pelo mesmo byte, e a segunda fui eu.**

  1. `AUDITORIA_MEDHUB.md` registra, na entrada do `audit_resumos`: *"um regex
     corrompido por 0x08 passou despercebido na 1a escrita: linter verde, check
     morto"*.
  2. Na s187, escrevendo `tools/selo.py` por heredoc, escrevi `\\b` dentro de uma
     string Python **nao-raw**. O `\\b` virou **backspace (0x08)** e foi gravado
     literalmente no arquivo. Dois regexes nasceram corrompidos:
       - `(?:[^*]*<0x08>)?(?:RESOLVID...)` -- nunca casava, e **todo achado
         RESOLVIDO do ledger aparecia como "SEM TERMINAL"** no selo;
       - `atualiza[cç][aã]o<0x08>` -- o dedupe de secao de continuacao morria.
     O modulo importava sem erro, os testes nao existiam ainda, e a saida era
     *plausivel* -- so nao era verdade.

**Por que vira gate e nao licao:** o defeito e invisivel por construcao. O byte
nao aparece no editor, o Python nao reclama, o regex compila e simplesmente
**nunca casa**. E a forma mais pura de *sensor que existe, roda e nao alcanca* --
a pergunta que organiza a janela inteira.

Nasce BLOCK: a base e ZERO por construcao (varri e limpei os 2 no mesmo commit).

⚠️ **Escopo declarado:** cobre `tools/`, `app/` e `core/` -- codigo e dado
versionado. Nao cobre `resumos/` (conteudo clinico, onde o `audit_resumos` ja tem
o check de encoding) nem `history/` (registro historico, imutavel por contrato).
Tab e newline sao legitimos e ficam de fora.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# C0 control chars menos os tres legitimos: \t (09), \n (0A), \r (0D).
PROIBIDOS = bytes(b for b in range(0x00, 0x20) if b not in (0x09, 0x0A, 0x0D))
DIRS = ("tools", "app", "core")
EXTS = (".py", ".json", ".md", ".html", ".ini")


def _fontes():
    for d in DIRS:
        base = os.path.join(ROOT, d)
        for raiz, subdirs, arquivos in os.walk(base):
            subdirs[:] = [s for s in subdirs if s not in ("__pycache__", "_archive", "chroma")]
            for a in arquivos:
                if a.endswith(EXTS):
                    yield os.path.join(raiz, a)


def test_nenhum_fonte_tem_caracter_de_controle():
    achados = []
    for caminho in _fontes():
        with open(caminho, "rb") as fh:
            dados = fh.read()
        for b in PROIBIDOS:
            i = dados.find(bytes([b]))
            if i >= 0:
                linha = dados[:i].count(b"\n") + 1
                rel = os.path.relpath(caminho, ROOT).replace("\\", "/")
                achados.append(f"{rel}:{linha} tem 0x{b:02X}")
    assert achados == [], (
        "caracter de controle em fonte -- o defeito e INVISIVEL no editor e faz regex "
        "compilar e nunca casar (s187, `selo.py`): " + "; ".join(achados[:10]))


def test_o_gate_pega_o_byte_plantado(tmp_path):
    """Um gate que nunca viu um positivo e um gate nao testado. Reproduz o caso
    real: `\\b` numa string nao-raw virando backspace dentro de um regex."""
    alvo = tmp_path / "corrompido.py"
    alvo.write_bytes('rx = re.compile(r"atualiza\x08")\n'.encode("utf-8"))
    dados = alvo.read_bytes()
    encontrados = [b for b in PROIBIDOS if bytes([b]) in dados]
    assert encontrados == [0x08]


def test_o_regex_corrompido_de_fato_nunca_casa():
    """A prova do dano, nao so da presenca: e por isso que o byte e grave."""
    import re
    # Os padroes REAIS do selo.py, com e sem o byte. O prefixo `\*\*` e o que torna
    # a corrupcao fatal: com o grupo opcional vazio, o regex passa a exigir
    # `**RESOLVIDOS` colado, e o ledger escreve `** 12/12 RESOLVIDOS`. Sem esse
    # prefixo a diferenca some -- foi o que a 1a versao deste teste errou.
    bom = re.compile(r"\*\*(?:[^*]*)?(?:RESOLVID[OA]S?)")
    ruim = re.compile("\\*\\*(?:[^*]*\x08)?(?:RESOLVID[OA]S?)")
    alvo = "-- **MEDIA (agregado)** -- **12/12 RESOLVIDOS (contado)**"
    assert bom.search(alvo), "o regex integro tem que casar"
    assert not ruim.search(alvo), "o corrompido nao casa -- e foi isso que zerou o selo"


def test_escopo_do_gate_esta_declarado():
    doc = sys.modules[__name__].__doc__.replace("*", "").lower()
    assert "escopo declarado" in doc
    assert "nao cobre" in doc
    assert list(_fontes()), "lista de fontes vazia tornaria o teste verde por vacuidade"
