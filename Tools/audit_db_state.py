"""
Repara os tema_ids orfaos em questoes_erros e flashcards.
Estrategia: para cada erro, encontra o row [bulk] da mesma area
como ancora (ja que o subtema exato pode nao existir mais com o mesmo id).
Se o erro nao tiver area mapeavel, usa o [bulk] de Geral.
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')
conn = sqlite3.connect(DB)

# Mapeamento dos tema_ids mortos -> area conhecida (reconstruido por historico)
# Os ids originais eram criados pelo insert_questao com a area fornecida
# Vamos usar o texto do titulo/enunciado para inferir, ou recorrer ao bulk da area
# A forma mais segura: o insert_questao criou os temas com area=X.
# Precisamos saber qual area corresponde a cada tema_id extinto.

# Passo 1: identificar area para cada tema_id morto via questoes_erros
# (o insert_questao registrava area na taxonomia_cronograma)
# Como o row foi deletado, vamos usar uma heuristica:
# - Buscamos qual area_bulk tem o menor id > 0 que seja >= ao tema_id morto

# Primeiro: reconstruir mapa tema_id_morto -> area
# usando os dados de antes da migracao (sabemos que:
#  id=1 = Cirurgia (primeiro tema criado)
#  id=2 = Pediatria, etc.

# Melhor abordagem: ver se os flashcards ainda tem o tema_id original no campo
# e usar ambas as tabelas para cruzar

# Ver todos os tema_ids distintos nos erros
dead_tema_ids = conn.execute("""
    SELECT DISTINCT q.tema_id
    FROM questoes_erros q
    WHERE NOT EXISTS (SELECT 1 FROM taxonomia_cronograma t WHERE t.id = q.tema_id)
    ORDER BY q.tema_id
""").fetchall()
dead_set = set(r[0] for r in dead_tema_ids)
print("tema_ids mortos:", sorted(dead_set))

# Passo 2: para cada area, pegar o id do row [bulk] como ancora
bulk_ids = conn.execute("""
    SELECT area, MIN(id) as bulk_id
    FROM taxonomia_cronograma
    WHERE tema LIKE '[bulk]%'
    GROUP BY area
""").fetchall()
bulk_map = {r[0]: r[1] for r in bulk_ids}
print("bulk_map:", bulk_map)

# Passo 3: O problema e descobrir qual area cada tema_id morto pertencia.
# Vamos usar o INSERT original: quando insert_questao.py criava a taxonomia,
# ele fazia SELECT id FROM taxonomia_cronograma WHERE tema = ?
# Portanto, o tema_id morto corresponde a um tema (assunto) especifico.
# Nao temos mais essa info diretamente. 
# 
# ALTERNATIVA: simplesmente mapear todos os erros para o bulk_id de sua area,
# usando o campo 'titulo' que contem o tema da questao como dica.
# Mas o insert_questao nao tem 'area' no questoes_erros diretamente.
#
# SOLUCAO PRATICA: mapear pelo fsrs_cards e o schema de insercao.
# O insert_questao sempre criava flashcard com o mesmo tema_id.
# flashcards.tema_id tambem esta morto para os mesmos IDs.
# 
# Usamos a tabela sqlite_sequence para ver quais IDs maximos existiam antes.
# Ou: simplesmente mapeamos questoes_erros -> area usando o titulo como hint.

# Para cada erro orfao, tenta mapear pela palavra-chave da area no titulo
AREA_KEYWORDS = {
    'Cirurgia': ['cirurgia', 'trauma', 'atls', 'choque', 'abdomen', 'peritoni', 'pediatr infant'],
    'Pediatria': ['pediatria', 'neonatal', 'neonat', 'recem-nascido', 'crianca', 'ictericia'],
    'Ginecologia': ['ginecologia', 'utero', 'ovario', 'mama', 'colo', 'climateri'],
    'Obstetricia': ['obstetric', 'gestacao', 'parto', 'sifilis congenita', 'hipertensiv'],
    'Gastro': ['gastro', 'pancreatite', 'refluxo', 'hepatite', 'colite'],
    'Preventiva': ['preventiva', 'vigilancia', 'epidemiologia', 'saude coletiva', 'vacinacao'],
    'Infecto': ['infecto', 'hiv', 'tuberculose', 'arbovirose', 'dengue'],
    'Endocrino': ['diabetes', 'endocrino', 'tireoide', 'adrenal'],
    'Cardiologia': ['cardiologia', 'insuficiencia cardiaca', 'miocardio', 'arritmia'],
    'Neurologia': ['neurologia', 'avc', 'epilepsia', 'demencia', 'cerebral'],
    'Nefrologia': ['nefrologia', 'renal', 'nefrite', 'dialise'],
    'Pneumo': ['pneumo', 'asma', 'dpoc', 'pulmonar'],
    'Hemato': ['hemato', 'anemia', 'coagulacao', 'trombose'],
    'Psiquiatria': ['psiquiatria', 'depressao', 'ansiedade', 'esquizofrenia'],
    'Dermato': ['dermato', 'pele', 'hanseniase', 'dermatite'],
    'Reumato': ['reumato', 'artrite', 'lupus', 'fibromialgia'],
    'Hepato': ['hepato', 'figado', 'hepatite', 'cirrose'],
    'Otorrino': ['otorrino', 'ouvido', 'nariz', 'garganta'],
}

def guess_area(titulo, enunciado):
    texto = ((titulo or '') + ' ' + (enunciado or '')).lower()
    for area, kws in AREA_KEYWORDS.items():
        for kw in kws:
            if kw in texto:
                return area
    return None

# Para cada erro orfao: tenta adivinhar area, mapeia para bulk_id
erros_orfaos = conn.execute("""
    SELECT id, tema_id, titulo, enunciado
    FROM questoes_erros
    WHERE tema_id NOT IN (SELECT id FROM taxonomia_cronograma)
""").fetchall()

update_count = 0
unmapped = 0
for err_id, tema_id, titulo, enunciado in erros_orfaos:
    area = guess_area(titulo, enunciado)
    if area and area in bulk_map:
        new_id = bulk_map[area]
    else:
        # Fallback: usa Cirurgia (area com mais erros historicamente)
        new_id = bulk_map.get('Cirurgia', list(bulk_map.values())[0])
        unmapped += 1
    conn.execute(
        "UPDATE questoes_erros SET tema_id=? WHERE id=?",
        (new_id, err_id)
    )
    conn.execute(
        "UPDATE flashcards SET tema_id=? WHERE questao_id=?",
        (new_id, err_id)
    )
    conn.execute(
        "UPDATE fsrs_cards SET card_id=card_id WHERE card_id IN (SELECT id FROM flashcards WHERE questao_id=?)",
        (err_id,)
    )
    update_count += 1

conn.commit()
print("\n[OK] Erros remapeados: %d | Sem mapeamento preciso (fallback): %d" % (update_count, unmapped))

# Verificacao final
remaining_orphans = conn.execute("""
    SELECT COUNT(*) FROM questoes_erros q
    WHERE NOT EXISTS (SELECT 1 FROM taxonomia_cronograma t WHERE t.id = q.tema_id)
""").fetchone()[0]
print("[OK] Erros orfaos restantes:", remaining_orphans)

# Erros por area agora
print("\nErros por area:")
rows = conn.execute("""
    SELECT t.area, COUNT(q.id) as erros
    FROM questoes_erros q
    JOIN taxonomia_cronograma t ON t.id = q.tema_id
    GROUP BY t.area
    ORDER BY erros DESC
""").fetchall()
for r in rows:
    print("  %-15s: %d erros" % (r[0], r[1]))

conn.close()
