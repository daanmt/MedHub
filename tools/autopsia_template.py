# -*- coding: utf-8 -*-
"""Template HTML da Autopsia dos Simulados. So texto: nenhuma logica de dados aqui."""

TPL = r"""<title>Autópsia dos Simulados</title>
<style>
:root{
  --paper:#ECEFE9; --card:#FAFBF8; --sunk:#E2E6DE;
  --ink:#161A17; --ink2:#4A544C; --ink3:#7B857D;
  --line:rgba(22,26,23,.13); --line2:rgba(22,26,23,.28);
  --teal:#1A5654; --teal-ink:#123E3C; --teal-wash:#DCE9E6;
  --rose:#A03A5D; --rose-ink:#7C2946; --rose-wash:#F4E1E7;
  --ochre:#8A6A12; --ochre-ink:#68500C; --ochre-wash:#F2E9CE;
  --on:#FFFFFF;
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
  --sh:0 1px 2px rgba(0,0,0,.45),0 12px 30px -16px rgba(0,0,0,.75);
  color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--paper);color:var(--ink);
  font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
.mn{font-family:ui-monospace,"SF Mono",SFMono-Regular,Consolas,monospace;font-variant-numeric:tabular-nums}
h1,h2,h3{margin:0;font-weight:670;letter-spacing:-.025em;text-wrap:balance;line-height:1.14}
h1{font-size:clamp(27px,4.4vw,42px)}
h2{font-size:clamp(18px,2.3vw,23px)}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 90px}
:focus-visible{outline:2px solid var(--teal);outline-offset:2px}
button{font-family:inherit;cursor:pointer}

/* masthead */
.top{padding:46px 0 26px}
.eye{font-size:11px;font-weight:750;letter-spacing:.14em;text-transform:uppercase;color:var(--teal);margin:0 0 13px}
.top h1{margin-bottom:14px;max-width:19ch}
.sub{font-size:17px;line-height:1.55;color:var(--ink2);max-width:62ch;margin:0}
.track{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:30px 0 8px}
.sim{background:var(--card);border:1px solid var(--line2);padding:15px 16px}
.sim .sn{font-size:11px;font-weight:750;letter-spacing:.11em;text-transform:uppercase;color:var(--ink3)}
.sim .sd{font-size:11.5px;color:var(--ink3);margin-top:1px}
.sim .row{display:flex;align-items:flex-end;gap:9px;margin-top:9px}
.sim .sc{font-size:37px;font-weight:680;letter-spacing:-.04em;line-height:.9;font-variant-numeric:tabular-nums}
.sim .of{font-size:13px;color:var(--ink3);padding-bottom:3px}
.sim .dl{font-size:12.5px;font-weight:700;color:var(--teal);padding-bottom:3px;margin-left:auto}
.gauge{height:5px;background:var(--sunk);margin-top:12px;position:relative}
.gauge i{position:absolute;left:0;top:0;height:100%;background:var(--teal);display:block}
.gauge b{position:absolute;top:-3px;width:1px;height:11px;background:var(--ink3)}
.simfoot{font-size:11.5px;color:var(--ink3);margin-top:9px;display:flex;justify-content:space-between;gap:8px}
@media(max-width:980px){.track{grid-template-columns:repeat(2,1fr)}}
@media(max-width:520px){.track{grid-template-columns:1fr}}

.bar{display:flex;align-items:baseline;gap:12px;border-bottom:2px solid var(--ink);padding-bottom:7px;margin:46px 0 18px;flex-wrap:wrap}
.bar h2{flex:1;min-width:200px}
.bar .note{font-size:12px;color:var(--ink3);max-width:46ch}

/* ── ONDE A CADEIA QUEBRA ─────────────── */
.stages{display:grid;grid-template-columns:1fr;gap:1px;background:var(--line2);border:1px solid var(--line2)}
.stg{display:grid;grid-template-columns:190px 1fr 62px;gap:14px;align-items:center;width:100%;
  background:var(--card);border:0;text-align:left;color:inherit;padding:11px 15px}
.stg:hover{background:var(--sunk)}
.stg.on{background:var(--teal-wash)}
.stg .snm{font-size:14.2px;font-weight:640;letter-spacing:-.01em}
.stg .sds{font-size:11.8px;color:var(--ink3);margin-top:1px;line-height:1.35}
.stg .sbar{height:9px;background:var(--sunk);position:relative;min-width:40px}
.stg .sbar i{position:absolute;left:0;top:0;height:100%;background:var(--rose);display:block}
.stg .sbar u{position:absolute;top:0;height:100%;background:var(--teal);opacity:.42;display:block;text-decoration:none}
.stg .snum{text-align:right;font-size:19px;font-weight:680;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.stg .snum s{display:block;font-size:10.5px;font-weight:600;color:var(--ink3);text-decoration:none;letter-spacing:.04em}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:11.5px;color:var(--ink3);margin:9px 0 0;padding:0 1px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend i{width:11px;height:9px;display:inline-block}
@media(max-width:720px){.stg{grid-template-columns:1fr 52px;gap:8px}.stg .sbar{grid-column:1/-1}}

/* mecanismos */
.mecs{display:flex;flex-direction:column;gap:1px;background:var(--line2);border:1px solid var(--line2)}
.mec{background:var(--card)}
.mhead{display:grid;grid-template-columns:26px 1fr auto;gap:13px;align-items:center;width:100%;
  padding:13px 15px;background:none;border:0;text-align:left;color:inherit}
.mhead:hover{background:var(--sunk)}
.mec.open .mhead{background:var(--sunk)}
.chev{width:22px;height:22px;border:1px solid var(--line2);display:flex;align-items:center;justify-content:center;
  font-size:13px;color:var(--ink3);transition:transform .16s ease;flex-shrink:0}
.mec.open .chev{transform:rotate(45deg);border-color:var(--teal);color:var(--teal)}
.mname{font-size:15.5px;font-weight:640;letter-spacing:-.012em;display:block}
.mres{font-size:13px;color:var(--ink3);margin-top:2px;line-height:1.4;max-width:72ch;display:block}
.mec.open .mres{display:none}
.spark{display:flex;align-items:center;gap:9px;flex-shrink:0}
.pips{display:flex;gap:2px;align-items:flex-end;height:24px}
.pip{width:13px;background:var(--teal);opacity:.85}
.pip.z{background:var(--line2);height:2px!important}
.mtot{font-size:20px;font-weight:680;letter-spacing:-.03em;min-width:26px;text-align:right;font-variant-numeric:tabular-nums}
.mbody{display:none;padding:2px 15px 20px 54px;border-top:1px solid var(--line)}
.mec.open .mbody{display:block}
.mblock{margin-bottom:15px}
.mblock:last-child{margin-bottom:0}
.mlab{font-size:10.5px;font-weight:750;letter-spacing:.11em;text-transform:uppercase;color:var(--ink3);margin-bottom:5px}
.mtext{font-size:15.3px;line-height:1.6;color:var(--ink2);max-width:74ch}
.mtext strong{color:var(--ink);font-weight:600}
.ritual{background:var(--teal-wash);border-left:3px solid var(--teal);padding:12px 15px;max-width:74ch}
.ritual .mlab{color:var(--teal-ink)}
.ritual .mtext{color:var(--ink)}
.mcases{display:flex;flex-wrap:wrap;gap:6px;margin-top:3px}
.cbtn{font-size:12px;padding:4px 9px;border:1px solid var(--line2);background:var(--card);color:var(--ink2)}
.cbtn:hover{border-color:var(--teal);color:var(--teal-ink)}
.cbtn .s{font-weight:700;color:var(--ink3);margin-right:5px}
.cbtn.all{background:var(--teal);border-color:var(--teal);color:var(--on);font-weight:640}
.pill{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:600;
  color:var(--ochre-ink);background:var(--ochre-wash);border:1px solid var(--ochre);padding:4px 5px 4px 11px}
.pill button{border:0;background:rgba(0,0,0,.09);color:inherit;width:17px;height:17px;font-size:12px;line-height:1;padding:0}
@media(max-width:640px){.mbody{padding-left:15px}.mhead{grid-template-columns:22px 1fr;gap:10px}.spark{grid-column:2;margin-top:6px}}

/* filtros */
.filters{position:sticky;top:0;z-index:30;background:var(--paper);padding:11px 0 9px;
  border-bottom:1px solid var(--line2);display:flex;flex-direction:column;gap:8px}
.filters::before{content:"";position:absolute;inset:0 -20px auto -20px;background:var(--paper);z-index:-1;border-bottom:1px solid var(--line2)}
.frow{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.chip{font-size:12.5px;padding:4px 10px;border:1px solid transparent;background:none;color:var(--ink3);
  border-radius:2px;line-height:1.5}
.chip:hover{color:var(--ink);background:var(--sunk)}
.chip.on{background:var(--ink);color:var(--paper);font-weight:600}
.chip .n{opacity:.55;margin-left:5px;font-variant-numeric:tabular-nums;font-size:11px}
.chip.sub{font-size:12px;padding:3px 9px;color:var(--ink3)}
.chip.sub.on{background:var(--teal);color:var(--on)}
.sep{width:1px;align-self:stretch;background:var(--line2);margin:2px 5px}
.search{margin-left:auto;display:flex;align-items:center;gap:6px;border:1px solid var(--line2);
  background:var(--card);padding:0 9px;height:28px;max-width:210px;flex:0 1 210px}
.search svg{width:13px;height:13px;flex-shrink:0;stroke:var(--ink3);fill:none;stroke-width:2}
.search input{border:0;background:none;color:var(--ink);font:inherit;font-size:12.5px;width:100%;padding:0;outline:none}
.search input::placeholder{color:var(--ink3)}
.search:focus-within{border-color:var(--teal)}
.count{font-size:11.5px;color:var(--ink3);font-variant-numeric:tabular-nums;white-space:nowrap}
@media(max-width:640px){.search{margin-left:0;flex:1 1 100%;max-width:none}}

/* lista de erros */
.list{display:flex;flex-direction:column;gap:9px;padding-top:18px}
.err{background:var(--card);border:1px solid var(--line);scroll-margin-top:130px}
.err.open{border-color:var(--line2);box-shadow:var(--sh)}
.err.hit{border-color:var(--teal)}
.ehead{width:100%;padding:13px 15px;background:none;border:0;text-align:left;color:inherit;display:flex;gap:13px;align-items:flex-start}
.ehead:hover{background:var(--sunk)}
.emain{flex:1;min-width:0}
.etitle{font-size:15.5px;font-weight:620;letter-spacing:-.012em;line-height:1.32;margin-bottom:7px;display:block}
.tags{display:flex;flex-wrap:wrap;gap:5px;align-items:center}
.tag{font-size:11px;padding:2.5px 7px;border:1px solid var(--line2);color:var(--ink3);white-space:nowrap}
.tag.sim{font-weight:750;letter-spacing:.05em;color:var(--teal-ink);border-color:var(--teal);background:var(--teal-wash)}
.tag.mec{background:var(--sunk);border-color:transparent;color:var(--ink2);font-weight:600}
.tag.brk{background:var(--rose-wash);border-color:var(--rose);color:var(--rose-ink);font-weight:640}
.tag.auto{font-style:italic;opacity:.75}
.tag.cx{border-color:var(--ochre);color:var(--ochre-ink);background:var(--ochre-wash)}
.eid{font-size:11.5px;color:var(--ink3);flex-shrink:0;padding-top:2px}
.ebody{display:none}
.err.open .ebody{display:block}
.eblock{padding:0 15px 15px}
.elab{font-size:10.5px;font-weight:750;letter-spacing:.11em;text-transform:uppercase;color:var(--ink3);margin-bottom:5px}
.etext{font-size:15.2px;line-height:1.62;color:var(--ink2);text-align:justify;
  text-justify:inter-word;hyphens:auto;-webkit-hyphens:auto}
.etext.serif{font-family:Georgia,"Iowan Old Style",serif;font-size:16px;color:var(--ink)}
/* colapso de bloco longo */
.clipw{position:relative}
.clipw.off .etext{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.clipw.off::after{content:"";position:absolute;left:0;right:0;bottom:0;height:26px;pointer-events:none;
  background:linear-gradient(to bottom,transparent,var(--card))}
.eblock.arm .clipw.off::after{background:linear-gradient(to bottom,transparent,var(--rose-wash))}
.elabrow{display:flex;align-items:center;gap:9px;margin-bottom:5px}
.elabrow .elab{margin:0}
.tgl{margin-left:auto;font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--ink3);background:none;border:0;padding:2px 4px;flex-shrink:0}
.tgl:hover{color:var(--teal-ink)}
.eblock.arm{background:var(--rose-wash);margin:0 15px 15px;padding:12px 15px;border-left:3px solid var(--rose)}
.eblock.arm .elab{color:var(--rose-ink)}
.eblock.arm .etext{color:var(--ink)}
.eblock.exp{border-left:3px solid var(--teal);margin:0 15px 15px;padding:2px 0 2px 14px}
.empty{padding:56px 20px;text-align:center;color:var(--ink3);font-size:14.5px}

/* o discriminador que faltou */
.gap{margin:0 15px 15px;background:var(--rose-wash);border-left:3px solid var(--rose);padding:11px 14px}
.gap .elab{color:var(--rose-ink);margin-bottom:4px}
.gap .g{font-size:15px;line-height:1.5;color:var(--ink);font-weight:560}
.gap .mecl{font-size:11.5px;color:var(--rose-ink);margin-top:6px;opacity:.85}
.lnk{background:none;border:0;padding:0;font:inherit;color:inherit;text-decoration:underline;
  text-underline-offset:2px;font-weight:640}

/* comando da questao */
.cmd{margin:0 15px 15px;background:var(--sunk);border-left:3px solid var(--ink3);padding:11px 14px}
.cmd .elab{margin-bottom:4px}
.cmd .q{font-family:Georgia,"Iowan Old Style",serif;font-size:16.5px;line-height:1.45;color:var(--ink);font-weight:600}
.cmd.miss .q{font-style:italic;font-weight:400;color:var(--ink3);font-family:inherit;font-size:14px}

/* alternativas com % da turma */
.alts{margin:0 15px 15px;border:1px solid var(--line2)}
.alt{display:grid;grid-template-columns:26px 1fr 92px;gap:10px;align-items:center;padding:9px 12px;font-size:14px}
.alts.parcial .alt{grid-template-columns:26px 1fr}
.alt+.alt{border-top:1px solid var(--line)}
.alt .lt{font-weight:700;color:var(--ink3);font-variant-numeric:tabular-nums}
.alt .tx{color:var(--ink2);line-height:1.4}
.alt .pc{position:relative;height:16px;background:var(--sunk)}
.alt .pc i{position:absolute;left:0;top:0;height:100%;background:var(--line2);display:block}
.alt .pc s{position:absolute;right:5px;top:0;line-height:16px;font-size:11px;color:var(--ink2);
  text-decoration:none;font-variant-numeric:tabular-nums}
.alt.ok{background:var(--teal-wash)}
.alt.ok .lt,.alt.ok .tx{color:var(--teal-ink)}
.alt.ok .pc i{background:var(--teal);opacity:.55}
.alt.bad{background:var(--rose-wash)}
.alt.bad .lt,.alt.bad .tx{color:var(--rose-ink)}
.alt.bad .pc i{background:var(--rose);opacity:.55}
.alt .mk{font-size:13px;font-weight:800;margin-right:2px}
@media(max-width:600px){.alt{grid-template-columns:24px 1fr;gap:7px}.alt .pc{grid-column:2}}

/* lane simples (S3/S4, sem % por alternativa) */
.split{margin:0 15px 15px;border:1px solid var(--line2);background:var(--paper)}
.lane{display:grid;grid-template-columns:96px 1fr;align-items:stretch;font-size:14.2px;line-height:1.45}
.lane+.lane{border-top:1px solid var(--line2)}
.lane .lb{padding:10px 11px;font-size:10.5px;font-weight:750;letter-spacing:.09em;text-transform:uppercase;
  display:flex;align-items:center;gap:6px;border-right:1px solid var(--line2)}
.lane .lt{padding:10px 13px;color:var(--ink)}
.lane.bad .lb{background:var(--rose-wash);color:var(--rose-ink)}
.lane.bad .lt{color:var(--ink2)}
.lane.ok .lb{background:var(--teal-wash);color:var(--teal-ink)}
.mark{font-size:14px;font-weight:800}
@media(max-width:600px){.lane{grid-template-columns:1fr}.lane .lb{border-right:0;border-bottom:1px solid var(--line2)}}

/* ── ESCADA: cadeia de habilidades com semaforo ── */
.ladder{list-style:none;margin:0 15px 15px;padding:0;border:1px solid var(--line2)}
.rung{display:grid;grid-template-columns:30px 1fr auto;gap:12px;align-items:flex-start;padding:10px 12px}
.rung+.rung{border-top:1px solid var(--line)}
.rung .rn{width:22px;height:22px;border:1px solid var(--line2);display:flex;align-items:center;justify-content:center;
  font-size:11.5px;font-weight:700;color:var(--ink3);font-variant-numeric:tabular-nums;flex-shrink:0}
.rung .rstage{font-size:10px;font-weight:750;letter-spacing:.1em;text-transform:uppercase;color:var(--ink3);display:block;margin-bottom:2px}
.rung .rtxt{font-size:14.3px;line-height:1.45;color:var(--ink2);display:block}
.rung .rst{font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;white-space:nowrap;
  padding-top:3px;color:var(--ink3)}
.rung.ok{background:var(--teal-wash)}
.rung.ok .rn{border-color:var(--teal);color:var(--teal-ink)}
.rung.ok .rtxt{color:var(--ink)}
.rung.ok .rst,.rung.ok .rstage{color:var(--teal-ink)}
.rung.quebrado{background:var(--rose-wash);box-shadow:inset 3px 0 0 var(--rose)}
.rung.quebrado .rn{border-color:var(--rose);color:var(--rose-ink);font-weight:800}
.rung.quebrado .rtxt{color:var(--ink);font-weight:560}
.rung.quebrado .rst,.rung.quebrado .rstage{color:var(--rose-ink)}
.rung.aberto{background:var(--card)}
.rung.aberto .rtxt{color:var(--ink3)}
.ladkey{display:flex;gap:14px;flex-wrap:wrap;font-size:11.3px;color:var(--ink3);margin:-9px 15px 15px;padding-left:2px}

/* ── CARDS FSRS ─────────────────────────── */
.cards{margin:0 15px 15px;display:flex;flex-direction:column;gap:1px;background:var(--line2);border:1px solid var(--line2)}
.fc{background:var(--card);padding:11px 13px}
.fcmeta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:6px}
.fct{font-size:10px;font-weight:750;letter-spacing:.09em;text-transform:uppercase;padding:2px 6px;
  background:var(--sunk);color:var(--ink2)}
.fct.elo_quebrado{background:var(--rose-wash);color:var(--rose-ink)}
.fct.armadilha{background:var(--ochre-wash);color:var(--ochre-ink)}
.fcd{font-size:11px;color:var(--ink3);border:1px solid var(--line2);padding:2px 6px;white-space:nowrap}
.fcd.novo{border-color:var(--ochre);color:var(--ochre-ink);background:var(--ochre-wash);font-weight:640}
.fcd.late{border-color:var(--rose);color:var(--rose-ink);background:var(--rose-wash);font-weight:640}
.fcd.deg{border-color:transparent;background:var(--sunk);color:var(--ink2);font-weight:640}
.fcq{font-size:14.6px;line-height:1.45;color:var(--ink);font-weight:560}
.fcc{font-size:12.8px;color:var(--ink3);line-height:1.4;margin-bottom:3px}
.fca{font-size:14px;line-height:1.5;color:var(--ink2);margin-top:6px;padding-left:11px;border-left:2px solid var(--teal)}
.cardstat{font-size:11.5px;color:var(--ink3);margin:-9px 15px 15px;padding-left:2px}

footer{margin-top:56px;padding-top:20px;border-top:1px solid var(--line2)}
footer p{font-size:12.3px;color:var(--ink3);max-width:82ch;margin:0 0 7px}
code{font-family:ui-monospace,Consolas,monospace;font-size:11.8px;background:var(--sunk);padding:1px 5px}
</style>

<div class="wrap">
<header class="top">
  <p class="eye">MedHub · Autópsia dos simulados · 157 erros mapeados</p>
  <h1>Quatro provas, um punhado de bugs</h1>
  <p class="sub">Os erros dos Simulados 2, 3, 4 e 5 reunidos num lugar só — navegáveis pelo <strong>mecanismo que os produziu</strong> e pelo <strong>degrau da cadeia em que o raciocínio quebrou</strong>. Cada caso mostra a escada inteira: o que você executou, onde parou, e os flashcards que nasceram dali.</p>
  <div class="track" id="track"></div>
</header>

<div class="bar">
  <h2>Onde a cadeia quebra</h2>
  <p class="note">Cada erro tem uma cadeia de habilidades sequenciais. A barra mostra quantos degraus daquele tipo você <strong>executou</strong> e em quantos a cadeia <strong>parou</strong>. Clique para filtrar os erros que quebraram ali.</p>
</div>
<div class="stages" id="stages"></div>
<p class="legend">
  <span><i style="background:var(--rose)"></i>degrau onde a cadeia quebrou</span>
  <span><i style="background:var(--teal);opacity:.42"></i>degrau executado antes da quebra</span>
  <span>Degraus depois da quebra não entram na conta — nunca chegaram a ser testados.</span>
</p>

<div class="bar">
  <h2>Mecanismos</h2>
  <p class="note">Ordenados por frequência. As barras mostram a distribuição entre os três simulados.</p>
</div>
<div class="mecs" id="mecs"></div>

<div class="bar" style="margin-bottom:0;border-bottom:0">
  <h2>Todos os erros</h2>
  <p class="note">Clique num caso para abrir a vinheta, a escada de habilidades, o bug sistêmico e os cards forjados.</p>
</div>
<div class="filters">
  <div class="frow">
    <span id="fsim"></span><span class="sep"></span><span id="fmacro"></span>
    <label class="search">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4.2-4.2"/></svg>
      <input type="search" id="q" placeholder="Buscar" aria-label="Buscar nos erros">
    </label>
  </div>
  <div class="frow" id="subrow" style="display:none"><span id="fsub"></span></div>
  <div class="frow" id="pillrow" style="display:none"><span id="pills"></span><span class="count" id="cnt"></span></div>
  <div class="frow" id="cntrow"><span class="count" id="cnt2"></span></div>
</div>
<div class="list" id="list"></div>
<div class="empty" id="empty" style="display:none">Nenhum erro corresponde a esses filtros.</div>

<footer>
  <p><strong>Fonte:</strong> <code>ipub.db</code> — tabelas <code>questoes_erros</code>, <code>flashcards</code> e <code>fsrs_cards</code>. Simulado 2 (ids 622–667), Simulado 3 (719–758), Simulado 4 (781–814), Simulado 5 (815–851). O texto das questões dos <strong>Simulados 2 e 5 é verbatim do PDF da prova</strong>, com o percentual da turma em cada alternativa; Simulados 3 e 4 usam o registro condensado do banco, porque o PDF dessas provas não está no repositório. No Simulado 5, duas questões (Q20 e Q100) vieram truncadas no export da plataforma — confirmadas CERTA pelo usuário, mas sem enunciado recuperável, por isso não aparecem como caso mapeado aqui.</p>
  <p><strong>Sobre a classificação:</strong> o <em>mecanismo</em> dos 34 erros do Simulado 4 foi classificado à mão a partir dos comentários da banca; os 86 dos Simulados 2 e 3, automaticamente a partir do texto de análise registrado — casos marcados <em>classif. auto</em> podem conter imprecisão. O <em>degrau em que a cadeia quebrou</em> e a <em>etapa cognitiva</em> de cada degrau saem de uma heurística revisada caso a caso à mão (20 elos e 38 etapas corrigidos manualmente); a curadoria vive em <code>core/simulados/curadoria.json</code>. O vínculo card ↔ degrau é inferido por sobreposição lexical e é o elo mais frágil da página.</p>
  <p><strong>Regenerar:</strong> <code>python -X utf8 tools/autopsia_simulados.py</code>.</p>
</footer>
</div>

<script>
const D = __DATA__;
const $ = s => document.querySelector(s);
const esc = s => (s||"").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const SIMK = ["S2","S3","S4","S5"];
const ETAPA = {}; D.etapas.forEach(e => ETAPA[e.k] = e);
let fSim = null, fMacro = null, fArea = null, fMec = null, fEtapa = null, fQ = "";

/* ── trilha ── */
$("#track").innerHTML = SIMK.map((k,i) => {
  const s = D.sims[k], prev = i ? D.sims[SIMK[i-1]].score : null;
  const dl = prev === null ? "" : `<span class="dl">+${s.score-prev}</span>`;
  return `<div class="sim"><div class="sn">${esc(s.nome)}</div><div class="sd">${s.data}</div>
    <div class="row"><span class="sc">${s.score}</span><span class="of">/100</span>${dl}</div>
    <div class="gauge"><i style="width:${s.score}%"></i><b style="left:60%"></b></div>
    <div class="simfoot"><span>${s.erros} erros mapeados</span><span>piso ENAMED 60</span></div></div>`;
}).join("");

/* ── onde a cadeia quebra ── */
const stat = {};
D.etapas.forEach(e => stat[e.k] = {brk:0, ok:0});
D.erros.forEach(e => e.cad.forEach(b => {
  if (b.st === "quebrado") stat[b.tipo].brk++;
  else if (b.st === "ok") stat[b.tipo].ok++;
}));
const ordStg = D.etapas.slice().sort((a,b) => stat[b.k].brk - stat[a.k].brk);
const maxStg = Math.max(...D.etapas.map(e => stat[e.k].brk + stat[e.k].ok), 1);
$("#stages").innerHTML = ordStg.map(e => {
  const s = stat[e.k], wb = s.brk/maxStg*100, wo = s.ok/maxStg*100;
  return `<button class="stg" data-etapa="${e.k}" aria-pressed="false">
    <span><span class="snm">${esc(e.n)}</span><span class="sds">${esc(e.d)}</span></span>
    <span class="sbar" title="${s.brk} quebras · ${s.ok} executados">
      <i style="width:${wb}%"></i><u style="left:${wb}%;width:${wo}%"></u></span>
    <span class="snum">${s.brk}<s>quebras</s></span></button>`;
}).join("");

/* ── mecanismos ── */
const byMec = m => D.erros.filter(e => e.mec === m);
const maxMec = Math.max(...D.ordem.map(m => byMec(m).length));
$("#mecs").innerHTML = D.ordem.map(m => {
  const info = D.mec[m], list = byMec(m);
  if (!list.length) return "";
  const per = SIMK.map(k => list.filter(e => e.sim === k).length);
  const pips = per.map((n,i) => n
    ? `<span class="pip" style="height:${Math.max(4, n/maxMec*24)}px" title="${SIMK[i]}: ${n}"></span>`
    : `<span class="pip z" title="${SIMK[i]}: 0"></span>`).join("");
  const cases = `<button class="cbtn all" data-filter-mec="${m}">Ver os ${list.length} na lista ↓</button>` +
    list.map(e => `<button class="cbtn" data-goto="${e.id}"><span class="s">${e.sim}</span>${esc(e.tema||e.area)}</button>`).join("");
  return `<div class="mec" data-mec="${m}">
    <button class="mhead" data-toggle="${m}" aria-expanded="false">
      <span class="chev" aria-hidden="true">+</span>
      <span><span class="mname">${info.nome}</span><span class="mres">${info.resumo}</span></span>
      <span class="spark"><span class="pips">${pips}</span><span class="mtot">${list.length}</span></span>
    </button>
    <div class="mbody">
      <div class="mblock"><div class="mlab">Como funciona</div><div class="mtext">${info.mec}</div></div>
      <div class="mblock ritual"><div class="mlab">O ritual que desarma</div><div class="mtext">${info.ritual}</div></div>
      <div class="mblock"><div class="mlab">Onde apareceu — ${list.length} ${list.length===1?"caso":"casos"}</div>
        <div class="mcases">${cases}</div></div>
    </div></div>`;
}).join("");

/* ── filtros ── */
const nMacro = m => D.erros.filter(e => e.macro === m).length;
const chip = (g,v,lab,n,cls) => `<button class="chip${cls?" "+cls:""}" data-f="${g}" data-v="${v==null?"":esc(v)}">${esc(lab)}<span class="n">${n}</span></button>`;
$("#fsim").innerHTML = chip("sim",null,"Tudo",D.erros.length) +
  SIMK.map(k => chip("sim",k,k,D.sims[k].erros)).join("");
$("#fmacro").innerHTML = D.macro_ordem.filter(nMacro).map(m => chip("macro",m,D.macro_nome[m],nMacro(m))).join("");

function subchips(){
  if (!fMacro) return "";
  const subs = [...new Set(D.erros.filter(e=>e.macro===fMacro).map(e=>e.area))]
    .sort((a,b)=>D.erros.filter(e=>e.area===b).length-D.erros.filter(e=>e.area===a).length);
  if (subs.length < 2) return "";
  return subs.map(a => chip("area",a,a,D.erros.filter(e=>e.area===a).length,"sub")).join("");
}

/* ── peças do card ── */
function ladder(e){
  if (!e.cad.length) return "";
  const rows = e.cad.map(b => {
    const st = b.st === "ok" ? "executado" : (b.st === "quebrado" ? "quebrou aqui" : "não alcançado");
    return `<li class="rung ${b.st}">
      <span class="rn">${b.i+1}</span>
      <span><span class="rstage">${esc(ETAPA[b.tipo].n)}</span><span class="rtxt">${esc(b.txt)}</span></span>
      <span class="rst">${st}</span></li>`;
  }).join("");
  return `<div class="eblock" style="padding-bottom:9px"><div class="elab">Cadeia de habilidades</div></div>
    <ol class="ladder">${rows}</ol>
    <p class="ladkey">Verde = degrau que você executou · vermelho = onde a cadeia parou · cinza = degrau que a questão nunca chegou a testar.</p>`;
}

function fsrsChips(c){
  const out = [];
  if (c.bloco !== null && c.bloco !== undefined)
    out.push(`<span class="fcd deg">degrau ${c.bloco+1}</span>`);
  if (c.st === "novo" || c.visto === null)
    out.push(`<span class="fcd novo">nunca visto</span>`);
  else
    out.push(`<span class="fcd">visto há ${c.visto}d</span>`);
  if (c.vence !== null && c.vence !== undefined){
    if (c.vence < 0) out.push(`<span class="fcd late">atrasado ${Math.abs(c.vence)}d</span>`);
    else if (c.vence === 0) out.push(`<span class="fcd late">vence hoje</span>`);
    else out.push(`<span class="fcd">vence em ${c.vence}d</span>`);
  }
  if (c.reps) out.push(`<span class="fcd mn">${c.reps} rev${c.lapses?` · ${c.lapses} lapso${c.lapses>1?"s":""}`:""}</span>`);
  return out.join("");
}

function cardsBlock(e){
  if (!e.cards.length) return "";
  const novos = e.cards.filter(c => c.st === "novo").length;
  const nota = novos === e.cards.length
    ? `${e.cards.length===1?"Este card ainda não foi introduzido":"Nenhum destes cards foi introduzido ainda"} — o erro segue sem nenhuma passagem de reforço.`
    : (novos ? `${e.cards.length - novos} já em circulação, ${novos} ainda não introduzido${novos>1?"s":""}.`
             : `Todos já em circulação no FSRS.`);
  const items = e.cards.map(c => `<div class="fc">
    <div class="fcmeta"><span class="fct ${c.tipo}">${esc(c.tipo.replace("_"," "))}</span>${fsrsChips(c)}
      <span class="fcd mn">#${c.id}</span></div>
    ${c.ctx?`<div class="fcc">${esc(c.ctx)}</div>`:""}
    <div class="fcq">${esc(c.p)}</div>
    ${c.r?`<div class="fca">${esc(c.r)}</div>`:""}</div>`).join("");
  return `<div class="eblock" style="padding-bottom:9px"><div class="elab">Cards forjados neste erro — ${e.cards.length}</div></div>
    <div class="cards">${items}</div><p class="cardstat">${nota}</p>`;
}

function gapBlock(e){
  if (!e.gap) return "";
  return `<div class="gap"><div class="elab">O discriminador que faltou</div>
    <div class="g">${esc(e.gap)}</div>
    <div class="mecl">Instância de <button class="lnk" data-filter-mec="${e.mec}">${esc(D.mec[e.mec].nome)}</button> — o mecanismo inteiro está na seção acima.</div></div>`;
}

function respostas(e){
  const mx = Math.max(...e.alts.map(a => a.pct || 0), 1);
  const linhas = e.alts.map(a => {
    const mk = a.role === "ok" ? '<span class="mk">✓</span>'
             : (a.role === "bad" ? '<span class="mk">✗</span>' : "");
    const pc = e.altp ? ""
      : `<span class="pc"><i style="width:${(a.pct||0)/mx*100}%"></i><s>${a.pct}%</s></span>`;
    return `<div class="alt ${a.role}"><span class="lt">${mk}${a.letra}</span>
      <span class="tx">${esc(a.txt)}</span>${pc}</div>`;
  }).join("");
  const nota = e.altp
    ? "Só o gabarito e a alternativa marcada foram registrados nesta prova — os outros distratores não constam."
    : "Percentual = fatia da turma que marcou cada alternativa.";
  return `<div class="alts${e.altp ? " parcial" : ""}">${linhas}</div><p class="cardstat">${nota}</p>`;
}

/* bloco de texto com botao de compactar */
let _bid = 0;
function bloco(lab, txt, cls, serif){
  if (!txt) return "";
  const id = "b" + (++_bid);
  const longo = txt.length > 260;
  return `<div class="eblock ${cls||""}">
    <div class="elabrow"><div class="elab">${esc(lab)}</div>
      ${longo?`<button class="tgl" data-clip="${id}" aria-expanded="true">compactar</button>`:""}</div>
    <div class="clipw" id="${id}"><div class="etext${serif?" serif":""}">${esc(txt)}</div></div></div>`;
}

function card(e){
  const brk = e.cad[e.quebrado];
  const cx = e.cx && e.cx.toLowerCase().startsWith("alt") ? `<span class="tag cx">Alta complexidade</span>` : "";
  const cmd = e.cmd
    ? `<div class="cmd"><div class="elab">O que a questão pediu</div><div class="q">${esc(e.cmd)}</div></div>`
    : `<div class="cmd miss"><div class="elab">O que a questão pediu</div><div class="q">O comando não foi capturado no registro deste erro — só o contexto do caso.</div></div>`;
  return `<article class="err" id="e${e.id}">
    <button class="ehead" data-e="${e.id}" aria-expanded="false">
      <span class="emain"><span class="etitle">${esc(e.titulo)}</span>
        <span class="tags"><span class="tag sim">${e.sim}${e.qnum?" Q"+e.qnum:""}</span><span class="tag">${esc(e.area)}</span>
        <span class="tag mec" data-filter-mec="${e.mec}" title="Filtrar por este mecanismo">${esc(D.mec[e.mec].nome)}</span>
        ${brk?`<span class="tag brk" data-filter-etapa="${brk.tipo}" title="Filtrar erros que quebraram nesta etapa">quebrou em: ${esc(ETAPA[brk.tipo].n)}</span>`:""}
        ${cx}${e.conf==="auto"?'<span class="tag auto">classif. auto</span>':""}</span></span>
      <span class="eid mn">#${e.id}</span>
    </button>
    <div class="ebody">
      ${bloco("A vinheta", e.enun, "", true)}
      ${cmd}
      ${respostas(e)}
      ${gapBlock(e)}
      ${ladder(e)}
      ${bloco("Por que é armadilha", e.arm, "arm")}
      ${bloco("O que faltou", e.falt)}
      ${bloco("Racional correto", e.expl, "exp", true)}
      ${cardsBlock(e)}
    </div></article>`;
}

/* ── render ── */
function render(){
  const q = fQ.trim().toLowerCase();
  const vis = D.erros.filter(e =>
    (!fSim || e.sim === fSim) && (!fMacro || e.macro === fMacro) &&
    (!fArea || e.area === fArea) && (!fMec || e.mec === fMec) &&
    (!fEtapa || (e.cad[e.quebrado] && e.cad[e.quebrado].tipo === fEtapa)) &&
    (!q || [e.titulo,e.tema,e.area,e.enun,e.cmd,e.ok,e.bad,e.arm,e.falt,e.expl,e.tipo,
            e.cad.map(b=>b.txt).join(" "), e.cards.map(c=>c.p+" "+c.r).join(" ")]
        .join(" ").toLowerCase().includes(q)));
  $("#list").innerHTML = vis.map(card).join("");
  $("#empty").style.display = vis.length ? "none" : "block";
  const pills = [];
  if (fMec) pills.push(`<span class="pill">${esc(D.mec[fMec].nome)}<button data-clr="mec" aria-label="Remover filtro de mecanismo">×</button></span>`);
  if (fEtapa) pills.push(`<span class="pill">quebrou em: ${esc(ETAPA[fEtapa].n)}<button data-clr="etapa" aria-label="Remover filtro de etapa">×</button></span>`);
  $("#pillrow").style.display = pills.length ? "flex" : "none";
  $("#pills").innerHTML = pills.join("");
  const sc = subchips();
  $("#subrow").style.display = sc ? "flex" : "none";
  $("#fsub").innerHTML = sc;
  const txt = `${vis.length} de ${D.erros.length} erros`;
  $("#cnt").textContent = txt; $("#cnt2").textContent = txt;
  $("#cntrow").style.display = pills.length ? "none" : "flex";
  document.querySelectorAll("[data-f]").forEach(b => {
    const g = b.dataset.f, v = b.dataset.v || null;
    b.classList.toggle("on", (g === "sim" ? fSim : g === "macro" ? fMacro : fArea) === v);
  });
  document.querySelectorAll("[data-etapa]").forEach(b => {
    const on = b.dataset.etapa === fEtapa;
    b.classList.toggle("on", on); b.setAttribute("aria-pressed", on);
  });
}

function toFilters(){ document.querySelector(".filters").scrollIntoView({behavior:"smooth", block:"start"}); }

document.addEventListener("click", ev => {
  const t = ev.target.closest("[data-filter-mec],[data-filter-etapa],[data-etapa],[data-toggle],[data-e],[data-f],[data-goto],[data-clr],[data-clip],#clr");
  if (!t) return;
  if (t.hasAttribute("data-clr")) {
    if (t.dataset.clr === "mec") fMec = null; else fEtapa = null;
    render(); return;
  }
  if (t.hasAttribute("data-filter-mec")) {
    const m = t.dataset.filterMec; fMec = (fMec === m ? null : m); render(); toFilters(); return;
  }
  if (t.hasAttribute("data-filter-etapa")) {
    const k = t.dataset.filterEtapa; fEtapa = (fEtapa === k ? null : k); render(); toFilters(); return;
  }
  if (t.hasAttribute("data-etapa")) {
    const k = t.dataset.etapa; fEtapa = (fEtapa === k ? null : k); render(); toFilters(); return;
  }
  if (t.hasAttribute("data-toggle")) {
    const m = t.closest(".mec"); t.setAttribute("aria-expanded", m.classList.toggle("open")); return;
  }
  if (t.hasAttribute("data-e")) {
    const a = t.closest(".err"); t.setAttribute("aria-expanded", a.classList.toggle("open"));
    a.classList.remove("hit"); return;
  }
  if (t.hasAttribute("data-clip")) {
    const w = document.getElementById(t.dataset.clip);
    const off = w.classList.toggle("off");
    t.textContent = off ? "expandir" : "compactar";
    t.setAttribute("aria-expanded", !off); return;
  }
  if (t.hasAttribute("data-f")) {
    const v = t.dataset.v || null, g = t.dataset.f;
    if (g === "sim") fSim = (fSim === v ? null : v);
    else if (g === "macro") { fMacro = (fMacro === v ? null : v); fArea = null; }
    else fArea = (fArea === v ? null : v);
    render(); return;
  }
  if (t.hasAttribute("data-goto")) {
    const id = t.dataset.goto;
    fSim = fMacro = fArea = fMec = fEtapa = null; $("#q").value = ""; fQ = "";
    render();
    const el = document.getElementById("e" + id);
    if (el) { el.classList.add("open","hit"); el.querySelector(".ehead").setAttribute("aria-expanded","true");
      el.scrollIntoView({behavior:"smooth", block:"center"}); }
    return;
  }
  if (t.id === "clr") { fSim = fMacro = fArea = fMec = fEtapa = null; $("#q").value = ""; fQ = ""; render(); }
});
$("#q").addEventListener("input", e => { fQ = e.target.value; render(); });
render();
</script>
"""
