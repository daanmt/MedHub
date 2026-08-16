# -*- coding: utf-8 -*-
"""Decide, em contexto, se um 'e' isolado e a conjuncao ou o verbo 'é'.

Regras de ALTA PRECISAO apenas: na duvida, deixa a conjuncao (falso-negativo
custa um acento faltando; falso-positivo custa o bug que o usuario reportou).
Validado contra resumos/**/*.md, que tem os acentos corretos.
"""
import re

# adjetivos/participios que so aparecem como predicativo -> antes deles, "e" e verbo
PRED = (r"obrigatori[oa]|indicad[oa]|contraindicad[oa]|necessari[oa]|suficiente|possivel|"
        r"impossivel|important|fundamental|essencial|classic[oa]|tipic[oa]|atipic[oa]|"
        r"exclusiv[oa]|definid[oa]|considerad[oa]|caracterizad[oa]|feit[oa]|realizad[oa]|"
        r"compost[oa]|formad[oa]|causad[oa]|provocad[oa]|associad[oa]|marcad[oa]|"
        r"raro|rara|comum|frequente|incomum|benign[oa]|malign[oa]|segur[oa]|"
        r"prefer[ie]ncial|mandatori[oa]|opcional|desnecessari[oa]|util|inutil|"
        r"proporcional|inversamente|diretamente|igual|diferente|semelhante|"
        r"compativel|incompativel|sugestiv[oa]|patognomonic[oa]|especific[oa]|sensivel|"
        r"maior|menor|melhor|pior|preferivel|aceitavel|inaceitavel|adequad[oa]|"
        r"inadequad[oa]|correto|incorreto|verdadeir[oa]|fals[oa]|normal|anormal|"
        r"transitori[oa]|permanente|reversivel|irreversivel|autolimitad[oa]|"
        r"letal|fatal|grave|leve|moderad[oa]|agud[oa]|cronic[oa]|precoce|tardi[oa]")

REGRAS = [
    # 1. interrogativo + e
    (re.compile(r"\b(qual|quais|o que|como|quando|onde|quem|quanto|quanta)\s+e\b", re.I),
     lambda m: m.group(1) + " é"),
    # 2. pronome/demonstrativo + e
    (re.compile(r"\b(isso|isto|aquilo|este|esta|esse|essa|aquele|aquela|ele|ela|"
                r"o qual|a qual|que)\s+e\b", re.I),
     lambda m: m.group(1) + " é"),
    # 3. negacao + e (excluindo o par correlativo "nao e ... sim")
    (re.compile(r"\bnao\s+e\b(?!\s+sim\b)", re.I),
     lambda m: m.group(0)[:-1] + "é"),
    # 4. e + superlativo (o mais / a melhor / o unico ...)
    (re.compile(r"\be\s+(?=(?:o|a|os|as)\s+(?:mais|menos|melhor|pior|unic[oa]|primeir[oa]|"
                r"ultim[oa]|maior|menor|padrao)\b)", re.I),
     lambda m: "é "),
    # 5. e + predicativo adjetival
    (re.compile(r"\be\s+(?=(?:" + PRED + r")\b)", re.I),
     lambda m: "é "),
    # 6. e + "um/uma" + substantivo (predicativo nominal): "e uma emergencia"
    (re.compile(r"\be\s+(?=(?:um|uma)\s+[a-zà-ÿ]{3,})", re.I),
     lambda m: "é "),
    # 7. e + preposicao de definicao: "e de escolha", "e por", "e para"
    (re.compile(r"\be\s+(?=de\s+(?:escolha|eleicao|primeira|segunda|rotina|exclusao)\b)", re.I),
     lambda m: "é "),
    # 8. inicio de oracao apos ponto-e-virgula/travessao + e
    (re.compile(r"(--|;)\s+e\s+(?=(?:" + PRED + r")\b)", re.I),
     lambda m: m.group(1) + " é "),
]


def corrige(txt):
    if not txt:
        return txt
    for rx, rep in REGRAS:
        txt = rx.sub(rep, txt)
    return txt
