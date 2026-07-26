"""Load balancing do agendamento FSRS (s128 -- pedido do usuario).

## O problema

O FSRS agenda cada card isoladamente: calcula o intervalo otimo `I` e crava
`due = hoje + I`. Como nada olha o calendario, a carga diaria fica grumosa --
um dia com 60 cards ao lado de dois dias com 3. O usuario sente isso como
sobrecarga pontual e, na pratica, empurra o excedente para o dia seguinte,
o que degrada o proprio agendamento que o FSRS calculou.

## A ideia

A curva de retencao e ~plana numa vizinhanca pequena de `I`: revisar no dia
`I-1` ou `I+1` muda a probabilidade de recall em fracao de ponto percentual.
Entao existe folga de graca. Este modulo escolhe, DENTRO dessa folga, o dia de
MENOR carga ja agendada -- achatando o calendario sem tocar no modelo de memoria.

## Fronteiras duras (por que isto e seguro)

- **Nao altera `stability` nem `difficulty`.** O que o FSRS aprendeu sobre o card
  fica intocado; move-se apenas a DATA, dentro da janela.
- **Janela proporcional e conservadora:** +-5% do intervalo, com piso de 1 dia.
  Um card de 10 dias anda no maximo 1 dia; um de 180, no maximo 9.
- **So mexe em card de revisao (`state == 2`) com intervalo >= 4 dias.** Passos
  de aprendizado/relearning sao curtos e intra-sessao: mover 1 dia num card de
  2 dias e erro de 50%, nao folga.
- **Nunca move para o passado** e nunca encurta abaixo do piso da janela.
- Modulo **PURO**: recebe a carga como dict e devolve uma data. Nao importa
  sqlite3, nao abre conexao (a consulta vive em `app/utils/db.py`, conforme a
  regra de SSOT). Isso o torna testavel sem banco.
"""
from datetime import date, timedelta

# Abaixo disto o intervalo e curto demais para ter folga real.
INTERVALO_MINIMO = 4
# Fracao do intervalo usada como janela (para cada lado).
FRACAO_JANELA = 0.05
# Teto absoluto de deslocamento, para nao esticar demais intervalos longos.
DESLOCAMENTO_MAXIMO = 10


def folga_de(intervalo_dias: int) -> int:
    """Quantos dias, para cada lado, o card pode andar sem custo de memoria.

    Retorna 0 quando o intervalo e curto demais para comportar folga.
    """
    if intervalo_dias is None or intervalo_dias < INTERVALO_MINIMO:
        return 0
    return max(1, min(DESLOCAMENTO_MAXIMO, round(intervalo_dias * FRACAO_JANELA)))


def janela(alvo: date, intervalo_dias: int, hoje: date):
    """Dias candidatos, em ordem de preferencia (mais perto do alvo primeiro).

    A ordem importa para o desempate: entre dois dias de carga igual, o mais
    proximo do que o FSRS calculou vence -- o balanceamento so desvia quando
    ha ganho real de carga.
    """
    f = folga_de(intervalo_dias)
    if not f:
        return [alvo]
    candidatos = []
    for d in range(0, f + 1):
        for lado in ((0,) if d == 0 else (-1, 1)):
            dia = alvo + timedelta(days=d * lado)
            if dia > hoje and dia not in candidatos:   # nunca hoje nem passado
                candidatos.append(dia)
    return candidatos


def escolher_dia(alvo: date, intervalo_dias: int, carga: dict, hoje: date,
                 state: int = 2):
    """Escolhe o dia de menor carga dentro da janela de folga.

    Args:
        alvo: data que o FSRS calculou.
        intervalo_dias: intervalo em dias (`scheduled_days`).
        carga: {date: n_cards_ja_agendados}. Dias ausentes contam 0.
        hoje: data corrente (injetada -- mantem a funcao deterministica).
        state: estado FSRS; so 2 (revisao) e elegivel.

    Returns:
        (dia_escolhido, deslocamento_em_dias). Deslocamento 0 = nao mexeu.
    """
    if int(state or 0) != 2:
        return alvo, 0
    candidatos = janela(alvo, intervalo_dias, hoje)
    if len(candidatos) <= 1:
        return alvo, 0
    # min() e estavel: preserva a ordem de preferencia no empate.
    melhor = min(candidatos, key=lambda d: carga.get(d, 0))
    return melhor, (melhor - alvo).days


def resumo_carga(carga: dict, inicio: date, dias: int = 14):
    """Linha de texto por dia -- usado pelo CLI de previsao."""
    linhas = []
    for i in range(dias):
        d = inicio + timedelta(days=i)
        n = carga.get(d, 0)
        linhas.append((d, n, "#" * min(n, 60)))
    return linhas
