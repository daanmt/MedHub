"""Suite do load balancer do agendamento FSRS (s128). Puro -- nao toca o db."""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.utils.fsrs_balance import (escolher_dia, folga_de, janela,  # noqa: E402
                                    DESLOCAMENTO_MAXIMO)

HOJE = date(2026, 7, 26)
falhas = []


def check(desc, cond, got=""):
    print(("  OK  " if cond else "  FALHOU  ") + desc + (f" (got {got})" if got != "" else ""))
    if not cond:
        falhas.append(desc)


print("[folga] intervalo curto nao tem folga")
check("intervalo 1 -> 0", folga_de(1) == 0, folga_de(1))
check("intervalo 3 -> 0", folga_de(3) == 0, folga_de(3))
check("intervalo None -> 0", folga_de(None) == 0, folga_de(None))

print("[folga] intervalo medio/longo escala a 5%, com piso 1 e teto")
check("intervalo 4 -> 1", folga_de(4) == 1, folga_de(4))
check("intervalo 10 -> 1", folga_de(10) == 1, folga_de(10))
check("intervalo 60 -> 3", folga_de(60) == 3, folga_de(60))
check("intervalo 180 -> 9", folga_de(180) == 9, folga_de(180))
check(f"intervalo 1000 respeita teto {DESLOCAMENTO_MAXIMO}",
      folga_de(1000) == DESLOCAMENTO_MAXIMO, folga_de(1000))

print("[janela] ordenada por proximidade do alvo e sem passado")
alvo = HOJE + timedelta(days=10)
j = janela(alvo, 10, HOJE)
check("alvo e o primeiro candidato", j[0] == alvo, j[0])
check("3 candidatos p/ folga 1", len(j) == 3, len(j))
check("nenhum candidato <= hoje", all(d > HOJE for d in j))
j_curto = janela(HOJE + timedelta(days=2), 2, HOJE)
check("intervalo curto -> so o alvo", j_curto == [HOJE + timedelta(days=2)], j_curto)

print("[escolher] desvia para o dia mais vazio")
carga = {alvo: 50, alvo - timedelta(days=1): 3, alvo + timedelta(days=1): 40}
dia, desloc = escolher_dia(alvo, 10, carga, HOJE)
check("escolheu o dia de carga 3", dia == alvo - timedelta(days=1), dia)
check("deslocamento -1", desloc == -1, desloc)

print("[escolher] empate preserva o alvo do FSRS")
carga_plana = {alvo: 5, alvo - timedelta(days=1): 5, alvo + timedelta(days=1): 5}
dia, desloc = escolher_dia(alvo, 10, carga_plana, HOJE)
check("empate -> fica no alvo", dia == alvo and desloc == 0, (dia, desloc))

print("[escolher] dia ausente do dict conta como carga 0")
dia, desloc = escolher_dia(alvo, 10, {alvo: 30}, HOJE)
check("desvia para dia vazio", desloc != 0, desloc)

print("[fronteiras duras]")
dia, desloc = escolher_dia(alvo, 2, {alvo: 99}, HOJE)
check("intervalo curto NAO e balanceado", desloc == 0, desloc)
for st in (0, 1, 3):
    dia, desloc = escolher_dia(alvo, 10, {alvo: 99}, HOJE, state=st)
    check(f"state={st} (nao-revisao) nao e balanceado", desloc == 0, desloc)
perto = HOJE + timedelta(days=5)
dia, _ = escolher_dia(perto, 5, {d: 0 for d in (perto - timedelta(days=1), perto)}, HOJE)
check("nunca agenda no passado ou hoje", dia > HOJE, dia)

print("[invariante] o deslocamento nunca excede a folga")
import random  # noqa: E402
random.seed(7)
pior = 0
for _ in range(400):
    iv = random.randint(1, 400)
    a = HOJE + timedelta(days=iv)
    c = {a + timedelta(days=k): random.randint(0, 80)
         for k in range(-DESLOCAMENTO_MAXIMO - 2, DESLOCAMENTO_MAXIMO + 3)}
    _, ds = escolher_dia(a, iv, c, HOJE)
    pior = max(pior, abs(ds))
    if abs(ds) > folga_de(iv):
        check(f"deslocamento {ds} excede folga {folga_de(iv)} p/ intervalo {iv}", False)
        break
else:
    check(f"400 sorteios: |deslocamento| <= folga (pior caso {pior}d)", True)

print()
if falhas:
    print(f"FALHAS: {len(falhas)}")
    for f in falhas:
        print("  -", f)
    sys.exit(1)
print("TODOS OS CHECKS PASSARAM (load balancer FSRS)")
