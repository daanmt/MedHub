# Plano de Implementação — Streamlit UI para IPUB

> **Destinatário:** Antigravity (implementação local)  
> **Projeto:** [github.com/daanmt/MedHub](https://github.com/daanmt/MedHub)  
> **Objetivo:** Interface gráfica local para o sistema de estudos de residência médica IPUB/UFRJ — navegação, edição e visualização dos arquivos `.md` do projeto sem necessidade de CLI ou editor de texto.

---

## 1. Visão Geral da Arquitetura

```
IPUB/
├── app/                        ← NOVO: pasta raiz do Streamlit
│   ├── streamlit_app.py        ← entry point (st.navigation ou multipage)
│   ├── pages/
│   │   ├── 01_dashboard.py
│   │   ├── 02_caderno_erros.py
│   │   ├── 03_resumos.py
│   │   ├── 04_progresso.py
│   │   └── 05_historico.py
│   ├── components/
│   │   ├── md_editor.py        ← editor/viewer de markdown reutilizável
│   │   ├── error_card.py       ← card de entrada de erro
│   │   └── sidebar.py          ← sidebar com estado global
│   └── utils/
│       ├── parser.py           ← parsing de caderno_erros.md e progresso.md
│       └── file_io.py          ← leitura/escrita segura de arquivos .md
├── .streamlit/
│   └── config.toml             ← tema, porta, etc.
└── requirements_streamlit.txt  ← dependências isoladas do app
```

> A pasta `app/` fica dentro do repositório existente, sem alterar nenhum arquivo atual.

---

## 2. Páginas e Funcionalidades

### 2.1 🏠 Dashboard (`01_dashboard.py`)

**Propósito:** visão consolidada do estado atual de estudo.

**Componentes:**
- **Métricas rápidas** (`st.metric`) lidas de `caderno_erros.md`:
  - Total de erros registrados
  - Erros por área (barra horizontal com `st.bar_chart`)
  - Distribuição por tipo de erro (pizza via `plotly.express`)
- **Último estado** (`ESTADO.md`): renderizado como markdown em `st.expander`
- **Resumo de progresso** (`progresso.md`): seções colapsáveis por área
- **Sessões recentes**: lista as últimas 5 entradas em `history/`, com data e preview

**Leitura de dados:**
```python
# utils/parser.py
def get_error_stats(path="caderno_erros.md") -> dict:
    # parse entradas numeradas: "## Erro N" ou "### N."
    # retorna {total, por_area, por_tipo}
```

---

### 2.2 📖 Caderno de Erros (`02_caderno_erros.py`)

**Propósito:** principal interface de uso — visualizar, filtrar e registrar erros.

**Layout:** duas colunas (filtros | lista de erros)

**Funcionalidades:**
- **Filtros laterais** (`st.sidebar`):
  - Área (`st.multiselect`): Cirurgia, Clínica Médica, GO, Pediatria, Preventiva
  - Tipo de erro (`st.multiselect`): raciocínio, conceitual, atenção, etc.
  - Busca por texto (`st.text_input`)
  - Ordenar por: data, área, relevância
- **Lista de erros:** cada entrada renderizada como `st.expander` com:
  - Cabeçalho: número + área + tag de tipo
  - Corpo: questão, raciocínio errado, raciocínio correto, insight
  - Botão **Editar** → abre modal/formulário inline
- **Botão "+ Novo Erro"** no topo → formulário `st.form`:
  - Campos: Área, Tipo, Questão, Raciocínio errado, Correto, Insight, Tags
  - Submit → append no `caderno_erros.md` preservando formato existente

**Formato de entrada em `caderno_erros.md`** (o parser deve suportar):
```markdown
## Erro 37
**Área:** Clínica Médica  
**Tipo:** Raciocínio  
**Questão:** ...  
**Errado:** ...  
**Correto:** ...  
**Insight:** ...
```

---

### 2.3 📚 Resumos por Área (`03_resumos.py`)

**Propósito:** navegar e consultar os resumos clínicos em `Temas/`.

**Layout:** sidebar de navegação + área de conteúdo

**Funcionalidades:**
- **Árvore de navegação** na sidebar:
  - Nível 1: Cirurgia, Clínica Médica, GO, Pediatria, Preventiva
  - Nível 2: subespecialidades (subpastas detectadas automaticamente via `os.walk`)
  - Nível 3: arquivos `.md` individuais
  - Implementar como `st.radio` aninhado ou `st.selectbox` hierárquico
- **Visualizador de conteúdo:**
  - `st.markdown` para renderização com suporte a tabelas e listas
  - Toggle **"Modo Edição"** → substitui por `st.text_area` com o conteúdo raw
  - Botão **Salvar** no modo edição → escreve de volta no arquivo
  - Botão **Novo Resumo** → cria novo `.md` na pasta selecionada com template padrão
- **Busca global** (`st.text_input` no topo): varre todos os `.md` em `Temas/` por substring

**Template de novo resumo:**
```markdown
# [Título]

## Definição

## Critérios Diagnósticos

## Tratamento

## Pontos de Prova
```

---

### 2.4 📈 Progresso (`04_progresso.py`)

**Propósito:** visualização analítica do progresso de estudos.

**Componentes:**
- **Parse de `progresso.md`**: extrair tabelas e seções por área
- **Gráfico de barras agrupado** (plotly): acertos × erros por área
- **Heatmap de sessões** (plotly `imshow` ou calendar heatmap): frequência por dia de estudo lida dos arquivos em `history/`
- **Tabela interativa** (`st.dataframe`): erros com colunas filtráveis
- **Linha do tempo** de sessões de estudo: datas dos arquivos em `history/`

**Parser de `history/`:**
```python
def parse_sessions(history_dir="history/") -> pd.DataFrame:
    # lê cada .md em history/, extrai data do nome do arquivo ou front-matter
    # retorna DataFrame com colunas: data, temas, n_questoes, erros
```

---

### 2.5 🗓️ Histórico de Sessões (`05_historico.py`)

**Propósito:** log de sessões de estudo para revisão.

**Funcionalidades:**
- Lista de sessões em `history/` ordenadas por data (mais recente primeiro)
- Cada sessão como `st.expander` com conteúdo markdown renderizado
- Filtro por data (`st.date_input` range)
- Botão **"+ Nova Sessão"** → abre formulário com campos:
  - Data, Temas estudados, N° de questões, Erros cometidos, Observações
  - Gera arquivo `history/YYYY-MM-DD_sessao.md` com o conteúdo formatado

---

## 3. Componentes Reutilizáveis

### `components/md_editor.py`
```python
def md_viewer_editor(content: str, file_path: str, edit_mode: bool = False):
    """
    Se edit_mode=False: renderiza st.markdown
    Se edit_mode=True: st.text_area + botão Salvar
    Retorna (novo_conteudo, foi_salvo)
    """
```

### `components/sidebar.py`
```python
def render_sidebar():
    """
    - Logo/título do projeto
    - Link rápido para ESTADO.md
    - Indicador de sessão ativa
    - Navegação global entre páginas
    """
```

### `utils/file_io.py`
```python
def read_md(path: str) -> str: ...
def write_md(path: str, content: str) -> None: ...
    # sempre faz backup em .bak antes de escrever
def append_md(path: str, block: str) -> None: ...
    # append seguro preservando estrutura
```

---

## 4. Configuração do Streamlit

### `.streamlit/config.toml`
```toml
[theme]
base = "dark"
primaryColor = "#4A90D9"        # azul médico
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1C2333"
textColor = "#FAFAFA"
font = "sans serif"

[server]
port = 8501
headless = false
runOnSave = true

[browser]
gatherUsageStats = false
```

---

## 5. Dependências

### `requirements_streamlit.txt`
```
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.20.0
watchdog>=4.0.0      # hot reload no modo dev
```

> Não há dependência de banco de dados — toda a persistência é via arquivos `.md` existentes.

---

## 6. Entry Point

### `app/streamlit_app.py`
```python
import streamlit as st

st.set_page_config(
    page_title="IPUB — Residência Médica",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "Estudo": [
        st.Page("pages/01_dashboard.py",       title="Dashboard",        icon="🏠"),
        st.Page("pages/02_caderno_erros.py",   title="Caderno de Erros", icon="📖"),
        st.Page("pages/03_resumos.py",         title="Resumos por Área", icon="📚"),
    ],
    "Análise": [
        st.Page("pages/04_progresso.py",       title="Progresso",        icon="📈"),
        st.Page("pages/05_historico.py",       title="Histórico",        icon="🗓️"),
    ],
}

pg = st.navigation(pages)
pg.run()
```

---

## 7. Como Rodar

```bash
# Na raiz do repositório IPUB:
pip install -r requirements_streamlit.txt
streamlit run app/streamlit_app.py
```

---

## 8. Decisões de Design

| Decisão | Justificativa |
|---|---|
| Arquivos `.md` como banco de dados | Compatibilidade total com Claude Code e workflows existentes |
| Sem banco SQL/SQLite | Evita dependências extras; arquivos são portáveis |
| Backup automático `.bak` ao editar | Segurança sem necessidade de git commit manual |
| `st.navigation` (multipage API nova) | Streamlit ≥ 1.31 — mais flexível que pages/ automático |
| Plotly para gráficos | Interatividade nativa no Streamlit sem bibliotecas extras |
| `os.walk` dinâmico para Temas/ | Detecta novas subpastas automaticamente sem configuração |

---

## 9. Ordem de Implementação Sugerida

1. **Fase 1 — Base:** `utils/file_io.py` + `utils/parser.py` + configuração `.streamlit/config.toml`
2. **Fase 2 — Leitura:** Dashboard (read-only) + Resumos (visualizador) + Histórico (listagem)
3. **Fase 3 — Escrita:** Caderno de Erros (formulário de novo erro) + editor de Resumos
4. **Fase 4 — Análise:** Progresso (gráficos plotly, heatmap de sessões)
5. **Fase 5 — Polimento:** sidebar global, tema dark, responsividade mobile

---

## 10. Notas para o Implementador

- **Caminhos relativos:** o app deve resolver caminhos relativos à **raiz do repositório** (onde estão `caderno_erros.md`, `Temas/`, etc.), não à pasta `app/`. Usar `Path(__file__).parent.parent` como root.
- **Formato do `caderno_erros.md`:** o parser precisa ser tolerante — inspecionar o arquivo atual antes de escrever o regex de parse, pois o formato pode variar entre entradas antigas e novas.
- **Edição concorrente:** como o app é local/single-user, não é necessário lock de arquivos. O backup `.bak` é suficiente.
- **Workflows `.agents/`:** não integrar na primeira versão — manter como CLI/Claude Code. A UI foca em leitura/escrita de dados, não em orquestração de agentes.
