# Estilo MedHub — Spec de Formatação para Resumos

> Este documento define o padrão de formatação para todos os resumos em `Temas/`.
> Qualquer agente que criar ou editar resumos DEVE seguir estas regras.

---

## Estrutura Geral

- Título: `# Nome do Tema` (H1, sem metadata de fonte/autor)
- Seções: `## 1. Nome da Seção` (H2 numerado)
- Subseções: `### 1.1 Nome` (H3)
- Sub-sub: `**Título em negrito:**` seguido de bullets

---

## Formatação de Conteúdo

### Usar SEMPRE
- **Bullets hierárquicos** com `-` para organizar informações
- **Negrito** para termos-chave, nomes de drogas, diagnósticos
- `⭐` para conceitos fundamentais que não podem ser esquecidos
- `⚠️ Padrão de prova:` para armadilhas de examinador e nuances
- `🔴` para armadilhas na seção final "Armadilhas de Prova"
- Blocos `>` (blockquote) para destaques e alertas importantes
- Separadores `---` entre seções principais

### NUNCA usar
- **Tabelas** — em qualquer tamanho ou formato. Sempre converter para bullets hierárquicos. Sem exceções.
- Fluxogramas ou algoritmos em ASCII (blocos ` ``` `) — converter para bullets hierárquicos com condicionais em texto (`→ se X:`, `→ se não:`)
- Headers de metadata no topo (fonte, autor, ano, versão)
- Linguagem motivacional ou didática ("Vamos lá!", "Caro aluno")
- Emojis decorativos (apenas ⭐, ⚠️, 🔴 com função semântica)
- **Referências a questões de prova dentro do texto** — nunca escrever "Foco do erro na Q1", "Q2 na prova", "Questão 3 abordou...", etc. O conteúdo aprendido com questões deve ser incorporado de forma natural ao tema, como se sempre tivesse feito parte do resumo. O resumo é um documento técnico de referência, não um caderno de erros.

---

## Tom

- Direto e técnico. O leitor é médico.
- Frases curtas. Informação densa.
- Priorizar o raciocínio clínico sobre a memorização pura.
- Toda informação deve servir para resolver questões de prova.

---

## Seção Final Obrigatória

Todo resumo DEVE terminar com:

```
## N. Armadilhas de Prova

- 🔴 [armadilha 1]
- 🔴 [armadilha 2]
...
```

Esta seção consolida todos os `⚠️ Padrão de prova` espalhados pelo resumo + armadilhas adicionais do `caderno_erros.md`.

---

## Referências de Estilo (exemplos reais)

- `Temas/Cirurgia/Trauma.md` — formatação de referência para trauma
- `Temas/Clínica Médica/Cardiologia/Insuficiência Cardíaca.md` — formatação de referência para clínica
- `Temas/GO/[OBS] Sangramentos da Primeira Metade.md` — formatação de referência para GO
