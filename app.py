import streamlit as st

st.set_page_config(page_title='Time Sheet App')

st.title('Time Sheet App')
st.subheader('Formulário de cadastro')

with st.form('registration_form', clear_on_submit=True, border=0):
    col1, col2 = st.columns(2)
    date = col1.date_input('Data de cadastro', format='DD/MM/YYYY',
                           help='Inclua uma data para o cadastro de ponto')
    time = col2.time_input('Hora de cadastro', value='now', step=60,
                           help='Inclua um horário para o cadastro de ponto')

    period = st.selectbox('Período diário', placeholder='Escolha uma opção',
                          options=['Início', 'Almoço', 'Término'])
    deploy = st.checkbox('Período de deploy')
    obs = st.text_input('Observações')
    submit = st.form_submit_button(label='Cadastrar', use_container_width=True)

if submit:
    if period == 'Início' and not deploy:
        st.success('O dia está começando')
    elif period == 'Início' and deploy:
        st.error('Hora do trabalho noturno')
    elif period == 'Almoço':
        st.warning('Volto em uma hora')
    elif period == 'Término' and not deploy:
        st.success('Sextou, casseta!')
    elif period == 'Término' and deploy:
        st.error('A noite é uma criança!')
