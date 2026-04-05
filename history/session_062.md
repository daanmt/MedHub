---
session: 062
date: 2026-04-05
agent: Antigravity
area: Pediatria
tema: Icterícia e Sepse Neonatal
questoes_analisadas: 3
erros_inseridos: 3
ids_sqlite: 345–347
---

# Sessão 062 — Análise de Sepse Neonatal (Pediatria)

## Resumo executivo

Sessão de análise de erros com foco em **Icterícia e Sepse Neonatal** (Pediatria). Processamento de 3 questões erradas, identificação de 3 lacunas clínicas distintas, inserção no SQLite e atualização cumulativa do resumo.

---

## Lacunas identificadas e integradas

### 1. Perfil discriminador da *Listeria monocytogenes*
- **Lacuna:** confusão entre GBS e *Listeria* como agentes de sepse precoce neonatal.
- **Lição:** A *Listeria* tem tríade exclusiva: **LA marrom-acastanhado** (corioamnionite grave) + **exantema pústulo-eritematoso ao nascimento** (antes de qualquer exposição nosocomial) + **monocitose acentuada** no hemograma.
- GBS: agente mais comum, mas jamais causa LA marrom, exantema cutâneo ao nascimento nem monocitose.
- Transmissão: transplacentária após intoxicação alimentar materna (mãe habitualmente assintomática).

### 2. Exceção SBP — taquipneia isolada nas primeiras 6h
- **Lacuna:** aplicação da regra geral "ATB empírico em qualquer suspeita" sem reconhecer a exceção de taquipneia isolada.
- **Lição:** RN com taquipneia como único sinal clínico < 6h de vida, sem deterioração sistêmica → **observação clínica + aguardar hemocultura**. PCR coletada às 6h tem valor preditivo limitado (eleva-se após 12–24h). ATB empírico apenas se evolução desfavorável ou hemocultura positiva.

### 3. Classificação da ampicilina
- **Lacuna:** não reconhecer a ampicilina como pertencente ao grupo das penicilinas (aminopenicilina).
- **Lição:** Ampicilina = aminopenicilina (penicilina de espectro ampliado). Importa para alergia cruzada e para entender o mecanismo de ação do esquema padrão de sepse neonatal precoce (ampicilina + gentamicina).

---

## Artefatos modificados

| Artefato | Modificação |
|---|---|
| `ipub.db` | 3 erros inseridos (IDs 345–347) via `tools/insert_questao.py` |
| `resumos/Pediatria/Icterícia e Sepse Neonatal.md` | +2 blocos clínicos (*Listeria* discriminador + exceção SBP) + 2 armadilhas cumulativas na seção "Armadilhas de Prova" |
| `ESTADO.md` | Entrada da sessão 062 adicionada em "Últimas sessões" |

---

## Estado ao fechar

- Banco: 347+ erros no `ipub.db`
- Resumo Sepse Neonatal: atualizado com padrão *Listeria* + exceção taquipneia
- Nenhum PDF pendente (Zero PDF cumprido)
- Próximo passo: continuar com bloco de questões ou novo tema clínico
