import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

def run(cmd):
    print(f"Running...")
    subprocess.run(cmd, shell=True, check=True)

# Q7
run("""python tools/insert_questao.py \
  --area "Clinica Medica" --tema "Tireotoxicose" \
  --titulo "TSH e T4 altos" \
  --enunciado "Criança agitada, baixo peso. T3 e T4 livres altos. TSH ALTO." \
  --correta "Resistência aos hormônios tireoidianos." \
  --marcada "Hipotireoidismo." \
  --erro "Lacuna de conhecimento" \
  --elo "Diagnosticar o padrão de laboratório TSH e T4/T3 altos associado à clínica tireotóxica infantil." \
  --armadilha "Olhar para o TSH alto e ancorar em hipotireoidismo sem ler T3/T4 e a clínica." \
  --complexidade "Alta" \
  --habilidades "Perceber a clínica de tireotoxicose -> Checar hormônios (T4 alto concorda com clínica) -> Checar TSH (TSH alto é paradoxal, era pra estar suprimido) -> TSH alto + T4 alto = Adenoma TSH ou Resistência Periférica." \
  --faltou "A combinação de TSH elevado com T4 livre elevado define hipertireoidismo secundário (TSHoma) ou Resistência aos Hormônios Tireoidianos (causa familiar clássica)." \
  --explicacao "Se a hipófise funciona bem, T4 alto gera feedback e derruba o TSH. TSH elevado JUNTAMENTE com T4 elevado significa que a hipófise perdeu o sensor (Resistência aos hormônios tireoidianos, autossômica dominante) ou virou produtora autônoma (TSHoma)." \
  --frente_contexto "Criança apresenta perda de peso e taquicardia. O laboratório mostra T4 Livre elevado e TSH também elevado. A mãe possui os mesmos achados." \
  --frente_pergunta "Qual é a principal hipótese diagnóstica para esse padrão laboratorial (ausência de feedback negativo)?" \
  --verso_resposta "Resistência aos hormônios tireoidianos." \
  --verso_regra_mestre "TSH elevado na presença de T4 e T3 altos reflete falha no feedback negativo na hipófise, sendo as duas principais causas: Resistência Aos Hormônios Tireoidianos e Adenoma produtor de TSH (TSHoma)." \
  --verso_armadilha "Diagnosticá-la com hipotireoidismo devido ao TSH elevado, ignorando completamente os níveis tóxicos do T4 Livre."
""")

# Q8
run("""python tools/insert_questao.py \
  --area "Clinica Medica" --tema "Tireotoxicose" \
  --titulo "Doença de Graves e TRAb" \
  --enunciado "Tireotoxicose, exoftalmia, bócio difuso. Qual a fisiopatologia?" \
  --correta "Anticorpo anti receptor de TSH (TRAb)." \
  --marcada "Secreção autônoma de TSH." \
  --erro "Lacuna de conhecimento" \
  --elo "Desconhecer que o mecanismo fisiopatológico fundacional do Graves é a autoimunidade estimulante pelo TRAb." \
  --armadilha "Secreção autônoma de TSH gera bócio e clínica similar, mas não exoftalmia." \
  --complexidade "Baixa" \
  --habilidades "Graves = Bócio difuso + Oftalmopatia -> Causada por autoanticorpo TRAb." \
  --faltou "A Doença de Graves é causada pela presença do TRAb (Anticorpo estimulador do receptor do TSH)." \
  --explicacao "O TRAb liga-se ao receptor do TSH na tireoide, estimulando crescimento (bócio) e produção sem fim. Ele também ataca retro-órbita (oftalmopatia) e pele (mixedema)." \
  --frente_contexto "Paciente apresenta bócio difuso, hipercaptação cintilográfica e oftalmopatia tireoidiana evidente." \
  --frente_pergunta "Qual é o principal marcador imunológico patogênico dessa doença?" \
  --verso_resposta "TRAb (Anticorpo antirreceptor de TSH)." \
  --verso_regra_mestre "A presença da oftalmopatia e dermopatia atreladas ao hipertireoidismo aponta infalivelmente para a Doença de Graves, causada pelo TRAb." \
  --verso_armadilha "Confundir a fisiopatologia com mutação autônoma do nódulo (Plummer) ou tumor hipofisário."
""")

# Q9
run("""python tools/insert_questao.py \
  --area "Clinica Medica" --tema "Tireotoxicose" \
  --titulo "Hepatite severa por Metimazol" \
  --enunciado "Graves em uso de metimazol 80mg. TGO 382, TGP 560. TSH suprimido. Qual a melhor conduta definitiva?" \
  --correta "Indicar tratamento com radioiodo." \
  --marcada "Trocar metimazol pelo propiltiouracil." \
  --erro "Erro de aplicacao" \
  --elo "Saber que ambas as tionamidas podem dar necrose hepática, e a falha hepática severa com uma contraindica a troca cruzada." \
  --armadilha "Como PTU é opção pra gestante, o aluno acha que PTU salva o fígado. É o inverso." \
  --complexidade "Media" \
  --habilidades "Detectar TGO/TGP altas -> Tionamida falhou/tóxica -> Suspender -> Terapia ablativa (cirurgia ou radioiodo) vira obrigatória -> Oftalmopatia grave não descrita, então radioiodo é ok." \
  --faltou "Se o paciente desenvolver toxicidade hepática severa ao Metimazol, o Propiltiouracil NÃO é alternativa, pois o risco hepatotóxico cruzado é altíssimo. Deve-se partir para tratamento ablativo (radioiodo ou tireoidectomia)." \
  --explicacao "Metimazol tem risco de hepatite colestática e PTU tem risco de necrose hepática fulminante. A elevação de transaminases para 3x o valor normal é indicação formal para parar Tionamida e não tentar a outra. A escolha recai sobre iodo radioativo." \
  --frente_contexto "Paciente com Graves em uso de Metimazol evolui com TGO/TGP acima de 300 U/L (lesão hepática severa)." \
  --frente_pergunta "A troca pelo propiltiouracil (PTU) é recomendada?" \
  --verso_resposta "Não." \
  --verso_regra_mestre "Diante de efeitos adversos severos de uma Tionamida (hepatotoxicidade, agranulocitose), a troca pela outra Tionamida é formalmente contraindicada. Parte-se para radioiodo ou cirurgia." \
  --verso_armadilha "Acreditar que o PTU é protetor hepático ou a droga de resgate padrão."
""")

# Q10
run("""python tools/insert_questao.py \
  --area "Clinica Medica" --tema "Tireotoxicose" \
  --titulo "Tionamidas e Placenta" \
  --enunciado "Nas gestantes com hipertireoidismo..." \
  --correta "O tratamento do hipoparatireoidismo na gravidez consiste na reposição de cálcio e vit D." \
  --marcada "O TRAb prediz hipotireoidismo neonatal." \
  --erro "Lacuna de conhecimento" \
  --elo "Desconhecer que as Tionamidas (PTU/Metimazol) atravessam livremente a barreira placentária, podendo inibir a tireoide fetal." \
  --armadilha "Considerar que o que protege o feto é a ausência de passagem de fármaco, quando na verdade é a regulação de dose." \
  --complexidade "Baixa" \
  --habilidades "Descartar a D porque Tionamidas passam placenta -> Aceitar a da Paratireoide." \
  --faltou "As drogas antitireoidianas (Tionamidas: PTU e Metimazol) cruzam a barreira placentária e podem causar hipotireoidismo e bócio fetal se usadas em excesso na gestante." \
  --explicacao "O TRAb materno geralmente causa hipertireoidismo transitório neonatal (anticorpo estimulador), não hipo. As Tionamidas obrigatoriamente cruzam a placenta (por isso titula-se na gestante visando T4L no limite superior, pra poupar o feto)." \
  --frente_contexto "Gestante em tratamento para Doença de Graves recebe altas doses de drogas antitireoidianas (Metimazol/PTU)." \
  --frente_pergunta "Qual é o principal risco tireoidiano para o feto provocado diretamente pelas medicações?" \
  --verso_resposta "Hipotireoidismo e bócio fetal." \
  --verso_regra_mestre "As Tionamidas atravessam livremente a barreira placentária. Para prevenir o bloqueio exagerado na tireoide do feto, a dose na mãe deve mirar o limite superior (leve hipertireoidismo materno)." \
  --verso_armadilha "Acreditar que essas drogas não passam pela placenta e por isso são permitidas na gestação."
""")
