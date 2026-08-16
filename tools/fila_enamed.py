# -*- coding: utf-8 -*-
"""Gera o artefato 'A Fila Errada': cronograma EMED S15-S30 reordenado pelo ENAMED.

Fontes (todas versionadas):
  core/simulados/fila_enamed_payload.json  -- payload pronto do artefato
  core/simulados/guia_enare.json           -- guia estatistico ENARE parseado (n=453)
  core/simulados/blueprint_enamed.json     -- blueprint do ENAMED medido (n=95 + n=120)
  core/simulados/plano_fila_enamed.json    -- plano de reordenacao (puxar/empurrar/fila)
  core/simulados/micro_temas.py            -- peso de cada tema dentro da sua especialidade

Uso: python -X utf8 tools/fila_enamed.py [--out CAMINHO.html]
Para regerar o payload apos novo simulado ou novo sync do Drive, ver o
protocolo em core/simulados/plano_fila_enamed.json (_doc).
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "core", "simulados", "fila_enamed_payload.json"),
                   encoding="utf-8"))

TPL = r"""<title>A Fila Errada</title>
<style>
:root{
  --paper:#ECEFE9; --card:#FAFBF8; --sunk:#E2E6DE;
  --ink:#161A17; --ink2:#4A544C; --ink3:#7B857D;
  --line:rgba(22,26,23,.13); --line2:rgba(22,26,23,.28);
  --teal:#1A5654; --teal-ink:#123E3C; --teal-wash:#DCE9E6;
  --rose:#A03A5D; --rose-ink:#7C2946; --rose-wash:#F4E1E7;
  --ochre:#8A6A12; --ochre-ink:#68500C; --ochre-wash:#F2E9CE;
  --on:#FFFFFF;
  --s1:#008C84; --s2:#A07A0C;            /* series validadas p/ os graficos */
  --grid:rgba(22,26,23,.10);
  --sh:0 1px 2px rgba(22,26,23,.05),0 10px 26px -16px rgba(22,26,23,.3);
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#101413; --card:#181D1B; --sunk:#212825;
  --ink:#E7EDE8; --ink2:#AEBAB1; --ink3:#7D8A80;
  --line:rgba(231,237,232,.14); --line2:rgba(231,237,232,.3);
  --teal:#57ADA8; --teal-ink:#7FC9C4; --teal-wash:#14312F;
  --rose:#D98BA4; --rose-ink:#EBA9BE; --rose-wash:#361A24;
  --ochre:#C9A54A; --ochre-ink:#DEBF74; --ochre-wash:#332A10;
  --on:#101413;
  --s1:#12A99C; --s2:#A38228;
  --grid:rgba(231,237,232,.12);
  --sh:0 1px 2px rgba(0,0,0,.45),0 12px 30px -16px rgba(0,0,0,.75);
  color-scheme:dark;
}}
:root[data-theme="dark"]{
  --paper:#101413; --card:#181D1B; --sunk:#212825;
  --ink:#E7EDE8; --ink2:#AEBAB1; --ink3:#7D8A80;
  --line:rgba(231,237,232,.14); --line2:rgba(231,237,232,.3);
  --teal:#57ADA8; --teal-ink:#7FC9C4; --teal-wash:#14312F;
  --rose:#D98BA4; --rose-ink:#EBA9BE; --rose-wash:#361A24;
  --ochre:#C9A54A; --ochre-ink:#DEBF74; --ochre-wash:#332A10;
  --on:#101413;
  --s1:#12A99C; --s2:#A38228;
  --grid:rgba(231,237,232,.12);
  --sh:0 1px 2px rgba(0,0,0,.45),0 12px 30px -16px rgba(0,0,0,.75);
  color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--paper);color:var(--ink);
  font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
.mn{font-family:ui-monospace,"SF Mono",SFMono-Regular,Consolas,monospace;font-variant-numeric:tabular-nums}
h1,h2{margin:0;font-weight:670;letter-spacing:-.025em;text-wrap:balance;line-height:1.14}
h1{font-size:clamp(27px,4.4vw,42px)}
h2{font-size:clamp(18px,2.3vw,23px)}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px 90px}
:focus-visible{outline:2px solid var(--teal);outline-offset:2px}
button{font-family:inherit;cursor:pointer}
p{margin:0 0 13px}

.top{padding:46px 0 8px}
.eye{font-size:11px;font-weight:750;letter-spacing:.14em;text-transform:uppercase;color:var(--teal);margin:0 0 13px}
.top h1{margin-bottom:15px;max-width:17ch}
.lede{font-size:17.5px;line-height:1.56;color:var(--ink2);max-width:64ch}
.lede strong{color:var(--ink);font-weight:620}

.bar{display:flex;align-items:baseline;gap:12px;border-bottom:2px solid var(--ink);padding-bottom:7px;margin:48px 0 18px;flex-wrap:wrap}
.bar h2{flex:1;min-width:220px}
.bar .note{font-size:12px;color:var(--ink3);max-width:44ch}

/* cartoes de numero */
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:22px 0 4px}
.tile{background:var(--card);border:1px solid var(--line2);padding:14px 15px}
.tile .k{font-size:10.5px;font-weight:750;letter-spacing:.1em;text-transform:uppercase;color:var(--ink3)}
.tile .v{font-size:31px;font-weight:680;letter-spacing:-.035em;line-height:1.05;margin-top:6px;font-variant-numeric:tabular-nums}
.tile .d{font-size:12.5px;color:var(--ink3);margin-top:4px;line-height:1.35}
.tile.alert{border-color:var(--rose)}
.tile.alert .v{color:var(--rose-ink)}

/* prosa */
.prose{max-width:68ch;font-size:15.6px;line-height:1.62;color:var(--ink2)}
.prose strong{color:var(--ink);font-weight:600}
.prose em{font-style:italic}

/* figuras */
figure{margin:22px 0 8px;background:var(--card);border:1px solid var(--line2);padding:17px 18px 14px}
figcaption{font-size:12.3px;color:var(--ink3);line-height:1.45;margin-top:11px;max-width:78ch}
.legend{display:flex;gap:15px;flex-wrap:wrap;font-size:12px;color:var(--ink2);margin-bottom:13px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:11px;height:11px;border-radius:50%;display:inline-block}
.sw.hollow{border-radius:0;width:2px;height:13px;background:var(--ink3)}
.chart{width:100%;overflow-x:auto}
svg{display:block;max-width:100%;height:auto}
.axl{font-size:11.5px;fill:var(--ink3)}
.lbl{font-size:12.5px;fill:var(--ink);font-weight:560}
.val{font-size:11.5px;fill:var(--ink2);font-variant-numeric:tabular-nums}
.gridline{stroke:var(--grid);stroke-width:1}

/* tabelas de troca */
.swap{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:20px}
@media(max-width:840px){.swap{grid-template-columns:1fr}}
.col{background:var(--card);border:1px solid var(--line2)}
.colh{padding:12px 14px;border-bottom:1px solid var(--line2);display:flex;align-items:baseline;gap:9px;flex-wrap:wrap}
.colh .t{font-size:14.5px;font-weight:680;letter-spacing:-.01em}
.colh .n{font-size:11.5px;color:var(--ink3);margin-left:auto;font-variant-numeric:tabular-nums}
.col.up .colh{background:var(--teal-wash)}
.col.up .colh .t{color:var(--teal-ink)}
.col.down .colh{background:var(--rose-wash)}
.col.down .colh .t{color:var(--rose-ink)}
.row{padding:10px 14px;border-top:1px solid var(--line);display:grid;grid-template-columns:52px 1fr;gap:11px;align-items:start}
.row:first-of-type{border-top:0}
.rate{font-size:14px;font-weight:700;font-variant-numeric:tabular-nums;letter-spacing:-.02em;padding-top:1px}
.col.up .rate{color:var(--teal-ink)}
.col.down .rate{color:var(--rose-ink)}
.rt{font-size:14.3px;line-height:1.35;color:var(--ink);font-weight:560}
.meta{font-size:11.5px;color:var(--ink3);margin-top:3px;line-height:1.4}
.mk{display:inline-block;font-size:10px;font-weight:750;letter-spacing:.05em;text-transform:uppercase;
  padding:1.5px 5px;background:var(--sunk);color:var(--ink2);margin-right:5px}
.mk.w{background:var(--ochre-wash);color:var(--ochre-ink)}

/* fila completa */
table{width:100%;border-collapse:collapse;font-size:13.6px}
th{text-align:left;font-size:10.5px;font-weight:750;letter-spacing:.09em;text-transform:uppercase;color:var(--ink3);
  padding:8px 9px;border-bottom:1px solid var(--line2);position:sticky;top:0;background:var(--paper)}
th.r,td.r{text-align:right;font-variant-numeric:tabular-nums}
td{padding:7px 9px;border-bottom:1px solid var(--line);color:var(--ink2);vertical-align:top}
tr:hover td{background:var(--sunk)}
td.tema{color:var(--ink)}
.pos{color:var(--ink3);font-variant-numeric:tabular-nums}
.tw{max-height:0;overflow:hidden}
details>summary{cursor:pointer;font-size:13.5px;color:var(--teal-ink);padding:9px 0;font-weight:600;list-style:none}
details>summary::-webkit-details-marker{display:none}
details>summary::before{content:"+ ";font-weight:800}
details[open]>summary::before{content:"– "}
.scroll{overflow-x:auto;border:1px solid var(--line2);background:var(--card)}

.warn{background:var(--ochre-wash);border-left:3px solid var(--ochre);padding:13px 16px;margin:20px 0;max-width:74ch}
.warn .k{font-size:10.5px;font-weight:750;letter-spacing:.1em;text-transform:uppercase;color:var(--ochre-ink);margin-bottom:5px}
.warn p{font-size:14.4px;line-height:1.55;color:var(--ink);margin:0 0 8px}
.warn p:last-child{margin:0}

footer{margin-top:56px;padding-top:20px;border-top:1px solid var(--line2)}
footer p{font-size:12.3px;color:var(--ink3);max-width:82ch;margin:0 0 8px}
code{font-family:ui-monospace,Consolas,monospace;font-size:11.8px;background:var(--sunk);padding:1px 5px}
</style>

<div class="wrap">
<header class="top">
  <p class="eye">MedHub · Cronograma EMED × ENAMED · semanas 15–30</p>
  <h1>A fila está certa. A prova é que é outra.</h1>
  <p class="lede">O cronograma não está gastando tempo com tema que cai pouco — a alocação por área bate quase perfeitamente com o guia estatístico. <strong>O problema é qual guia.</strong> As 16 semanas restantes foram desenhadas com o formato do ENARE, e a prova de 13/09 tem outro formato. Isso deixa <strong>12 slots a mais em Clínica Médica</strong> e <strong>14 a menos em Cirurgia e Pediatria</strong> exatamente na janela que antecede o ENAMED.</p>
</header>

<div class="tiles">
  <div class="tile"><div class="k">Janela até o ENAMED</div><div class="v">28<span style="font-size:17px;font-weight:600"> dias</span></div><div class="d">a 100q/dia × 5d/sem = ~2.000 questões</div></div>
  <div class="tile"><div class="k">Onde isso te deixa</div><div class="v">S19</div><div class="d">o ENAMED cai no meio da semana 19 do cronograma</div></div>
  <div class="tile"><div class="k">Blocos pendentes</div><div class="v">82</div><div class="d">158 task-slots em S15–S30</div></div>
  <div class="tile alert"><div class="k">Cabem antes da prova</div><div class="v">75</div><div class="d">task-slots — 47% do que resta</div></div>
</div>

<div class="bar">
  <h2>O cronograma está calibrado para outra prova</h2>
  <p class="note">Composição por grande área: o que o EMED reservou em S15–S30 contra o que o ENAMED cobra.</p>
</div>

<figure>
  <div class="legend">
    <span><i class="sw" style="background:var(--s2)"></i>EMED S15–S30 (slots)</span>
    <span><i class="sw" style="background:var(--s1)"></i>ENAMED medido</span>
    <span><i class="sw hollow"></i>guia ENARE</span>
  </div>
  <div class="chart">__CHART1__</div>
  <figcaption>O EMED acompanha o ENARE quase linha a linha (Clínica Médica 41,8% × 39,75%; Cirurgia 13,9% × 12,58%; Pediatria 13,3% × 12,36%). O ENAMED é uma prova achatada — cinco áreas entre 10% e 27%. <strong>A distância entre o ponto ocre e o ponto verde é o erro de calibragem.</strong> ENAMED medido = média de duas amostras independentes: as 95 questões do Simulado 2 classificadas uma a uma e os 120 erros dos Simulados 2–4.</figcaption>
</figure>

<div class="prose">
  <p>Vale insistir no que <em>não</em> foi encontrado: a hipótese de que o cronograma reserva as semanas iniciais a temas de baixa incidência <strong>não se sustenta</strong>. Medida contra o guia ENARE, a alocação por área do EMED tem razão entre 0,8 e 1,6 em 18 das 20 especialidades — é um cronograma bem construído. Ele só foi construído para o exame errado no que diz respeito a 13 de setembro.</p>
  <p>A consequência é aritmética. A 100 questões por dia, cinco dias por semana, sobram cerca de 2.000 questões até a prova — o suficiente para atravessar S14 e parar dentro da S19. Tudo que estiver agendado de S20 em diante <strong>não existe para o ENAMED</strong>. A fila não é uma preferência: é uma seleção de 75 slots entre 158.</p>
</div>

<div class="bar">
  <h2>O desequilíbrio da janela</h2>
  <p class="note">Slots reservados hoje em S15–S20 menos os slots que o blueprint do ENAMED justifica.</p>
</div>

<figure>
  <div class="legend">
    <span><i class="sw" style="background:var(--rose);border-radius:2px"></i>slots a mais do que a prova cobra</span>
    <span><i class="sw" style="background:var(--s1);border-radius:2px"></i>slots a menos do que a prova cobra</span>
  </div>
  <div class="chart">__CHART2__</div>
  <figcaption>Clínica Médica ocupa 32 dos 75 slots da janela quando o ENAMED justificaria 20. Pediatria e Cirurgia, juntas, aparecem com 11 slots a menos do que deveriam. Preventiva e GO estão praticamente no ponto.</figcaption>
</figure>

<div class="bar">
  <h2>A troca</h2>
  <p class="note">17 blocos entram, 15 saem. Saldo de 32 contra 33 slots — a janela não cresce.</p>
</div>

<div class="swap">
  <div class="col up">
    <div class="colh"><span class="t">Puxar para antes do ENAMED</span><span class="n">__NUP__ blocos · __TUP__ slots</span></div>
    __UP__
  </div>
  <div class="col down">
    <div class="colh"><span class="t">Empurrar para depois</span><span class="n">__NDN__ blocos · __TDN__ slots</span></div>
    __DOWN__
  </div>
</div>

<div class="warn">
  <div class="k">Três blocos saem contra o meu conselho</div>
  <p><strong>Diabetes na Gestação</strong> (7,67/slot, 2 erros nos simulados) e <strong>Vitalidade Fetal</strong> (7,67/slot) são bons temas — saem só porque GO já está com a cota cheia de blocos ainda melhores. Se sobrar folga na janela, são os dois primeiros a voltar.</p>
  <p><strong>Doenças Inflamatórias do Tecido Conjuntivo</strong> sai com 46% de acerto histórico em 24 questões — é o seu pior número entre todos os blocos pendentes. Vale 1 slot: mantenha se puder.</p>
</div>

<div class="bar">
  <h2>A fila inteira</h2>
  <p class="note">Os 82 blocos por rendimento esperado por slot. Ordem sugerida de execução, de cima para baixo.</p>
</div>

<details>
  <summary>Abrir os 82 blocos ranqueados</summary>
  <div class="scroll">
  <table>
    <thead><tr><th class="r">#</th><th class="r">rend/slot</th><th class="r">slots</th><th>S atual</th><th>Área</th><th>Tema</th><th>Por quê</th></tr></thead>
    <tbody>__FILA__</tbody>
  </table>
  </div>
</details>

<div class="bar">
  <h2>Como o número foi feito</h2>
  <p class="note">Duas camadas, cada uma da fonte que a sustenta.</p>
</div>

<div class="prose">
  <p><strong>Camada macro — de onde vem o peso da grande área.</strong> Não do guia. O guia ENARE descreve o ENARE, e medimos que o ENAMED tem outro formato. O peso macro vem de duas amostras do próprio ENAMED: as 95 questões do Simulado 2, classificadas uma a uma por área, e a distribuição dos 120 erros dos Simulados 2, 3 e 4. As duas concordam dentro de 6 pontos em todas as áreas.</p>
  <p><strong>Camada micro — de onde vem o peso do tema dentro da área.</strong> Do guia ENARE, que tem 453 questões de 2019 a 2024. Esta camada transfere entre bancas: quais temas de Ginecologia caem mais é uma propriedade da medicina e do edital, não do formato da prova. Cada bloco recebeu de 0,5 (ausente do guia) a 3,0 (topo do TOP-10 ou subárea dominante), com a justificativa registrada linha a linha na tabela acima.</p>
  <p><strong>Camada de fraqueza.</strong> Bônus de até +1,0 para bloco que já custou erro nos três simulados ou que tem acerto histórico abaixo de 70% com pelo menos 20 questões. É o que promove <em>Reanimação Neonatal</em> e <em>Câncer de Colo</em> acima de pares de mesma prevalência.</p>
  <p><strong>Custo.</strong> O rendimento é dividido pelo número de task-slots que o EMED reservou ao bloco — um tema que precisa de 4 passagens custa 4× mais do que um que precisa de 1. É isso que derruba <em>Urologia</em> (4 slots, ausente do guia) e <em>Pneumonias Bacterianas</em> (4 slots) na fila.</p>
</div>

<div class="warn">
  <div class="k">O que não confiar</div>
  <p><strong>O split fino dentro de Clínica Médica é a camada mais mole.</strong> Ele vem das proporções do ENARE renormalizadas — a única fonte com amostra suficiente para 14 especialidades. No Simulado 2, Infectologia teve 6,3% das questões contra os 2,9% que esse método atribui. Se você acha que Infecto e Pneumo caem mais do que a fila sugere, você provavelmente está certo, e <em>Pneumonias Bacterianas</em> merece revisão manual antes de descer.</p>
  <p><strong>O baseline da ordem atual vem do <code>grade.json</code>, derivado do PDF.</strong> A planilha do Drive foi sincronizada pela última vez em 26/07 e você reordena o xlsx à mão. Se já mexeu em S15+ desde então, confira antes de aplicar.</p>
  <p><strong>Reordenar tem custo.</strong> O EMED espaça teoria e revisão de propósito. A troca preserva o par (teoria e revisão viajam juntas), mas encurta alguns intervalos. Para tema que você já domina isso é barato; para tema frio, não.</p>
</div>

<footer>
  <p><strong>Fontes:</strong> <code>core/cronograma/grade.json</code> (352 tasks, derivado de <code>Cronograma.pdf</code>) · <code>ipub.db</code> (<code>questoes_erros</code>, <code>taxonomia_cronograma</code>) · <code>Guia_Estatístico_-_ENARE.pdf</code>, páginas 8–28 · <code>Simulado 2 - pt1..5.pdf</code>, 95 questões classificadas.</p>
  <p><strong>Datas:</strong> hoje 16/08/2026 · ENAMED 13/09/2026 (28 dias) · fim da grade EMED 25/10/2026 (70 dias). Ritmo assumido: 100 questões/dia, 5 dias por semana, conforme decidido na sessão 145.</p>
  <p><strong>Não é o guia do ENAMED.</strong> Os três guias disponíveis são ENARE, UERJ e USP-SP; o Estratégia não publicou um guia estatístico do ENAMED. O ENARE é o mais próximo por ser exame nacional multi-institucional, e é usado aqui só na camada micro, justamente porque a camada macro não transfere.</p>
</footer>
</div>
"""


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---------------- chart 1: dumbbell ----------------
def chart1(macro):
    W, RH, L, R = 760, 46, 178, 58
    H = 22 + len(macro) * RH + 26
    mx = 45.0
    px = lambda v: L + v / mx * (W - L - R)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Composição por grande área: EMED contra ENAMED">']
    for g in (0, 10, 20, 30, 40):
        x = px(g)
        out.append(f'<line class="gridline" x1="{x:.1f}" y1="16" x2="{x:.1f}" y2="{22+len(macro)*RH:.0f}"/>')
        out.append(f'<text class="axl" x="{x:.1f}" y="{H-8}" text-anchor="middle">{g}%</text>')
    for i, m in enumerate(macro):
        y = 22 + i * RH + RH / 2 - 6
        a, b, n = px(m["emed"]), px(m["enamed"]), px(m["enare"])
        out.append(f'<text class="lbl" x="{L-13}" y="{y+4:.1f}" text-anchor="end">{esc(m["area"])}</text>')
        out.append(f'<line x1="{min(a,b):.1f}" y1="{y:.1f}" x2="{max(a,b):.1f}" y2="{y:.1f}" '
                   f'stroke="var(--line2)" stroke-width="2"/>')
        out.append(f'<line x1="{n:.1f}" y1="{y-7:.1f}" x2="{n:.1f}" y2="{y+7:.1f}" stroke="var(--ink3)" '
                   f'stroke-width="2"><title>guia ENARE: {m["enare"]}%</title></line>')
        out.append(f'<circle cx="{b:.1f}" cy="{y:.1f}" r="6" fill="var(--s1)" stroke="var(--card)" stroke-width="2">'
                   f'<title>ENAMED medido: {m["enamed"]}% (simulado {m["sim"]}% · erros {m["err"]}%)</title></circle>')
        out.append(f'<circle cx="{a:.1f}" cy="{y:.1f}" r="6" fill="var(--s2)" stroke="var(--card)" stroke-width="2">'
                   f'<title>EMED S15-S30: {m["emed"]}% dos slots</title></circle>')
        ta = "end" if a < b else "start"
        tb = "start" if a < b else "end"
        out.append(f'<text class="val" x="{a + (-10 if a<b else 10):.1f}" y="{y+4:.1f}" text-anchor="{ta}">{m["emed"]}%</text>')
        out.append(f'<text class="val" x="{b + (10 if a<b else -10):.1f}" y="{y+4:.1f}" text-anchor="{tb}">{m["enamed"]}%</text>')
    out.append("</svg>")
    return "\n".join(out)


# ---------------- chart 2: diverging ----------------
def chart2(jan):
    W, RH, L = 760, 42, 178
    H = 16 + len(jan) * RH + 26
    mx = 13.0
    zero = L + (W - L - 50) / 2
    half = (W - L - 50) / 2
    px = lambda v: zero + v / mx * half
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Excesso e déficit de slots na janela pré-ENAMED">']
    for g in (-10, -5, 5, 10):
        x = px(g)
        out.append(f'<line class="gridline" x1="{x:.1f}" y1="10" x2="{x:.1f}" y2="{16+len(jan)*RH:.0f}"/>')
        out.append(f'<text class="axl" x="{x:.1f}" y="{H-8}" text-anchor="middle">{abs(g)}</text>')
    for i, m in enumerate(jan):
        y = 16 + i * RH + 8
        d = m["delta"]
        x0, x1 = (zero, px(d)) if d >= 0 else (px(d), zero)
        col = "var(--rose)" if d >= 0 else "var(--s1)"
        out.append(f'<text class="lbl" x="{L-13}" y="{y+15:.1f}" text-anchor="end">{esc(m["area"])}</text>')
        out.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{max(2,x1-x0):.1f}" height="20" rx="3" fill="{col}">'
                   f'<title>{esc(m["area"])}: {m["hoje"]} slots hoje, {m["ideal"]} justificados pelo ENAMED</title></rect>')
        lx = (x1 + 8) if d >= 0 else (x0 - 8)
        an = "start" if d >= 0 else "end"
        sig = "+" if d >= 0 else ""
        out.append(f'<text class="val" x="{lx:.1f}" y="{y+14:.1f}" text-anchor="{an}">{sig}{d:.0f} slots</text>')
    out.append(f'<line x1="{zero:.1f}" y1="10" x2="{zero:.1f}" y2="{16+len(jan)*RH:.0f}" stroke="var(--ink2)" stroke-width="1.5"/>')
    out.append(f'<text class="axl" x="{zero:.1f}" y="{H-8}" text-anchor="middle">0</text>')
    out.append("</svg>")
    return "\n".join(out)


def linhas(bl, up):
    o = []
    for b in bl:
        mot = "".join(f'<span class="mk w">{esc(m)}</span>' for m in b["mot"])
        o.append(f'<div class="row"><span class="rate">{b["r"]:.1f}</span><span>'
                 f'<span class="rt">{esc(b["rotulo"])}</span>'
                 f'<span class="meta"><span class="mk">{esc(b["area"])}</span>'
                 f'<span class="mk">S{b["s"]} · {b["t"]} slot{"s" if b["t"]>1 else ""}</span>{mot}<br>{esc(b["just"])}</span>'
                 f'</span></div>')
    return "\n".join(o)


def fila(bl):
    o = []
    for i, b in enumerate(bl, 1):
        mot = " · ".join(b["mot"])
        o.append(f'<tr><td class="r pos">{i}</td><td class="r">{b["r"]:.1f}</td><td class="r">{b["t"]}</td>'
                 f'<td class="pos">S{b["s"]}</td><td>{esc(b["area"])}</td><td class="tema">{esc(b["rotulo"])}</td>'
                 f'<td>{esc(b["just"])}{(" · " + esc(mot)) if mot else ""}</td></tr>')
    return "\n".join(o)


def render():
    return (TPL.replace("__CHART1__", chart1(D["macro"]))
               .replace("__CHART2__", chart2(D["janela"]))
               .replace("__UP__", linhas(D["puxar"], True))
               .replace("__DOWN__", linhas(D["empurrar"], False))
               .replace("__NUP__", str(len(D["puxar"])))
               .replace("__TUP__", str(sum(b["t"] for b in D["puxar"])))
               .replace("__NDN__", str(len(D["empurrar"])))
               .replace("__TDN__", str(sum(b["t"] for b in D["empurrar"])))
               .replace("__FILA__", fila(D["fila"])))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.path.join(ROOT, "artifacts", "fila-enamed.html"))
    a = ap.parse_args()
    html = render()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK -> {a.out} | {len(html):,} bytes | {len(D['fila'])} blocos | "
          f"{len(D['puxar'])} puxar / {len(D['empurrar'])} empurrar")


if __name__ == "__main__":
    main()
