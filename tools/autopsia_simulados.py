# -*- coding: utf-8 -*-
"""Gera a Autopsia dos Simulados: 120 erros cruzados com cadeia de habilidades e fila FSRS.

Fontes:
  ipub.db                        -- SSOT dos erros, flashcards e estado FSRS (read-only)
  core/simulados/curadoria.json  -- camada autoral (mecanismo, elo quebrado, etapa por bloco)
  Simulado 2 - pt*.pdf           -- texto verbatim do S2 (IP Estrategia MED, gitignored)

Read-only sobre o ipub.db: zero write. Uso:
  python -X utf8 tools/autopsia_simulados.py [--out CAMINHO.html]
"""
import argparse
import json
import os
import re
import sqlite3
import unicodedata
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "ipub.db")
CURADORIA = os.path.join(ROOT, "core", "simulados", "curadoria.json")
CACHE_S2 = os.path.join(ROOT, "core", "simulados", "_s2_questoes.json")  # gitignored (IP)
CACHE_S5 = os.path.join(ROOT, "core", "simulados", "_s5_questoes.json")  # gitignored (IP)

SIMS = {
    "S2": {"nome": "Simulado 2", "data": "02/08/2026", "score": 54, "erros": 46,
           "ids": range(622, 668), "fonte": "pdf"},
    "S3": {"nome": "Simulado 3", "data": "06/08/2026", "score": 60, "erros": 40,
           "ids": range(719, 759), "fonte": "db"},
    "S4": {"nome": "Simulado 4", "data": "13/08/2026", "score": 66, "erros": 34,
           "ids": range(781, 815), "fonte": "db"},
    "S5": {"nome": "Simulado 5", "data": "17/08/2026", "score": 63, "erros": 37,
           "ids": range(815, 852), "fonte": "pdf"},
}
SIMK = ["S2", "S3", "S4", "S5"]

# Vinculo direto id-do-erro <-> numero-da-questao (1-100) no Simulado 5. Conhecido e
# determinístico (ordem de insercao dos 4 blocos == ordem crescente de numero), ao
# contrario do S2 que precisa de bijecao por similaridade lexical (casa_s2).
S5_NUMS = [3, 5, 8, 11, 14, 17, 18, 22, 23, 24, 25, 27, 28, 33, 34, 43, 45, 46,
           52, 54, 55, 56, 57, 58, 61, 65, 68, 69, 72, 73, 74, 77, 79, 87, 88, 98, 99]
S5_ID_TO_NUM = dict(zip(range(815, 852), S5_NUMS))


# --------------------------------------------------------------------------
# 1. Reacentuacao cosmetica
# --------------------------------------------------------------------------
# O corpus do ipub.db foi gravado sem diacriticos. Este dicionario restaura os
# acentos por palavra inteira. REGRA DURA: nenhuma entrada ambigua -- uma palavra
# so entra aqui se a forma SEM acento nao for, ela propria, uma palavra valida do
# portugues. Foi assim que "e"->"e'" (conjuncao virando verbo) contaminou 30 dos
# 120 enunciados na versao anterior; "as"->"a`s" tinha o mesmo defeito.
ACC = {
 "nao":"não","sao":"são","ja":"já","apos":"após","ate":"até","alem":"além","tambem":"também",
 "porem":"porém","criterio":"critério","criterios":"critérios","diagnostico":"diagnóstico",
 "diagnosticos":"diagnósticos","clinico":"clínico","clinica":"clínica","clinicos":"clínicos",
 "clinicas":"clínicas","cirurgico":"cirúrgico","cirurgica":"cirúrgica","cirurgicos":"cirúrgicos",
 "cirurgicas":"cirúrgicas","medico":"médico","medica":"médica","medicos":"médicos","medicas":"médicas",
 "pratica":"prática","publico":"público","publica":"pública","basico":"básico","basica":"básica",
 "indicacao":"indicação","indicacoes":"indicações","avaliacao":"avaliação","avaliacoes":"avaliações",
 "investigacao":"investigação","classificacao":"classificação","confirmacao":"confirmação",
 "internacao":"internação","reposicao":"reposição","exposicao":"exposição","infeccao":"infecção",
 "infeccoes":"infecções","inflamacao":"inflamação","obstrucao":"obstrução","hipertensao":"hipertensão",
 "hipotensao":"hipotensão","distensao":"distensão","lesao":"lesão","lesoes":"lesões","pressao":"pressão",
 "funcao":"função","reducao":"redução","elevacao":"elevação","ausencia":"ausência","presenca":"presença",
 "urgencia":"urgência","emergencia":"emergência","frequencia":"frequência","frequencias":"frequências",
 "consequencia":"consequência","evidencia":"evidência","evidencias":"evidências","sequencia":"sequência",
 "incidencia":"incidência","prevalencia":"prevalência","referencia":"referência","resistencia":"resistência",
 "insuficiencia":"insuficiência","deficiencia":"deficiência","adolescencia":"adolescência",
 "gestacao":"gestação","obstetrica":"obstétrica","obstetrico":"obstétrico","pediatrico":"pediátrico",
 "pediatrica":"pediátrica","hematologico":"hematológico","hematologica":"hematológica",
 "neurologico":"neurológico","neurologica":"neurológica","cardiaco":"cardíaco","cardiaca":"cardíaca",
 "hepatico":"hepático","hepatica":"hepática","pancreatico":"pancreático","torax":"tórax",
 "toracica":"torácica","toracico":"torácico","pelvico":"pélvico","pelvica":"pélvica","cranio":"crânio",
 "cronico":"crônico","cronica":"crônica","cronicas":"crônicas","cronicos":"crônicos",
 "tipico":"típico","tipica":"típica","atipico":"atípico","atipica":"atípica","atipicos":"atípicos",
 "atipicas":"atípicas","especifico":"específico","especifica":"específica","especificos":"específicos",
 "especificas":"específicas","sistemico":"sistêmico","sistemica":"sistêmica","generico":"genérico",
 "generica":"genérica","unico":"único","unica":"única","multiplas":"múltiplas","multiplos":"múltiplos",
 "proprio":"próprio","propria":"própria","proximo":"próximo","proxima":"próxima","ultimo":"último",
 "ultima":"última","possivel":"possível","impossivel":"impossível","util":"útil","dificil":"difícil",
 "facil":"fácil","rapido":"rápido","rapida":"rápida","obrigatorio":"obrigatório","obrigatoria":"obrigatória",
 "necessario":"necessário","necessaria":"necessária","niveis":"níveis","nivel":"nível","orgao":"órgão",
 "orgaos":"órgãos","serie":"série","area":"área","areas":"áreas","tres":"três","voce":"você","mae":"mãe",
 "crianca":"criança","criancas":"crianças","ossea":"óssea","osseo":"ósseo","padrao":"padrão",
 "padroes":"padrões","regua":"régua","serico":"sérico","serica":"sérica","atencao":"atenção",
 "opcao":"opção","opcoes":"opções","questao":"questão","questoes":"questões","raciocinio":"raciocínio",
 "memoria":"memória","duvida":"dúvida","so":"só","ha":"há","epidemiologico":"epidemiológico",
 "epidemiologica":"epidemiológica","estatistica":"estatística","sindrome":"síndrome","hemolise":"hemólise",
 "ictericia":"icterícia","vacinacao":"vacinação","imunizacao":"imunização","terapeutica":"terapêutica",
 "farmaco":"fármaco","farmacos":"fármacos","antibiotico":"antibiótico","antibioticos":"antibióticos",
 "hemodinamica":"hemodinâmica","hemodinamico":"hemodinâmico","respiratoria":"respiratória",
 "respiratorio":"respiratório","circulatorio":"circulatório","metabolico":"metabólico",
 "metabolica":"metabólica","endocrino":"endócrino","obstetricia":"obstetrícia","cardiologia":"cardiologia",
 "eletrolitos":"eletrólitos","leucocitos":"leucócitos","hidroaereo":"hidroaéreo","abdominal":"abdominal",
 "anemia":"anemia","biopsia":"biópsia","cateter":"cateter","calculo":"cálculo","calculos":"cálculos",
 "sifilis":"sífilis","tuberculose":"tuberculose","cervice":"cérvice","utero":"útero","uterina":"uterina",
 "hernia":"hérnia","hernias":"hérnias","tecnica":"técnica","tecnicas":"técnicas","estagio":"estágio",
 "protese":"prótese","anticorpo":"anticorpo","antigeno":"antígeno","gastrico":"gástrico",
 "gastrica":"gástrica","colica":"cólica","ciclico":"cíclico","ciclicos":"cíclicos","ciclica":"cíclica",
 "ciclicas":"cíclicas","volemica":"volêmica","volemico":"volêmico","limitrofe":"limítrofe",
 "hipoglicorraquia":"hipoglicorraquia","liquor":"líquor","tonus":"tônus","sequela":"sequela",
 "sequelas":"sequelas","radiografia":"radiografia","radiologico":"radiológico","radiologica":"radiológica",
 "endoscopica":"endoscópica","endoscopico":"endoscópico","laparoscopia":"laparoscopia",
 "hipoxemia":"hipoxemia","dispneia":"dispneia","apneia":"apneia","cianose":"cianose","edema":"edema",
 "escore":"escore","escores":"escores","indice":"índice","indices":"índices","maxima":"máxima",
 "minima":"mínima","maximo":"máximo","minimo":"mínimo","media":"média","hipotese":"hipótese",
 "hipoteses":"hipóteses","analise":"análise","parametro":"parâmetro","parametros":"parâmetros",
 "historia":"história","antibioticoterapia":"antibioticoterapia","corticoide":"corticoide",
 "ambulatorio":"ambulatório","laboratorio":"laboratório","laboratorial":"laboratorial",
 "obito":"óbito","obitos":"óbitos","letalidade":"letalidade","mortalidade":"mortalidade",
}

# Expansao (sessao 147): varredura de vocabulario dos 157 erros contra o dicionario acima
# encontrou ~300 palavras ainda sem diacritico. Mesma regra dura do bloco ACC -- nenhuma
# entrada ambigua. Verbos conjugados que colidem com a forma acentuada ficam de fora
# (ex.: "indica"/"aplica"/"seria"/"varia"/"deveria" -- 3a pessoa do presente/condicional,
# muito mais frequentes no corpus do que o substantivo/adjetivo homografo).
ACC.update({
 "aplicacao":"aplicação","classificacao":"classificação","notificacao":"notificação",
 "ulceracao":"ulceração","observacao":"observação","expansao":"expansão","amamentacao":"amamentação",
 "resolucao":"resolução","edicao":"edição","populacao":"população","secrecao":"secreção",
 "perfuracao":"perfuração","estratificacao":"estratificação","direcao":"direção","dilatacao":"dilatação",
 "sensibilizacao":"sensibilização","sensibilizacoes":"sensibilizações","reclassificacao":"reclassificação",
 "participacao":"participação","irritacao":"irritação","infiltracao":"infiltração","incisao":"incisão",
 "desidratacao":"desidratação","acao":"ação","acoes":"ações","transmissao":"transmissão",
 "transicao":"transição","infusao":"infusão","hidratacao":"hidratação","formacao":"formação",
 "divisao":"divisão","destruicao":"destruição","deambulacao":"deambulação","convulsoes":"convulsões",
 "compressao":"compressão","combinacao":"combinação","alteracao":"alteração","violencia":"violência",
 "vascularizacao":"vascularização","tumoracao":"tumoração","suplementacao":"suplementação",
 "situacao":"situação","preservacao":"preservação","manifestacao":"manifestação","localizacao":"localização",
 "insercao":"inserção","fixacao":"fixação","exclusao":"exclusão","excecao":"exceção",
 "estabilizacao":"estabilização","erupcao":"erupção","duracao":"duração","descricao":"descrição",
 "desatencao":"desatenção","consolidacao":"consolidação","condicao":"condição","ampliacao":"ampliação",
 "agitacao":"agitação","admissao":"admissão","vibracao":"vibração","transfusao":"transfusão",
 "tentacao":"tentação","supervisao":"supervisão","retracao":"retração","restricao":"restrição",
 "resseccao":"ressecção","respiracao":"respiração","recomendacao":"recomendação","realizacao":"realização",
 "protecao":"proteção","progressao":"progressão","prevencao":"prevenção","poluicao":"poluição",
 "oxidacao":"oxidação","ordenacao":"ordenação","operatorio":"operatório","operatorios":"operatórios",
 "monitorizacao":"monitorização","microinvasao":"microinvasão","mediacao":"mediação",
 "manutencao":"manutenção","leucodeplecao":"leucodepleção","irradiacao":"irradiação",
 "intoxicacao":"intoxicação","interacao":"interação","inducao":"indução","incontinencia":"incontinência",
 "homologacao":"homologação","glicuronidacao":"glicuronidação","extensao":"extensão",
 "distribuicao":"distribuição","disseminacao":"disseminação","deterioracao":"deterioração",
 "desobstrucao":"desobstrução","descompressao":"descompressão","demencia":"demência",
 "definicao":"definição","declaracao":"declaração","conversao":"conversão",
 "contraindicacoes":"contraindicações","contraindicacao":"contraindicação","conizacao":"conização",
 "complicacao":"complicação","compensacao":"compensação","calcificacao":"calcificação",
 "atualizacao":"atualização","atribuicoes":"atribuições","aspiracao":"aspiração",
 "transformacao":"transformação","ventilacao":"ventilação","vasodilatacao":"vasodilatação",
 "reavaliacao":"reavaliação","proliferacao":"proliferação",
 "provavel":"provável","estavel":"estável","incompativel":"incompatível","compativel":"compatível",
 "razoavel":"razoável","favoravel":"favorável","desfavoravel":"desfavorável","disponivel":"disponível",
 "irritavel":"irritável","plausiveis":"plausíveis","plausivel":"plausível","testavel":"testável",
 "inviavel":"inviável","ultrassensivel":"ultrassensível","visivel":"visível","sensivel":"sensível",
 "intermediario":"intermediário","cenario":"cenário","ministerio":"ministério","calendario":"calendário",
 "usuario":"usuário","territorio":"território","terapeutico":"terapêutico","secundario":"secundário",
 "diario":"diário","tubario":"tubário","confirmatorio":"confirmatório","solitario":"solitário",
 "biliopancreatico":"biliopancreático","intraoperatorio":"intraoperatório","compulsoria":"compulsória",
 "involuntaria":"involuntária","horaria":"horária","primaria":"primária","voluntaria":"voluntária",
 "tubaria":"tubária","etaria":"etária","mandatoria":"mandatória","malaria":"malária",
 "secundaria":"secundária","intermediaria":"intermediária","reumatica":"reumática",
 "toxico":"tóxico","toxica":"tóxica","septico":"séptico","prognostico":"prognóstico",
 "historico":"histórico","miocardica":"miocárdica","miocardico":"miocárdico",
 "flogisticos":"flogísticos","ectopica":"ectópica","sobrediagnostico":"sobrediagnóstico",
 "pleuritica":"pleurítica","mitotico":"mitótico","cistico":"cístico","cistica":"cística",
 "antipsicotico":"antipsicótico","alergica":"alérgica","alergico":"alérgico","alergicos":"alérgicos",
 "sintomatico":"sintomático","psiquiatrica":"psiquiátrica","profilatica":"profilática",
 "plasmatico":"plasmático","pericardico":"pericárdico","pericardica":"pericárdica",
 "osmotico":"osmótico","osmotica":"osmótica","logica":"lógica","colonico":"colônico",
 "colonica":"colônica","alcoolica":"alcoólica","benzodiazepinico":"benzodiazepínico",
 "benzodiazepinicos":"benzodiazepínicos","acessorio":"acessório","topico":"tópico","topica":"tópica",
 "empirica":"empírica","empirico":"empírico","ecologico":"ecológico","assintomatica":"assintomática",
 "classica":"clássica","classico":"clássico","classicos":"clássicos","sistemicos":"sistêmicos",
 "simetrica":"simétrica","simetricas":"simétricas","biologico":"biológico","biologica":"biológica",
 "patologico":"patológico","mecanica":"mecânica","periferico":"periférico","periferica":"periférica",
 "pneumococica":"pneumocócica","piogenica":"piogênica","letargico":"letárgico",
 "fisiopatologico":"fisiopatológico","antifungico":"antifúngico","antifungicos":"antifúngicos",
 "antalgico":"antálgico","analgesicos":"analgésicos","amazonica":"amazônica",
 "neutrofilica":"neutrofílica","megaloblastica":"megaloblástica","micologico":"micológico",
 "morfologicas":"morfológicas","mamario":"mamário","laparoscopica":"laparoscópica",
 "isquemica":"isquêmica","genetica":"genética","glicemico":"glicêmico","glicemica":"glicêmica",
 "folico":"fólico","fenilcetonuria":"fenilcetonúria","epidemiologicos":"epidemiológicos",
 "diafragmatica":"diafragmática","vocabulario":"vocabulário","ventilatorio":"ventilatório",
 "vasoplegico":"vasoplégico","urinaria":"urinária","urinario":"urinário",
 "ultrassonografica":"ultrassonográfica","tireotoxica":"tireotóxica","tipicos":"típicos",
 "tetanogenico":"tetanogênico","termico":"térmico","teorica":"teórica","tecnico":"técnico",
 "pelvicas":"pélvicas","peptica":"péptica",
 "sibilancia":"sibilância","vigilancia":"vigilância","recorrencia":"recorrência","coerencia":"coerência",
 "circunferencia":"circunferência","abstinencia":"abstinência","tolerancia":"tolerância",
 "persistencia":"persistência","intercorrencias":"intercorrências","imunodeficiencia":"imunodeficiência",
 "neoadjuvancia":"neoadjuvância","consciencia":"consciência","potencia":"potência",
 "substancia":"substância","proteica":"proteica","endometrio":"endométrio","pulmao":"pulmão",
 "puerperio":"puerpério","murmurio":"murmúrio","cordao":"cordão","tendao":"tendão","balao":"balão",
 "medalhao":"medalhão","fabrica":"fábrica","justica":"justiça","gestao":"gestão","estao":"estão",
 "entao":"então","sessoes":"sessões","regioes":"regiões","fracoes":"frações","eleicao":"eleição",
 "anatomica":"anatômica","assimetricas":"assimétricas","caracteristicas":"características",
 "excentrica":"excêntrica","exofitica":"exofítica","volumica":"volúmica",
 # segunda leva (cauda longa da mesma varredura)
 "relacao":"relação","epigastricos":"epigástricos","disfuncao":"disfunção","decisao":"decisão",
 "servico":"serviço","secretorio":"secretório","invasao":"invasão","sistemicas":"sistêmicas",
 "percussao":"percussão","inflamatoria":"inflamatória","transtoracica":"transtorácica",
 "ressecao":"ressecção","pressorico":"pressórico","histopatologica":"histopatológica",
 "flutuacao":"flutuação","taquicardica":"taquicárdica","tabagico":"tabágico","suspensao":"suspensão",
 "suprapubica":"suprapúbica","substituicao":"substituição","subclinico":"subclínico",
 "sorologico":"sorológico","sorologica":"sorológica","sonolencia":"sonolência","solucao":"solução",
 "sindromico":"sindrômico","semiologico":"semiológico","sedentario":"sedentário","saudavel":"saudável",
 "satisfatoria":"satisfatória","revisao":"revisão","reversao":"reversão","ressonancia":"ressonância",
 "repeticao":"repetição","repercussao":"repercussão","reorientacao":"reorientação",
 "reincidencia":"reincidência","reidratacao":"reidratação","regressao":"regressão",
 "refrataria":"refratária","redutivel":"redutível","reconstrucao":"reconstrução",
 "recomendacoes":"recomendações","reacao":"reação","razao":"razão","questionario":"questionário",
 "queimacao":"queimação","puncao":"punção","psiquiatrico":"psiquiátrico","proteinuria":"proteinúria",
 "programacao":"programação","profissao":"profissão","prioritario":"prioritário",
 "precaucao":"precaução","possiveis":"possíveis","poliuria":"poliúria","politicas":"políticas",
 "politica":"política","polimorfico":"polimórfico","placentaria":"placentária","piuria":"piúria",
 "piogenicas":"piogênicas",
 "periodica":"periódica","perfuracoes":"perfurações","parasitologica":"parasitológica",
 "palpavel":"palpável","palpacao":"palpação","orientacao":"orientação","organizacao":"organização",
 "organica":"orgânica","operatoria":"operatória","oncotica":"oncótica","obstetricas":"obstétricas",
 "observaveis":"observáveis","nutricao":"nutrição","numerico":"numérico","normotensao":"normotensão",
 "normocromica":"normocrômica","normocitica":"normocítica","neutrofilico":"neutrofílico",
 "neuropatica":"neuropática","mutacao":"mutação","movimentacao":"movimentação",
 "mnemonico":"mnemônico","mitotica":"mitótica","mitocondria":"mitocôndria",
 "miopericardica":"miopericárdica","miocardicos":"miocárdicos","migratoria":"migratória",
 "migracao":"migração","metastatica":"metastática","metabolicos":"metabólicos",
 "meningoencefalica":"meningoencefálica","medicacoes":"medicações","medicacao":"medicação",
 "mansonica":"mansônica","manipulacao":"manipulação","mamografico":"mamográfico",
 "mamaria":"mamária","magnetica":"magnética","logico":"lógico","legislacao":"legislação",
 "introducao":"introdução","intraoperatoria":"intraoperatória","intervencoes":"intervenções",
 "intervencao":"intervenção","interrupcao":"interrupção","interferencia":"interferência",
 "intercorrencia":"intercorrência","insulinica":"insulínica","inspecao":"inspeção",
 "inibicao":"inibição","informacoes":"informações","informacao":"informação",
 "influencia":"influência","inflamatorio":"inflamatório","infancia":"infância",
 "inespecifico":"inespecífico","indistinguiveis":"indistinguíveis","inalatorio":"inalatório",
 "imunossupressao":"imunossupressão","imunocromatografico":"imunocromatográfico",
 "improvavel":"improvável","impressao":"impressão","idiopatica":"idiopática",
 "iatrogenica":"iatrogênica","horario":"horário","histopatologico":"histopatológico",
 "histologico":"histológico","hipotonico":"hipotônico","hipotalamico":"hipotalâmico",
 "hipocromica":"hipocrômica","hipocaloricas":"hipocalóricas","hipertonico":"hipertônico",
 "hiperglicemico":"hiperglicêmico","hepatoesplenica":"hepatoesplênica","hematologicos":"hematológicos",
 "glicolitico":"glicolítico","friavel":"friável","formulacao":"formulação","fisico":"físico",
 "fisica":"física","farmacologica":"farmacológica","expressao":"expressão","exigencias":"exigências",
 "exigencia":"exigência","execucao":"execução","exacerbacao":"exacerbação","etica":"ética",
 "esqueletica":"esquelética","escorpiao":"escorpião","escoliotica":"escoliótica",
 "erradicacao":"erradicação","epileptica":"epiléptica","enzimaticos":"enzimáticos",
 "enzimatico":"enzimático","endemicas":"endêmicas","embrionario":"embrionário",
 "eliminacao":"eliminação","efusao":"efusão","educacao":"educação","dramatico":"dramático",
 "dispeptico":"dispéptico","direcoes":"direções","diagnosticas":"diagnósticas",
 "detectavel":"detectável","desnutricao":"desnutrição","desnecessario":"desnecessário",
 "desnecessaria":"desnecessária","dermatologico":"dermatológico","dependencia":"dependência",
 "decisoes":"decisões","cronologica":"cronológica","critico":"crítico","convulsao":"convulsão",
 "contrario":"contrário","confusao":"confusão","conferencias":"conferências","condicoes":"condições",
 "conclusao":"conclusão","comunitaria":"comunitária","comprovacao":"comprovação",
 "competencia":"competência","compensatorio":"compensatório","combinacoes":"combinações",
 "coloracao":"coloração","colestatica":"colestática","clinicopatologico":"clinicopatológico",
 "climaterio":"climatério","citologicos":"citológicos","cisticos":"císticos","cisticas":"císticas",
 "circulacao":"circulação","cessacao":"cessação","cefalica":"cefálica",
 "caracteristicos":"característicos","bioquimico":"bioquímico","biometrico":"biométrico",
 "biologicos":"biológicos","bancario":"bancário","autorizacao":"autorização",
 "automatico":"automático","atuacao":"atuação","atopica":"atópica","assintomatico":"assintomático",
 "arteria":"artéria","ardencia":"ardência","apresentacao":"apresentação",
 "antitetanicos":"antitetânicos","antitetanico":"antitetânico","antitetanica":"antitetânica",
 "antimitocondria":"antimitocôndria","antifungicas":"antifúngicas",
 "angioembolizacao":"angioembolização","anestesico":"anestésico","amniotico":"amniótico",
 "aminolevulinico":"aminolevulínico","alteracoes":"alterações","aloimunizacao":"aloimunização",
 "agressao":"agressão","afirmacao":"afirmação","adesao":"adesão","academica":"acadêmica",
 "diabetica":"diabética","pilorica":"pilórica","pontuacao":"pontuação",
})
_WORD = re.compile(r"[A-Za-zÀ-ÿ]+")


def reacc(txt):
    """Restaura diacriticos por palavra inteira. Nunca toca palavras fora do dicionario."""
    if not txt:
        return ""

    def sub(m):
        w = m.group(0)
        r = ACC.get(w.lower())
        if r is None:
            return w
        if w.isupper() and len(w) > 1:
            return r.upper()
        if w[0].isupper():
            return r[0].upper() + r[1:]
        return r

    return reacc_verbo(_WORD.sub(sub, txt))


AREA_FIX = {"Obstetricia": "Obstetrícia", "Endocrino": "Endócrino"}

# Os 5 grandes blocos da prova. Especialidades cirurgicas (ortopedia, otorrino,
# oftalmo, urologia) entram em Cirurgia; todas as subespecialidades clinicas
# entram em Clinica Medica.
MACRO = {
    "Cirurgia": "Cirurgia", "Ortopedia": "Cirurgia", "Otorrino": "Cirurgia", "Oftalmo": "Cirurgia",
    "Pediatria": "Pediatria",
    "Preventiva": "Preventiva",
    "Ginecologia": "GO", "Obstetrícia": "GO", "GO": "GO",
}
MACRO_ORDEM = ["Clínica Médica", "Cirurgia", "GO", "Pediatria", "Preventiva"]
MACRO_NOME = {"Clínica Médica": "Clínica Médica", "Cirurgia": "Cirurgia",
              "GO": "G.O.", "Pediatria": "Pediatria", "Preventiva": "Preventiva"}


# --------------------------------------------------------------------------
# 2. Cadeia de habilidades: etapa cognitiva + elo quebrado
# --------------------------------------------------------------------------
ETAPAS = [
    ("quadro",      "Reconhecer o quadro",   "Fechar a sindrome a partir da vinheta."),
    ("dado",        "Ler o dado",            "Extrair o que o exame, o lab ou a imagem realmente diz."),
    ("discriminar", "Discriminar",           "Usar o achado que separa -- ou que EXCLUI o diagnostico vizinho."),
    ("regua",       "Aplicar a regua",       "Consultar o criterio objetivo: escore, cutoff, classificacao."),
    ("fato",        "Saber o fato",          "Recall puro: o conteudo estava ou nao estava na memoria."),
    ("conduta",     "Decidir a conduta",     "Escolher o tratamento, o exame ou o encaminhamento."),
    ("ordem",       "Ordenar e priorizar",   "Colocar os passos certos na sequencia certa."),
]
ETAPA_NOME = {k: n for k, n, _ in ETAPAS}
ETAPA_DESC = {k: d for k, _, d in ETAPAS}

REGRAS = [
    ("discriminar", r"\bexclui|excluir|exclus|descarta|afasta|diferenciar|diferencia\b|distinguir|"
                    r"nao confundir|separar a|separar o| versus | vs\.? |diferencial"),
    ("ordem",       r"\bordenar|ordem |sequencia|cronolog|priorizar|prioridade|antes de|primeiro passo|"
                    r"hierarquia|so depois|nessa ordem|antes do|antes da"),
    ("regua",       r"\bclassificar|classifica|escore|score|criterio|criterios|cut ?off|estadiar|"
                    r"estadiamento|pontuar|somar|calcular|graduar|estratificar|aplicar o|aplicar a |"
                    r"aplicar os|rotular|escala|regua|mnemonico|faixa"),
    ("dado",        r"\bler |leitura|interpretar|interpreta|medir|mensurar|radiograf|tomograf|"
                    r"ultrassom|eletrocardio|gasometria|exame fisico|otoscopia"),
    ("conduta",     r"\bconduta|conduzir|escolher|indicar|indicacao|tratar|tratamento|prescrev|"
                    r"solicitar|pedir |manejo|abordagem|decidir|encaminhar|agir|reservar|"
                    r"suspender|manter|iniciar|completar|recoletar|repetir"),
    ("quadro",      r"\breconhecer|identificar|diagnosticar|suspeitar|localizar|perceber|caracterizar|"
                    r"confirmar"),
    ("fato",        r"\bsaber|conhecer|lembrar|associar|memoriz|incorporar|dominar|recuperar|"
                    r"valorizar|deduzir|concluir|traduzir"),
]


def tipo_bloco(txt):
    t = _asc(txt)
    for k, rx in REGRAS:
        if re.search(rx, t):
            return k
    return "fato"


def _asc(s):
    return unicodedata.normalize("NFKD", (s or "")).encode("ascii", "ignore").decode().lower()


def split_cadeia(txt):
    """Quebra a cadeia em '->' de topo -- ignora setas dentro de parenteses."""
    out, buf, depth = [], [], 0
    i, n = 0, len(txt or "")
    while i < n:
        c = txt[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth = max(0, depth - 1)
        if depth == 0 and txt.startswith("->", i):
            out.append("".join(buf).strip())
            buf = []
            i += 2
            continue
        buf.append(c)
        i += 1
    out.append("".join(buf).strip())
    return [b for b in out if b]


STOP = set("""para com que como uma pelo pela dos das nos nas por sem sob ate mais menos deve devem
ser esta este essa esse aquele isso quando onde qual quais nao sim seus suas dele dela entre sobre
apos antes cada todo toda todos todas ainda outro outra mesmo mesma pelos pelas""".split())


def toks(s):
    return set(w for w in re.findall(r"[a-z]{4,}", _asc(s)) if w not in STOP)


def _cob(alvo, base):
    return len(alvo & base) / len(alvo) if alvo else 0.0


def _jac(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


MEC_PREF = {
    "exclui": "discriminar", "escore": "regua", "comporta": "regua", "contexto": "fato",
    "lacuna": "fato", "inversao": "fato", "categoria": "discriminar", "negativo": "discriminar",
    "par": "ordem", "degrau-anterior": "conduta", "desatualizada": "fato",
}


def analisa_cadeia(rec, mec, cur):
    """Devolve a cadeia com etapa cognitiva e semaforo por bloco."""
    blocos = split_cadeia(rec["habilidades_sequenciais"] or "")
    if not blocos:
        return [], None
    sid = str(rec["id"])
    ovr_t = cur.get("tipo_bloco", {}).get(sid, {})
    falt, arm, tp = toks(rec["o_que_faltou"]), toks(rec["armadilha_prova"]), toks(rec["tipo_erro"])
    pref = MEC_PREF.get(mec)
    out = []
    for i, b in enumerate(blocos):
        tb = toks(b)
        t = ovr_t.get(str(i)) or tipo_bloco(b)
        s = _cob(tb, falt) * 3.0 + _jac(tb, falt) * 2.0 + _cob(tb, arm) * 1.0 + _jac(tb, tp) * 0.5
        if pref and t == pref:
            s += 0.45
        # vies posicional reforcado (s147): a cobertura lexical falseia positivo em blocos
        # curtos (1 palavra em comum ja da cobertura alta) e tendia a marcar a quebra num
        # degrau anterior bem executado em vez do ultimo de fato tentado -- feedback do
        # usuario ("confundindo a quebra com o ultimo passo executado"). 0.12 -> 0.38 muda
        # o desempate sem apagar um sinal lexical realmente forte (score>=1.0).
        s += 0.38 * (i / max(1, len(blocos) - 1))
        out.append({"i": i, "txt": reacc(b), "tipo": t, "_s": s})

    quebrado = cur.get("elo_quebrado", {}).get(sid)
    quebrado = int(quebrado) if quebrado is not None else max(out, key=lambda x: x["_s"])["i"]
    quebrado = min(quebrado, len(out) - 1)
    for x in out:
        x["st"] = "quebrado" if x["i"] == quebrado else ("ok" if x["i"] < quebrado else "aberto")
        del x["_s"]
    return out, quebrado


def termos_zona(frase, alvo):
    """Palavras de conteudo da frase que tambem estao no vocabulario-alvo (gap+falt) --
    cobre o discriminador quando ele nao e numero nem gatilho de negacao (o KEYRX do
    cliente so pega esses dois; um achado nominal como 'ventriculomegalia' ou 'irritacao
    peritoneal' passava batido)."""
    return list(dict.fromkeys(w for w in re.findall(r"[A-Za-zÀ-ÿ]{4,}", frase) if _asc(w) in alvo))


def zonas_destaque(enun, gap, falt):
    """Restringe o destaque de dados-chave na vinheta a(s) frase(s) que de fato carregam
    o discriminador -- em vez do KEYRX cego rodando no texto inteiro e marcando qualquer
    numero/negacao, relevante ou nao para ESSA questao (framing errado -- feedback do
    usuario s148: "faltam dados discriminantes... enquanto dados nao-relevantes estao
    destacados"; o highlight servia pra achar numero, nao pra achar o que decide).

    Reusa a mesma maquina de sobreposicao lexical (toks/_cob/_jac) que ja localiza o elo
    quebrado em analisa_cadeia, agora contra o vocabulario de gap+falt (a descricao ja
    curada do que decide a questao, escrita durante /analisar-questao). Devolve
    [{"z":[ini,fim], "t":[termos]}, ...] em coordenadas de caractere sobre `enun`, em
    ordem de aparicao no texto; sem zona = sem destaque (silencio > ruido, mesmo criterio
    da CSS hardening anterior).
    """
    alvo = toks(gap) | toks(falt)
    if not alvo or not enun:
        return []
    frases = [f for f in _FIM.split(enun) if f.strip()]
    if not frases:
        return []
    scored = sorted(((_cob(alvo, toks(f)) * 2.0 + _jac(alvo, toks(f)), f) for f in frases),
                     key=lambda x: -x[0])
    if scored[0][0] <= 0:
        return []
    corte = scored[0][0] * 0.6
    out = []
    for s, f in scored:
        if s < corte or len(out) >= 2:
            break
        i = enun.find(f)
        if i == -1:
            continue
        out.append({"z": [i, i + len(f)], "t": termos_zona(f, alvo)})
    out.sort(key=lambda z: z["z"][0])
    return out


# --------------------------------------------------------------------------
# 3. Comando da questao
# --------------------------------------------------------------------------
_FIM = re.compile(r"(?<=[.!?])\s+")

# marcadores de comando: o que distingue a frase que PERGUNTA da frase que descreve
_CMD_RX = re.compile(
    r"assinale|marque|indique|julgue|analise|considerando|com base|baseado|acerca|"
    r"diante d[aeo]|\bqual\b|\bquais\b|o que |conduta|alternativa|hipotese|"
    r"exame mais|proximo passo|correto afirmar|incorreto|verdadeir|\bfalsa\b|recomenda|"
    r"deve[:.]?$|esta[:.]?$|\be[:.]?$|\bsao\b", re.I)

# "e" isolado so vira "é" onde o portugues nao admite a conjuncao: depois de
# interrogativo, ou nas formulas fixas de comando de prova. Qualquer padrao em
# que a conjuncao caiba fica de fora -- foi essa ambiguidade que produziu os 30
# enunciados corrompidos da versao anterior.
_VERBO = [
    (re.compile(r"\b(qual|o que|como|quando|onde|quem|isso|este|esse|aquele)\s+e\b", re.I),
     lambda m: m.group(1) + " é"),
    (re.compile(r"\be\s+(correto|incorreto|verdadeiro|falso)\s+afirmar\b", re.I),
     lambda m: "é " + m.group(1) + " afirmar"),
]


def reacc_verbo(txt):
    """Reacentua o verbo 'e'->'é' apenas em contextos sintaticamente inequivocos."""
    for rx, rep in _VERBO:
        txt = rx.sub(rep, txt or "")
    return txt


def separa_comando(enun):
    """Isola a pergunta final da vinheta. Devolve (contexto, comando, achado?)."""
    if not enun:
        return "", "", False
    e = enun.strip()
    frases = [f for f in _FIM.split(e) if f.strip()]
    if not frases:
        return e, "", False

    # 1. ultima frase interrogativa -- o caso limpo
    if "?" in e:
        corte = e.rfind("?")
        cabeca = e[:corte + 1]
        pontos = [m.end() for m in _FIM.finditer(cabeca[:-1])]
        ini = pontos[-1] if pontos else 0
        return e[:ini].strip(), e[ini:corte + 1].strip(), True

    # 2. comando sem "?": quase sempre a ultima frase, terminada em ":" ou imperativa
    ult = frases[-1].strip()
    if 12 <= len(ult) <= 400 and _CMD_RX.search(_asc(ult)):
        ctx = e[:e.rfind(ult)].strip()
        return ctx, ult, True
    return e, "", False


# --------------------------------------------------------------------------
# 4. Flashcards + FSRS
# --------------------------------------------------------------------------
def _dias(ts, hoje):
    if not ts:
        return None
    s = str(ts).split(".")[0]
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return (hoje - datetime.strptime(s, f).date()).days
        except ValueError:
            continue
    return None


ESTADO_FSRS = {0: "novo", 1: "aprendendo", 2: "revisao", 3: "reaprendendo"}


def liga_card_ao_bloco(card, cadeia, quebrado):
    """Mapeia o card ao degrau da cadeia que ele reforca (lexical + vies pelo tipo)."""
    if not cadeia:
        return None, 0.0
    alvo = toks(" ".join(filter(None, [card["frente_pergunta"], card["verso_resposta"],
                                       card["verso_regra_mestre"]])))
    melhor, score = None, 0.0
    for b in cadeia:
        s = _jac(toks(b["txt"]), alvo) + _cob(toks(b["txt"]), alvo) * 0.8
        if card["tipo"] in ("elo_quebrado", "armadilha") and b["i"] == quebrado:
            s += 0.20
        if s > score:
            melhor, score = b["i"], s
    return (melhor, round(score, 3)) if score >= 0.16 else (None, round(score, 3))


# --------------------------------------------------------------------------
# 5. Simulado 2 -- texto verbatim do PDF
# --------------------------------------------------------------------------
def parse_s2():
    if os.path.exists(CACHE_S2):
        return json.load(open(CACHE_S2, encoding="utf-8"))
    pdfs = [os.path.join(ROOT, f"Simulado 2 - pt{p}.pdf") for p in range(1, 6)]
    if not all(os.path.exists(p) for p in pdfs):
        return []
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader
    raw = []
    for p in pdfs:
        for pg in PdfReader(p).pages:
            raw.append(pg.extract_text() or "")
    raw = re.sub("[\uE000-\uF8FF]", "", "\n".join(raw))  # glifos de icone do PDF
    lines = []
    for ln in raw.split("\n"):
        s = ln.strip()
        if (not s or s.startswith("https://") or re.match(r"^\d{2}/\d{2}/\d{4},? \d{2}:\d{2}", s)
                or re.match(r"^\d+/\d+$", s) or re.match(r"^Pág\. \d+ de \d+$", s)
                or s.startswith("LISTA 1o Simulado")
                or s in ("Responder", "Estratégia Questões", "Exibir:", "Organizar:Opções",
                         "Mostrar 20 por vez", "Ordenação padrão")):
            continue
        s = s.replace("Ver solução e comentários", "").replace("VER HISTÓRICO DE RESPOSTAS", "").strip()
        if s:
            lines.append(s)
    MARK = re.compile(r"^(\d{10})\s*(ERRADA|CERTA)\s*(\d+)%\s*ACERTARAM(.*)$")
    ALT = re.compile(r"^([A-E])(\d{1,3})%$")
    QN = re.compile(r"Questão\s*(\d+)\s*ESTRATÉGIA MED 2026")
    qs, cur, alt = [], None, None
    for s in lines:
        m = MARK.match(s)
        if m:
            if cur:
                qs.append(cur)
            n = QN.search(m.group(4))
            cur = {"qid": m.group(1), "status": m.group(2), "pct_turma": int(m.group(3)),
                   "num": int(n.group(1)) if n else None, "_e": [], "alts": []}
            alt = None
            tail = QN.sub("", m.group(4)).strip()
            if tail:
                cur["_e"].append(tail)
            continue
        if cur is None:
            continue
        n = QN.search(s)
        if n and cur["num"] is None:
            cur["num"] = int(n.group(1))
            s = QN.sub("", s).strip()
            if not s:
                continue
        a = ALT.match(s)
        if a:
            alt = {"letra": a.group(1), "pct": int(a.group(2)), "_t": []}
            cur["alts"].append(alt)
            continue
        (alt["_t"] if alt else cur["_e"]).append(s)
    if cur:
        qs.append(cur)
    for q in qs:
        q["enun"] = _limpa(" ".join(q.pop("_e")))
        for a in q["alts"]:
            a["txt"] = _limpa(" ".join(a.pop("_t")))
    os.makedirs(os.path.dirname(CACHE_S2), exist_ok=True)
    json.dump(qs, open(CACHE_S2, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return qs


RODAPE_RX = re.compile(
    r"\s*(?:Questão\s*\d+\s*ESTRATÉGIA MED 2026|ESTRATÉGIA MED 2026|LISTA 1o Simulado|"
    r"Exibir:|Organizar:|Mostrar \d+ por vez|Ordenação padrão|Responder)\b")


def _limpa(s):
    """Corta o rodape/cabecalho da plataforma que vaza no fim de um bloco de texto."""
    s = re.sub(r"\s+", " ", s or "").strip()
    m = RODAPE_RX.search(s)
    return (s[:m.start()] if m else s).strip()


def parse_s5():
    """Texto verbatim do Simulado 5, ja extraido e corrigido em tools/parse_simulado5_v2.py
    (bug de ordem 'Questao N' antes do MARK corrigido; Q20/Q100 confirmadas CERTA pelo
    usuario mas ausentes do PDF exportado -- nao entram aqui pois nao viram erro)."""
    if os.path.exists(CACHE_S5):
        return json.load(open(CACHE_S5, encoding="utf-8"))
    return []


def casa_s5(db_rows, qs):
    """Vinculo direto erro-do-db <-> questao do PDF do S5, por S5_ID_TO_NUM (conhecido)."""
    by_num = {q["num"]: q for q in qs}
    out = {}
    for r in db_rows:
        num = S5_ID_TO_NUM.get(r["id"])
        if num is not None and num in by_num:
            out[r["id"]] = by_num[num]
    return out


def casa_s2(db_rows, qs):
    """Bijecao erro-do-db <-> questao ERRADA do PDF por sobreposicao de alternativas."""
    err = [q for q in qs if q["status"] == "ERRADA"]
    if not err:
        return {}
    out = {}
    for r in db_rows:
        eo, eb, en = toks(r["alternativa_correta"]), toks(r["alternativa_marcada"]), toks(r["enunciado"])
        best, bs = None, 0.0
        for q in err:
            sa = max((_jac(eo, toks(a["txt"])) for a in q["alts"]), default=0)
            sb = max((_jac(eb, toks(a["txt"])) for a in q["alts"]), default=0)
            sc = sa * 2 + sb * 1.5 + _jac(en, toks(q["enun"])) * 3
            if sc > bs:
                best, bs = q, sc
        if best is not None and bs >= 1.0:
            out[r["id"]] = best
    return out


def marca_alternativas(q, ok_txt, bad_txt):
    """Rotula cada alternativa do PDF como gabarito / marcada / distrator.

    O gabarito e identificado primeiro pelo percentual: a plataforma reporta
    "N% ACERTARAM", entao a alternativa cujo percentual e N e a certa. A
    sobreposicao lexical so desempata. A marcada nunca colide com o gabarito.
    """
    to, tb = toks(ok_txt), toks(bad_txt)
    alts = [dict(a) for a in q["alts"]]
    if not alts:
        return alts
    lex_ok = {i: _jac(to, toks(a["txt"])) for i, a in enumerate(alts)}
    cand = [i for i, a in enumerate(alts) if a["pct"] == q["pct_turma"]]
    io = max(cand or range(len(alts)), key=lambda i: lex_ok[i])
    resto = [i for i in range(len(alts)) if i != io]
    ib = max(resto, key=lambda i: _jac(tb, toks(alts[i]["txt"]))) if resto else None
    for i, a in enumerate(alts):
        a["role"] = "ok" if i == io else ("bad" if i == ib else "")
        a.pop("_t", None)
    return alts


# --------------------------------------------------------------------------
# 6. Montagem
# --------------------------------------------------------------------------
def build(hoje=None):
    hoje = hoje or date.today()
    cur = json.load(open(CURADORIA, encoding="utf-8"))
    mecs = cur["mecanismo"]
    confs = cur["conf_mecanismo"]

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    ids = [i for s in SIMK for i in SIMS[s]["ids"]]
    q = ",".join(map(str, ids))
    rows = con.execute(f"select * from questoes_erros where id in ({q}) order by id").fetchall()

    cards_by_q = {}
    for c in con.execute(f"""select fl.*, fs.state, fs.due, fs.last_review, fs.reps, fs.lapses,
                                    fs.stability, t.area as t_area, t.tema as t_tema
                             from flashcards fl
                             left join fsrs_cards fs on fs.card_id = fl.id
                             left join taxonomia_cronograma t on t.id = fl.tema_id
                             where fl.questao_id in ({q}) order by fl.id"""):
        cards_by_q.setdefault(c["questao_id"], []).append(c)

    temas = {r["id"]: r for r in con.execute("select id, area, tema from taxonomia_cronograma")}

    s2 = parse_s2()
    s2rows = [r for r in rows if r["id"] in SIMS["S2"]["ids"]]
    s2map = casa_s2(s2rows, s2) if s2 else {}

    s5 = parse_s5()
    s5rows = [r for r in rows if r["id"] in SIMS["S5"]["ids"]]
    s5map = casa_s5(s5rows, s5) if s5 else {}

    recs = []
    for r in rows:
        eid = r["id"]
        sim = next(k for k in SIMK if eid in SIMS[k]["ids"])
        mec = mecs.get(str(eid), "lacuna")
        cadeia, quebrado = analisa_cadeia(r, mec, cur)
        tx = temas.get(r["tema_id"])
        area = AREA_FIX.get((tx["area"] if tx else ""), (tx["area"] if tx else "")) or "--"
        tema = reacc(tx["tema"] if tx else "")

        pq = s2map.get(eid) or s5map.get(eid)
        if pq:                                   # S2/S5: texto verbatim do PDF, ja acentuado
            enun_pdf = pq["enun"] or ""
            if len(enun_pdf) < 150:
                # "Texto de apoio" colapsado no export: a vinheta nao veio no PDF, mas
                # o usuario a colou manualmente no chat e ela foi persistida no registro.
                enun_db = reacc(re.sub(r"^S\d+ Q\d+ \(\d+% acertaram\)\.?\s*", "", r["enunciado"] or ""))
                if len(enun_db) > len(enun_pdf):
                    enun_pdf = enun_db
            ctx, cmd, achou = separa_comando(enun_pdf)
            enun, comando, cmd_src = ctx, cmd, ("prova" if achou else "ausente")
            alts = marca_alternativas(pq, r["alternativa_correta"], r["alternativa_marcada"])
            pct_turma, qnum = pq["pct_turma"], pq["num"]
            fonte = "prova"
        else:                                    # S3/S4: registro do ipub.db
            bruto = re.sub(r"^S\d+ Q\d+ \(\d+% acertaram\)\.?\s*", "", r["enunciado"] or "")
            ctx, cmd, achou = separa_comando(reacc(bruto))
            enun, comando, cmd_src = ctx, cmd, ("registro" if achou else "ausente")
            alts = []
            m = re.match(r"^S\d+ Q(\d+) \((\d+)% acertaram\)", r["enunciado"] or "")
            qnum = int(m.group(1)) if m else None
            pct_turma = int(m.group(2)) if m else None
            fonte = "registro"

        cds = []
        for c in cards_by_q.get(eid, []):
            bloco, _ = liga_card_ao_bloco(c, cadeia, quebrado)
            d_last = _dias(c["last_review"], hoje)
            d_due = _dias(c["due"], hoje)
            cds.append({
                "id": c["id"], "tipo": c["tipo"] or "conteudo", "bloco": bloco,
                "ctx": reacc(c["frente_contexto"]), "p": reacc(c["frente_pergunta"]),
                "r": reacc(c["verso_resposta"]), "reg": reacc(c["verso_regra_mestre"]),
                "arm": reacc(c["verso_armadilha"]),
                "st": ESTADO_FSRS.get(c["state"] if c["state"] is not None else 0, "novo"),
                "visto": d_last, "vence": (-d_due if d_due is not None else None),
                "reps": c["reps"] or 0, "lapses": c["lapses"] or 0,
                "stab": round(c["stability"] or 0, 1),
            })

        if not alts:                       # S3/S4: so o par conhecido, mesmo desenho
            alts = [{"letra": "", "pct": None, "role": "bad",
                     "txt": reacc(r["alternativa_marcada"] or "")},
                    {"letra": "", "pct": None, "role": "ok",
                     "txt": reacc(r["alternativa_correta"] or "")}]
            alts_parciais = True
        else:
            alts_parciais = False

        gap = cadeia[quebrado]["txt"] if cadeia else ""
        hl = zonas_destaque(enun, gap, r["o_que_faltou"] or "")

        recs.append({
            "id": eid, "sim": sim, "qnum": qnum, "mec": mec, "conf": confs.get(str(eid), "auto"),
            "area": area, "macro": MACRO.get(area, "Clínica Médica"),
            "gap": gap, "altp": alts_parciais,
            "tema": tema, "titulo": reacc(r["titulo"] or ""),
            "cx": r["complexidade"] or "Media", "fonte": fonte,
            "enun": enun, "hl": hl, "cmd": comando, "cmdsrc": cmd_src,
            "ok": reacc(r["alternativa_correta"] or ""), "bad": reacc(r["alternativa_marcada"] or ""),
            "alts": alts, "pct": pct_turma,
            "tipo": reacc(r["tipo_erro"] or ""), "falt": reacc(r["o_que_faltou"] or ""),
            "expl": reacc(r["explicacao_correta"] or ""), "arm": reacc(r["armadilha_prova"] or ""),
            "cad": cadeia, "quebrado": quebrado, "cards": cds,
        })
    con.close()

    etapas = [{"k": k, "n": n, "d": d} for k, n, d in ETAPAS]
    return {"erros": recs, "mec": cur["mecanismos_prosa"], "ordem": cur["ordem_mecanismos"],
            "macro_ordem": MACRO_ORDEM, "macro_nome": MACRO_NOME,
            "sims": {k: {kk: vv for kk, vv in v.items() if kk != "ids"} for k, v in SIMS.items()},
            "etapas": etapas, "hoje": hoje.isoformat()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.path.join(ROOT, "artifacts", "autopsia-simulados.html"))
    a = ap.parse_args()
    data = build()
    from tools.autopsia_template import TPL  # noqa: F401  (import tardio: template e so texto)
    html = TPL.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(html)
    q = sum(1 for e in data["erros"] if e["cmd"])
    c = sum(len(e["cards"]) for e in data["erros"])
    print(f"OK -> {a.out} | {len(html):,} bytes | {len(data['erros'])} erros | "
          f"{q} com comando | {c} cards")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ROOT)
    main()
