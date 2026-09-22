# -*- coding: utf-8 -*-
"""Corrige artifacts/autopsia-2026-09-20.html com o racional declarado em 22/09/2026 (s191):
fecha os 21 elos, marca cards cunhados x triados, reclassifica a Q77 como chute declarado
tardio e recalcula os placares. Le o JSON ja fechado (fechar_autopsia.py) como fonte."""
import json, re, html, sys
sys.path.insert(0, r'C:\Users\daanm\AppData\Local\Temp\claude\C--Users-daanm-medhub\4789433d-623d-45e3-b2ab-1716ef7240e1\scratchpad')
from build_lote import M

P = 'artifacts/autopsia-2026-09-20.html'
J = 'artifacts/autopsia-2026-09-20.json'
h = open(P, encoding='utf-8').read()
d = json.load(open(J, encoding='utf-8'))
byn = {q['n']: q for q in d['questoes']}
esc = html.escape

# Elo fechado, em portugues acentuado (a versao sem acento do lote e para o CLI)
ELO = {
 8: 'H3 -- a ferramenta não estava disponível: sem o GASA, a decisão foi pelo perfil epidemiológico (tabagismo -> carcinomatose). A amilase de 80 foi lida como alta e é normal: ascite pancreática pede valores da ordem de milhares. Base ausente + ancoragem no número.',
 9: 'H2 -- lesão de Janeway e manchas de Roth não foram reconhecidas como fenômenos de endocardite ("passaram como detalhe"); sem eles, o par valvulopatia + febre fechou em febre reumática. Base ausente.',
 11: 'H4 -- discriminador identificado e NÃO usado: a glicorraquia normal não virou exclusão da tuberculose porque o conceito estava errado ("pensava que ambas não deixavam tanto estrago como a bacteriana"). A TB consome muito a glicose; quem poupa é o criptococo no imunodeprimido.',
 13: 'Base ausente confirmada: "chute no escuro, por desconhecer o achado" -- o sinal de Courvoisier não existia no repertório (tema-zero). O acerto foi sorteio.',
 14: 'H3-H5 -- a pielonefrite obstrutiva foi reconhecida; o que faltou foi o manejo: antibiótico de ITU alta complicada (ceftriaxona), a contraindicação da terapia expulsiva com febre/obstrução e o par urgente (drenar) x definitivo (ureterorrenolitotripsia). Base ausente, não leitura.',
 16: 'H4 -- sabia da manobra, mas achava que Dix-Hallpike só TRATA a VPPB (confundiu com Epley); o nistagmo assustou e empurrou para a ressonância. Base ausente; o veredito CONTESTÁVEL do gabarito se mantém.',
 30: 'H1 -- "não obstruído" passou batido: o espectro foi escolhido pelo órgão ("intestino = anaeróbios e gram-negativos"), não pela flora presente. Discriminador não usado.',
 36: 'Pergunta composta -- a palavra "mediador" venceu "aguda + primeira recrutada": ele sabia que o neutrófilo chega primeiro, mas não o tinha como mediador/efetor, e a célula T entrou como "gerente da resposta imune". O discriminador era o tempo, não a hierarquia.',
 43: 'H1/H2 -- "não sei estadiar segundo a FIGO, tampouco tenho o cutoff de tamanho": "limitada ao colo" virou lesão inicial e os 6 cm não viraram IB3. Base ausente.',
 45: 'H3 -- a exceção do desejo reprodutivo foi aplicada (fugiu da histerectomia por isso), mas com um conceito errado: achava que a ablação endometrial permite gestar depois. Ela destrói a camada basal e impede a biópsia seriada que a atipia exige.',
 47: 'H2 -- AGC foi lido como "alto grau cervical" e, portanto, conização; a origem endometrial da célula glandular não entrou no filtro. Base ausente.',
 50: 'PARCIAL -- a herdabilidade da idade da menopausa estava presente ("a menopausa precoce na mãe me fez pensar em causa genética"); o que faltou foi o cutoff dos 35 anos para excluir o distrator "idade > 30". Nuance, não base ausente.',
 51: 'H1/H2 -- sem a cinética e sem a zona discriminatória, duas exclusões erradas fecharam o caso: "sangramento exclui gestação tópica" (20-30% das gestações viáveis sangram) e "beta subindo + sangramento = mola" (mola cursa com beta muito alto, > 100.000). Fato no contexto errado.',
 56: 'PARCIAL -- A e B foram eliminadas por princípio (vacina inativada liberada; TARV nunca se suspende); o chute foi entre C e D. Lacunas reais: RPMO < 34 semanas independe da carga viral (H3) e inibidor de protease x ergot (H4).',
 57: 'H1 -- a tríade confusão + ataxia + nistagmo não foi reconhecida como Wernicke; miastenia gravis é tema desconhecido (fica para a grade de Neuro). Base ausente.',
 58: 'H1 -- "não sei ler o traçado": o pareamento mecanismo x tipo existia (compressão cefálica = precoce), o reconhecimento no traçado não; o contexto "RPMO há 2 h -> variável" também não foi usado. Base ausente.',
 73: 'H2 -- diretriz desatualizada: não lembrava o esquema do PCDT e achava que ciprofloxacina cobria gonococo. Veredito CONTESTÁVEL do gabarito mantido (azitromicina isolada não é 1ª linha).',
 74: 'H4 -- override do dado explícito: ele LEU "nega uso de antibióticos há 2 meses" e mesmo assim manteve C. difficile por causa do tempo de internação. O discriminador não falhou por invisibilidade, falhou por peso. Topografia cecal e cobertura sistêmica da neutropenia febril também ficaram fora.',
 77: '"Marquei direto. Foi chute." -- reclassificada em 22/09 como chute declarado tardio (na prova não havia marca). Base ausente: a regra "antibiótico aumenta o risco de SHU na STEC" não estava disponível para comparar A e D.',
 91: 'H2/H3 -- "mimetizar" foi lido corretamente como PRODUZIR o quadro; o que faltou foi a lista de causas médicas reversíveis (hipotireoidismo, hipercalcemia) e o teste do par inteiro. Base ausente.',
 99: 'H1/H2 -- "ignorei o discriminador": o IMC não foi calculado (118/4 = 29,5 = sobrepeso) e o rótulo veio do peso absoluto. Ancoragem no número.',
}
RAC = {
 8: 'Q8: me pareceu alta [a amilase]. Não lembrava do GASA, decidi pelo "perfil".',
 9: 'A mácula na mão me chamou a atenção, mas não conhecia as manchas de Roth. Passaram como detalhe.',
 11: 'Pleocitose linfocítica, lembrava que neutrófilo era bactéria. Além disso, não usei o discriminador da glicorraquia corretamente. Pensava que ambas não deixavam tanto estrago como a bacteriana, ou seja, não usei o discriminador.',
 13: 'Nem um nem outro, foi chute no escuro, por desconhecer o achado.',
 14: 'Reconheci a pielonefrite, mas não lembrava o manejo exato do cálculo, tampouco o esquema correto.',
 16: 'O nistagmo me assustou, e eu até lembrava da manobra, mas não sabia que ele era exame diagnóstico, achava que apenas tratava a VPPB.',
 30: 'Não mudou. Eu achei que deveria cobrir anaeróbios e gram-negativos. Associei intestino ao esquema, ignorando o discriminador.',
 36: 'A palavra "mediador" me empurrou para linfócito T, pois tenho ele como o "gerente" da resposta imune. Fiquei entre ele e neutrófilo, e até sabia que os neutrófilos chegavam primeiro, mas não que eram mediadores.',
 43: 'Não sei estadiar segundo a FIGO, tampouco tenho o cutoff de tamanho.',
 45: 'Considerei e inclusive achei que a ablação permitia a gestação depois. Fugi de histerectomia por isso mesmo.',
 47: 'Não considerei, imaginei que AGC era igual a alto risco e, portanto, deveria conizar.',
 50: 'Suponho que a partir dos 30-35 anos, mas sendo sincero fiquei na dúvida. A menopausa precoce na mãe me fez pensar em causa genética de falência ovariana precoce.',
 51: 'O colo fechado excluiu a D, e o sangramento me fez excluir a C. No entanto, não calculei o beta e supus que o aumento do beta associado ao sangramento apontava para mola.',
 56: 'Cheguei sim [a eliminar A e B], pois conhecia essa informação.',
 57: 'Chutei. Sequer conheço a miastenia gravis.',
 58: 'Não sei ler o traçado da cardiotoco. Imaginei que as contrações vinham junto da desaceleração e pensei em compressão de polo cefálico.',
 73: 'Não lembrava do esquema e achei que cipro pegava gonococo.',
 74: 'Li sim, mas o tempo de internação me fez supor o Clostridium difficile.',
 77: 'Marquei direto. Foi chute.',
 91: 'Produzem.',
 99: 'Não, ignorei o discriminador.',
}
CURTO = {  # para a lista-resumo da secao
 8: 'sem o GASA, decidiu pelo perfil; amilase 80 é normal', 9: 'Janeway/Roth não reconhecidos -> febre reumática',
 11: 'glicorraquia normal vista e não usada (achava que a TB poupa a glicose)', 13: 'chute no escuro: Courvoisier desconhecido',
 14: 'reconheceu a pielonefrite; faltou o manejo (drenar + ceftriaxona; definitivo = litotripsia)',
 16: 'Dix-Hallpike tido como tratamento (confundiu com Epley); nistagmo assustou', 30: '"não obstruído" passou batido; espectro pelo órgão',
 36: '"mediador" venceu "aguda + primeira"; célula T como gerente', 43: 'não estadia pela FIGO; sem o cutoff de 4 cm',
 45: 'achava que ablação permite gestar depois', 47: 'AGC lido como alto grau cervical -> conizar',
 50: 'parcial: tinha a herdabilidade, faltou o cutoff de 35 anos', 51: 'sem cinética nem zona discriminatória; "sangramento exclui tópica"',
 56: 'parcial: eliminou A e B por princípio; chute entre C e D', 57: 'tríade de Wernicke não reconhecida',
 58: 'não lê o traçado da CTG', 73: 'esquema antigo na memória (cipro cobria gonococo)',
 74: 'leu "nega antibiótico" e sobrescreveu pela internação', 77: 'marcou direto -- chute declarado tardio',
 91: 'leu "mimetizar" certo; faltou a lista de causas reversíveis', 99: 'não calculou o IMC; carimbou pelo peso',
}
assert set(ELO) == set(RAC) == set(CURTO), 'dicionarios desalinhados'

def art_span(n):
    m = re.search(r'<article class="q" id="q%d" .*?</article>' % n, h, re.S)
    assert m, n
    return m

n_elo = n_ask = n_cards = 0
for n in sorted(ELO):
    m = art_span(n)
    a = m.group(0)
    # 1. Elo que quebrou -> racional (blockquote) + elo fechado
    bq = ('<blockquote class="racional"><span class="k">Seu racional, declarado em 22/09</span>%s</blockquote>' % esc(RAC[n]))
    novo_p = '<p><span class="tg ok">fechado em 22/09</span> %s</p>' % esc(ELO[n])
    a2, k = re.subn(r'(<div class="field key"><div class="k">Elo que quebrou</div>)((?:<blockquote class="racional">.*?</blockquote>)?)<p>.*?</p></div>',
                    lambda mm: mm.group(1) + mm.group(2) + bq + novo_p + '</div>', a, count=1, flags=re.S)
    assert k == 1, ('elo', n)
    n_elo += 1
    # 2. Pergunta em aberto -> respondida
    a2, k = re.subn(r'<div class="field ask"><div class="k">Pergunta em aberto para você</div>(<p>.*?</p>)</div>',
                    lambda mm: '<div class="field ask done"><div class="k">Pergunta respondida em 22/09</div>' + mm.group(1).replace('<p>', '<p class="muted">', 1) + '</div>', a2, count=1, flags=re.S)
    assert k == 1, ('ask', n)
    n_ask += 1
    h = h[:m.start()] + a2 + h[m.end():]

# 3. Cards: cunhado x triado (todas as 56)
for n, q in byn.items():
    m = art_span(n)
    a = m.group(0)
    errou = q['marcada'] != q['gabarito']
    keep = set((M.get(n) or {}).get('keep', []))
    extra = (M.get(n) or {}).get('extra', [])
    mc = re.search(r'<div class="field"><div class="k">Cards candidatos \(ainda não cunhados\)</div><ul class="cands">(.*?)</ul></div>', a, re.S)
    if mc:
        lis = re.findall(r'<li>.*?</li>', mc.group(1), re.S)
        novos = []
        for i, li in enumerate(lis):
            if errou and i in keep:
                tag = '<span class="tg ok">cunhado 22/09</span>'
            elif errou:
                tag = '<span class="tg neutral">triado: fora (dedutível ou redundante)</span>'
            else:
                tag = '<span class="tg neutral">não cunhado -- incerteza no ledger</span>'
            novos.append(li.replace('<span class="tg neutral">arbitrario</span>', tag))
        for e in extra:
            novos.append('<li><b>%s</b><span>%s</span><span class="tg ok">cunhado 22/09 (autorado no fechamento)</span></li>' % (esc(e['frente_pergunta']), esc(e['verso_resposta'])))
        if errou:
            lab = 'Cards (cunhados em 22/09: %d de %d candidatos)' % (len(keep) + len(extra), len(lis) + len(extra))
        else:
            lab = 'Cards candidatos (não cunhados -- acerto no chute registrado como incerteza no ledger de habilidades)'
        bloco = '<div class="field"><div class="k">%s</div><ul class="cands">%s</ul></div>' % (lab, ''.join(novos))
        a = a[:mc.start()] + bloco + a[mc.end():]
        n_cards += 1
    elif errou and extra:
        novos = ''.join('<li><b>%s</b><span>%s</span><span class="tg ok">cunhado 22/09 (autorado no fechamento)</span></li>' % (esc(e['frente_pergunta']), esc(e['verso_resposta'])) for e in extra)
        bloco = '<div class="field"><div class="k">Cards (cunhados em 22/09: %d, autorados no fechamento -- a Autópsia não tinha candidato)</div><ul class="cands">%s</ul></div>' % (len(extra), novos)
        a = a.replace('</div>\n  </div>\n</article>', '</div>' + bloco + '\n  </div>\n</article>', 1)
        n_cards += 1
    h = h[:m.start()] + a + h[m.end():]

# 4. Q77 -> chute declarado tardio
m = art_span(77); a = m.group(0)
a = a.replace('<span class="pill crit">Errou</span><span class="pill ok">Raciocínio / execução</span>',
              '<span class="pill crit">Errou</span><span class="pill na">Chute declarado em 22/09</span><span class="pill warn">Base ausente</span>', 1)
a = a.replace('data-nat="raciocinio"', 'data-nat="base"', 1)
h = h[:m.start()] + a + h[m.end():]

# 5. Placares
rep = [
 ('o que ele esconde é que 39 das 100 respostas foram chute.', 'o que ele esconde é que 40 das 100 respostas foram chute (39 declarados na prova + a Q77, declarada em 22/09).'),
 ('<span><b>39</b> chutes declarados</span>', '<span><b>40</b> chutes declarados</span>'),
 ('<div class="v num">44/61</div><div class="d">72% de acerto', '<div class="v num">44/60</div><div class="d">73% de acerto'),
 ('<div class="v num">14/39</div><div class="d">36% --', '<div class="v num">14/40</div><div class="d">35% --'),
 ('<div class="tile warn"><div class="k">Base ausente</div><div class="v num">43</div>', '<div class="tile warn"><div class="k">Base ausente</div><div class="v num">44</div>'),
 ('<td><b>PED</b> <span class="muted">Pediatria</span></td><td class="num">11/20</td><td class="num">10/13</td><td class="num">1/7</td>',
  '<td><b>PED</b> <span class="muted">Pediatria</span></td><td class="num">11/20</td><td class="num">10/12</td><td class="num">1/8</td>'),
 ('<button class="fchip v-warn" data-f="nat" data-v="base">Base ausente <span class="num">43</span></button>', '<button class="fchip v-warn" data-f="nat" data-v="base">Base ausente <span class="num">44</span></button>'),
 ('<button class="fchip v-ok" data-f="nat" data-v="raciocinio">Raciocínio / execução <span class="num">13</span></button>', '<button class="fchip v-ok" data-f="nat" data-v="raciocinio">Raciocínio / execução <span class="num">12</span></button>'),
]
for old, new in rep:
    assert h.count(old) == 1, old[:60]
    h = h.replace(old, new)

# 6. Secao "Perguntas em aberto" -> respondidas
sec = re.search(r'<div class="eyebrow">Para fechar o diagnóstico</div>\s*<h2>Perguntas em aberto sobre o seu raciocínio</h2>\s*<p>.*?</p>\s*<ul class="asks">.*?</ul>', h, re.S)
assert sec
itens = ''.join('<li><a href="#q%d"><span class="num">Q%02d</span> %s</a></li>' % (n, n, esc(CURTO[n])) for n in sorted(CURTO))
novo_sec = ('<div class="eyebrow">Diagnóstico fechado</div>\n  <h2>As 21 perguntas, respondidas em 22/09</h2>\n'
            '  <p>Você trouxe o racional de cada uma (1 linha por questão) e o elo foi fechado com ele -- o racional declarado vence o inferido. '
            'Leitura honesta: 5 das 21 são bug de execução (Q11, Q30, Q74, Q99 = discriminador visto e não convertido; Q36 = palavra-gatilho); '
            'as outras 16 são cobertura, o que confirma o diagnóstico acima. O caso mais instrutivo é a Q74: a negativa foi lida e mesmo assim sobrescrita -- o discriminador não falhou por invisibilidade, falhou por peso.</p>\n'
            '  <p class="muted">Persistido no mesmo dia: 42 erros em <code>questoes_erros</code> (ids 1044-1085) com 52 cards cunhados (81 candidatos triados pelo teste de regenerabilidade); os 14 acertos no chute viraram <code>incerteza</code> no ledger de habilidades. A Q77 passou a chute declarado (39 -> 40).</p>\n'
            '  <ul class="asks">%s</ul>' % itens)
h = h[:sec.start()] + novo_sec + h[sec.end():]

# 7. CSS do bloco respondido
h = h.replace('.field.ask{border-left:3px solid var(--warn);background:var(--warn-soft);padding:8px 12px;border-radius:0 4px 4px 0}',
              '.field.ask{border-left:3px solid var(--warn);background:var(--warn-soft);padding:8px 12px;border-radius:0 4px 4px 0}\n.field.ask.done{border-left-color:var(--accent);background:var(--accent-soft)}', 1)
assert '.field.ask.done' in h

open(P, 'w', encoding='utf-8').write(h)
print('elos fechados:', n_elo, '| asks:', n_ask, '| blocos de cards marcados:', n_cards)
print('sobrou "pendente" no Elo?', len(re.findall(r'Elo que quebrou</div>(?:<blockquote.*?</blockquote>)?<p>pendente', h, re.S)))
print('sobrou "Pergunta em aberto"?', h.count('Pergunta em aberto para você'), '| "ainda não cunhados"?', h.count('ainda não cunhados'))
