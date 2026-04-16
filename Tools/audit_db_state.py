import sqlite3, os
conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db'))

# Remove a linha duplicada (guarda id=21, remove id=22)
conn.execute("DELETE FROM sessoes_bulk WHERE id=22")

# Reverte o duplo incremento em taxonomia_cronograma
# O script foi chamado 2x: +88 feitas / +80 acertos. Deve ser +44 / +40.
# Portanto: subtrai 44 e 40 de volta.
conn.execute("""
    UPDATE taxonomia_cronograma
    SET questoes_realizadas = questoes_realizadas - 44,
        questoes_acertadas  = questoes_acertadas  - 40
    WHERE area = 'Cirurgia' AND tema LIKE '[bulk]%'
""")
# Recalcula percentual
conn.execute("""
    UPDATE taxonomia_cronograma
    SET percentual_acertos = CAST(questoes_acertadas AS REAL) / questoes_realizadas * 100
    WHERE area = 'Cirurgia' AND tema LIKE '[bulk]%' AND questoes_realizadas > 0
""")

conn.commit()

# Verificacao final
total = conn.execute("SELECT SUM(questoes_feitas), SUM(questoes_acertadas) FROM sessoes_bulk").fetchone()
print("TOTAL bulk: q=%d | a=%d" % (total[0], total[1]))
cir = conn.execute("SELECT SUM(questoes_feitas), SUM(questoes_acertadas) FROM sessoes_bulk WHERE area='Cirurgia'").fetchone()
print("Cirurgia: q=%d | a=%d" % (cir[0], cir[1]))
rows = conn.execute("SELECT id, sessao_num, questoes_feitas FROM sessoes_bulk WHERE area='Cirurgia'").fetchall()
print("Linhas Cirurgia:", rows)
conn.close()
print("[OK] Correcao concluida. Total esperado: 3064")
