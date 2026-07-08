# Session 112 -- DM Complicações Crônicas: 58q/51a (87,9%) + 7 erros -> 7 cards (762-768)

**Data:** 2026-07-07
**Ferramenta:** Claude Code (Sonnet 5)
**Continuidade:** Sessão 111 (fecha s110 parte 2)

---

## O que foi feito

**Bloco único (operador exausto, só esta lista hoje):** revisão por questões de Diabetes Mellitus - Complicações Crônicas (S12, task 8/13 do cronograma). 58q/51a (87,9%), o melhor resultado percentual das últimas sessões. Volume registrado via `registrar_sessao_bulk.py --sessao 112 --area Endocrino`.

**Análise dos 7 erros (`/analisar-questao`, protocolo de habilidades sequenciais):**
- **Q1/Q4 -- enunciado negativo (2x no mesmo bloco):** "mostra-se INADEQUADO"/"conceito inadequado" -- marcou a alternativa VERDADEIRA como se fosse a falsa. Q1: PND somática é sensitivo-motora, não "apenas" sensitiva (a palavra "apenas" era o restritor inválido). Q4: diabético mal controlado tem glicose salivar aumentada (fato tangencial, odontológico).
- **Q3 -- via dos poliois:** acúmulo de sorbitol é intracelular, não extracelular; alternativas B/D quase idênticas (só a preposição muda) -- duvidou de "glicação de proteínas" (AGEs, mecanismo real) em vez de pegar a inversão dentro/fora.
- **Q2 -- pé diabético, infecção leve:** classificação de gravidade (leve/limitada à pele, sem sinais sistêmicos) define curativo tópico + reavaliação antes de escalar para ATB sistêmico -- exsudato purulento/odor "pareciam graves" e empurraram para ATB sistêmico de largada. Flag banca-dependente (IDSA classicamente já indica oral mesmo em leve).
- **Q5 -- tricíclicos:** contraindicação é restrita à neuropatia autonômica CARDIOVASCULAR (arritmia/QT/hipotensão ortostática), não à categoria "autonômica" inteira -- generalizou o escopo na asserção-porque.
- **Q6 -- pé de Charcot:** denervação autonômica causa VASODILATAÇÃO (não vasoconstrição) em microvasos, por perda do tônus simpático -- inversão intuitiva (57% da turma errou na mesma direção). Conteúdo novo no resumo (não existia).
- **Q7 -- DM pós-ICP:** diretriz SBC/SBHCI 2017 -- terapêuticas de controle NÃO reduzem efetivamente óbito/eventos no diabético revascularizado (fato contraintuitivo, citação literal; 72% da turma errou pro lado "otimista"). Conteúdo novo no resumo.

**Padrão vivo confirmado:** enunciado negativo (Q1+Q4) segue reincidindo dentro do mesmo bloco -- 3ª sessão consecutiva com esse padrão (s110 Pré-Natal Q1+Q3, agora DM Q1+Q4).

## Artefatos criados/modificados

- `resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Crônicas.md` -- nova seção 5.5 (Neuroartropatia de Charcot), fato de diretriz SBC/SBHCI em §6, ressalva de tricíclicos em §4.6, 6 novas armadilhas em §8 + 3 bullets inline (§1.1, §4.4, §5.4).
- `ipub.db` -- +58q/51a (sessão 112, Endocrino); +7 erros -> 7 cards (762-768), todos ancorados no elo. Local-only.

## Próximos passos

1. FSRS: 0 atrasados + 3 hoje, backlog 386 novos.
2. Próximo bloco de conteúdo (S12): Medicina de Família e Comunidade (extensivo, recomendado pelo day_plan) -- cards de erro frescos puxando reincidência. Fila seguinte: Apendicite Aguda, HAS Pt.2, Distúrbios do Potássio, Cefaleias+Epilepsias.
3. Slot de simulado previsto ainda em S12 (ciclo de 4 semanas).
