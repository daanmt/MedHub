"""FSRS fiel — scheduler de repetição espaçada do MedHub (adapter sobre py-fsrs).

Esta classe é um **adapter** fino sobre `py-fsrs` (open-spaced-repetition),
a implementação de referência do algoritmo FSRS (mesma org do `fsrs4anki`).
Substitui a fórmula caseira anterior, preservando a interface
`init_card()` / `evaluate(card, rating)` consumida por `app.utils.db.record_review`
e o schema `fsrs_cards`/`fsrs_revlog` (nenhuma coluna nova).

Mapeamento de estado: MedHub usa `state` 0=New, 1=Learning, 2=Review,
3=Relearning. py-fsrs usa 1=Learning, 2=Review, 3=Relearning (sem "New").
Um card MedHub com `state==0` ou `stability` ausente é tratado como card
novo (nunca revisado) do py-fsrs. O `step` do py-fsrs não é persistido no
schema atual — é reconstruído como 0; sem passos de aprendizagem nem de
reaprendizagem (abaixo), nenhum ramo da biblioteca o consulta. Desde 28/09/2026
o adapter NÃO produz mais `state` 3: ele só existe como legado no banco.

Datas: py-fsrs opera em UTC tz-aware; o MedHub armazena datetimes naive
locais (compatível com os dados existentes). O adapter converte nas bordas.

Retenção-alvo: `REQUEST_RETENTION = 0.9`.

Parâmetros (R2/F112, s186): o adapter passou a **consultar** `core/fsrs_params.json`
por `app.utils.regua.carregar_parametros`, que só entrega quando o arquivo se
declara `adotado` E a régua sob a qual foi ajustado é a régua de escrita. Nas
demais saídas -- e hoje é o caso -- vale o default de referência do py-fsrs, e
`MOTIVO_PARAMETROS` diz qual delas foi. A meta de retenção fica em **0,90** até
haver `review_duration_ms` medido pelo player (rider declarado do R2: sem duração
real, 0,70/0,80 é a saída mais fraca por construção).
"""

from datetime import datetime, timezone

from fsrs import Scheduler, Card, Rating

from app.utils.regua import REGUA_ATUAL, carregar_parametros

REQUEST_RETENTION = 0.9

#: Parâmetros em vigor + por que são esses. O motivo é exposto (e não só logado)
#: porque "está usando o default" e "está usando o que o R1 mediu" são estados
#: diferentes que produzem o MESMO agendamento silencioso -- e a diferença entre
#: eles é exatamente o que o operador precisa saber ao ler um intervalo.
PARAMETROS, MOTIVO_PARAMETROS = carregar_parametros(regua=REGUA_ATUAL)

# Scheduler único reutilizado.
# - learning_steps=(): sem fase de "passos curtos" (minutos) — cada review opera
#   direto no modelo DSR, com intervalos em dias desde a 1ª revisão. Isso é fiel
#   ao FSRS (modelo de memória) e evita depender do `step` (que o schema não
#   persiste); cards graduam para Review imediatamente.
# - relearning_steps=() (F140, s204 -- decisão do operador em 28/09/2026: "volta
#   apenas no dia seguinte; 'hoje' é apenas no redrill"): nota 1 sobre card de
#   Review FICA em Review, com intervalo em dias (piso de 1). A reaprendizagem do
#   dia é do re-drill do player, que não grava; o motor não a duplica.
#   ⚰️ Até 28/09/2026 o passo ficava no default da biblioteca (600 s): o card ia
#   a Relearning (3) com `due` em 10 min, o lote seguinte do mesmo dia o
#   re-servia e uma 2ª nota era gravada (F32, F140). O state 3 segue existindo
#   só como LEGADO: card nele volta a Review na próxima nota, qualquer que seja.
# - enable_fuzzing=False: intervalos determinísticos/reproduzíveis.
#: Argumentos-base do Scheduler: a FONTE ÚNICA. `tools/fsrs_optimize.py` parte
#: daqui para o replay da métrica -- digitados em dois lugares, divergiriam em
#: silêncio (`test_scheduler_do_otimizador_usa_os_kwargs_de_producao`).
KWARGS_BASE = dict(desired_retention=REQUEST_RETENTION, learning_steps=(),
                   relearning_steps=(), enable_fuzzing=False)
_KWARGS_SCHEDULER = dict(KWARGS_BASE)
if PARAMETROS is not None:
    _KWARGS_SCHEDULER["parameters"] = PARAMETROS
_SCHEDULER = Scheduler(**_KWARGS_SCHEDULER)


def _parse_dt(value):
    """Converte valor armazenado (str/datetime/None/NaN) em datetime tz-aware.

    datetimes naive são interpretados como horário local. Retorna None se o
    valor for ausente/inválido.
    """
    if value is None:
        return None
    if isinstance(value, float):  # pandas NaN/NaT
        return None
    if isinstance(value, str):
        s = value.strip()
        if not s or s.lower() in ("none", "nat", "nan"):
            return None
        s = s.replace("T", " ")
        parsed = None
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(s, fmt)
                break
            except ValueError:
                continue
        value = parsed
    if isinstance(value, datetime):
        return value.astimezone() if value.tzinfo is None else value
    return None


class FSRS:
    """Adapter de interface estável sobre o Scheduler do py-fsrs."""

    def __init__(self, w=None):
        # `w` mantido por compatibilidade de assinatura; ignorado (py-fsrs usa
        # seus próprios parâmetros de referência).
        self.scheduler = _SCHEDULER

    def init_card(self):
        """Estado inicial de um card novo (state=0=New), no shape do schema."""
        return {
            "state": 0,
            "stability": 0.0,
            "difficulty": 0.0,
            "elapsed_days": 0,
            "scheduled_days": 0,
            "reps": 0,
            "lapses": 0,
            "last_review": None,
            "due": datetime.now(),
        }

    def evaluate(self, card, rating, quando=None):
        """Aplica a avaliação (1=Again, 2=Hard, 3=Good, 4=Easy) e retorna o
        próximo estado no shape consumido por `record_review` (9 chaves).

        `quando` (s193, datetime LOCAL naive) = o instante da REVISÃO: o intervalo
        conta a partir dele, não da hora em que se grava. None = agora. Revisão que
        não é posterior à última do card -> ValueError: o py-fsrs NÃO recusa um
        `review_datetime` anterior ao `last_review` -- calcula `days < 1` e trata
        como revisão de curto prazo, em silêncio. A guarda mora aqui por isso."""
        rating = int(rating)
        now_utc = (datetime.now(timezone.utc) if quando is None
                   else quando.astimezone(timezone.utc))
        reps = int(card.get("reps") or 0)
        lapses = int(card.get("lapses") or 0)
        state = card.get("state")
        stability = card.get("stability")
        last_review = _parse_dt(card.get("last_review"))
        if quando is not None and last_review is not None and now_utc <= last_review:
            raise ValueError(
                "revisao em %s nao e posterior a ultima do card (%s) -- o estado "
                "FSRS so anda para a frente" % (quando, last_review.replace(tzinfo=None)))

        is_new = (not state) or int(state) == 0 or not stability

        if is_new:
            fcard = Card()  # card fresco do py-fsrs (nunca revisado)
        else:
            due_aware = _parse_dt(card.get("due")) or now_utc
            fcard = Card.from_dict({
                "card_id": int(card.get("card_id") or 1),
                "state": int(state),
                "step": 0,
                "stability": float(stability),
                "difficulty": float(card.get("difficulty") or 5.0),
                "due": due_aware.isoformat(),
                "last_review": last_review.isoformat() if last_review else None,
            })

        new_card, _log = self.scheduler.review_card(fcard, Rating(rating), now_utc)

        due_local = new_card.due.astimezone().replace(tzinfo=None)
        last_review_local = now_utc.astimezone().replace(tzinfo=None)
        elapsed_days = (now_utc - last_review).days if last_review else 0
        scheduled_days = max(0, (new_card.due - now_utc).days)
        reps += 1
        if rating == 1 and not is_new:
            lapses += 1

        return {
            "state": int(new_card.state),
            "stability": float(new_card.stability),
            "difficulty": float(new_card.difficulty),
            "elapsed_days": int(elapsed_days),
            "scheduled_days": int(scheduled_days),
            "reps": reps,
            "lapses": lapses,
            "last_review": last_review_local,
            "due": due_local,
        }
