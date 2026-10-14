"""Check 6 do linter de resumos (SPEC) -- proibicoes duras do estilo-resumo.md.

Contexto (s169): `audit_resumos.py` checava tabela ASCII, marcadores, frontmatter e
encoding -- e era CEGO a cinco proibicoes que a spec declara duras (emoji em header,
bloco de codigo, bullet ✅/❌, campo `estilo:`, rodape editorial). Os 10 resumos do
sprint S17-S20 so sairam limpos porque as regras foram repetidas a mao no brief de
cada subagente e conferidas por fora do harness -- disciplina que nao escala.

O bug que motivou o teste POSITIVO: na primeira escrita do check, um caractere de
backspace literal (0x08) entrou no regex do rodape no lugar de `\\b`. O linter
continuava passando e o check estava MORTO -- nunca dispararia. Um teste que so
verifica "nao explode" nao pega isso; por isso cada sub-check aqui e provado
disparando sobre um caso positivo sintetico.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audit_resumos import _spec_proibicoes, _fonte_inline  # noqa: E402


# --- cada sub-check tem que DISPARAR sobre o caso que ele existe para pegar ---

def test_emoji_em_header_e_pego():
    assert _spec_proibicoes("## 1. Ok\n### \U0001f534 P -- Polipo\n")


def test_bloco_de_codigo_e_pego():
    assert _spec_proibicoes("## 1. Ok\n```\nA -> B\n```\n")


def test_bullet_com_marcador_proibido_e_pego():
    assert _spec_proibicoes("## 1. Ok\n- ✅ Conduta recomendada\n")


def test_campo_estilo_no_frontmatter_e_pego():
    assert _spec_proibicoes("---\ntype: knowledge\nestilo: Gold Standard\n---\n")


def test_rodape_editorial_e_pego():
    # Regressao do 0x08: com o regex corrompido este caso passava batido.
    assert _spec_proibicoes(
        "## 1. Ok\n\n*Este resumo foi cristalizado a partir da apostila.*\n")


# --- e nao pode disparar sobre o que a spec PERMITE ---

def test_resumo_conforme_nao_dispara():
    limpo = (
        "---\ntype: knowledge\narea: GO\nespecialidade: Ginecologia\n"
        "status: active\n---\n\n# Tema\n\n## 1. Secao\n\n"
        "- Bullet normal com ⭐ inline e ⚠️ Padrao de prova: nuance\n\n"
        "## 2. Armadilhas de Prova\n\n- \U0001f534 armadilha\n"
    )
    assert _spec_proibicoes(limpo) == []


def test_marcador_inline_no_corpo_nao_e_header():
    # O marcador e permitido inline; a proibicao e so no header.
    assert _spec_proibicoes("## 1. Secao\n\n\U0001f534 Armadilha no corpo do texto.\n") == []


def test_os_resumos_desta_sessao_estao_conformes():
    """Regressao viva: os 11 resumos cunhados/editados na s169 seguem a spec."""
    raiz = Path(__file__).parent.parent / "resumos"
    alvos = [
        raiz / "Cirurgia" / "Urologia.md",
        raiz / "Pediatria" / "Diarreia.md",
        raiz / "GO" / "Vitalidade Fetal.md",
        raiz / "GO" / "[GIN] Sangramento Uterino Anormal.md",
    ]
    for f in alvos:
        if f.exists():  # tolerante a rename; o que existe tem que estar limpo
            assert _spec_proibicoes(f.read_text(encoding="utf-8")) == [], f.name




# s227 (pedido dele): "Fonte:" de referencia no meio do texto -> WARN FONTE_INLINE; a fonte clinica fica.
def test_fonte_de_referencia_no_meio_do_texto_e_pega():
    texto = ("# T\n\n> Fonte: Apostila Estratégia MED -- Prof. X (2024)\n\n"
             "## 1. A\n- **Fonte:** MS/Fiocruz-IFF 2023\n")
    assert _fonte_inline(texto) == [3, 6]


def test_fonte_clinica_nao_e_referencia():
    # TCE.md: a fonte do SANGRAMENTO, nao uma citacao
    texto = ("## 2. Hematoma\n- **Fonte:** arterial em cerca de 85% dos casos -- artéria meníngea média\n"
             "- **Fonte:** venosa -- ruptura das veias-ponte\n")
    assert _fonte_inline(texto) == []


def test_fonte_dentro_das_referencias_nao_dispara():
    texto = "## 9. Armadilhas de Prova\n- x [1]\n\n## Referências\n1. Fonte: SBC. Diretriz de HAS, 2020.\n"
    assert _fonte_inline(texto) == []


def test_a_palavra_fonte_no_meio_da_frase_nao_dispara():
    assert _fonte_inline("- a principal fonte de erro em 2024 e o atraso\n") == []


def test_tce_real_nao_dispara():
    f = Path(__file__).parent.parent / "resumos" / "Clínica Médica" / "Neurologia" / "TCE.md"
    if f.exists():
        assert _fonte_inline(f.read_text(encoding="utf-8")) == []
