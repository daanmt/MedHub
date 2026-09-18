"""lastro.py -- o tema clínico tem conteúdo escrito? Regra ÚNICA, por SEÇÃO.

F103/F106 (s185). Antes, o `[SEM-LASTRO]` do `insert_questao` casava o tema contra o
**nome do arquivo** (exato + fuzzy de stem). Um resumo guarda-chuva -- um `.md` que
cobre vários temas em seções -- ficava invisível, e a pendência "criar resumo" que isso
gera produziria um **duplicado**. Foi o que quase aconteceu com `Rede de Atenção
Psicossocial (RAPS)`, que estava na fila como tarefa e já tinha `## 4.` dedicado em
`Psiquiatria Social e Reforma Psiquiátrica.md`.

🔴 A REGRA É POR SEÇÃO, NUNCA POR MENÇÃO SOLTA. Camadas, na ordem, e cada veredito
positivo devolve o **motivo** (bool sozinho não é auditável):

  1. `arquivo`  -- nome do `.md` casa o tema (exato ou fuzzy de stem; o que já existia).
  2. `pdf`      -- existe PDF-fonte par na taxonomia EMED (o que já existia).
  3. `secao`    -- um heading `#..####` de algum resumo casa o tema.
  4. `alias`    -- o tema aparece no `aliases:` do frontmatter de algum resumo.
  5. `mapa`     -- `core/lastro_alias.json`, escape hatch MANUAL para o que as camadas
                   acima não alcançam. Vazio por padrão: entrada aqui é dívida declarada,
                   não solução.

⚠️ O QUE FOI DELIBERADAMENTE DEIXADO DE FORA: **conteúdo solto no corpo**. Medido em
17/09/2026, `Esquistossomose` aparece 1 vez em `Parasitoses.md:43` -- uma armadilha sobre
a forma hepatoesplênica dentro de um diferencial de cirrose. Contar isso como lastro
inflaria a cobertura exatamente como o `cli_signature_check` inflava ao casar flag por
presença de string ("string presente != coberto"). O `[SEM-LASTRO]` para esse tema está
CERTO, e o F106 -- que afirmava o contrário -- é achado falso.

⚠️ LIMITE DECLARADO: a camada 3 casa duas palavras quando o **prefixo comum vale >= 75%
da mais longa** (dobrado sem acento). Isso separa flexão de radical coincidente --
`intestinais` x `Intestinal` = 9/11 = 0,82 passa; `quantica` x `quantitativos` = 6/13 = 0,46
não passa. A régua anterior, de prefixo fixo de 6, dava lastro a um tema inventado contra
`## Distúrbios Plaquetários Quantitativos`; foi a suíte que pegou. Ainda assim é **sintático**:
não sabe sinonímia (`AVC` x `acidente vascular encefálico`).
Para isso existe a camada 5, e ela é manual de propósito -- um mapa que alguém mantém é
honesto; um matcher semântico que erra em silêncio, não.

📏 RAIO MEDIDO (17/09/2026, 302 temas da taxonomia): 16 temas ganham lastro pelas camadas
3-4 que a regra antiga não via -- `Nefropatia Diabetica` -> Diabetes/Complicações,
`Asma - Exacerbacao` -> Asma.md, `Infeccao Latente por Tuberculose` -> Tuberculose.md,
`Sindrome Antifosfolipide` -> Hemostasia.md, `RAPS` -> Psiquiatria Social. 15 dos 16 são
inequívocos a olho. O 16º, `Rastreamento e prevenção`, casa com a seção homônima de
`Tumores Anexiais e Câncer de Ovário.md` -- e é **fraco por o nome do tema ser genérico**,
não por falha da regra: qualquer regra sintática casaria. Fica declarado em vez de
maquiado. (A régua anterior, de um token forte, dava 58 flips com erros grosseiros --
`Cancer de Pulmao - Estadiamento` -> `Urologia.md`.)

CONSERVADOR POR CONTRATO (herdado do F31): se não consegue nem checar (raiz ausente,
erro de leitura), devolve `(True, "indeterminado: ...")`. Nunca acusar ausência de lastro
por falha de leitura -- o par Siamese Twins só é sinalizado quando a ausência é
POSITIVAMENTE confirmada.
"""

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MAPA = ROOT / "core" / "lastro_alias.json"

#: conectivos e termos genéricos demais para servirem de evidência sozinhos
_STOP = {
    "de", "da", "do", "das", "dos", "e", "em", "no", "na", "nos", "nas", "a", "o",
    "as", "os", "para", "por", "com", "sem", "ao", "aos", "the", "geral", "gerais",
    "outros", "outras", "parte", "tipo", "tipos", "caso", "casos", "aspectos",
}
_RATIO = 0.75         #: prefixo comum / palavra mais longa -- separa flexao de radical coincidente


def _dobrar(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).casefold()


def _tokens(tema):
    brutos = re.findall(r"[A-Za-zÀ-ÿ]{3,}", tema or "")
    return [_dobrar(t) for t in brutos if _dobrar(t) not in _STOP]


def _mesma_palavra(a, b):
    """Flexao da MESMA palavra, nao radical coincidente.

    O prefixo comum tem de valer >= _RATIO da palavra mais longa. `intestinais`
    x `intestinal` = 9/11 = 0,82 (passa); `quantica` x `quantitativos` = 6/13 =
    0,46 (nao passa -- foi o falso positivo que a suite pegou, casando o tema
    contra `## Disturbios Plaquetarios Quantitativos`).
    """
    n = 0
    for ca, cb in zip(a, b):
        if ca != cb:
            break
        n += 1
    return n / max(len(a), len(b), 1) >= _RATIO


def _casa(tokens, texto):
    """TODOS os tokens do tema presentes no heading -- precisao, nao recall.

    🔴 A versao anterior aceitava UM token forte (>=7) e foi medida como frouxa
    demais: 58 temas mudavam de veredito e varios errados -- `Cancer de Pulmao -
    Estadiamento` casava com um heading de `Urologia.md`, `Controle de Hemorragia
    Exsanguinante (ATLS)` com `Assistencia ao Parto.md`. Palavras como hemorragia,
    neoplasias, tumores e trauma aparecem em heading de meio corpus.

    A assimetria de custo manda em precisao: um falso "tem lastro" ESCONDE resumo
    faltante e e invisivel; um falso "nao tem" so gera uma conferencia. Exigir o
    heading inteiro equivale a "existe secao intitulada com este tema" -- que e o
    que lastro deveria significar. O que essa regra nao alcanca cai na camada 5,
    que e manual de proposito.
    """
    if not tokens:
        return False
    palavras = set(re.findall(r"[a-z]+", _dobrar(texto)))
    return all(any(_mesma_palavra(t, p) for p in palavras) for t in tokens)


def _por_nome_ou_pdf(tema, raiz):
    """Camadas 1 e 2 -- o que já existia em `insert_questao._tem_lastro`."""
    try:
        import importlib
        gtc = importlib.import_module("app.engine.get_topic_context")
        if gtc._find_resumo(tema) is not None:
            return "arquivo"
    except Exception:
        pass
    alvo = _dobrar(tema)
    if alvo:
        for p in raiz.rglob("*"):
            if p.suffix.lower() == ".pdf" and alvo in _dobrar(p.stem):
                return "pdf"
    return None


def tem_lastro(tema, raiz=None):
    """(bool, motivo). Veja a docstring do módulo para as 5 camadas e os limites."""
    raiz = Path(raiz) if raiz else (ROOT / "resumos")
    if not raiz.is_dir():
        return True, f"indeterminado: raiz de resumos ausente ({raiz})"
    tokens = _tokens(tema)
    if not tokens:
        return True, "indeterminado: tema sem token utilizavel"

    motivo = _por_nome_ou_pdf(tema, raiz)
    if motivo:
        return True, motivo

    try:
        for p in raiz.rglob("*.md"):
            if p.name == "INDEX.md":
                continue
            try:
                texto = p.read_text(encoding="utf-8")
            except Exception:
                continue
            for linha in texto.splitlines():
                s = linha.strip()
                if s.startswith("#") and _casa(tokens, s.lstrip("#")):
                    return True, f"secao: {p.name}"
                if s.startswith("aliases:") and _casa(tokens, s):
                    return True, f"alias: {p.name}"
    except Exception as e:
        return True, f"indeterminado: varredura falhou ({e})"

    try:
        if MAPA.exists():
            mapa = json.loads(MAPA.read_text(encoding="utf-8"))
            chave = _dobrar(tema)
            for k, v in mapa.items():
                if _dobrar(k) == chave:
                    return True, f"mapa: {v}"
    except Exception:
        pass

    return False, None
