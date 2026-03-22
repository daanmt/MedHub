import sqlite3
import pandas as pd
from datetime import datetime

with sqlite3.connect('ipub.db') as conn:
    c = conn.cursor()

    c.execute("SELECT id FROM taxonomia_cronograma WHERE tema = 'Insuficiência Cardíaca'")
    res = c.fetchone()
    tema_id = res[0] # it was already successfully created in the prior run!

    c.execute("DELETE FROM questoes_erros WHERE tema_id = ? AND date(data_registro) = date('now', 'localtime')", (tema_id,))

    erros = [
        {
            "titulo": "Perfil L (Frio e Seco): Reposição Volêmica Inicial",
            "o_que_faltou": "Falha em reconhecer que o Perfil L (hipoperfusão sem congestão) exige reposição de fluidos antes de inotrópicos.",
            "enunciado": "Idoso com IC isquêmica, extremidades frias, hipotenso, sem congestão pulmonar.",
            "explicacao": "Perfil Frio e Seco (L) indica hipovolemia/baixo débito puro. A conduta INICIAL é administrar 250ml de SF 0,9%. Dobutamina é a segunda linha apenas se refratário ao volume.",
            "armadilha": "Usar Inotrópicos como primeira linha no Perfil L. Inotrópicos sem volume não funcionam bem e pioram o cenário; volume é o passo 1."
        },
        {
            "titulo": "Betabloqueadores: Não Iniciar em Descompensação Ativa",
            "o_que_faltou": "Desconhecer que BBs têm efeito inotrópico negativo agudo e não devem ser iniciados em pacientes congestos/descompensados.",
            "enunciado": "Manejo crônico vs agudo da IC com fração de ejeção reduzida.",
            "explicacao": "BBs demandam MESE para benefício. Iniciar em dose baixa, titular a cada 2 SEMANAS. Nunca iniciar na fase aguda/congesta. O tartarato de metoprolol não reduz mortalidade, só o succinato.",
            "armadilha": "Achar que BB deve ser introduzido para 'salvar' o paciente na fase aguda. Ele deprime a bomba a curtíssimo prazo, só salva a longo prazo."
        },
        {
            "titulo": "Euvolemia como Pré-requisito para Betabloqueador",
            "o_que_faltou": "Ansiedade em associar o BB prematuramente antes da resolução da congestão periférica e pulmonar.",
            "enunciado": "Paciente com IC prévia, ainda com refluxo hepatojugular e edema MMII leve após 15 dias de diurético.",
            "explicacao": "Como o paciente AINDA apresenta sinais de congestão, a conduta correta é AUMENTAR a dose da furosemida para alcançar a euvolemia. BBs são totalmente contraindicados até que não haja retenção hídrica.",
            "armadilha": "Achar que melhora parcial dos sintomas autoriza a entrada do Betabloqueador. O paciente tem que estar seco."
        },
        {
            "titulo": "Taxonomia Atualizada das Frações de Ejeção",
            "o_que_faltou": "Gap na classificação (Fração Levemente Reduzida vs Reduzida) e limite da Doença Renal Estágio 2.",
            "enunciado": "Hipertensa diabética com FEVE de 43% e TFG 60mL/min.",
            "explicacao": "FEVE < 40% = Reduzida. FEVE 40-49% = Levemente Reduzida (nova classificação). TFG 60-89 = DRC Estágio 2.",
            "armadilha": "Confundir 43% como 'Fração Reduzida' clássica, quando cai no limbo moderno da 'Levemente Reduzida/Intermediária'."
        },
        {
            "titulo": "Síndrome Cardiorrenal Pré-Renal (Iatrogenia Diurética)",
            "o_que_faltou": "Não identificar que hipotensão, tontura e piora aguda de Cr/Ur (relação  > 40) após diurese é Hipovolemia.",
            "enunciado": "Idoso com IC recebe Furosemida 8/8h. No 5º dia, sintomas somem, mas surge hipotensão, Cr pula de 1.5 para 3.8 e Ur para 202.",
            "explicacao": "A diurese vigorosa reduziu a congestão, mas secou o volume arterial efetivo. Isso gera insuficiência renal pré-renal. A conduta é: suspender diurético e HIDRATAR.",
            "armadilha": "Ver o edema de base e achar que o doente ainda tá congesto hemodinamicamente. O intravascular já secou!"
        },
        {
            "titulo": "Estenose Bilateral de Artéria Renal e Uso de IECA",
            "o_que_faltou": "Incapacidade de correlacionar a piora dramática da função renal após introdução de IECA com a restrição vascular periférica grave.",
            "enunciado": "Piora de Cr de 0.8 para 3.2 duas semanas após início de Captopril 25mg 3x.",
            "explicacao": "Pioras de Cr > 30% ou agudas severas pós-IECA indicam causa renovascular (Estenose Arterial Bilateral). O IECA deve ser SUSPENSO e trocado por Nitrato + Hidralazina.",
            "armadilha": "Achar que aumento de diurético resolve o 'cardiorrenal', quando na verdade o culpado da agressão glomerular é a droga bloqueadora do SRAA."
        },
        {
            "titulo": "Pulso Alternans vs Pulso Paradoxal",
            "o_que_faltou": "Imprecisão propedêutica na identificação do Pulso Alternans como marcador de insuficiência biventricular, confundindo com o Eletro.",
            "enunciado": "Jovem com IC Aguda pós-gripal (Miocardite), mostrando variação na amplitude sistólica da PAI batimento a batimento.",
            "explicacao": "Pulso Alternans (ondas alternadas na PAM arterial) = IC Grave. Pulso Paradoxal = Tamponamento Cardíaco. Alternans Elétrico (QRS variando) = Derrame pericárdico massivo.",
            "armadilha": "A curva hemodinâmica mostrava variação batimento a batimento e não por ciclos respiratórios. A mistura de conceitos de Alternans derruba o candidato."
        },
        {
            "titulo": "Hipocalcemia como Causa Reversível de IC",
            "o_que_faltou": "Achismo fisiológico sugerindo que Hipercalemia desliga a contratilidade. Ela causa arritmia, não insuficiência.",
            "enunciado": "Qual distúrbio gera etiologia reversível contínua de Insuficiência Cardíaca Pura?",
            "explicacao": "O Cálcio é o íon direto do inotropismo. A Hipocalcemia Severa reduz drasticamente a contratilidade miocárdica de forma completamente reversível. Potássio afeta a polarização/arritmias, não falha contrátil.",
            "armadilha": "Potássio mata do coração e associa isso à Insuciência Cardíaca, mas de morte súbita elétrica, não de falha de bomba."
        },
        {
            "titulo": "ICFEp: Nenhum Impacto Antigo de IECA/BB na Mortalidade",
            "o_que_faltou": "Aplicar o protocolo cego de mortalidade da ICFEr para a ICFEp, superestimando IECA/BB.",
            "enunciado": "Paciente com FE 51%, Dispneia, Edema, HAS longa. Qual o objetivo macro do tratamento?",
            "explicacao": "Na ICFEp, até iSGLT2 engrenar, nenhuma droga clássica (IECA, BRA, BB, ARM) reduziu MORTALIDADE. Tratamento é puramente sintomático e manejo das comorbidades (BCC di-hidro, Furosemida).",
            "armadilha": "Querer aplicar o Tripé da Salvação (BRA/IECA + BB + ARM) pra qualquer paciente cansado, ignorando a FEVE normal."
        },
        {
            "titulo": "BCC Não Di-hidropiridínico na ICFEp",
            "o_que_faltou": "Pânico injustificado de Diltiazem/Verapamil em pacientes com IC de qualquer tipo.",
            "enunciado": "Paciente com ICFEp (FE 72%), hipertenso a 180x110 e FC de 112bpm. Qual o triplo bloqueio?",
            "explicacao": "BCCs cardiodepressores SÃO CONTRAINDICADOS NA ICFEr. Porém, na ICFEp (o problema é relaxamento), o Diltiazem é excelente para HAS + controle cronotrópico negativo. Enalapril + Furosemida + Diltiazem forma um combo genial.",
            "armadilha": "O segredo é dominar a patogênese: ICFEp = Ventrículo concêntrico que não relaxa, logo um cronotrópico negativo ajuda brutalmente a encher na diástole."
        }
    ]

    for err in erros:
        c.execute("""
            INSERT INTO questoes_erros 
            (tema_id, titulo, complexidade, enunciado, alternativa_correta, alternativa_marcada, tipo_erro, habilidades_sequenciais, o_que_faltou, explicacao_correta, armadilha_prova, data_registro)
            VALUES (?, ?, 'Difícil', ?, 'A', 'B', 'Conceitual', 'Diagnóstico -> Terapêutica', ?, ?, ?, datetime('now', 'localtime'))
        """, (tema_id, err['titulo'], err['enunciado'], err['o_que_faltou'], err['explicacao'], err['armadilha']))
    
    conn.commit()
    print("Sucesso Inquestionável! Ingestão perfeita dos cards metacognitivos de IC!")
