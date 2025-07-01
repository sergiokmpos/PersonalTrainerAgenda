import streamlit as st
import pandas as pd
import datetime
from collections import defaultdict

# =========================
# CONFIGURAÇÕES GERAIS
# =========================
SALAS = ['Sala 1', 'Sala 2', 'Sala 3']
HORARIOS = [f"{h:02d}:00" for h in range(6, 22)]
CSV_FILE = 'agendamentos.csv'
MAX_VAGAS_POR_HORARIO = 3
SENHA_PROFESSOR = "admin123"

# =========================
# FUNÇÕES
# =========================
def init_csv():
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
    df = pd.read_csv(CSV_FILE)
    novo = pd.DataFrame([[aluno, data, horario, sala, professor]],
                        columns=['Aluno', 'Data', 'Horario', 'Sala', 'Professor'])
    df = pd.concat([df, novo], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def contar_ocupacao(df, data, horario, sala):
    df_copy = df.copy()
    df_copy['Data_str'] = pd.to_datetime(df_copy['Data']).dt.strftime('%Y-%m-%d')
    return len(df_copy[(df_copy['Data_str'] == data) & (df_copy['Horario'] == horario) & (df_copy['Sala'] == sala)])

# =========================
# INICIALIZAÇÃO
# =========================
init_csv()

if "tipo_usuario" not in st.session_state:
    st.session_state["tipo_usuario"] = None

# =========================
# LOGIN
# =========================
if st.session_state["tipo_usuario"] is None:
    st.title("🎯 Selecione seu perfil")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sou Aluno"):
            st.session_state["tipo_usuario"] = "aluno"

    with col2:
        with st.form("form_prof"):
            st.write("Sou Professor")
            senha = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar como Professor")
            if submit:
                if senha == SENHA_PROFESSOR:
                    st.session_state["tipo_usuario"] = "professor"
                else:
                    st.error("Senha incorreta!")

    st.stop()

# =========================
# TELA PRINCIPAL (após login)
# =========================
tipo = st.session_state["tipo_usuario"]
st.sidebar.success(f"Você está logado como: **{tipo.upper()}**")
if st.sidebar.button("Sair"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

aba = st.radio("Escolha a visualização", ["📌 Agendar", "📊 Grade semanal"])

# =========================
# AGENDAMENTO
# =========================
if aba == "📌 Agendar":
    st.header("Agendar nova aula")
    with st.form("form_agendamento"):
        if tipo == "professor":
            aluno = st.text_input("Nome do aluno")
        else:
            aluno = st.text_input("Seu nome")

        data = st.date_input("Data", min_value=datetime.date.today())
        horario = st.selectbox("Horário", HORARIOS)
        sala = st.selectbox("Sala", SALAS)
        professor = st.text_input("Professor responsável")
        enviar = st.form_submit_button("Agendar")

        if enviar:
            data_str = data.strftime('%Y-%m-%d')
            df_current = pd.read_csv(CSV_FILE)
            df_current['Data'] = pd.to_datetime(df_current['Data']).dt.strftime('%Y-%m-%d')

            if contar_ocupacao(df_current, data_str, horario, sala) >= MAX_VAGAS_POR_HORARIO:
                st.error(f"Limite de {MAX_VAGAS_POR_HORARIO} alunos por sala nesse horário atingido!")
            else:
                salvar_agendamento(aluno, data_str, horario, sala, professor)
                st.success("Aula agendada com sucesso!")
                st.rerun()

# =========================
# GRADE SEMANAL
# =========================
elif aba == "📊 Grade semanal":
    st.header("📊 Grade semanal")

    sala_selecionada = st.selectbox("Sala", SALAS)
    data_na_semana = st.date_input("Escolha uma data na semana", datetime.date.today())

    dia_da_semana = data_na_semana.weekday()
    primeiro_dia_semana = data_na_semana - datetime.timedelta(days=dia_da_semana)
    ultimo_dia_semana = primeiro_dia_semana + datetime.timedelta(days=6)
    dias_semana_datas = [primeiro_dia_semana + datetime.timedelta(days=i) for i in range(7)]

    df = pd.read_csv(CSV_FILE)
    df['Data'] = pd.to_datetime(df['Data']).dt.date

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

    dias_da_semana_nomes = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    st.markdown(f"### Semana: {primeiro_dia_semana.strftime('%d/%m')} - {ultimo_dia_semana.strftime('%d/%m')}")

    colunas_cabecalho = st.columns(8)
    colunas_cabecalho[0].write("Horário")
    for i, dia_data in enumerate(dias_semana_datas):
        colunas_cabecalho[i+1].markdown(f"**{dias_da_semana_nomes[i]}**\n{dia_data.strftime('%d/%m')}")

    for hora in HORARIOS:
        cols = st.columns(8)
        cols[0].markdown(f"**{hora}**")
        for i, dia_data in enumerate(dias_semana_datas):
            slot = agenda.get((hora, dia_data), {})
            alunos = slot.get('alunos', [])
            prof = slot.get('professor', '')

            linhas = []

            for vaga_idx in range(MAX_VAGAS_POR_HORARIO):
                if vaga_idx < len(alunos):
                    if tipo == "professor":
                        linhas.append(f"{vaga_idx+1}. {alunos[vaga_idx]}")
                    else:
                        linhas.append(f'{vaga_idx+1}. <span style="color:red"><b>(ocupado)</b></span>')
                else:
                    linhas.append(f'{vaga_idx+1}. <span style="color:green"><b>(vazio)</b></span>')

            if prof:
                linhas.append(f"<i>Prof: {prof}</i>")

            cols[i+1].markdown("<br>".join(linhas), unsafe_allow_html=True)
