import json
import os
import requests
import re
from pathlib import Path
from datetime import datetime

# Caminho para o banco e para o cache
BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "ipub.db"
CACHE_PATH = BASE_DIR / "flashcards_cache.json"

SYSTEM_PROMPT = """Você é um especialista em criação de flashcards para residência médica (Método MedHub).
Sua tarefa é transformar o ELO QUEBRADO de um erro de questão em um flashcard de retenção ativa de ALTO NÍVEL.

REGRAS ABSOLUTAS:
1. A FRENTE deve ser uma pergunta cirúrgica que só pode ser respondida por quem domina o conceito que falhou.
2. A FRENTE NÃO deve recriar a questão original — ela testa o CONCEITO ISOLADO do elo.
3. A FRENTE deve ter contexto mínimo (máx 1-2 linhas) + pergunta direta (máx 2 linhas).
4. O VERSO deve ter: resposta direta (1-2 linhas) + regra mestre (1-2 linhas).
5. O VERSO não deve ter cadeia de raciocínio completa, gabarito comentado nem repetição do caso.
6. A REGRA MESTRE deve ser um "bijou" de conhecimento (curta, memorizável e prática).

Responda SOMENTE em JSON válido, sem markdown:
{
  "frente_contexto": "...",   // mini-contexto clínico (pode ser vazio "")
  "frente_pergunta": "...",   // pergunta cirúrgica sobre o elo
  "verso_resposta": "...",    // resposta direta
  "verso_regra_mestre": "...", // regra que previne o erro (Conceito de Ouro)
  "verso_armadilha": "..."    // armadilha do examinador (se houver, senão "")
}"""

def build_flashcard_via_llm(entry: dict) -> dict:
    """Chama Claude API para gerar frente/verso do flashcard a partir do elo."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY não configurada no ambiente.")

    user_content = f"""
ERRO #{entry.get('numero', '?')} — {entry.get('area', '')} › {entry.get('tema', '')}

ELO QUEBRADO / HABILIDADE: {entry.get('elo_quebrado', '')}
O QUE FALTOU: {entry.get('o_que_faltou', '')}
EXPLICAÇÃO CORRETA: {entry.get('explicacao_correta', '')}
ARMADILHA: {entry.get('armadilha', '')}
CASO CLÍNICO (base): {entry.get('caso', '')[:400]}

Gere o flashcard (JSON)."""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        },
        json={
            "model": "claude-3-5-sonnet-20240620",
            "max_tokens": 800,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_content}]
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Erro na API do Claude: {response.text}")

    data = response.json()
    raw = data["content"][0]["text"].strip()
    
    # Limpeza de markdown se necessário
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]
        
    card_data = json.loads(raw.strip())
    
    return {
        "id": f"{entry.get('id', '0')}_elo",
        "tipo": "elo_quebrado",
        "area": entry.get("area", ""),
        "tema": entry.get("tema", ""),
        "erro_origem": entry.get("id", 0),
        "frente_contexto": card_data.get("frente_contexto", ""),
        "frente_pergunta": card_data.get("frente_pergunta", ""),
        "verso_resposta": card_data.get("verso_resposta", ""),
        "verso_regra_mestre": card_data.get("verso_regra_mestre", ""),
        "verso_armadilha": card_data.get("verso_armadilha", ""),
    }

def load_or_generate_flashcards(entries: list[dict], force_regen: bool = False) -> list[dict]:
    """Carrega do cache ou gera via LLM."""
    cache = {}
    if CACHE_PATH.exists() and not force_regen:
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                cache = {str(c["erro_origem"]): c for c in json.load(f)}
        except:
            cache = {}
    
    flashcards = []
    newly_generated = False
    
    for entry in entries:
        entry_id = str(entry.get("id", ""))
        
        if entry_id in cache:
            flashcards.append(cache[entry_id])
        else:
            try:
                # Aqui o Agente Antigravity pode intervir se estiver rodando em ambiente local
                # sem API key, mas nesta implementação mantemos o código para o usuário.
                card = build_flashcard_via_llm(entry)
                flashcards.append(card)
                cache[entry_id] = card
                newly_generated = True
            except Exception as e:
                print(f"Erro ao gerar card para erro #{entry_id}: {e}")
                continue
    
    if newly_generated:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(list(cache.values()), f, ensure_ascii=False, indent=2)
            
    return flashcards
