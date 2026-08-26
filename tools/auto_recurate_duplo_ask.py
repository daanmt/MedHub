import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

PROMPT_SISTEMA = """Você é um arquiteto de conhecimento médico especialista em Repetição Espaçada (FSRS).
Sua missão é fatiar flashcards que violam o Princípio da Informação Mínima (duplo-ask).

REGRAS:
1. Fatie o card original em 2 cards estritamente atômicos (Pai e Filho).
2. Cada card deve focar em UM único aspecto (ex: diagnóstico em um, conduta no outro).
3. Incorpore o contexto na própria pergunta.
4. Retorne APENAS um JSON válido com a seguinte estrutura de chaves:
{
  "frente_pai": "...",
  "verso_pai": "...",
  "frente_filho": "...",
  "verso_filho": "...",
  "regra_mestre_filho": "..."
}"""

def obter_alvos():
    res = subprocess.run([sys.executable, "-X", "utf8", "tools/audit_card_atomicity.py", "--json"], 
                         capture_output=True, text=True, encoding="utf-8")
    try:
        achados = json.loads(res.stdout)
        
        # Filtra os duplo-ask e pega IDs unicos
        alvos_dict = {}
        for a in achados:
            if "duplo-ask" in a["padrao"]:
                if a["id"] not in alvos_dict:
                    alvos_dict[a["id"]] = a
                    
        alvos = list(alvos_dict.values())
        
        # O audit json corta a string e nao traz o verso. 
        # Vamos ao DB buscar o texto real e completo:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for alvo in alvos:
            cursor.execute("SELECT frente_pergunta, verso_resposta FROM flashcards WHERE id = ?", (alvo["id"],))
            row = cursor.fetchone()
            if row:
                alvo["frente_pergunta"] = row[0]
                alvo["verso_resposta"] = row[1]
                
        conn.close()
        return alvos
    except Exception as e:
        print(f"Erro no obter_alvos: {e}")
        return []

def fatiar_com_gemini(alvo):
    prompt_user = f"ÁREA: {alvo.get('area', 'N/A')}\nTEMA: {alvo.get('tema', 'N/A')}\nFRENTE ORIGINAL: {alvo.get('frente_pergunta')}\nVERSO ORIGINAL: {alvo.get('verso_resposta')}"
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=PROMPT_SISTEMA,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )
    
    response = model.generate_content(prompt_user)
    return json.loads(response.text)

def aplicar_transacao(alvo, dados_fatiados):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        pai_id = alvo["id"]
        
        cursor.execute('''
            UPDATE flashcards 
            SET frente_pergunta = ?, verso_resposta = ?, needs_qualitative = 0 
            WHERE id = ?
        ''', (dados_fatiados["frente_pai"], dados_fatiados["verso_pai"], pai_id))
        
        cursor.execute("SELECT questao_id, tema_id, frente_contexto FROM flashcards WHERE id = ?", (pai_id,))
        meta = cursor.fetchone()
        if meta:
            q_id, t_id, ctx = meta
            cursor.execute('''
                INSERT INTO flashcards 
                (questao_id, tema_id, tipo, frente_contexto, frente_pergunta, verso_resposta, verso_regra_mestre, quality_source, needs_qualitative)
                VALUES (?, ?, 'FrontBack', ?, ?, ?, ?, 'qualitative', 0)
            ''', (q_id, t_id, ctx, dados_fatiados["frente_filho"], dados_fatiados["verso_filho"], dados_fatiados.get("regra_mestre_filho", "")))
            
            novo_id = cursor.lastrowid
            cursor.execute("INSERT INTO fsrs_cards (card_id, due) VALUES (?, ?)", (novo_id, datetime.now()))
            
            conn.commit()
            print(f"✅ Card {pai_id} fatiado! Novo filho: {novo_id}")
            return True
        else:
            print(f"⚠️ Metadados não encontrados para o Pai {pai_id}.")
    except Exception as e:
        print(f"❌ Erro SQL no card {alvo['id']}: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()
    return False

def main():
    alvos = obter_alvos()
    if not alvos:
        print("Nenhum 'duplo-ask' pendente encontrado!")
        return

    print(f"🚀 Iniciando Auto-Curadoria com Gemini para os duplo-ask...\n")
    sucessos = 0
    
    # Processando apenas os proximos 5 para manter pequenos lotes iterativos (Lote 3)
    alvos_lote = alvos[:5]
    
    for i, alvo in enumerate(alvos_lote):
        print(f"[{i+1}/{len(alvos_lote)}] Processando ID {alvo['id']} ({alvo['tema']})...")
        try:
            dados = fatiar_com_gemini(alvo)
            if aplicar_transacao(alvo, dados):
                sucessos += 1
        except Exception as e:
            print(f"❌ Falha no LLM/JSON para card {alvo['id']}: {e}")

    print(f"\n🎉 Operação Limpa-Banco concluída! {sucessos}/{len(alvos_lote)} fatiados com sucesso.")

if __name__ == "__main__":
    main()
