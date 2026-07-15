# Session 120 — S13 conversacional (SUS/Imunizações/Colecistite) + pendências quentes

**Data:** 2026-07-12 a 2026-07-15 (sessão contínua, 4 dias)
**Ferramenta:** Claude Code (Opus 4.8)
**Continuidade:** Sessão 119 (drenagem FSRS)

---

## O que foi feito

**Pendências quentes + dormências (abertura):**
- Icterícia neonatal (dif 8): refresh D8 dos 5 discriminadores (direta/colestase, ABO×Rh pelo tipo materno, baixa ingesta×leite materno, AVB×hepatite banca-dep, IGIV só hemólise isoimune). `review_log 87`.
- Mini-drill de enunciado negativo (3 questões): lição do checksum (nº de F=1) → PLAYBOOK. **Depois SUSPENSO a pedido do usuário** (ver Decisões).
- Card 209 (paracoco) reforjado: circular ("por que RX imperativo") → discriminador aguda×crônica + mímico TB. card_version 4, FSRS preservado.
- Card urocultura na sepse neonatal (nuance, tema 115) — recall que falhou fresco.
- Intoxicações Exógenas (dormência, 17d, 86%): refresh comprimido (grid das 5 toxíndromes + antídotos + pegadinhas). `review_log 88`.

**S13 — três blocos aula → questões → análise:**
- **SUS I (D5):** 1ª aula saiu da memória e **cortou os Atributos da APS** (Starfield) — o usuário desconfiou e perguntou pelo PDF; corrigi ancorando no EMED. **Criado resumo gold** `Princípios e Diretrizes do SUS.md` (auto_check PASS). 22q/72,7%; 5 cards dos erros (811-815). `review_log 89`, D5 (usuario), tema_id 297.
- **Imunizações III (D8):** aula ancorada no escopo exato do Cronograma.pdf (tópicos 11-23) + apostila EMED. 25q/72% (4 questões desatualizadas descartadas); 7 cards (816-822). `review_log 90`. **Recalibrado D10** pós-análise (ver Decisões), tema_id 265.
- **Colecistite/Colangite (D10):** aula completa ancorada no resumo gold s116 (escada cístico→colecistostomia × colédoco→CPRE). 18q/83,3% (melhor bloco); 3 cards (823-825). `review_log 91`, D10 (usuario), tema_id 298 (tema nasceu).

## Padrões de erro identificados

- **SUS (6 erros):** cluster de **Atributos da APS** (Q1 coordenação=AB; Q3 desprescrição=coordenação×longitudinalidade; Q6 longitudinalidade exclusiva da APS) + discriminação de princípio (Q4 igualdade×universalidade; Q5 integralidade×equidade). Q2 = enunciado negativo genuíno (checksum).
- **Imunizações (7 erros):** 3 recall frescos do que foi ensinado na aula 2h antes (palivizumabe não interfere; antitérmico só MenB; influenza ≥6m) → **valida o D10**; 2 "fora da normalidade" (IGIV+Reye; pós-exposição vacina×VZIG); 1 pneumonia por faixa; Q3 = **lacuna de conteúdo** (mãe HIV+ pode receber sarampo), NÃO execução — correção do usuário.
- **Colecistite (3 erros):** Q1 = eixo central (colecistostomia [colecistite] × CPRE [colangite]) — drenou a estrutura errada; Q2 microbiologia (enterobactérias); Q3 critério de imagem TG18 (inflamação, não só cálculo).

## Artefatos criados/modificados

- **Novo:** `resumos/Preventiva/Princípios e Diretrizes do SUS.md` (gold, auto_check PASS).
- **Modificado:** `PLAYBOOK_EXECUCAO_PROVA.md` (checksum do enunciado negativo + reincidência SUS Q2).
- **Cards (ipub.db, local):** 811-825 (15 de erro) + urocultura (tema 115) + reforge 209.
- **review_log 87-91**; dificuldades: Icterícia/Sepse Neonatal=8 (aula), Intoxicações (refresh), SUS=5, Imunizações=10, Colecistite=10 (todas usuario nos temas S13).
- **Volume:** sessoes_bulk +65q (SUS 22 + Imuniza 25 + Colecistite 18); acumulado 5026.
- **Memórias:** `feedback_aula_base_ancorar_pdf_emed`, `feedback_imunizacoes_d10_onboarding`.

## Decisões tomadas

- **Ancorar aula-base no PDF do EMED SEMPRE** (não cortar PDFs da busca) — a aula de SUS de memória omitiu a seção de APS. Memória + regra.
- **Criar resumo de SUS** apesar do sprint question-first — instrução explícita do usuário supera o default.
- **Imunizações recalibrado D10** (usuario): dificuldade absoluta no "fora da normalidade"; **Imunizações - Revisão** deve ser onboarding D10 completo (não refresh).
- **Enunciado negativo SUSPENSO** como foco: o usuário mostrou que os erros eram de CONTEÚDO, não de estrutura da pergunta; o agente estava deixando o padrão blindar o mergulho clínico (reforça `feedback_analise_hard_soft_skill`).

## Próximos passos

- **Imunizações - Revisão (S13):** onboarding D10 completo, extremamente didático, foco em eventos adversos/intervalos/imunoglobulina/contraindicações.
- **Backfill do resumo de Imunizações:** gaps de Teoria III (Raiva pós-exposição, COVID, Dengue, Herpes-Zóster sem seção própria).
- **S13 restante:** Endometriose, Pré-Natal II, DII, Pneumo Intensiva II, Transtornos de Humor, Hepatologia/Icterícia (revisão), Arboviroses/Meningites/Sepse (revisão por questões), Sepse (revisão).
- **FSRS:** 22 atrasados + backlog 425 — drenar.
- **Cronograma:** db em S12 (Drive não sincronizado); posição real = S13 (usuário fechou S12). Rodar `--sync-drive` quando houver xlsx local.
