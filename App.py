import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import uuid
import os
import locale
import re # Importa re aqui em cima

# --- Configuração da Página ---
st.set_page_config(
    layout="wide",
    page_title="Sistema de Gerenciamento de Alunos e Agenda",
)

# --- Funções Auxiliares ---
def calculate_age(born_date):
    if pd.isna(born_date) or born_date is None:
        return None
    today = date.today()
    try:
        born_date_only = born_date if isinstance(born_date, date) else born_date.date()
        return today.year - born_date_only.year - ((today.month, today.day) < (born_date_only.month, born_date_only.day))
    except Exception as e:
        st.error(f"Erro ao calcular idade para data {born_date}: {e}")
        return None

# --- Gerenciamento de Estado e Carregamento Inicial ---
if 'student_db' not in st.session_state:
    try:
        if os.path.exists('students.csv'):
             st.session_state.student_db = pd.read_csv('students.csv')
             if 'ID' not in st.session_state.student_db.columns:
                  st.session_state.student_db['ID'] = ''
             st.session_state.student_db['ID'] = st.session_state.student_db['ID'].apply(lambda x: str(uuid.uuid4()) if pd.isna(x) or x == '' else x)
             if 'Date of Birth' in st.session_state.student_db.columns:
                  st.session_state.student_db['Date of Birth'] = pd.to_datetime(st.session_state.student_db['Date of Birth'], errors='coerce').dt.date
             else:
                  st.session_state.student_db['Date of Birth'] = pd.NA
        else:
            st.session_state.student_db = pd.DataFrame(columns=[
                'ID', 'Name', 'Date of Birth', 'Gender', 'Email', 'Phone', 'Address',
                'Emergency Contact', 'Medical Conditions', 'Goals', 'Additional Information'
            ])
            st.session_state.student_db = st.session_state.student_db.astype({
                 'ID': str, 'Name': str, 'Date of Birth': 'object',
                 'Gender': str, 'Email': str, 'Phone': str, 'Address': str,
                 'Emergency Contact': str, 'Medical Conditions': str,
                 'Goals': str, 'Additional Information': str
            })
        st.success("Banco de dados de alunos carregado ou inicializado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao carregar banco de dados de alunos: {e}")
        st.session_state.student_db = pd.DataFrame(columns=[
                'ID', 'Name', 'Date of Birth', 'Gender', 'Email', 'Phone', 'Address',
                'Emergency Contact', 'Medical Conditions', 'Goals', 'Additional Information'
            ])
        st.session_state.student_db = st.session_state.student_db.astype({
                 'ID': str, 'Name': str, 'Date of Birth': 'object',
                 'Gender': str, 'Email': str, 'Phone': str, 'Address': str,
                 'Emergency Contact': str, 'Medical Conditions': str,
                 'Goals': str, 'Additional Information': str
            })

if 'schedule_df' not in st.session_state:
    try:
        now = datetime.now()
        month_days = calendar.monthrange(now.year, now.month)[1]
        days = [datetime(now.year, now.month, day).date() for day in range(1, month_days + 1)]
        schedule = pd.DataFrame(days, columns=['Date'])
        schedule['Scheduled Student IDs'] = [[] for _ in range(len(schedule))]
        st.session_state.schedule_df = schedule
        st.success("Agenda do mês atual criada!")
    except Exception as e:
        st.error(f"Erro ao criar agenda: {e}")
        st.session_state.schedule_df = pd.DataFrame(columns=['Date', 'Scheduled Student IDs'])

if 'add_form_key_counter' not in st.session_state:
    st.session_state.add_form_key_counter = 0

if 'update_student_id' not in st.session_state:
     st.session_state.update_student_id = None

def save_student_db():
    try:
        df_to_save = st.session_state.student_db.copy()
        if 'Date of Birth' in df_to_save.columns:
             df_to_save['Date of Birth'] = df_to_save['Date of Birth'].apply(
                 lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (date, datetime)) else ''
             )
        df_to_save.to_csv('students.csv', index=False)
        st.success("Banco de dados de alunos salvo!")
    except Exception as e:
        st.error(f"Erro ao salvar banco de dados de alunos: {e}")

# --- Funções para as Páginas ---
def agenda_page():
    st.title("🗓️ Agenda do Mês Atual")
    schedule = st.session_state.schedule_df.copy()

    if not schedule.empty:
        schedule['Date_dt'] = pd.to_datetime(schedule['Date'])
        schedule['Weekday'] = schedule['Date_dt'].dt.weekday
        try:
             locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
             schedule['Weekday'] = schedule['Weekday'].apply(lambda x: calendar.day_name[x].capitalize())
        except:
             schedule['Weekday'] = schedule['Weekday'].apply(lambda x: calendar.day_name[x].capitalize())

        schedule['Number of Students'] = schedule['Scheduled Student IDs'].apply(len)
        schedule['Availability'] = schedule['Number of Students'].apply(lambda x: 'Ocupado' if x > 0 else 'Disponível')

        st.write("### Resumo da Agenda")
        st.dataframe(schedule[['Date', 'Weekday', 'Number of Students', 'Availability']], use_container_width=True)

        st.write("---")
        st.write("### Gerenciar Agendamentos por Dia")

        selected_date_input = st.date_input(
            "Selecione uma data:",
            min_value=schedule['Date_dt'].min().date(),
            max_value=schedule['Date_dt'].max().date(),
            value=schedule['Date_dt'].min().date(),
            key='schedule_date_selector'
        )

        selected_index_list = st.session_state.schedule_df.index[st.session_state.schedule_df['Date'] == selected_date_input].tolist()

        if not selected_index_list:
             st.warning(f"Data selecionada ({selected_date_input}) não encontrada na agenda do mês atual.")
             return

        selected_index = selected_index_list[0]
        current_scheduled_ids = st.session_state.schedule_df.loc[selected_index, 'Scheduled Student IDs']

        scheduled_students_info = []
        if current_scheduled_ids:
            agendados_df = st.session_state.student_db[st.session_state.student_db['ID'].isin(current_scheduled_ids)].copy()
            agendados_df['agendado_order'] = pd.Categorical(agendados_df['ID'], categories=current_scheduled_ids, ordered=True)
            agendados_df = agendados_df.sort_values('agendado_order')
            for index, row in agendados_df.iterrows():
                 scheduled_students_info.append(f"{row['Name']} (ID: {row['ID'][:4]}...)")

        st.write(f"**Alunos agendados para {selected_date_input.strftime('%d/%m/%Y')}:**")
        if scheduled_students_info:
            for info in scheduled_students_info:
                st.markdown(f"- {info}")
        else:
            st.write("Nenhum aluno agendado para esta data.")

        st.write("---")

        available_students = st.session_state.student_db.copy()

        if not available_students.empty:
             if 'ID' in available_students.columns:
                  available_students['Name_ID'] = available_students['Name'] + ' (ID: ' + available_students['ID'].str[:4] + '...)'
             else:
                  available_students['Name_ID'] = available_students['Name']
                  st.warning("Coluna 'ID' não encontrada no banco de dados de alunos. Funcionalidade limitada.")

             default_selection_options = []
             if 'ID' in available_students.columns:
                 agendados_df_selection = available_students[available_students['ID'].isin(current_scheduled_ids)].copy()
                 agendados_df_selection['agendado_order'] = pd.Categorical(agendados_df_selection['ID'], categories=current_scheduled_ids, ordered=True)
                 agendados_df_selection = agendados_df_selection.sort_values('agendado_order')
                 default_selection_options = agendados_df_selection['Name_ID'].tolist()

             selected_students_to_manage_options = available_students['Name_ID'].tolist() if 'Name_ID' in available_students.columns else []

             selected_students_to_manage = st.multiselect(
                 f"Selecione alunos para agendar ou remover de {selected_date_input.strftime('%d/%m/%Y')}:",
                 options=selected_students_to_manage_options,
                 default=default_selection_options,
                 key=f'manage_schedule_multiselect_{selected_date_input.strftime("%Y%m%d")}'
             )

             selected_ids_to_manage = []
             if 'ID' in available_students.columns:
                 selected_ids_to_manage = [
                     available_students.loc[available_students['Name_ID'] == name_id, 'ID'].iloc[0]
                     for name_id in selected_students_to_manage
                 ]

             if st.button("Atualizar Agendamentos", key=f'update_schedule_button_{selected_date_input.strftime("%Y%m%d")}'):
                 try:
                     st.session_state.schedule_df.loc[selected_index, 'Scheduled Student IDs'] = selected_ids_to_manage
                     st.success(f"Agendamentos atualizados para {selected_date_input.strftime('%d/%m/%Y')}!")
                 except Exception as e:
                      st.error(f"Erro ao atualizar agendamentos: {e}")
        else:
            st.info("Nenhum aluno disponível para agendar.")
    else:
        st.info("Agenda vazia. Verifique se houve um erro ao criar a agenda.")


def student_registration_page():
    st.title("🧑‍🎓 Cadastro de Alunos")
    student_db = st.session_state.student_db

    st.write("### Banco de Dados de Alunos")
    if not student_db.empty:
        student_db_display = student_db.copy()
        if 'Date of Birth' in student_db_display.columns:
             student_db_display['Age'] = student_db_display['Date of Birth'].apply(calculate_age)
             student_db_display['Age'] = student_db_display['Age'].apply(lambda x: int(x) if pd.notna(x) else '')
             display_cols = ['Name', 'Age', 'Date of Birth', 'Gender', 'Email', 'Phone', 'Emergency Contact', 'Medical Conditions', 'Goals', 'Additional Information', 'ID']
             display_cols = [col for col in display_cols if col in student_db_display.columns]
             st.dataframe(student_db_display[display_cols], use_container_width=True)
        else:
            st.dataframe(student_db, use_container_width=True)
    else:
        st.info("Nenhum aluno cadastrado ainda.")

    st.write("---")
    st.write("### Adicionar Novo Aluno")
    add_form_key = f'add_student_form_{st.session_state.add_form_key_counter}'

    with st.form(key=add_form_key, clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nome Completo *", key=f'{add_form_key}_name')
            dob = st.date_input("Data de Nascimento *", value=date.today(), max_value=date.today(), key=f'{add_form_key}_dob')
            gender = st.selectbox("Gênero *", ["Masculino", "Feminino", "Outro", "Não Especificado"], index=3, key=f'{add_form_key}_gender')
            email = st.text_input("Email", key=f'{add_form_key}_email')
            phone = st.text_input("Telefone", key=f'{add_form_key}_phone')
        with col2:
            address = st.text_area("Endereço", key=f'{add_form_key}_address')
            emergency_contact = st.text_input("Contato de Emergência *", key=f'{add_form_key}_emergency_contact')
            medical_conditions = st.text_area("Condições Médicas", key=f'{add_form_key}_medical_conditions')
            goals = st.text_area("Objetivos", key=f'{add_form_key}_goals')
            additional_info = st.text_area("Informações Adicionais", key=f'{add_form_key}_additional_info')

        submit_button = st.form_submit_button(label='Cadastrar Aluno')

        if submit_button:
            if not name or not emergency_contact:
                st.warning("Os campos 'Nome Completo' e 'Contato de Emergência' são obrigatórios.")
            else:
                try:
                    new_student_id = str(uuid.uuid4())
                    new_student_data = {
                        'ID': [new_student_id],
                        'Name': [name],
                        'Date of Birth': [dob],
                        'Gender': [gender],
                        'Email': [email],
                        'Phone': [phone],
                        'Address': [address],
                        'Emergency Contact': [emergency_contact],
                        'Medical Conditions': [medical_conditions],
                        'Goals': [goals],
                        'Additional Information': [additional_info]
                    }
                    new_student_df = pd.DataFrame(new_student_data)
                    st.session_state.student_db = pd.concat([st.session_state.student_db, new_student_df], ignore_index=True)
                    save_student_db()
                    st.success(f"Aluno '{name}' cadastrado com sucesso! (ID: {new_student_id[:4]}...)")
                    st.session_state.add_form_key_counter += 1
                except Exception as e:
                    st.error(f"Erro ao cadastrar aluno: {e}")

    st.write("---")
    st.write("### Gerenciar Alunos Existentes")

    student_options = ["-- Selecione um aluno para gerenciar --"]
    if not student_db.empty and 'ID' in student_db.columns:
         student_options.extend([f"{row['Name']} (ID: {row['ID'][:4]}...)" for index, row in student_db.iterrows()])
    elif not student_db.empty:
         st.warning("Coluna 'ID' não encontrada no banco de dados de alunos. Gerenciamento por nome pode não ser único.")
         student_options.extend([f"{row['Name']}" for index, row in student_db.iterrows()])
    else:
         st.info("Não há alunos para gerenciar (excluir/atualizar).")

    selected_student_option = st.selectbox(
        "Selecione um aluno para gerenciar:",
        options=student_options,
        key='manage_student_selectbox'
    )

    selected_student_id = None
    student_to_manage_row = pd.DataFrame()

    if selected_student_option != "-- Selecione um aluno para gerenciar --":
        try:
            id_match = re.search(r'\(ID: (....)', selected_student_option)
            if id_match and 'ID' in st.session_state.student_db.columns:
                 selected_student_id_part = id_match.group(1)
                 matching_students = st.session_state.student_db[st.session_state.student_db['ID'].str.startswith(selected_student_id_part, na=False)]
                 if not matching_students.empty:
                      selected_student_id = matching_students['ID'].iloc[0]
                      student_to_manage_row = st.session_state.student_db[st.session_state.student_db['ID'] == selected_student_id]
                      if not student_to_manage_row.empty:
                           student_data = student_to_manage_row.iloc[0]
                           st.write(f"Aluno selecionado: **{student_data['Name']}** (ID Completo: {selected_student_id})")
                      else:
                           st.error("Erro interno: Aluno selecionado não encontrado após busca por ID completo.")
                           selected_student_id = None
                           student_to_manage_row = pd.DataFrame()
                 else:
                      st.warning("Aluno selecionado não encontrado pelo ID. Verifique o banco de dados.")
                      selected_student_id = None
                      student_to_manage_row = pd.DataFrame()
            elif 'ID' not in st.session_state.student_db.columns:
                 student_name_only = selected_student_option.strip()
                 matching_students = st.session_state.student_db[st.session_state.student_db['Name'] == student_name_only]
                 if not matching_students.empty:
                      if len(matching_students) > 1:
                           st.warning(f"Vários alunos encontrados com o nome '{student_name_only}'. Operações podem afetar múltiplos registros.")
                      student_to_manage_row = matching_students.iloc[[0]]
                      student_data = student_to_manage_row.iloc[0]
                      st.write(f"Aluno selecionado (por nome): **{student_data['Name']}**")
                 else:
                      st.warning(f"Aluno com nome '{student_name_only}' não encontrado.")
                      selected_student_id = None
                      student_to_manage_row = pd.DataFrame()
            else:
                 st.warning("Formato de seleção inesperado. Selecione um aluno válido da lista.")
                 selected_student_id = None
                 student_to_manage_row = pd.DataFrame()
        except Exception as e:
             st.error(f"Erro ao processar seleção do aluno: {e}")
             selected_student_id = None
             student_to_manage_row = pd.DataFrame()

    if not student_to_manage_row.empty:
         student_data = student_to_manage_row.iloc[0]
         is_managed_by_id = ('ID' in student_data and pd.notna(student_data['ID']) and student_data['ID'] in st.session_state.student_db['ID'].values)

         manage_col1, manage_col2 = st.columns(2)

         with manage_col1:
             delete_key = f'delete_button_{student_data["ID"]}' if is_managed_by_id else f'delete_button_name_{student_data["Name"]}'
             if st.button(f"Excluir '{student_data['Name'].split(' ')[0]}'", key=delete_key):
                 try:
                     if is_managed_by_id:
                         st.session_state.student_db = st.session_state.student_db[st.session_state.student_db['ID'] != student_data['ID']].reset_index(drop=True)
                         student_id_to_remove = student_data['ID']
                         for index in st.session_state.schedule_df.index:
                             scheduled_ids = st.session_state.schedule_df.loc[index, 'Scheduled Student IDs']
                             updated_scheduled_ids = [id for id in scheduled_ids if id != student_id_to_remove]
                             st.session_state.schedule_df.loc[index, 'Scheduled Student IDs'] = updated_scheduled_ids
                     else:
                         st.warning(f"Excluindo TODOS os alunos com o nome '{student_data['Name']}' pois a coluna 'ID' não está presente ou válida.")
                         ids_to_remove = []
                         if 'ID' in st.session_state.student_db.columns:
                             ids_to_remove = st.session_state.student_db[st.session_state.student_db['Name'] == student_data['Name']]['ID'].tolist()
                         st.session_state.student_db = st.session_state.student_db[st.session_state.student_db['Name'] != student_data['Name']].reset_index(drop=True)
                         if ids_to_remove:
                              for student_id_to_remove in ids_to_remove:
                                   for index in st.session_state.schedule_df.index:
                                       scheduled_ids = st.session_state.schedule_df.loc[index, 'Scheduled Student IDs']
                                       updated_scheduled_ids = [id for id in scheduled_ids if id != student_id_to_remove]
                                       st.session_state.schedule_df.loc[index, 'Scheduled Student IDs'] = updated_scheduled_ids
                     save_student_db()
                     st.success(f"Aluno(s) '{student_data['Name']}' excluído(s) com sucesso!")
                     st.session_state.manage_student_selectbox = "-- Selecione um aluno para gerenciar --"
                     st.session_state.update_student_id = None
                 except Exception as e:
                      st.error(f"Erro ao excluir aluno: {e}")

         with manage_col2:
             update_init_key = f'update_init_button_{student_data["ID"]}' if is_managed_by_id else f'update_init_button_name_{student_data["Name"]}'
             if st.button(f"Atualizar '{student_data['Name'].split(' ')[0]}'", key=update_init_key, disabled=not is_managed_by_id):
                if is_managed_by_id:
                    st.session_state.update_student_id = student_data['ID']
                else:
                    st.warning("Atualização por nome não é suportada devido a potenciais duplicatas. Necessita da coluna 'ID' válida.")

    if st.session_state.update_student_id is not None:
        update_id = st.session_state.update_student_id
        student_to_update_row = st.session_state.student_db[st.session_state.student_db['ID'] == update_id]

        if not student_to_update_row.empty:
            student_data_u = student_to_update_row.iloc[0]
            st.write("---")
            st.write("### Atualizar Dados do Aluno Selecionado")
            update_form_key = f'update_student_form_{update_id}'
            with st.form(key=update_form_key):
                col1_u, col2_u = st.columns(2)
                with col1_u:
                    st.text_input("ID do Aluno", value=student_data_u['ID'], disabled=True)
                    name_u = st.text_input("Nome Completo *", value=student_data_u['Name'])
                    default_dob_u = student_data_u['Date of Birth'] if isinstance(student_data_u['Date of Birth'], date) else date.today()
                    dob_u = st.date_input("Data de Nascimento *", value=default_dob_u, max_value=date.today())
                    gender_u = st.selectbox("Gênero *", ["Masculino", "Feminino", "Outro", "Não Especificado"], index=["Masculino", "Feminino", "Outro", "Não Especificado"].index(student_data_u['Gender']))
                    email_u = st.text_input("Email", value=student_data_u['Email'])
                    phone_u = st.text_input("Telefone", value=student_data_u['Phone'])
                with col2_u:
                    address_u = st.text_area("Endereço", value=student_data_u['Address'])
                    emergency_contact_u = st.text_input("Contato de Emergência *", value=student_data_u['Emergency Contact'])
                    medical_conditions_u = st.text_area("Condições Médicas", value=student_data_u['Medical Conditions'])
                    goals_u = st.text_area("Objetivos", value=student_data_u['Goals'])
                    additional_info_u = st.text_area("Informações Adicionais", value=student_data_u['Additional Information'])

                update_col_buttons = st.columns(2)
                with update_col_buttons[0]:
                    update_submit_button = st.form_submit_button(label='Salvar Atualizações')
                with update_col_buttons[1]:
                    cancel_update_button = st.form_submit_button(label='Cancelar')

                if update_submit_button:
                    if not name_u or not emergency_contact_u:
                         st.warning("Os campos 'Nome Completo' e 'Contato de Emergência' são obrigatórios.")
                    else:
                         try:
                             index_to_update_list = st.session_state.student_db.index[st.session_state.student_db['ID'] == update_id].tolist()
                             if index_to_update_list:
                                 index_to_update = index_to_update_list[0]
                                 st.session_state.student_db.loc[index_to_update, 'Name'] = name_u
                                 st.session_state.student_db.loc[index_to_update, 'Date of Birth'] = dob_u
                                 st.session_state.student_db.loc[index_to_update, 'Gender'] = gender_u
                                 st.session_state.student_db.loc[index_to_update, 'Email'] = email_u
                                 st.session_state.student_db.loc[index_to_update, 'Phone'] = phone_u
                                 st.session_state.student_db.loc[index_to_update, 'Address'] = address_u
                                 st.session_state.student_db.loc[index_to_update, 'Emergency Contact'] = emergency_contact_u
                                 st.session_state.student_db.loc[index_to_update, 'Medical Conditions'] = medical_conditions_u
                                 st.session_state.student_db.loc[index_to_update, 'Goals'] = goals_u
                                 st.session_state.student_db.loc[index_to_update, 'Additional Information'] = additional_info_u
                                 save_student_db()
                                 st.success(f"Dados do aluno '{name_u}' (ID: {update_id[:4]}...) atualizados com sucesso!")
                                 st.session_state.update_student_id = None
                             else:
                                 st.error("Erro: O aluno a ser atualizado não foi encontrado no banco de dados. A lista pode ter sido modificada.")
                                 st.session_state.update_student_id = None
                         except Exception as e:
                            st.error(f"Erro ao atualizar aluno: {e}")

                if cancel_update_button:
                     st.session_state.update_student_id = None

        else:
            st.error("Erro interno: Aluno a ser atualizado não encontrado no banco de dados do estado da sessão.")
            st.session_state.update_student_id = None


def contact_and_version_page():
    st.title("ℹ️ Contato e Versão do Aplicativo")
    st.write("Para qualquer dúvida ou suporte, entre em contato:")
    st.markdown("Email: [exemplo@exemplo.com](mailto:exemplo@exemplo.com)")
    st.write("---")
    st.write("### Versão do Aplicativo")
    st.write("1.4.0 (IndentationError Corrigido, Código Conciso)")


# --- Navegação na Barra Lateral ---
st.sidebar.title("🧭 Navegação")
page = st.sidebar.radio("Ir para", ["Agenda", "Cadastro de Alunos", "Contato e Versão"], key='main_navigation')

# Lógica para limpar o estado de atualização do aluno
if 'update_student_id' in st.session_state and st.session_state.update_student_id is not None:
    current_selectbox_selection = st.session_state.get('manage_student_selectbox', "-- Estado inicial --")
    # Clear if page changed or if the selectbox selection is the default one
    if page != "Cadastro de Alunos" or current_selectbox_selection == "-- Selecione um aluno para gerenciar --":
         st.session_state.update_student_id = None
    # Clear if the selected ID in the selectbox does not match the ID being updated
    # This handles cases where the selectbox value changes *while* the update form is open
    else:
        aluno_atual_selecionado_pelo_id = None
        if current_selectbox_selection != "-- Estado inicial --" and 'ID' in st.session_state.student_db.columns:
            try:
                 id_match = re.search(r'\(ID: (....)', current_selectbox_selection)
                 if id_match:
                      selected_student_id_part = id_match.group(1)
                      matching_students = st.session_state.student_db[st.session_state.student_db['ID'].str.startswith(selected_student_id_part, na=False)]
                      if not matching_students.empty:
                           aluno_atual_selecionado_pelo_id = matching_students['ID'].iloc[0]
            except:
                 pass # Ignore errors here

        if st.session_state.update_student_id is not None and aluno_atual_selecionado_pelo_id != st.session_state.update_student_id:
             st.session_state.update_student_id = None


# Renderiza a página selecionada
if page == "Agenda":
    agenda_page()
elif page == "Cadastro de Alunos":
    student_registration_page()
elif page == "Contato e Versão":
    contact_and_version_page()

# --- Explicação do Tema (Simplificado) ---
st.sidebar.markdown("---")
st.sidebar.info("Tema (Amarelo/Preto): Requer arquivo `.streamlit/config.toml` na mesma pasta para personalização completa.")