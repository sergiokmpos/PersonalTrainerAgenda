import streamlit as st
import pandas as pd
import datetime
from collections import defaultdict

# Constantes
SALAS = ['Sala 1', 'Sala 2', 'Sala 3']
HORARIOS = [f"{h:02d}:00" for h in range(6, 22)]
CSV_FILE = 'agendamentos.csv'
MAX_VAGAS_POR_HORARIO = 3 # Define o limite de vagas

# Funções (mantidas as mesmas)
def init_csv():
    """Inicializa o arquivo CSV se não existir e garante a coluna Professor."""
    try:
        df = pd.read_csv(CSV_FILE)
        if 'Professor' not in df.columns:
            df['Professor'] = ''
            df.to_csv(CSV_FILE, index=False)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Aluno', 'Data', 'Horario', 'Sala', 'Professor'])
        df.to_csv(CSV_FILE, index=False)
    return df

def salvar_agendamento(aluno, data, horario, sala, professor):
    """Salva um novo agendamento no CSV."""
    df = pd.read_csv(CSV_FILE)
    novo = pd.DataFrame([[aluno, data, horario, sala, professor]],
                        columns=['Aluno', 'Data', 'Horario', 'Sala', 'Professor'])
    df = pd.concat([df, novo], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def contar_ocupacao(df, data, horario, sala):
    """Conta quantos agendamentos existem para um slot específico."""
    df_copy = df.copy()
    df_copy['Data_str'] = pd.to_datetime(df_copy['Data']).dt.strftime('%Y-%m-%d')
    return len(df_copy[(df_copy['Data_str'] == data) & (df_copy['Horario'] == horario) & (df_copy['Sala'] == sala)])

st.title("📅 Agendamento de Aulas - Estúdio de Pilates")

# Inicializa o CSV ao iniciar a app
init_csv()

aba = st.radio("Escolha a visualização", ["📌 Agendar", "📊 Grade semanal"])

# --- Injeção de CSS para a grade ---
st.markdown("""
<style>
/* Remove padding/margin dos blocos de coluna criados por st.columns para que as bordas se toquem */
div[data-testid="stHorizontalBlock"] {
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="stHorizontalBlock"] > div {
    padding: 0 !important; /* Padding dentro de cada coluna individual */
}

/* Estilo para o conteúdo dentro de cada célula */
.grid-cell-content {
    border-right: 1px solid #ddd; /* Borda direita */
    border-bottom: 1px solid #ddd; /* Borda inferior */
    padding: 8px 5px; /* Espaçamento interno */
    box-sizing: border-box; /* Inclui padding e borda no tamanho total */
    min-height: 70px; /* Altura mínima para cada célula (ajuste conforme necessário, pode precisar aumentar um pouco) */
    /* overflow-wrap: break-word; /* Quebra palavras longas */ /* Com nowrap abaixo, este pode não ser necessário */
    white-space: pre-wrap; /* Preserva quebras de linha do <br> */
    height: 100%; /* Faz o conteúdo preencher a altura da coluna pai */
    width: 100%; /* Faz o conteúdo preencher a largura da coluna pai */
    display: flex; /* Usa flexbox para alinhamento vertical/horizontal */
    flex-direction: column; /* Organiza conteúdo em coluna */
    justify-content: flex-start; /* Alinha conteúdo no topo */
    align-items: flex-start; /* Alinha conteúdo à esquerda */
    color: #333; /* Cor de texto padrão */
}

/* Estilo para o cabeçalho das células */
.header-cell-content {
    font-weight: bold;
    text-align: center;
    background-color: #f0f2f6; /* Fundo leve para cabeçalhos */
    justify-content: center; /* Centraliza horizontalmente */
    align-items: center; /* Centraliza verticalmente */
}

/* Adiciona borda superior à primeira linha (cabeçalho) */
div[data-testid="stHorizontalBlock"]:first-child .grid-cell-content {
     border-top: 1px solid #ddd;
}

/* Adiciona borda esquerda à primeira coluna (horários) */
div[data-testid="stHorizontalBlock"] > div:first-child .grid-cell-content {
     border-left: 1px solid #ddd;
}

/* Remove borda direita da última coluna */
div[data-testid="stHorizontalBlock"] > div:last-child .grid-cell-content {
     border-right: none;
}

/* Estilo específico para a célula de horário */
.time-cell-content {
     font-weight: bold;
     background-color: #f9f9f9; /* Fundo levemente diferente para a coluna de hora */
     justify-content: center;
     align-items: center;
}

/* Estilo para o span dentro das células que marca o texto "(vazio)" */
.empty-cell-text {
    color: #888; /* Cor cinza para o texto "(vazio)" */
    font-style: italic; /* Opcional: deixa o texto "(vazio)" em itálico */
    white-space: nowrap; /* <<<--- ADICIONADO: Impede que o texto (vazio) quebre linha se couber */
}

/* Estilo para o container da linha de vaga (número + conteúdo) */
/* Isso pode ajudar a manter o número e o conteúdo na mesma linha se white-space: normal no pai permitir quebra */
/* .vaga-line { display: inline-block; margin-right: 5px; } */ /* Pode ser uma alternativa complexa */


</style>
""", unsafe_allow_html=True)
# --- Fim da Injeção de CSS ---


if aba == "📌 Agendar":
    st.header("Agendar nova aula")
    with st.form("form_agendamento"):
        aluno = st.text_input("Nome do aluno")
        data = st.date_input("Data", min_value=datetime.date.today())
        horario = st.selectbox("Horário", HORARIOS)
        sala = st.selectbox("Sala", SALAS)
        professor = st.text_input("Professor responsável")
        enviar = st.form_submit_button("Agendar")

        if enviar:
            data_str = data.strftime('%Y-%m-%d')
            df_current = pd.read_csv(CSV_FILE)
            df_current['Data'] = pd.to_datetime(df_current['Data']).dt.strftime('%Y-%m-%d') # Formata para string para comparação

            if contar_ocupacao(df_current, data_str, horario, sala) >= MAX_VAGAS_POR_HORARIO:
                st.error(f"Limite de {MAX_VAGAS_POR_HORARIO} alunos por sala nesse horário atingido!")
            else:
                salvar_agendamento(aluno, data_str, horario, sala, professor)
                st.success("Aula agendada com sucesso!")
                st.rerun()

elif aba == "📊 Grade semanal":
    st.header("📊 Grade semanal")

    sala_selecionada = st.selectbox("Sala", SALAS)
    data_na_semana = st.date_input("Escolha uma data na semana", datetime.date.today())

    # --- Lógica para calcular a semana ---
    dia_da_semana = data_na_semana.weekday() # 0=Seg, 6=Dom
    primeiro_dia_semana = data_na_semana - datetime.timedelta(days=dia_da_semana)
    ultimo_dia_semana = primeiro_dia_semana + datetime.timedelta(days=6)
    dias_semana_datas = [primeiro_dia_semana + datetime.timedelta(days=i) for i in range(7)]
    # --- Fim da lógica para calcular a semana ---

    df = pd.read_csv(CSV_FILE)
    df['Data'] = pd.to_datetime(df['Data']).dt.date # Converter para objeto date

    df_semana = df[
        (df['Sala'] == sala_selecionada) &
        (df['Data'] >= primeiro_dia_semana) &
        (df['Data'] <= ultimo_dia_semana)
    ].copy()

    agenda = defaultdict(lambda: {'alunos': [], 'professor': ''})
    for _, row in df_semana.iterrows():
        dia = row['Data']
        hora = row['Horario']
        aluno = row['Aluno']
        prof = row['Professor']
        agenda[(hora, dia)]['alunos'].append(aluno)
        agenda[(hora, dia)]['professor'] = prof


    st.markdown(f"### 🗓️ Semana: {primeiro_dia_semana.strftime('%d/%m')} - {ultimo_dia_semana.strftime('%d/%m')}")

    # --- Estrutura da Grade ---
    # Cabeçalho
    colunas_cabecalho = st.columns(8)
    colunas_cabecalho[0].markdown('<div class="grid-cell-content header-cell-content time-cell-content">Horário</div>', unsafe_allow_html=True)
    dias_da_semana_nomes = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    for i, dia_data in enumerate(dias_semana_datas):
         colunas_cabecalho[i+1].markdown(f'<div class="grid-cell-content header-cell-content">**{dias_da_semana_nomes[i]}**<br><small>{dia_data.strftime("%d/%m")}</small></div>', unsafe_allow_html=True)

    # Corpo da Tabela
    for hora in HORARIOS:
        cols = st.columns(8)
        cols[0].markdown(f'<div class="grid-cell-content time-cell-content">**{hora}**</div>', unsafe_allow_html=True)

        for i, dia_data in enumerate(dias_semana_datas):
            slot = agenda.get((hora, dia_data), {})
            alunos = slot.get('alunos', [])
            prof = slot.get('professor', '')

            celulas_content = []

            # Preencher as 3 vagas
            for vaga_idx in range(MAX_VAGAS_POR_HORARIO):
                if vaga_idx < len(alunos):
                    # Se existir um aluno para esta vaga
                    celulas_content.append(f"{vaga_idx + 1} {alunos[vaga_idx]}")
                else:
                    # Se a vaga estiver vazia, adiciona "(vazio)" com o número e a classe de estilo
                    # Esta string já inclui o número e o (vazio) na mesma linha HTML
                    celulas_content.append(f'{vaga_idx + 1} <span class="empty-cell-text">(vazio)</span>')

            # Adiciona o professor APÓS as 3 vagas
            if prof:
                 celulas_content.append(f"Prof: {prof}")

            # Junta todos os elementos da lista com a tag <br> para quebra de linha
            # Isso garante que cada "item" na lista celulas_content (aluno, vaga vazia, prof)
            # fique em uma nova linha visual
            cell_html = "<br>".join(celulas_content)

            # Exibe o conteúdo da célula
            cols[i+1].markdown(f'<div class="grid-cell-content">{cell_html}</div>', unsafe_allow_html=True)