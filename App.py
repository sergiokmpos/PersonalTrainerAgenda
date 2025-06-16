import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

# Função para criar uma agenda de exemplo para o mês atual
def create_schedule():
    now = datetime.now()
    month_days = calendar.monthrange(now.year, now.month)[1]
    days = [datetime(now.year, now.month, day) for day in range(1, month_days + 1)]
    schedule = pd.DataFrame(days, columns=['Date'])
    schedule['Students'] = 0
    schedule['Available'] = 'Yes'
    return schedule

# Função para exibir a agenda em formato de calendário
def display_schedule(schedule):
    st.write("### Agenda do Mês Atual")
    
    # Criar um calendário com cada coluna sendo um dia da semana
    schedule['Weekday'] = schedule['Date'].dt.weekday
    schedule['Weekday'] = schedule['Weekday'].apply(lambda x: calendar.day_name[x])
    
    # Pivotar a tabela para que cada coluna seja um dia da semana
    calendar_view = schedule.pivot(index='Date', columns='Weekday', values=['Students', 'Available'])
    
    st.dataframe(calendar_view)

# Função para carregar o banco de dados de alunos a partir de um arquivo CSV
def load_student_db():
    try:
        return pd.read_csv('students.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Name', 'Age', 'Gender', 'Email', 'Phone', 'Address', 'Emergency Contact', 'Medical Conditions', 'Goals', 'Additional Information'])

# Função para salvar o banco de dados de alunos em um arquivo CSV
def save_student_db(df):
    df.to_csv('students.csv', index=False)

# Função para exibir o formulário de cadastro de alunos e operações CRUD
def student_registration():
    st.write("### Cadastro de Alunos")
    
    # Carregar banco de dados de alunos
    student_db = load_student_db()
    
    # Exibir banco de dados de alunos
    st.write("#### Banco de Dados de Alunos")
    st.dataframe(student_db)
    
    # Formulário de cadastro
    with st.form(key='student_form'):
        name = st.text_input("Nome")
        age = st.number_input("Idade", min_value=0)
        gender = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro"])
        email = st.text_input("Email")
        phone = st.text_input("Telefone")
        address = st.text_area("Endereço")
        emergency_contact = st.text_input("Contato de Emergência")
        medical_conditions = st.text_area("Condições Médicas")
        goals = st.text_area("Objetivos")
        additional_info = st.text_area("Informações Adicionais")
        
        submit_button = st.form_submit_button(label='Cadastrar')

        if submit_button:
            new_student = pd.DataFrame({
                'Name': [name],
                'Age': [age],
                'Gender': [gender],
                'Email': [email],
                'Phone': [phone],
                'Address': [address],
                'Emergency Contact': [emergency_contact],
                'Medical Conditions': [medical_conditions],
                'Goals': [goals],
                'Additional Information': [additional_info]
            })
            student_db = pd.concat([student_db, new_student], ignore_index=True)
            save_student_db(student_db)
            st.success(f"Aluno {name} cadastrado com sucesso!")
    
    # Operações CRUD
    st.write("#### Operações CRUD")
    
    # Excluir aluno
    delete_name = st.text_input("Digite o nome do aluno para excluir")
    if st.button("Excluir"):
        student_db = student_db[student_db['Name'] != delete_name]
        save_student_db(student_db)
        st.success(f"Aluno {delete_name} excluído com sucesso!")
    
    # Atualizar aluno
    update_name = st.text_input("Digite o nome do aluno para atualizar")
    if st.button("Atualizar"):
        student_to_update = student_db[student_db['Name'] == update_name]
        if not student_to_update.empty:
            with st.form(key='update_form'):
                name = st.text_input("Nome", value=student_to_update.iloc[0]['Name'])
                age = st.number_input("Idade", min_value=0, value=int(student_to_update.iloc[0]['Age']))
                gender = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro"], index=["Masculino", "Feminino", "Outro"].index(student_to_update.iloc[0]['Gender']))
                email = st.text_input("Email", value=student_to_update.iloc[0]['Email'])
                phone = st.text_input("Telefone", value=student_to_update.iloc[0]['Phone'])
                address = st.text_area("Endereço", value=student_to_update.iloc[0]['Address'])
                emergency_contact = st.text_input("Contato de Emergência", value=student_to_update.iloc[0]['Emergency Contact'])
                medical_conditions = st.text_area("Condições Médicas", value=student_to_update.iloc[0]['Medical Conditions'])
                goals = st.text_area("Objetivos", value=student_to_update.iloc[0]['Goals'])
                additional_info = st.text_area("Informações Adicionais", value=student_to_update.iloc[0]['Additional Information'])
                
                submit_button = st.form_submit_button(label='Atualizar')

                if submit_button:
                    student_db.loc[student_db['Name'] == update_name] = [name, age, gender, email, phone, address, emergency_contact, medical_conditions, goals, additional_info]
                    save_student_db(student_db)
                    st.success(f"Aluno {name} atualizado com sucesso!")
        else:
            st.error(f"Nenhum aluno encontrado com o nome {update_name}")

# Função para exibir informações de contato e versão do aplicativo
def contact_and_version():
    st.write("### Contato e Versão do Aplicativo")
    st.write("Para qualquer dúvida, entre em contato: exemplo@exemplo.com")
    st.write("Versão do Aplicativo: 1.0.0")

# Cria um aplicativo Streamlit com três páginas
st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para", ["Agenda", "Cadastro de Alunos", "Contato e Versão"])

if page == "Agenda":
    schedule = create_schedule()
    display_schedule(schedule)
elif page == "Cadastro de Alunos":
    student_registration()
elif page == "Contato e Versão":
    contact_and_version()
