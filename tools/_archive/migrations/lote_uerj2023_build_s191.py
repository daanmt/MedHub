# -*- coding: utf-8 -*-
"""Monta o lote de insert_questao (--errors-file) a partir da Autopsia UERJ 2023
(artifacts/autopsia-2026-09-20.json) + o racional declarado pelo operador em 22/09/2026.

Saida: tmp/lote_uerj2023.json (42 itens). Nao toca o banco.
Triagem de regenerabilidade feita pelo principal (arbitrario fica, dedutivel sai):
`keep` = indices dos cards_candidatos mantidos; `extra` = cards autorados aqui;
`edit` = sobrescrita de campos de um candidato mantido.
"""
import json, re, sys

SRC = 'artifacts/autopsia-2026-09-20.json'
OUT = 'tmp/lote_uerj2023.json'

def asc(s):
    if s is None:
        return s
    return (s.replace('→', '->').replace('—', '--').replace('–', '-')
             .replace('“', '"').replace('”', '"').replace('‘', "'")
             .replace('’', "'").replace('≥', '>=').replace('≤', '<='))

COMPLEX = {'direta': 'Baixa', 'fluxograma': 'Media', 'raciocinio': 'Alta'}

# n: dict(area, tema, tipo, elo, faltou, keep=[...], extra=[...], edit={idx:{campo:valor}}, racional=str|None)
M = {
 8: dict(area='Nefrologia', tema='Glomerulopatias', tipo='Lacuna de conhecimento',
    elo='H3: nao calculou o GASA (ferramenta ausente) e decidiu pelo perfil epidemiologico (tabagismo -> carcinomatose); leu amilase 80 como alta',
    faltou='GASA = albumina serica - albumina do liquido; < 1,1 exclui hipertensao portal; dentro do GASA baixo, proteina do liquido < 2,5 + poucas celulas = nefrotica; amilase do liquido so importa se > 1.000 ou > serica',
    keep=[0, 1],
    racional='me pareceu alta [amilase]. nao lembrava do GASA, decidi pelo perfil.'),
 9: dict(area='Cardiologia', tema='Endocardite Infecciosa', tipo='Lacuna de conhecimento',
    elo='H2: Janeway e Roth nao reconhecidos como fenomenos de endocardite -- passaram como detalhe; ancorou em valvulopatia + febre = febre reumatica',
    faltou='Fenomenos perifericos da endocardite (Janeway indolor/vascular, Osler doloroso/imunologico, Roth) e os 2 criterios maiores de Duke (hemoculturas + eco)',
    keep=[0, 1],
    edit={0: {'frente_pergunta': 'Qual lesao cutanea da endocardite e INDOLOR e qual e DOLOROSA -- e a que fenomeno (vascular ou imunologico) cada uma pertence?'}},
    racional='a macula na mao me chamou a atencao, mas nao conhecia as manchas de Roth. passaram como detalhe.'),
 11: dict(area='Infecto', tema='Meningites', tipo='Erro de aplicacao',
    elo='H4: discriminador identificado e nao usado -- glicorraquia normal nao virou exclusao de TB; conceito errado de que TB tambem poupa a glicose',
    faltou='Meningite tuberculosa = hipoglicorraquia marcada + proteina muito alta; criptococo no HIV = resposta inflamatoria pobre, glicose normal ou pouco reduzida',
    keep=[1],
    edit={1: {'verso_armadilha': 'Achar que so a bacteriana piogenica consome glicose: a TB tambem consome (hipoglicorraquia marcada). Glicose NORMAL em HIV com meningite subaguda linfocitica aponta criptococo -- pedir latex/antigeno criptococico e iniciar anfotericina B.'}},
    racional='pleocitose linfocitica, lembrava que neutrofilo era bacteria. nao usei o discriminador da glicorraquia; pensava que ambas nao deixavam tanto estrago como a bacteriana.'),
 14: dict(area='Cirurgia', tema='Nefrolitíase e Cólica Renal', tipo='Lacuna de conhecimento',
    elo='H3-H5: reconheceu a pielonefrite obstrutiva mas nao tinha o manejo -- antibiotico de ITU alta complicada, limiar de tamanho da expulsiva e o par urgente (drenagem) x definitivo (ureterorrenolitotripsia)',
    faltou='Sistema obstruido + infectado = drenar (duplo J/nefrostomia) + ceftriaxona; expulsiva so em calculo <= 10 mm SEM febre/obstrucao com repercussao; definitivo do calculo distal de 9 mm = ureterorrenolitotripsia',
    keep=[0, 1],
    racional='reconheci a pielonefrite, mas nao lembrava o manejo exato do calculo, tampouco o esquema correto.'),
 15: dict(area='Cardiologia', tema='Síndrome Coronariana Aguda', tipo='Lacuna de conhecimento',
    elo='H1/H2: mapa de paredes x arterias ausente (declarado); criterio de trombolise x ICP tambem ausente',
    faltou='DII/DIII/aVF = parede inferior = coronaria direita (80-90%); trombolise so se ICP primaria indisponivel em ate 120 min do 1o contato medico',
    keep=[0, 1]),
 16: dict(area='Otorrino', tema='Vertigem e Síndromes Vestibulares', tipo='Lacuna de conhecimento',
    elo='H4: sabia da manobra mas achava que Dix-Hallpike so TRATA a VPPB (confundiu com Epley); o nistagmo assustou e empurrou para imagem',
    faltou='Dix-Hallpike = DIAGNOSTICO (canal posterior); Epley = TRATAMENTO; sinais de nistagmo central que justificam RM (vertical, muda de direcao, sem latencia, nao fatigavel)',
    keep=[0, 1],
    racional='o nistagmo me assustou, e eu ate lembrava da manobra, mas nao sabia que ele era exame diagnostico, achava que apenas tratava a VPPB.'),
 17: dict(area='Cirurgia', tema='Marcadores Tumorais', tipo='Lacuna de conhecimento',
    elo='H1/H2: painel AFP / beta-hCG / DHL ausente (declarado); marcou CEA',
    faltou='AFP nunca se eleva no seminoma puro -- AFP elevada = tratar como nao-seminoma',
    keep=[0]),
 22: dict(area='Cirurgia', tema='Cirurgia Vascular', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): ordem de frequencia dos aneurismas viscerais',
    faltou='Esplenica (~60%) > hepatica (~20%) > mesenterica superior (~5%); gastroduodenal e rara',
    keep=[0]),
 23: dict(area='Cirurgia', tema='Tuberculose Intestinal', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): topografia da TB intestinal',
    faltou='Ileo terminal = maxima densidade de placas de Peyer + estase pela valvula ileocecal',
    keep=[0]),
 25: dict(area='Cirurgia', tema='Videolaparoscopia', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): arritmia mais frequente na insuflacao',
    faltou='Bradicardia sinusal por reflexo peritonio-vagal ao estiramento rapido do peritonio',
    keep=[0]),
 26: dict(area='Cirurgia', tema='Cicatrizacao', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): par de vitaminas da cicatrizacao',
    faltou='Vitamina C (hidroxilacao do colageno) e vitamina A (epitelizacao, reverte o efeito do corticoide)',
    keep=[0]),
 27: dict(area='Cirurgia', tema='Tuberculose Intestinal', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): indicacao cirurgica na TB intestinal',
    faltou='Obstrucao por estenose fibrotica ileocecal e a principal indicacao; o tratamento e clinico (RIPE)',
    keep=[0]),
 28: dict(area='Gastro', tema='Hemorragia Digestiva Alta', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): droga vasoativa da hemorragia varicosa',
    faltou='Terlipressina ou octreotide reduzem o fluxo esplancnico; iniciar antes da endoscopia',
    keep=[0]),
 29: dict(area='Cirurgia', tema='Resposta Metabólica ao Trauma (REMIT)', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): direcao dos efeitos sistemicos do TNF',
    faltou='TNF-alfa: febre, hipotensao (NO), hipercortisolemia, anorexia/caquexia',
    keep=[0]),
 30: dict(area='Cirurgia', tema='Avaliação e Manejo Pré-Operatório', tipo='Erro de aplicacao',
    elo='H1: o discriminador "nao obstruido" passou batido -- escolheu o espectro pela topografia (intestino = anaerobios) e nao pela flora presente',
    faltou='Gastroduodenal e delgado NAO obstruido = flora escassa e aerobia -> cefazolina; obstruido = estase + anaerobios -> acrescentar metronidazol (ou cefoxitina)',
    keep=[0],
    edit={0: {'verso_armadilha': 'Escolher o espectro pelo orgao ("intestino") em vez de pela flora: so a OBSTRUCAO (estase, supercrescimento) justifica somar anaerobicida -- cefazolina + metronidazol ou cefoxitina isolada.'}},
    racional='nao mudou. eu achei que deveria cobrir anaerobios e gram negativos. associei intestino ao esquema, ignorando o discriminador.'),
 31: dict(area='Cirurgia', tema='Resposta Metabólica ao Trauma (REMIT)', tipo='Lacuna de conhecimento',
    elo='H1: nao separa cortex de medula adrenal',
    faltou='Cortex: glomerulosa aldosterona, fasciculada cortisol, reticular DHEA; medula (crista neural): catecolaminas',
    keep=[0]),
 36: dict(area='Cirurgia', tema='Cicatrizacao', tipo='Armadilha',
    elo='Pergunta composta: a palavra "mediador" venceu "aguda + primeira recrutada"; sabia que o neutrofilo chega primeiro mas nao o tinha como mediador/efetor; celula T = "gerente" da resposta imune',
    faltou='Neutrofilo = primeira celula (horas, pico 24-48 h) e principal EFETORA/mediadora da inflamacao aguda (enzimas, ROS, NETs, citocinas); linfocito T e imunidade adaptativa, entra em dias',
    keep=[],
    extra=[dict(tipo='elo_quebrado',
        frente_contexto='Questao de base cirurgica: "qual celula e a primeira recrutada e potente mediadora da inflamacao AGUDA". O candidato hesitou entre neutrofilo e linfocito T.',
        frente_pergunta='Na inflamacao AGUDA, qual celula e a primeira recrutada e a principal efetora (mediadora) -- e por que a palavra "mediador" NAO aponta para o linfocito T?',
        verso_resposta='Neutrofilo: chega em horas (pico 24-48 h) e e a principal efetora da fase aguda -- libera enzimas, especies reativas de oxigenio, NETs e citocinas. O linfocito T pertence a imunidade ADAPTATIVA e entra em dias; "aguda" + "primeira" o excluem. O macrofago assume depois (48-72 h).',
        verso_regra_mestre='Aguda + primeira = imunidade inata; a celula mais abundante e de recrutamento mais rapido e o neutrofilo. Nao deixe uma palavra ("mediador") anular o discriminador temporal.',
        verso_armadilha='Ler "mediador" como "gerente da resposta imune" (linfocito T). O discriminador e o tempo, nao a hierarquia.')],
    racional='a palavra mediador me empurrou para linfocito T, pois tenho ele como o gerente da resposta imune. fiquei entre ele e neutrofilo, e ate sabia que os neutrofilos chegavam primeiro, mas nao que eram mediadores.'),
 38: dict(area='Cirurgia', tema='Doenças do Esôfago', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): mapa de eponimos -- triangulo de Killian',
    faltou='Zenker nasce no triangulo de Killian (entre tireofaringeo e cricofaringeo)',
    keep=[0]),
 39: dict(area='Cirurgia', tema='Tumores de Partes Moles', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): epidemiologia do desmoide',
    faltou='Mulheres jovens (20-40 anos), gatilho hormonal/cicatricial; associacao com PAF/Gardner (APC) e mutacao CTNNB1 nos esporadicos',
    keep=[0]),
 41: dict(area='Ginecologia', tema='Úlceras Genitais (IST)', tipo='Erro de aplicacao',
    elo='H1: trocou o no do fluxograma (vesiculas) por um discriminador semiologico (dor) -- racional declarado na prova',
    faltou='Fluxograma do MS sem laboratorio: 1a pergunta = lesoes vesiculosas (sim -> herpes; nao -> tratar sifilis + cancro mole)',
    keep=[0]),
 43: dict(area='Ginecologia', tema='Câncer de Colo do Útero', tipo='Lacuna de conhecimento',
    elo='H1/H2: nao sabe estadiar pela FIGO nem tem o cutoff de 4 cm (declarado); leu "limitada ao colo" como lesao inicial',
    faltou='FIGO 2018: IB1 < 2 cm, IB2 2-4 cm, IB3 >= 4 cm; a partir de IB3 = quimiorradiacao (cisplatina) + braquiterapia, nao cirurgia',
    keep=[0],
    racional='nao sei estadiar segundo a FIGO, tampouco tenho o cutoff de tamanho.'),
 45: dict(area='Ginecologia', tema='Câncer de Endométrio', tipo='Lacuna de conhecimento',
    elo='H3: aplicou a excecao do desejo reprodutivo (fugiu da histerectomia) mas achava que a ablacao endometrial PERMITE gestar depois -- conceito errado sobre o que a ablacao destroi',
    faltou='Ablacao destroi a camada funcional e basal do endometrio: inviabiliza a gestacao e impede a biopsia de seguimento; conservador = progestagenio (SIU-LNG 52 mg) + histeroscopia/biopsia seriadas',
    keep=[0],
    edit={0: {'verso_armadilha': 'Achar que ablacao endometrial preserva a fertilidade: ela destroi a camada basal (sem endometrio nao ha implantacao) e cria sinequias que impedem a biopsia seriada -- justamente o seguimento que a atipia exige. Morcelacao tambem sai: fragmenta tecido potencialmente maligno.'}},
    racional='considerei e inclusive achei que a ablacao permitia a gestacao depois. fugi de histerectomia por isso mesmo.'),
 47: dict(area='Ginecologia', tema='Rastreamento do Câncer de Colo do Útero', tipo='Lacuna de conhecimento',
    elo='H2: tratou AGC como equivalente a alto grau cervical (= conizar); nao considerou origem endometrial',
    faltou='AGC com colposcopia satisfatoria e normal: repetir citologia com atencao ao canal + USG transvaginal (endometrio) acima de 35 anos; excisao so se AGC persistente ou achado anormal',
    keep=[0],
    racional='nao considerei, imaginei que AGC era igual a alto risco e, portanto, deveria conizar.'),
 49: dict(area='Ginecologia', tema='Violência Sexual e Aborto Legal', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): requisitos legais do aborto por violencia sexual',
    faltou='Nenhum documento e exigivel: nem BO, nem laudo do IML, nem autorizacao judicial (CP art. 128, II; Portaria MS 1.508/2005)',
    keep=[0]),
 51: dict(area='Obstetrícia', tema='Sangramento da Primeira Metade', tipo='Erro de aplicacao',
    elo='H1/H2: nao calculou a cinetica nem confrontou 554 com a zona discriminatoria; exclusoes erradas -- "sangramento exclui gestacao topica" e "beta subindo + sangramento = mola" (fato no contexto errado: mola tem beta muito alto)',
    faltou='Zona discriminatoria TV ~1.500-2.000 mUI/mL: abaixo dela nao ver saco e o esperado; subida >= 35-53% em 48 h = curva viavel; sangramento ocorre em 20-30% das gestacoes viaveis (ameaca de abortamento); mola = beta muito alto (> 100.000), utero aumentado, cistos tecaluteinicos',
    keep=[0],
    edit={0: {'verso_armadilha': 'Ler "sangramento + sem saco gestacional" como mola ou aborto: mola cursa com beta muito ALTO (> 100.000) e utero grande para a idade gestacional; com beta de 554 subindo quase 4x em 72 h, colo fechado e anexos normais, a resposta e gestacao topica inicial -- repetir beta em 48 h + USG.'}},
    racional='o colo fechado excluiu a D, e o sangramento me fez excluir a C. no entanto, nao calculei o beta e supus que o aumento do beta associado ao sangramento apontava para mola.'),
 53: dict(area='Obstetrícia', tema='Pré-Natal', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): cada trimestre da USG responde a uma pergunta diferente',
    faltou='1o trimestre: viabilidade, datacao (CCN), numero de fetos e corionicidade (11-14 sem: lambda/T), translucencia nucal; liquido amniotico e crescimento sao do 2o/3o',
    keep=[0]),
 57: dict(area='Obstetrícia', tema='Hiperêmese Gravídica', tipo='Lacuna de conhecimento',
    elo='H1: triade confusao + ataxia + nistagmo nao reconhecida como Wernicke (chute); sequer conhece miastenia gravis',
    faltou='Wernicke = confusao + ataxia + alteracao oculomotora apos depleção de tiamina (hiperemese, perda de 10 kg); tiamina IV SEMPRE antes da glicose',
    keep=[0],
    edit={0: {'frente_contexto': 'Gestante de 30 semanas com confusao mental, ataxia e nistagmo; no inicio da gestacao teve vomitos incoerciveis com perda de 10 kg.',
              'frente_pergunta': 'Que sindrome explica confusao + ataxia + nistagmo em gestante com hiperemese previa, e qual a ordem obrigatoria entre tiamina e glicose no tratamento?'}},
    racional='chutei. sequer conheco a miastenia gravis.'),
 58: dict(area='Obstetrícia', tema='Assistência ao Parto', tipo='Lacuna de conhecimento',
    elo='H1: nao sabe ler o tracado da CTG (declarado) -- tinha o pareamento mecanismo x tipo, mas nao o reconhecimento no tracado; nao usou o contexto (RPMO ha 2 h -> variavel)',
    faltou='Precoce = espelha a contracao (nadir coincide com o pico), forma suave, compressao cefalica; variavel = abrupta, forma em V/W/U, inicio variavel, compressao funicular (RPMO/oligoamnio); tardia = nadir DEPOIS do pico, insuficiencia uteroplacentaria',
    keep=[0],
    edit={0: {'frente_pergunta': 'Cardiotocografia: como distinguir NO TRACADO as desaceleracoes precoce, variavel e tardia (tempo em relacao a contracao e forma), e qual o mecanismo de cada uma?',
              'verso_armadilha': 'Escolher a causa pela alternativa "mais clinica" sem classificar a desaceleracao. Rotura de membranas ha poucas horas tira o coxim de liquido do cordao -> desaceleracao VARIAVEL por compressao funicular. Precoce por compressao cefalica e fenomeno de fase ativa avancada/expulsivo, nao de colo com 2 cm.'}},
    racional='nao sei ler o tracado da cardiotoco. imaginei que as contracoes vinham junto da desaceleracao e pensei em compressao de polo cefalico.'),
 60: dict(area='Obstetrícia', tema='Síndromes Hipertensivas da Gestação', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): marcou benzodiazepinico antes do sulfato de magnesio na crise eclamptica',
    faltou='Sulfato de magnesio cessa e previne a crise (sem etapa de benzodiazepinico); AAS profilatico antes de 16 semanas',
    keep=[0, 1]),
 62: dict(area='Gastro', tema='Doença Inflamatória Intestinal', tipo='Erro de aplicacao',
    elo='Nao usou calprotectina fecal elevada nem sangue vivo; ancorou no sintoma mais antigo (artrite) e nao unificou em DII (chute)',
    faltou='Calprotectina fecal = inflamacao de mucosa (organico x funcional); artrite periferica tipo 1 da DII = pauciarticular, grandes articulacoes, acompanha a atividade intestinal',
    keep=[0, 1]),
 63: dict(area='Pediatria', tema='Dermatoses Comuns da Infância', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): morfologia da dermatite de fralda por Candida',
    faltou='Irritativa POUPA as pregas; candidiase INVADE as pregas com lesoes satelites -> nistatina/imidazol topico',
    keep=[0]),
 65: dict(area='Pediatria', tema='Infeccao do Trato Urinario na Infancia', tipo='Erro de aplicacao',
    elo='Nao usou a PA de 128x86 nem a historia de ITU febril de repeticao sem USG; tratou a anemia como problema isolado (chute)',
    faltou='Baixa estatura + HAS + anemia normocitica + ITU febril de repeticao na lactancia = DRC por nefropatia de refluxo -> funcao renal + USG/uretrocistografia',
    keep=[0]),
 66: dict(area='Pediatria', tema='Aleitamento Materno e Mastite Lactacional', tipo='Erro de aplicacao',
    elo='Fato no contexto errado: transferiu para o seio a associacao "alimentar deitado -> otite media", que vale so para mamadeira (chute)',
    faltou='Amamentar deitada ao seio e permitida; otite por decubito e da MAMADEIRA; fissura nao suspende a mamada -- corrigir a pega',
    keep=[0, 1]),
 67: dict(area='Pediatria', tema='Defeitos do Tubo Neural (Mielomeningocele)', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): associacao sindromica trocada (DSAV = Down); nao percorreu as raizes sacrais',
    faltou='Mielomeningocele lombossacra -> bexiga neurogenica (S2-S4), refluxo, DRC; hidrocefalia/Chiari II; nao ha cardiopatia associada',
    keep=[0]),
 73: dict(area='Infecto', tema='IST', tipo='Lacuna de conhecimento',
    elo='H2: diretriz desatualizada -- nao lembrava o esquema do PCDT e achava que ciprofloxacina cobria gonococo',
    faltou='PCDT IST: ceftriaxona 500 mg IM + azitromicina 1 g VO dose unica; quinolona saiu por resistencia (SenGono). Gabarito da banca (azitromicina isolada) e a "menos errada" -- questao CONTESTAVEL',
    keep=[0],
    edit={0: {'verso_armadilha': 'Ciprofloxacina: esquema antigo, abandonado no Brasil pela alta resistencia de N. gonorrhoeae as quinolonas (vigilancia SenGono). Se a ceftriaxona nao estiver entre as opcoes, a azitromicina e a "menos errada" -- nunca a quinolona.'}},
    racional='nao lembrava do esquema e achei que cipro pegava gonococo.'),
 74: dict(area='Pediatria', tema='Leucemias na Infância', tipo='Erro de aplicacao',
    elo='H4 override: LEU "nega antibiotico ha 2 meses" e mesmo assim manteve C. difficile por causa do tempo de internacao; nao usou a topografia cecal nem a exigencia de cobertura sistemica da neutropenia febril',
    faltou='Neutropenia grave + febre + espessamento de CECO + sem antibiotico previo = tiflite -> piperacilina-tazobactam (ou cefepime + metronidazol); vancomicina oral nao cobre neutropenia febril',
    keep=[0],
    edit={0: {'verso_armadilha': 'Deixar "internacao prolongada" vencer a negativa explicita de antibiotico previo: C. difficile e antibiotico-associado, e o espessamento e do CECO (tiflite), nao difuso. Vancomicina oral age so na luz intestinal e deixaria a neutropenia febril sem cobertura sistemica.'}},
    racional='li sim, mas o tempo de internacao me fez supor o Clostridium difficile.'),
 75: dict(area='Psiquiatria', tema='Transtornos Alimentares', tipo='Armadilha',
    elo='Pergunta composta: validou a alternativa pela segunda metade verdadeira (alcalose hipocloremica) sem checar a primeira (chute)',
    faltou='Anorexia nervosa: causas de morte = complicacoes clinicas da desnutricao (arritmia, realimentacao) e suicidio',
    keep=[0]),
 77: dict(area='Nefrologia', tema='Sindrome Hemolitico-Uremica', tipo='Lacuna de conhecimento',
    elo='base ausente: marcou direto sem comparar as alternativas -- chute declarado tardiamente (22/09); nao tinha a regra "antibiotico aumenta o risco de SHU na STEC"',
    faltou='Colite por STEC: antibiotico (quinolona, SMX-TMP) ativa o fago e libera mais toxina Shiga -> contraindicado; tratamento e suporte. Questao CONTESTAVEL (D tambem defensavel: ~2/3 dialisam)',
    keep=[0],
    racional='marquei direto. foi chute.'),
 88: dict(area='Preventiva', tema='Rastreamento e prevenção', tipo='Lacuna de conhecimento',
    elo='base ausente (chute): matriz nivel x estrategia; "alto risco" ainda e prevencao primaria',
    faltou='Terciaria = age em quem JA tem a doenca (evitar complicacao/reabilitar); alto risco sem doenca = primaria; estrategia clinica (individual) x comunitaria (populacional)',
    keep=[1],
    edit={1: {'verso_regra_mestre': 'O nivel e definido pelo momento na historia natural (sem doenca = primaria; doenca precoce assintomatica = secundaria; doenca instalada = terciaria), nunca pelo quanto a acao "soa preventiva". A estrategia e o alvo: individuo (clinica) x populacao (comunitaria). "Garantir acesso aos servicos para pessoas vulneraveis com doenca cronica" = terciaria + comunitaria.'}}),
 91: dict(area='Preventiva', tema='Saúde do Idoso', tipo='Lacuna de conhecimento',
    elo='H2/H3: leu "mimetizar" corretamente como PRODUZIR, mas nao tinha a lista de causas medicas reversiveis de sindrome depressiva no idoso e nao testou o par inteiro',
    faltou='Hipotireoidismo e hipercalcemia (hiperparatireoidismo) mimetizam depressao e revertem ao tratar; investigacao minima = TSH, calcio, B12/folato, sodio, funcao renal, hemograma',
    keep=[0, 1],
    racional='produzem [leu mimetizar como produzir o quadro].'),
 97: dict(area='Preventiva', tema='Testes Diagnósticos', tipo='Erro de aplicacao',
    elo='H3/H4: leu o TE que nao atingiu a FC submaxima como NEGATIVO (e inconclusivo) e nao acionou Bayes com pre-teste alta (chute)',
    faltou='TE sem 85% da FC maxima prevista = inconclusivo; homem de 66 anos com angina tipica 3/3 = pre-teste alta; Framingham estima risco de evento em ASSINTOMATICO, nao probabilidade de doenca em sintomatico',
    keep=[0, 1]),
 99: dict(area='Preventiva', tema='Prevenção Quaternária e Sobrediagnóstico', tipo='Erro de aplicacao',
    elo='H1/H2: ignorou o discriminador -- nao calculou o IMC (118/4 = 29,5 = sobrepeso) e carimbou obesidade pelo peso absoluto; ancoragem no numero',
    faltou='IMC 25-29,9 = sobrepeso, obesidade so >= 30; HAS exige 2 consultas distintas ou MAPA/MRPA; GJ 100-125 pede repeticao antes do rotulo',
    keep=[0],
    racional='nao, ignorei o discriminador.'),
}

CARD_FIELDS = ('frente_contexto', 'frente_pergunta', 'verso_resposta', 'verso_regra_mestre', 'verso_armadilha')

def card_from_candidate(c, q):
    return dict(tipo='elo_quebrado',
                frente_contexto='',
                frente_pergunta=asc(c['frente']).strip(),
                verso_resposta=asc(c['verso']).strip(),
                verso_regra_mestre='',
                verso_armadilha=asc(q.get('armadilha_banca') or '').strip())

def main():
    d = json.load(open(SRC, encoding='utf-8'))
    byn = {q['n']: q for q in d['questoes']}
    lote = []
    for n, m in M.items():
        q = byn[n]
        assert q['marcada'] != q['gabarito'], n
        cards = []
        for i in m.get('keep', []):
            c = card_from_candidate(q['cards_candidatos'][i], q)
            for k, v in (m.get('edit') or {}).get(i, {}).items():
                c[k] = asc(v)
            cards.append(c)
        for e in m.get('extra', []):
            cards.append({k: asc(v) for k, v in e.items()})
        assert cards, f'Q{n} sem card'
        for c in cards:
            for k in CARD_FIELDS:
                c[k] = asc(c.get(k) or '')
        cadeia = ' -> '.join(re.sub(r'^H\d+\s*', '', asc(h)) for h in q['cadeia'])
        item = dict(
            area=m['area'], tema=m['tema'],
            titulo=asc(f"UERJ 2023 Q{n} -- {q['tema']}")[:120],
            enunciado=asc(f"[UERJ 2023 · Q{n} · bloco {q['bloco']}] {q['pede']} Dados do caso e cadeia esperada: {cadeia}"),
            correta=asc(f"{q['gabarito']}) {q['alternativas'][q['gabarito']]}"),
            marcada=asc(f"{q['marcada']}) {q['alternativas'][q['marcada']]}"),
            erro=m['tipo'],
            elo=asc(m['elo']),
            armadilha=asc(q.get('armadilha_banca') or 'sem armadilha declarada'),
            complexidade=COMPLEX[q['tipo']],
            habilidades=cadeia,
            faltou=asc(m['faltou']),
            explicacao=asc(q['por_que_gabarito']),
            cards=cards,
        )
        lote.append(item)
    json.dump(lote, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('itens:', len(lote), 'cards:', sum(len(i['cards']) for i in lote))
    novos = sorted({(i['area'], i['tema']) for i in lote})
    print('pares (area,tema):', len(novos))
    for p in novos:
        print('  ', p)

if __name__ == '__main__':
    main()
