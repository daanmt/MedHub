import json
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Ledger-of-self: import resiliente — sem o modulo, a deteccao segue intacta.
try:
    sys.path.insert(0, str(ROOT_DIR / "tools"))
    from ledger_self import record as _ledger_record
except Exception:
    def _ledger_record(check, findings, root=None):
        pass

# --- Constantes de path ---
WATERMARK_PATH = ROOT_DIR / "history" / "card_watermark.json"
LIMITE_HANDOFF = 60


def _warn_total(output):
    """Extrai WARN_TOTAL da linha machine-readable do audit_resumos. 0 se ausente."""
    m = re.search(r"WARN_TOTAL=(\d+)", output)
    return int(m.group(1)) if m else 0


# ---------------------------------------------------------------------------
# Watermark de dado dos cards (Part-6, flashcards-integridade)
# ---------------------------------------------------------------------------

def card_watermark_atual(db_path=None):
    """Tripla do estado atual do dado, ou None se o banco esta inacessivel."""
    import sqlite3
    dbp = Path(db_path) if db_path else ROOT_DIR / "ipub.db"
    try:
        con = sqlite3.connect(f"file:{dbp.as_posix()}?mode=ro", uri=True)
        try:
            row = con.execute(
                "SELECT COALESCE(MAX(id), 0), COUNT(*), COALESCE(MAX(card_version), 0) "
                "FROM flashcards").fetchone()
        finally:
            con.close()
        return {"max_id": row[0], "count": row[1], "max_version": row[2]}
    except Exception as e:
        print(f"[WARN] CARD_WATERMARK: banco inacessivel ({e}) — "
              f"checks de card rodam por precaucao (fail-open).")
        return None


def card_watermark_mudou(db_path=None, marco_path=None):
    """(mudou: bool, atual) — True quando o dado avancou desde o ultimo marco."""
    atual = card_watermark_atual(db_path)
    if atual is None:
        return True, atual
    mp = Path(marco_path) if marco_path else WATERMARK_PATH
    if not mp.exists():
        return True, atual
    try:
        antigo = json.loads(mp.read_text(encoding="utf-8"))
    except Exception:
        print("[WARN] CARD_WATERMARK: marco ilegivel — tratado como 'mudou'.")
        return True, atual
    return antigo != atual, atual


def card_watermark_selar(atual, marco_path=None):
    """Persiste o marco — chamar SO depois que os checks de card rodaram."""
    if atual is None:
        return
    mp = Path(marco_path) if marco_path else WATERMARK_PATH
    try:
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(json.dumps(atual), encoding="utf-8")
    except Exception as e:
        print(f"[WARN] CARD_WATERMARK: falha ao selar o marco ({e}).")


# ---------------------------------------------------------------------------
# Invariantes macro de sesssao / HANDOFF
# ---------------------------------------------------------------------------

def check_session_pointer(handoff_path=None, history_dir=None):
    """Condição B2 do reconcile-contract (descolar part-4): o ponteiro de sessão do HANDOFF
    tem que apontar sessão REAL — `history/session_NNN.md` existe — ou a PRÓXIMA (max+1,
    a sessão em curso cujo log nasce no fechamento). Retorna (pointer, max, tipo) com tipo
    'alem_do_max' | 'arquivo_ausente'; None = ok. (Antes: só o caso aparentado >max+1, como
    WARN — F56: o contrato declarava BLOCKING e o código rebaixava em silêncio.)"""
    handoff = Path(handoff_path) if handoff_path else ROOT_DIR / "HANDOFF.md"
    history = Path(history_dir) if history_dir else ROOT_DIR / "history"
    if not handoff.exists() or not history.is_dir():
        return None
    try:
        text = handoff.read_text(encoding="utf-8")
    except Exception:
        return None
    nums = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("*Atualizado") or (
                s.startswith("#") and re.search(r"pr[oó]ximo passo", s, re.IGNORECASE)):
            # IGNORECASE (part-4): o HANDOFF real grafa 'S160' e o parser só via 's160' —
            # o check inteiro no-opava em silêncio.
            nums += [int(n) for n in re.findall(r"\bs(\d{2,3})\b", s, re.IGNORECASE)]
    if not nums:
        return None
    sessions = []
    for p in history.rglob("session_*.md"):
        m = re.fullmatch(r"session_(\d+)", p.stem)
        if m:
            sessions.append(int(m.group(1)))
    if not sessions:
        return None
    pointer, max_sess = max(nums), max(sessions)
    if pointer > max_sess + 1:
        return (pointer, max_sess, "alem_do_max")
    if pointer <= max_sess and not any(history.rglob(f"session_{pointer:03d}.md")):
        return (pointer, max_sess, "arquivo_ausente")
    return None


def check_rag_staleness(root=None):
    """F48 (descolar part-5): índice RAG stale sem sensor — 6 chunks serviam texto velho.
    Compara o mtime máximo de resumos/**/*.md com o carimbo `data/chroma/index_meta.json`
    (gravado por `rag.index_all`). Retorna (n_mais_novos, carimbo|None); None = tudo em dia.
    Sem carimbo = (n_resumos, None): 'indexação sem carimbo — re-rode index_resumos'."""
    base = Path(root) if root else ROOT_DIR
    resumos = base / "resumos"
    if not resumos.is_dir():
        return None
    try:
        import json
        from datetime import datetime
        meta = base / "data" / "chroma" / "index_meta.json"
        arquivos = [p for p in resumos.rglob("*.md") if p.name != "INDEX.md"]
        if not arquivos:
            return None
        if not meta.exists():
            return (len(arquivos), None)
        carimbo = json.loads(meta.read_text(encoding="utf-8")).get("indexed_at")
        # tolerância de 2s: o carimbo tem resolução de segundos e é gravado logo APÓS a
        # indexação dos arquivos — sem a folga, todo run acusaria os próprios arquivos.
        ts = datetime.fromisoformat(carimbo).timestamp() + 2.0
        novos = sum(1 for p in arquivos if p.stat().st_mtime > ts)
        return (novos, carimbo) if novos else None
    except Exception:
        return None


def check_needs_qualitative(db_path=None):
    """F52(b) (descolar part-4): `needs_qualitative=1` em card na fila ATIVA (state<2) viola
    o invariante do contrato FSRS e não tinha sensor (6 cards medidos na s160). Retorna a
    contagem (>0) ou None. mode=ro, fail-open (sensor indisponível = None, nunca crash)."""
    dbp = Path(db_path) if db_path else ROOT_DIR / "ipub.db"
    if not dbp.exists():
        return None
    try:
        import sqlite3
        con = sqlite3.connect(f"file:{dbp.as_posix()}?mode=ro", uri=True)
        try:
            n = con.execute(
                "SELECT COUNT(*) FROM flashcards f JOIN fsrs_cards c ON c.card_id = f.id "
                "WHERE f.needs_qualitative = 1 AND c.state < 2").fetchone()[0]
        finally:
            con.close()
        return int(n) if n else None
    except Exception:
        return None


def check_posicao_drift(handoff_path=None, db_path=None):
    """Invariante POSICAO_DRIFT: semana do HANDOFF nao pode divergir da SSOT do db."""
    handoff = Path(handoff_path) if handoff_path else ROOT_DIR / "HANDOFF.md"
    dbp = Path(db_path) if db_path else ROOT_DIR / "ipub.db"
    if not handoff.exists() or not dbp.exists():
        return None
    con = None
    try:
        import sqlite3
        con = sqlite3.connect(str(dbp))
        row = con.execute(
            "SELECT valor FROM preparacao_estado WHERE chave='semana_conteudo'"
        ).fetchone()
    except Exception:
        return None
    finally:
        if con is not None:
            con.close()
    if not row:
        return None
    try:
        semana_db = int(row[0])
    except (TypeError, ValueError):
        return None
    try:
        text = handoff.read_text(encoding="utf-8")
    except Exception:
        return None
    mencoes = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("- **Posicao:**"):
            mencoes += [int(n) for n in re.findall(r"conteudo\s+S(\d{1,2})\b", s)]
        elif s.startswith("*Atualizado") or (
                s.startswith("#") and re.search(r"pr[oó]ximo passo", s, re.IGNORECASE)):
            mencoes += [int(n) for n in re.findall(r"\bS(\d{1,2})\b", s)]
    if not mencoes:
        return None
    divergentes = [m for m in mencoes if m != semana_db]
    if divergentes:
        return (divergentes[0], semana_db)
    return None


def check_handoff_len(handoff_path=None, limite=LIMITE_HANDOFF):
    """Condicao B1 (reconcile-contract.md) — BLOCKING.

    Retorna (n_linhas, limite) quando estoura; None quando dentro do teto.
    """
    handoff = Path(handoff_path) if handoff_path else ROOT_DIR / "HANDOFF.md"
    if not handoff.exists():
        return None
    try:
        texto = handoff.read_text(encoding="utf-8")
    except Exception:
        return None
    n = len(texto.splitlines())
    return (n, limite) if n > limite else None


# ---------------------------------------------------------------------------
# F38 (AUDITORIA_MEDHUB) -- erros analisados que nao chegam a `questoes_erros`.
#
# O pipeline de analise tem DOIS finais: `insert_questao.py` (erro completo +
# cards) e `habilidades.py --add` (so a habilidade). Quando o agente SUBSTITUI
# um pelo outro em vez de encadear, o bloco entra em `sessoes_bulk` com N erros
# de volume e `questoes_erros` nao recebe uma linha -- os cards nascem sem
# ancora (`questao_id=NULL`) e o substrato canonico (tipo_erro, alternativa
# marcada, explicacao) so existe em prosa no log da sessao.
#
# 🔴 Fronteira: este check e um GUARDA DE REGRESSAO, nao um remendo. Ele nao
# recupera analise perdida -- so impede que a proxima passe silenciosa.
#
# Duas defesas contra falso positivo, ambas exigidas pelo proprio F38:
#   1. Volume importado da planilha (`/importar-planilha`) traz feitas/acertos
#      SEM os erros terem sido itemizados -- ausencia esperada, nao defeito.
#      Filtrado por `observacoes` de migracao historica.
#   2. Registro TARDIO e a norma, nao a excecao (o erro costuma entrar no dia
#      seguinte ao estudo). A janela de credito e d..d+1.
#
# 📐 Calibracao medida no historico real (52 dias-bloco, 790 erros esperados),
#    nao arbitrada: com janela d+1 o check acusa 1 dia e ele e VERDADEIRO
#    (2026-06-18, s085, Pediatria 38/23 -- "Ictericia e Sepse Neonatal" tem 26
#    cards e ZERO erros no db, assinatura exata do F38), com zero falsos
#    positivos. Com d+2 o unico positivo verdadeiro DESAPARECE: os 19 erros
#    registrados em 20/06 sao de Cirurgia/GO/Exantematicas, tema nenhum em
#    comum com o bloco de 18/06. Alargar a janela compra silencio, nao precisao.
# ---------------------------------------------------------------------------
MARCADORES_VOLUME_IMPORTADO = ("migracao historica", "migração histórica")
PISO_ERROS_ORFAOS = 3          # abaixo disso o sinal e ruido de bloco pequeno
JANELA_CREDITO_DIAS = 1        # d..d+1 conta como registro do bloco de d


def check_erros_orfaos(db_path=None, piso=PISO_ERROS_ORFAOS, desde=None):
    """Invariante F38: bloco com erros de volume tem que ter erro estruturado.

    Retorna lista de (data_sessao, n_erros_esperados) para os dias-bloco em que
    `sessoes_bulk` acusa >= `piso` erros e `questoes_erros` nao recebeu NENHUMA
    linha na janela de credito. None quando limpo (mesma convencao dos demais
    checks deste modulo).

    `desde` (ISO date, opcional) limita a varredura; sem ele varre o historico
    inteiro -- e barato (dezenas de dias-bloco) e o defeito e retroativo por
    natureza, entao truncar a janela esconderia exatamente o que se procura.
    """
    dbp = Path(db_path) if db_path else ROOT_DIR / "ipub.db"
    if not dbp.exists():
        return None
    con = None
    try:
        import sqlite3
        con = sqlite3.connect(str(dbp))
        filtro_import = " AND ".join(
            "LOWER(COALESCE(observacoes,'')) NOT LIKE ?" for _ in MARCADORES_VOLUME_IMPORTADO)
        params = [f"%{m}%" for m in MARCADORES_VOLUME_IMPORTADO]
        sql = (f"SELECT data_sessao, SUM(questoes_feitas - questoes_acertadas) esperados "
               f"FROM sessoes_bulk WHERE {filtro_import}")
        if desde:
            sql += " AND data_sessao >= ?"
            params.append(desde)
        sql += " GROUP BY data_sessao HAVING esperados >= ? ORDER BY data_sessao"
        params.append(piso)
        dias = con.execute(sql, params).fetchall()
        orfaos = []
        for data_sessao, esperados in dias:
            registrados = con.execute(
                "SELECT COUNT(*) FROM questoes_erros "
                "WHERE date(data_registro) BETWEEN ? AND date(?, ?)",
                (data_sessao, data_sessao, f"+{JANELA_CREDITO_DIAS} day")).fetchone()[0]
            if registrados == 0:
                orfaos.append((data_sessao, int(esperados)))
    except Exception:
        return None
    finally:
        if con is not None:
            con.close()
    return orfaos or None


# ---------------------------------------------------------------------------
# F43 (s159) -- suite que existe e nao roda.
#
# "Quais testes rodam" nao tem UM registro: tem TRES, todos mantidos a mao e
# nenhum ciente do outro --
#   1. `pytest.ini` -> `python_files` (allowlist explicita);
#   2. `tools/auto_check.py` -> suites invocadas por nome no harness;
#   3. `tools/test_pytest_bridge.py` -> os script-style rodados por subprocess.
# Uma suite fora dos tres existe, passa no code review, e nunca executa. E o
# mesmo modo de falha do D4/alcancabilidade ("artefato que funciona e ninguem
# alcanca") e do que atingiu `test_handoff_teto` na s156 -- com a diferenca de
# que la o arquivo estava registrado e a coleta e que quebrou.
#
# Nao ha orfa hoje (37/37 cobertas). Este check existe para que continue assim:
# o autor da proxima suite descobre que esqueceu de inscrever ANTES do commit,
# nao tres sessoes depois.
# ---------------------------------------------------------------------------
REGISTROS_DE_SUITE = (
    ("pytest.ini", "python_files"),
    ("tools/auto_check.py", None),
    ("tools/test_pytest_bridge.py", None),
)


def check_suites_orfas(root=None):
    """Invariante F43: toda `tools/test_*.py` citada em >= 1 registro de execucao.

    Retorna lista dos nomes orfaos; None quando todas cobertas (mesma convencao
    dos demais checks). Tolerante: registro ausente/ilegivel apenas nao cobre
    nada -- nunca levanta.
    """
    base = Path(root) if root else ROOT_DIR
    tools_dir = base / "tools"
    if not tools_dir.is_dir():
        return None
    suites = sorted(p.name for p in tools_dir.glob("test_*.py"))
    if not suites:
        return None
    corpus = []
    for rel, _campo in REGISTROS_DE_SUITE:
        alvo = base / rel
        try:
            corpus.append(alvo.read_text(encoding="utf-8"))
        except Exception:
            continue
    if not corpus:
        return None
    blob = "".join(corpus)   # busca por substring: separador e irrelevante
    orfas = [nome for nome in suites if nome not in blob]
    return orfas or None
