"""
CLI canônica para registrar um erro de questão no `ipub.db` atomicamente.

Transação de 4 passos em commit único:
1. Insert/update em `taxonomia_cronograma` (cria área+tema se não existir).
2. Insert em `questoes_erros` com metadados do erro.
3. Insert de cards em `flashcards`: N cards atômicos via `--cards-file`
   (cunhados pelo agente, ver `.claude/commands/estilo-flashcard.md`) OU o par
   `--frente_pergunta`+`--verso_resposta` (card qualitativo único). Erro sem
   card só com `--status` anulada/banca-divergente — o fallback heurístico foi
   REMOVIDO (part-1, incidente dos 68 em 2026-08-13): sem cards = falha alta.
4. Init de estado FSRS em `fsrs_cards` para cada card.

Vinculos opcionais (s199, elo questoes -> cards), na MESMA transacao: `--sessao ID`
grava `questoes_erros.sessao_bulk_id` (id da LINHA de `sessoes_bulk`, nunca o
`sessao_num`); `--emed LISTA_NUM` (ex.: `t40_7`) grava `emed_respostas.questao_erro_id`
pelo writer `db.emed_ligar_erro`. Vinculo recusado = nada gravado.

Assinatura canônica (17 args: 8 obrigatórios + 9 opcionais/qualidade) em
`.claude/commands/analisar-questao.md §9`. Exit 0 em sucesso, 1 em falha.
"""

import sqlite3
import argparse
import json
import sys
from datetime import datetime
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils import card_checks  # gate de qualidade — biblioteca pura, fonte unica (1.9a)
# F80 (s174): o RELOGIO do ipub.db e unico -- app.utils.db.agora() (LOCAL naive).
# Este CLI continua standalone no sqlite3 (AGENTE §6); so o carimbo vem de la,
# chamado pelo ATRIBUTO do modulo (db.agora()) para o teste congelar o instante.
import app.utils.db as db
import app.utils.areas as areas

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

# P3 part-4: eventos aguardando COMMIT — evento de transacao que faz rollback
# seria fato falso no log; o flush so acontece pos-commit (own_conn ou lote).
_EVENTOS_PENDENTES = []


def _flush_eventos():
    """Persiste os eventos pendentes (pos-commit). Nunca derruba o insert."""
    try:
        import event_log
        for tipo, dados in _EVENTOS_PENDENTES:
            event_log.registrar(tipo, dados)
    except Exception as e:
        print(f"[WARN] EVENT_LOG: flush falhou ({e}); eventos so no stdout.")
    _EVENTOS_PENDENTES.clear()

# --- Reincidencia (F25, PRD orquestracao part-3) ----------------------------
# Matcher lexical simples: normaliza, remove stopwords minimas, mede overlap de
# tokens. WARN informativo (politica s106/107) -- NUNCA bloqueia o insert.
LIMIAR_OVERLAP = 0.5   # fracao de tokens compartilhados sobre o MENOR conjunto
STOPWORDS = {"de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas",
             "um", "uma", "para", "por", "com", "sem", "que", "nao", "não",
             "mais", "menos", "antes", "apos", "após", "entre", "sobre",
             "qual", "quando", "como", "deve", "pode", "caso", "paciente"}


def _tokens(texto):
    """Tokens normalizados (>= 4 chars, sem stopwords) p/ o match lexical."""
    palavras = re.findall(r"[a-zA-ZÀ-ÿ0-9<>=]{4,}", (texto or "").lower())
    return {p for p in palavras if p not in STOPWORDS}


def checar_reincidencia(conn, tema_id, questao_id_novo, texto_novo):
    """F25: cruza o erro novo contra erros/cards EXISTENTES do mesmo tema.
    Retorna lista de hits [(tipo, id, overlap)]; vazia quando nada casa."""
    novos = _tokens(texto_novo)
    if not novos:
        return []
    hits = []
    cur = conn.cursor()
    cur.execute("SELECT id, habilidades_sequenciais, o_que_faltou FROM questoes_erros "
                "WHERE tema_id = ? AND id <> ?", (tema_id, questao_id_novo))
    for qid, hab, faltou in cur.fetchall():
        antigos = _tokens((hab or "") + " " + (faltou or ""))
        if antigos:
            overlap = len(novos & antigos) / min(len(novos), len(antigos))
            if overlap >= LIMIAR_OVERLAP:
                hits.append(("erro", qid, round(overlap, 2)))
    cur.execute("SELECT id, frente_pergunta, verso_resposta, verso_regra_mestre, "
                "verso_armadilha FROM flashcards "
                "WHERE tema_id = ? AND (questao_id IS NULL OR questao_id <> ?)",
                (tema_id, questao_id_novo))
    for cid, fp, vr, vrm, va in cur.fetchall():
        antigos = _tokens(" ".join(filter(None, (fp, vr, vrm, va))))
        if antigos:
            overlap = len(novos & antigos) / min(len(novos), len(antigos))
            if overlap >= LIMIAR_OVERLAP:
                hits.append(("card", cid, round(overlap, 2)))
    return hits


def _ensure_status_column(cursor):
    """F26: coluna `status` em questoes_erros (anulada | banca-divergente | NULL=valida).
    ALTER idempotente (aditivo, DEFAULT NULL) -- mesmo padrao CREATE-IF-NOT-EXISTS do repo."""
    cols = {r[1] for r in cursor.execute("PRAGMA table_info(questoes_erros)")}
    if "status" not in cols:
        cursor.execute("ALTER TABLE questoes_erros ADD COLUMN status TEXT DEFAULT NULL")


def _ensure_sessao_column(cursor):
    """s199: coluna `sessao_bulk_id` em questoes_erros -- de qual bloco (`sessoes_bulk.id`)
    o erro veio. ALTER idempotente (aditivo, NULL = erro sem bloco, o legado inteiro)."""
    cols = {r[1] for r in cursor.execute("PRAGMA table_info(questoes_erros)")}
    if "sessao_bulk_id" not in cols:
        cursor.execute("ALTER TABLE questoes_erros ADD COLUMN sessao_bulk_id INTEGER")


def _erros_vinculo(item):
    """Forma dos vinculos opcionais de um item de lote (`sessao`, `emed`), sem banco.
    A existencia de cada um so o writer confere, dentro da transacao."""
    erros = []
    sessao = item.get("sessao")
    if sessao is not None and (isinstance(sessao, bool) or not str(sessao).strip().isdigit()):
        erros.append(f"sessao invalida {sessao!r}: esperado o id (inteiro) da linha de sessoes_bulk")
    if item.get("emed") is not None:
        try:
            db.emed_chave(item["emed"])
        except ValueError as e:
            erros.append(str(e))
    return erros


def _tem_lastro(tema):
    """F31: o tema tem lastro escrito? Delega para `tools/utils/lastro.tem_lastro`.

    F103/F106 (s185): a regra era local e casava o tema contra o NOME do arquivo, cega a
    resumo guarda-chuva -- `Rede de Atencao Psicossocial (RAPS)` acusava `[SEM-LASTRO]` com
    um `## 4.` dedicado ja escrito, e a pendencia "criar resumo" produziria duplicado. A
    regra virou unica e mora em `tools/utils/lastro.py` (5 camadas, motivo nomeado, menção
    solta no corpo deliberadamente FORA). Reimplementar aqui seria o defeito do F95.

    Conservador: falha de leitura devolve True -- nunca acusar ausencia por nao conseguir
    checar (o par Siamese Twins so e sinalizado com ausencia POSITIVAMENTE confirmada).
    """
    try:
        from tools.utils.lastro import tem_lastro
        return tem_lastro(tema)[0]
    except Exception:
        return True




MSG_SEM_CARDS = (
    "cards ausente/vazio: todo erro valido exige cards cunhados "
    "pela regua (.claude/commands/estilo-flashcard.md) ou o par "
    "frente_pergunta+verso_resposta; erro SEM card so com "
    "status anulada/banca-divergente")
MSG_GATE_REPROVOU = (
    "gate de qualidade reprovou a cunhagem (regua "
    ".claude/commands/estilo-flashcard.md): ")


def avaliar_cunhagem(*, cards, status, titulo, tema, area, chamada,
                     frente_contexto=None, frente_pergunta=None,
                     verso_resposta=None, verso_regra_mestre=None,
                     verso_armadilha=None):
    """Deriva a lista de cards e roda o gate de qualidade. PURA: nao toca o banco.

    F107 (s185): fonte UNICA do contrato de cunhagem, usada pelos DOIS caminhos --
    o writer (`insert_questao`) e o pre-check (`checar_lote`, atras de `--dry-run`).
    Escrever um segundo sensor para o pre-check reproduziria o defeito de classe do
    F95/F102: dois sensores para a mesma condicao, com regras que divergem no tempo.

    Retorna {"cards", "tuplas", "erros", "avisos", "sem_cards"}. `erros` nao-vazio
    ou `sem_cards` = a cunhagem reprova; o que fazer com isso e do chamador (o writer
    levanta ValueError e o lote faz ROLLBACK TOTAL; o pre-check imprime e sai 1).
    """
    if status in ("anulada", "banca-divergente"):
        # F26: anulada/banca-divergente registra o ERRO mas NAO cunha card.
        return {"cards": [], "tuplas": [], "erros": [], "avisos": [],
                "sem_cards": False}
    if cards is None and frente_pergunta and verso_resposta:
        # Modo flags individuais (CLI single): converge para o caminho unico.
        cards = [{
            "tipo": "elo_quebrado",
            "frente_contexto": frente_contexto,
            "frente_pergunta": frente_pergunta,
            "verso_resposta": verso_resposta,
            "verso_regra_mestre": verso_regra_mestre,
            "verso_armadilha": verso_armadilha,
        }]
    if not cards:
        return {"cards": [], "tuplas": [], "erros": [], "avisos": [],
                "sem_cards": True}
    ctx = {"titulo": titulo, "tema": tema, "area": area}
    erros, avisos, tuplas = [], [], []
    for i, c in enumerate(cards):
        res = card_checks.validar_card(c, contexto=ctx)
        erros += [f"card {i}: {e_}" for e_ in res["erros"]]
        avisos += [f"card {i}: {a_}" for a_ in res["avisos"]]
        tuplas.append((
            c.get('tipo') or 'conteudo',
            c.get('frente_contexto') or '',
            (c.get('frente_pergunta') or '').strip(),
            (c.get('verso_resposta') or '').strip(),
            c.get('verso_regra_mestre') or '',
            c.get('verso_armadilha') or '',
        ))
    av_distrator = card_checks.checar_distrator(
        {"alternativa_marcada": chamada}, cards)
    if av_distrator:
        avisos.append(av_distrator)
    return {"cards": cards, "tuplas": tuplas, "erros": erros, "avisos": avisos,
            "sem_cards": False}


def checar_lote(errors_file):
    """Pre-check READ-ONLY de um errors-file: campos obrigatorios + o MESMO gate de
    cunhagem sobre o lote inteiro, SEM abrir transacao nem conexao.

    F107: o gate so existia dentro do writer, entao um lote de 25 so descobria o card
    reprovado depois de abrir a transacao -- e cada descoberta custava um ROLLBACK
    TOTAL. Medido na s184: 2 execucoes perdidas. Aqui os achados saem todos de uma vez.

    LIMITE DECLARADO (AGENTE 10.8): sem banco nao ha como modelar o dedupe por conteudo
    (area, tema, enunciado) que o writer aplica ANTES do gate. Item que o writer PULARIA
    por ja estar registrado ainda e avaliado aqui -- falso positivo conservador,
    declarado em vez de virar divergencia silenciosa entre os dois caminhos.

    Retorna [{"item": i, "titulo": str, "erros": [...], "avisos": [...]}]; vazio = passa.
    """
    try:
        with open(errors_file, encoding="utf-8") as fh:
            itens = json.load(fh)
    except Exception as e:
        return [{"item": -1, "titulo": "(arquivo)",
                 "erros": [f"errors-file ilegivel/JSON invalido: {e}"], "avisos": []}]
    if not isinstance(itens, list) or not itens:
        return [{"item": -1, "titulo": "(arquivo)",
                 "erros": ["errors-file deve ser um array JSON nao-vazio"],
                 "avisos": []}]
    achados = []
    for i, item in enumerate(itens):
        if not isinstance(item, dict):
            achados.append({"item": i, "titulo": "?",
                            "erros": ["deve ser objeto JSON"], "avisos": []})
            continue
        erros, avisos = [], []
        titulo = item.get("titulo", "?")
        faltando = [c for c in CAMPOS_OBRIGATORIOS if not str(item.get(c) or "").strip()]
        if faltando:
            erros.append("campos obrigatorios ausentes: " + ", ".join(faltando))
        st = item.get("status")
        if st and st not in ("anulada", "banca-divergente"):
            erros.append(f"status invalido '{st}'")
        try:
            areas.validar_area(item.get("area"), origem="checar_lote")
        except Exception as e:
            erros.append(f"area: {e}")
        erros += _erros_vinculo(item)
        crds = item.get("cards")
        if not st and crds is not None and (not isinstance(crds, list) or not crds):
            erros.append("'cards' deve ser lista nao-vazia (o fallback heuristico foi removido)")
        else:
            aval = avaliar_cunhagem(
                cards=crds, status=st, titulo=titulo, tema=item.get("tema"),
                area=item.get("area"), chamada=item.get("marcada"),
                frente_contexto=item.get("frente_contexto"),
                frente_pergunta=item.get("frente_pergunta"),
                verso_resposta=item.get("verso_resposta"),
                verso_regra_mestre=item.get("verso_regra_mestre"),
                verso_armadilha=item.get("verso_armadilha"))
            if aval["sem_cards"]:
                erros.append("sem 'cards' e sem par frente_pergunta+verso_resposta")
            erros += aval["erros"]
            avisos += aval["avisos"]
        if erros or avisos:
            achados.append({"item": i, "titulo": titulo,
                            "erros": erros, "avisos": avisos})
    return achados


def relatar_lote(achados, out=print):
    """Imprime os achados do pre-check. Retorna True se o lote passa (zero erro)."""
    com_erro = [a for a in achados if a["erros"]]
    for a in achados:
        alvo = "(arquivo)" if a["item"] < 0 else f"item {a['item']} ('{a['titulo']}')"
        for e in a["erros"]:
            out(f"[ERRO-DRY] {alvo}: {e}")
        for av in a["avisos"]:
            out(f"[AVISO-DRY] {alvo}: {av}")
    if com_erro:
        out(f"[DRY-RUN] REPROVADO: {len(com_erro)} item(ns) com erro. "
            f"NADA seria inserido (o writer faria ROLLBACK TOTAL).")
        return False
    avisos = sum(len(a["avisos"]) for a in achados)
    out(f"[DRY-RUN] OK: lote passa no gate de cunhagem"
        + (f" ({avisos} aviso(s), warn-first -- nao bloqueiam)." if avisos else "."))
    return True


def insert_questao(area, tema, enunciado, correta, chamada, erro, elo, armadilha,
                   complexidade="Media", habilidades="N/A", faltou="N/A", explicacao="N/A", titulo="Erro sem titulo",
                   frente_contexto=None, frente_pergunta=None,
                   verso_resposta=None, verso_regra_mestre=None, verso_armadilha=None,
                   cards=None, status=None, sessao=None, emed=None, conn=None):
    # print(f"DEBUG: Tentando inserir no banco: {os.path.abspath(DB_PATH)}")
    # F89 (s176): `area` e a precondicao mais BARATA -- vale antes do contrato de
    # cunhagem, para o chamador ver o primeiro problema real e nao o segundo. Foi por
    # esta porta que `GO` e `Clinica Medica`, dissolvidas na s097, voltaram com ids
    # novos: o writer criava a linha `(area, tema)` que recebesse.
    area = areas.validar_area(area, origem="insert_questao")
    # conn externa (part-4): participa de transacao maior (lote) -- nao abre,
    # nao commita, nao fecha; excecao PROPAGA para o rollback total do lote.
    own_conn = conn is None
    try:
        # Contrato de cunhagem (part-1): construir a lista de cards ANTES de
        # qualquer INSERT — contrato invalido nao grava nada. O fallback
        # heuristico foi REMOVIDO (o contrato s076 ja o havia aposentado e ele
        # reapareceu no incidente dos 68, 2026-08-13; so remocao de codigo segura).
        # F26: anulada/banca-divergente registra o ERRO (memoria do caso) mas NAO
        # cunha card (nao e lacuna real) e fica marcada p/ gate de evidencia.
        aval = avaliar_cunhagem(
            cards=cards, status=status, titulo=titulo, tema=tema, area=area,
            chamada=chamada, frente_contexto=frente_contexto,
            frente_pergunta=frente_pergunta, verso_resposta=verso_resposta,
            verso_regra_mestre=verso_regra_mestre, verso_armadilha=verso_armadilha)
        if aval["sem_cards"]:
            raise ValueError(MSG_SEM_CARDS)
        if aval["erros"]:
            raise ValueError(MSG_GATE_REPROVOU + " | ".join(aval["erros"]))
        cards_to_insert = aval["tuplas"]
        for a_ in aval["avisos"]:
            print(f"[AVISO-CARD] {a_}")
        # s199: forma do vinculo EMED antes de qualquer escrita.
        emed_lista, emed_num = db.emed_chave(emed) if emed is not None else (None, None)

        if own_conn:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON")  # part-1: FKs do schema impostas
        cursor = conn.cursor()
        _ensure_status_column(cursor)
        _ensure_sessao_column(cursor)
        if sessao is not None:
            try:
                existe = cursor.execute("SELECT 1 FROM sessoes_bulk WHERE id = ?",
                                        (int(sessao),)).fetchone()
            except sqlite3.OperationalError:
                existe = None
            if not existe:
                raise ValueError(f"sessao {sessao} nao existe em sessoes_bulk (o id e o da "
                                 f"LINHA, nunca o sessao_num)")

        # Verifica se o Tema já existe (por (area, tema) — evita re-poluir; UNIQUE no schema). Se não existir, cria.
        cursor.execute("SELECT id FROM taxonomia_cronograma WHERE area = ? AND tema = ?", (area, tema))
        row = cursor.fetchone()
        
        if row:
            tema_id = row[0]
        else:
            cursor.execute('''
                INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas, percentual_acertos, ultima_revisao)
                VALUES (?, ?, 0, 0, 0, ?)
            ''', (area, tema, db.agora().strftime('%Y-%m-%d')))
            tema_id = cursor.lastrowid

        # 1. Inserir a Questão Erro com Schema Expandido (+status F26)
        cursor.execute('''
            INSERT INTO questoes_erros
            (tema_id, titulo, complexidade, enunciado, alternativa_correta, alternativa_marcada,
             tipo_erro, habilidades_sequenciais, o_que_faltou, explicacao_correta, armadilha_prova, status,
             data_registro, sessao_bulk_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tema_id, titulo, complexidade, enunciado, correta, chamada,
              erro, habilidades, faltou, explicacao, armadilha, status,
              db.carimbo(),    # F80: relogio unico (LOCAL), nunca o DEFAULT UTC
              int(sessao) if sessao is not None else None))
        questao_id = cursor.lastrowid
        if emed_lista is not None:
            # s199: a resposta da aba Questoes aponta para o erro; recusa propaga e
            # derruba o erro junto (mesma transacao).
            db.emed_ligar_erro(conn, emed_lista, emed_num, questao_id)

        # 2. Inserção dos cards (lista construída no topo — caminho qualitativo
        # único; sempre quality_source='qualitative' e needs_qualitative=0).
        for tipo_card, fc_, fp_, vr_, vrm_, va_ in cards_to_insert:
            cursor.execute('''
                INSERT INTO flashcards (questao_id, tema_id, tipo,
                                        frente_contexto, frente_pergunta, verso_resposta,
                                        verso_regra_mestre, verso_armadilha,
                                        quality_source, needs_qualitative)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'qualitative', 0)
            ''', (questao_id, tema_id, tipo_card,
                  fc_, fp_, vr_, vrm_, va_))
            card_id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO fsrs_cards (card_id, state, due)
                VALUES (?, 0, ?)
            ''', (card_id, db.agora()))

        # 4. Atualizar ultima_revisao do tema (usado pelo widget Foco Crítico).
        #    NOTA ARQUITETURAL: questoes_realizadas e questoes_acertadas NÃO são
        #    incrementados aqui. O volume de questões é registrado via
        #    tools/registrar_sessao_bulk.py (separação de responsabilidades).
        cursor.execute('''
            UPDATE taxonomia_cronograma
            SET ultima_revisao = ?
            WHERE id = ?
        ''', (db.agora().strftime('%Y-%m-%d'), tema_id))

        try:
            cursor.execute('''
                UPDATE cronograma_progresso
                SET status = 'Concluído', updated_at = CURRENT_TIMESTAMP
                WHERE tema LIKE ?
            ''', (f"%{tema}%",))
        except Exception:
            pass  # tabela opcional — ignorar se não existir

        # P3 part-4: evento de geracao (ids/contagens — nunca texto clinico);
        # fica pendente ate o commit (lote comita em insert_batch).
        if cards_to_insert:
            _EVENTOS_PENDENTES.append(("generation", {
                "questao_id": questao_id, "n_cards": len(cards_to_insert),
                "avisos": len(aval["avisos"])}))

        if own_conn:
            conn.commit()
            _flush_eventos()
        if cards_to_insert:
            print(f"Sucesso! Questão '{titulo}' inserida. Flashcard IPUB High-Level [ID: {card_id}] gerado.")
        else:
            print(f"Sucesso! Questão '{titulo}' registrada SEM card (status: {status}).")
            print(f"[GATE-EVIDENCIA] Q {status} registrada p/ /pesquisar-evidencia; "
                  f"não conta como lacuna real nem entra na fila.")

        # F25 (pos-insert, read-only): sinaliza reincidencia sobre elo ja registrado.
        # O matcher NUNCA altera o resultado do insert (WARN informativo).
        if status not in ("anulada", "banca-divergente"):
            try:
                texto_novo = " ".join(t for t in (
                    elo, faltou if faltou != "N/A" else "", habilidades if habilidades != "N/A" else ""
                ) if t)
                hits = checar_reincidencia(conn, tema_id, questao_id, texto_novo)
                if hits:
                    alvos = ", ".join("%s %d (overlap %.2f)" % h for h in hits[:5])
                    print("[REINCIDENCIA] elo similar a: %s -- %dx no tema. "
                          "Candidato a padrao vivo (HANDOFF) e mini-drill "
                          "(fsrs_queue --pre-bloco)." % (alvos, len(hits)))
                    # P3 part-4: reincidencia vira evento persistido (metrica
                    # de 1a classe de um sistema error-driven). Ja pos-commit
                    # no modo single; no lote, flusha com o commit do lote.
                    ev = ("reincidencia", {"questao_id": questao_id, "hits": len(hits)})
                    if own_conn:
                        try:
                            import event_log
                            event_log.registrar(*ev)
                        except Exception:
                            pass
                    else:
                        _EVENTOS_PENDENTES.append(ev)
            except Exception:
                pass

        # F31 (pos-insert, read-only): tema sem lastro escrito (.md nem PDF-fonte).
        # WARN informativo -- NUNCA bloqueia; o par Siamese Twins (erro->db,
        # licao->resumo) ficou incompleto e vira candidato a criar/estender o resumo.
        try:
            if not _tem_lastro(tema):
                print("[SEM-LASTRO] '%s / %s' nao tem resumo (.md) nem PDF-fonte par -- "
                      "par Siamese Twins incompleto; candidato a criar/estender o resumo."
                      % (area, tema))
        except Exception:
            pass

        return True

    except Exception as e:
        if not own_conn:
            raise  # transacao do lote: o chamador faz o rollback TOTAL
        _EVENTOS_PENDENTES.clear()  # P3: rollback implicito -> evento seria fato falso
        print(f"Erro ao inserir no banco: {e}")
        return False
    finally:
        if own_conn and conn:
            conn.close()

CAMPOS_OBRIGATORIOS = ("area", "tema", "enunciado", "correta", "marcada",
                       "erro", "elo", "armadilha")


def insert_batch(errors_file, dry_run=False):
    """F24: insere um LOTE de erros (JSON array) numa transacao UNICA.

    - Validacao PRE-transacao: campos obrigatorios por item -> erro aponta item/campo,
      NADA inserido.
    - Dedupe por conteudo: (area, tema, enunciado) ja registrado -> item PULADO com
      aviso (re-execucao do mesmo lote nao duplica).
    - Qualquer excecao no meio -> ROLLBACK TOTAL (zero parcial).
    Cada item aceita os campos do modo single + opcionais `cards` (lista) e
    `status` (anulada | banca-divergente). Retorna True/False.
    """
    if dry_run:
        # F107: pre-check sem transacao -- o MESMO gate, todos os achados de uma vez.
        return relatar_lote(checar_lote(errors_file))
    try:
        with open(errors_file, encoding="utf-8") as fh:
            itens = json.load(fh)
    except Exception as e:
        print(f"[ERRO] errors-file ilegivel/JSON invalido: {e}. NADA inserido.")
        return False
    if not isinstance(itens, list) or not itens:
        print("[ERRO] errors-file deve ser um array JSON nao-vazio. NADA inserido.")
        return False
    for i, item in enumerate(itens):
        if not isinstance(item, dict):
            print(f"[ERRO] item {i}: deve ser objeto JSON. NADA inserido.")
            return False
        faltando = [c for c in CAMPOS_OBRIGATORIOS if not str(item.get(c) or "").strip()]
        if faltando:
            print(f"[ERRO] item {i} ('{item.get('titulo', '?')}'): campos obrigatorios "
                  f"ausentes: {', '.join(faltando)}. NADA inserido.")
            return False
        st = item.get("status")
        if st and st not in ("anulada", "banca-divergente"):
            print(f"[ERRO] item {i}: status invalido '{st}'. NADA inserido.")
            return False
        ruins = _erros_vinculo(item)
        if ruins:
            print(f"[ERRO] item {i} ('{item.get('titulo', '?')}'): {'; '.join(ruins)}. "
                  f"NADA inserido.")
            return False
        # Contrato de cunhagem (part-1): sem status de excecao, o item precisa de
        # cards OU do par frente_pergunta+verso_resposta — pego AQUI, pre-transacao.
        if not st:
            crds = item.get("cards")
            if crds is not None and (not isinstance(crds, list) or not crds):
                print(f"[ERRO] item {i} ('{item.get('titulo', '?')}'): 'cards' deve ser "
                      f"lista nao-vazia (o fallback heuristico foi removido). NADA inserido.")
                return False
            tem_par = (str(item.get("frente_pergunta") or "").strip()
                       and str(item.get("verso_resposta") or "").strip())
            if crds is None and not tem_par:
                print(f"[ERRO] item {i} ('{item.get('titulo', '?')}'): sem 'cards' e sem par "
                      f"frente_pergunta+verso_resposta. Cunhe pela regua "
                      f"(.claude/commands/estilo-flashcard.md) ou use status "
                      f"anulada/banca-divergente. NADA inserido.")
                return False

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # part-1: FKs do schema impostas
    inseridos, pulados = [], []
    try:
        cursor = conn.cursor()
        _ensure_status_column(cursor)
        for i, item in enumerate(itens):
            cursor.execute("""
                SELECT q.id FROM questoes_erros q
                JOIN taxonomia_cronograma t ON t.id = q.tema_id
                WHERE t.area = ? AND t.tema = ? AND TRIM(q.enunciado) = TRIM(?)
            """, (item["area"], item["tema"], item["enunciado"]))
            dup = cursor.fetchone()
            if dup:
                pulados.append((i, dup[0]))
                print(f"[SKIP] item {i}: erro ja registrado (questao id={dup[0]}) -- dedupe por conteudo.")
                continue
            insert_questao(
                area=item["area"], tema=item["tema"], enunciado=item["enunciado"],
                correta=item["correta"], chamada=item["marcada"], erro=item["erro"],
                elo=item["elo"], armadilha=item["armadilha"],
                complexidade=item.get("complexidade", "Média"),
                habilidades=item.get("habilidades", "N/A"),
                faltou=item.get("faltou", "N/A"),
                explicacao=item.get("explicacao", "N/A"),
                titulo=item.get("titulo", "Erro sem titulo"),
                frente_contexto=item.get("frente_contexto"),
                frente_pergunta=item.get("frente_pergunta"),
                verso_resposta=item.get("verso_resposta"),
                verso_regra_mestre=item.get("verso_regra_mestre"),
                verso_armadilha=item.get("verso_armadilha"),
                cards=item.get("cards"), status=item.get("status"),
                sessao=item.get("sessao"), emed=item.get("emed"),
                conn=conn,   # transacao do lote: excecao propaga p/ rollback total
            )
            inseridos.append(i)
        conn.commit()
        _flush_eventos()  # P3: eventos do lote so existem apos o commit real
    except Exception as e:
        conn.rollback()
        _EVENTOS_PENDENTES.clear()  # P3: rollback total -> nenhum evento
        print(f"[ERRO] lote abortado: {e}. ROLLBACK TOTAL -- zero inserido nesta execucao.")
        return False
    finally:
        conn.close()
    print(f"[OK] Lote: {len(inseridos)} erro(s) inserido(s), {len(pulados)} pulado(s) "
          f"por dedupe. Itens inseridos: {inseridos or '-'}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Script para pipeline Agente -> SQLite")
    # Obrigatorios NO MODO SINGLE (validados manualmente: com --errors-file eles
    # vem do JSON; a mensagem/exit 2 do parser.error preserva o contrato atual).
    parser.add_argument("--area")
    parser.add_argument("--tema")
    parser.add_argument("--enunciado")
    parser.add_argument("--correta")
    parser.add_argument("--marcada")
    parser.add_argument("--erro")
    parser.add_argument("--elo")
    parser.add_argument("--armadilha")
    parser.add_argument("--complexidade", default="Média")
    parser.add_argument("--habilidades", default="N/A")
    parser.add_argument("--faltou", default="N/A")
    parser.add_argument("--explicacao", default="N/A")
    parser.add_argument("--titulo", default="Erro sem titulo")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true",
                        help="F107: com --errors-file, roda campos obrigatorios + o "
                             "gate de cunhagem sobre o lote inteiro e imprime TODOS os "
                             "achados, sem abrir transacao nem conexao. exit 1 se "
                             "reprovar. Nao modela o dedupe por conteudo (limite "
                             "declarado na docstring de checar_lote).")
    # Campos estruturados para flashcard qualitativo (opcionais)
    parser.add_argument("--frente_contexto", default=None)
    parser.add_argument("--frente_pergunta", default=None)
    parser.add_argument("--verso_resposta", default=None)
    parser.add_argument("--verso_regra_mestre", default=None)
    parser.add_argument("--verso_armadilha", default=None)
    # Caminho agent-first: lista de N cards atômicos em JSON (UTF-8).
    # Cada item: {tipo?, frente_contexto?, frente_pergunta, verso_resposta, verso_regra_mestre?, verso_armadilha?}.
    # Quando fornecido, substitui a geração fixa elo+armadilha.
    parser.add_argument("--cards-file", dest="cards_file", default=None,
                        help="Path para JSON com lista de cards atômicos (ver estilo-flashcard.md)")
    # Part-4 (F24/F26):
    parser.add_argument("--errors-file", dest="errors_file", default=None,
                        help="LOTE: JSON array de erros completos (campos do modo single "
                             "+ opcionais cards/status por item) inseridos numa transacao "
                             "unica; item invalido = rollback total; dedupe por conteudo")
    parser.add_argument("--status", choices=["anulada", "banca-divergente"], default=None,
                        help="F26: registra o erro SEM cunhar card e marcado p/ gate de "
                             "evidencia (nao conta como lacuna real)")

    # s199 (elo questoes -> cards): vinculos opcionais, na mesma transacao do erro.
    parser.add_argument("--sessao", type=int, default=None,
                        help="id da LINHA de sessoes_bulk de onde o erro veio (nunca o "
                             "sessao_num); grava questoes_erros.sessao_bulk_id")
    parser.add_argument("--emed", default=None,
                        help="resposta da aba Questoes (LISTA_NUM, ex. t40_7); grava "
                             "emed_respostas.questao_erro_id. Resposta inexistente, ja "
                             "ligada ou certa-e-solida = nada gravado")

    args = parser.parse_args()

    if args.errors_file:
        ok = insert_batch(args.errors_file, dry_run=args.dry_run)
        sys.exit(0 if ok else 1)
    if args.dry_run:
        parser.error("--dry-run so existe com --errors-file (pre-check de lote)")

    faltando = ["--" + c for c in CAMPOS_OBRIGATORIOS if not getattr(args, c)]
    if faltando:
        parser.error(f"the following arguments are required: {', '.join(faltando)}")

    cards = None
    if args.cards_file:
        with open(args.cards_file, encoding="utf-8") as fh:
            cards = json.load(fh)

    # F27: o exit code reflete o resultado (simetrico ao modo --errors-file acima).
    # insert_questao retorna False em falha (own_conn) -> exit 1; sucesso -> exit 0.
    ok = insert_questao(
        area=args.area,
        tema=args.tema,
        enunciado=args.enunciado,
        correta=args.correta,
        chamada=args.marcada,
        erro=args.erro,
        elo=args.elo,
        armadilha=args.armadilha,
        complexidade=args.complexidade,
        habilidades=args.habilidades,
        faltou=args.faltou,
        explicacao=args.explicacao,
        titulo=args.titulo,
        frente_contexto=args.frente_contexto,
        frente_pergunta=args.frente_pergunta,
        verso_resposta=args.verso_resposta,
        verso_regra_mestre=args.verso_regra_mestre,
        verso_armadilha=args.verso_armadilha,
        cards=cards,
        status=args.status,
        sessao=args.sessao,
        emed=args.emed,
    )
    sys.exit(0 if ok else 1)
