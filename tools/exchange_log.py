"""exchange_log.py -- ledger append-only das trocas agente<->agente (canal direto).

PROVENIENCIA: adaptado de `tools/exchange_log.py` do agente irmao `/ai-eng`
(escrito por ele em 2026-09-08, s170), com autorizacao do operador. Motivo de
existir, na formulacao dele: handoff em arquivo morre, mensagem em transcript
evapora. Este ledger guarda CADA mensagem do canal cross-session (SendMessage)
com TEXTO INTEGRAL -- a memoria e o conteudo, nao o resumo.

O par de ledgers (o 'out' daqui + o 'out' do outro lado) reconstroi qualquer
troca sem depender de handoff: o que eu enviei esta aqui, o que ele enviou esta
la, e os dois juntos fecham a conversa.

DIFERENCAS PARA O ORIGINAL (2, ambas locais):
  - destino `history/exchange-log.jsonl` (o SSOT de historico do MedHub);
  - `LEDGER` era constante MORTA (append/read remontavam o caminho inline, em 2
    lugares). Agora e a fonte unica do caminho -- mesma doenca do achado G4
    desta sessao: numero/caminho em dois lugares que divergem.

Passo estrutural vive em hook, nao na memoria:
  PostToolUse matcher=SendMessage -> este script le o JSON do harness no stdin
  e grava 'out'. Mensagens RECEBIDAS chegam como turno de usuario (nao ha hook
  para elas): registro via --in (discricionario) ou --backfill.

Modos:
  (sem args, stdin JSON)   hook PostToolUse: grava a mensagem enviada
  --in --peer P --summary S --file F [--ts ISO]   registra mensagem recebida
  --backfill F.jsonl       importa registros prontos (mesmo schema)
  --report [N] [--full]    imprime os ultimos N registros (default 20)
Convencao no `summary` do SendMessage: comecar com "@peer:" ou "->peer:" faz o
hook preencher `peer`; sem isso `peer` fica vazio e `to` guarda o endereco cru.

Schema (1 JSON por linha): ts, dir (out|in), peer, to, session, msg_id, summary,
chars, sha (sha1 12 hex do texto), text. Append-only; nunca reescreve; exit 0
SEMPRE (um hook de registro jamais derruba o turno). stdlib only. UTF-8.
"""
import datetime
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join("history", "exchange-log.jsonl")
FIELDS = ("ts", "dir", "peer", "to", "session", "msg_id", "summary", "chars", "sha", "text")
PEER_RX = re.compile(r"^\s*(?:@|->|→)\s*([\w.-]+)\s*:")


def _now():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def _sha(text):
    return hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()[:12]


def make(direction, text, peer="", to="", session="", msg_id="", summary="", ts=None):
    text = text if isinstance(text, str) else str(text)
    return {
        "ts": ts or _now(), "dir": direction, "peer": peer or "", "to": to or "",
        "session": (session or "")[:8], "msg_id": msg_id or "", "summary": summary or "",
        "chars": len(text), "sha": _sha(text), "text": text,
    }


def append(rec, root=ROOT):
    """Grava 1 linha. Nunca levanta: retorna True/False."""
    try:
        path = os.path.join(root, LEDGER)
        d = os.path.dirname(path)
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
        return True
    except Exception as e:  # pragma: no cover
        print("[EXCHANGE-LOG] falhou (%s): %s" % (type(e).__name__, e))
        return False


def read(root=ROOT):
    path = os.path.join(root, LEDGER)
    out = []
    if not os.path.isfile(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except ValueError:
                out.append({"ts": "?", "dir": "?", "summary": "<linha corrompida>", "chars": 0, "sha": "", "text": ""})
    return out


def from_hook(payload, root=ROOT):
    """PostToolUse: payload do harness (tool_name, tool_input, tool_response, session_id)."""
    if payload.get("tool_name") not in (None, "SendMessage"):
        return None
    ti = payload.get("tool_input") or {}
    text = ti.get("message") or ""
    if not text:
        return None
    summary = ti.get("summary") or ""
    m = PEER_RX.match(summary)
    peer = m.group(1) if m else ""
    msg_id = ""
    tr = payload.get("tool_response")
    try:
        if isinstance(tr, str):
            tr = json.loads(tr)
        if isinstance(tr, dict):
            msg_id = tr.get("msg_id") or ""
    except ValueError:
        pass
    rec = make("out", text, peer=peer, to=ti.get("to") or "", session=payload.get("session_id") or "",
               msg_id=msg_id, summary=summary)
    append(rec, root)
    return rec


def backfill(path, root=ROOT):
    n = 0
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            raw = json.loads(ln)
            rec = make(raw.get("dir", "in"), raw.get("text", ""), peer=raw.get("peer", ""),
                       to=raw.get("to", ""), session=raw.get("session", ""), msg_id=raw.get("msg_id", ""),
                       summary=raw.get("summary", ""), ts=raw.get("ts"))
            append(rec, root)
            n += 1
    return n


def report(n=20, full=False, root=ROOT):
    recs = read(root)[-n:]
    print("[EXCHANGE-LOG] %d registro(s) mostrados, %d no ledger" % (len(recs), len(read(root))))
    for r in recs:
        who = r.get("peer") or r.get("to") or "?"
        print("- %s %-3s %-12s %s (%d chars, %s)" % (
            r.get("ts", "?")[:16], r.get("dir", "?"), who[:12], (r.get("summary") or "")[:90],
            r.get("chars", 0), r.get("sha", "")))
        if full:
            print("")
            print(r.get("text", ""))
            print("")


def main():
    argv = sys.argv[1:]
    try:  # saida sempre UTF-8 (hook seta [Console]::OutputEncoding=UTF8; pipes no Windows caem em cp1252)
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    def arg(k, default=""):
        return argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else default

    root = arg("--root", ROOT)  # --root so para teste em tempdir; producao usa o repo
    try:
        if "--report" in argv:
            i = argv.index("--report")
            n = int(argv[i + 1]) if i + 1 < len(argv) and argv[i + 1].isdigit() else 20
            report(n, full="--full" in argv, root=root)
            return
        if "--backfill" in argv:
            n = backfill(arg("--backfill"), root=root)
            print("[EXCHANGE-LOG] backfill: %d registro(s)" % n)
            return
        if "--in" in argv or "--out" in argv:  # registro manual (sem hook): texto em --file
            direction = "in" if "--in" in argv else "out"
            with open(arg("--file"), encoding="utf-8") as fh:
                text = fh.read()
            rec = make(direction, text, peer=arg("--peer"), to=arg("--to"), msg_id=arg("--msg-id"),
                       summary=arg("--summary"), ts=arg("--ts") or None)
            append(rec, root)
            print("[EXCHANGE-LOG] %s %s %s (%d chars)" % (direction, rec["ts"], rec["peer"], rec["chars"]))
            return
        raw = sys.stdin.buffer.read() if hasattr(sys.stdin, "buffer") else sys.stdin.read().encode("utf-8")
        if not raw or not raw.strip():
            return
        payload = json.loads(raw.decode("utf-8-sig", "replace"))  # -sig: PowerShell pode injetar BOM ao pipear
        rec = from_hook(payload, root)
        if rec:
            print("[EXCHANGE-LOG] out %s -> %s (%d chars)" % (rec["ts"], rec["peer"] or rec["to"][:24], rec["chars"]))
    except Exception as e:  # um hook de registro NUNCA derruba o turno
        print("[EXCHANGE-LOG] falhou (%s): %s" % (type(e).__name__, e))
    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()
