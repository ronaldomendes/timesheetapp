import streamlit as st

st.set_page_config(page_title='Time Sheet App')

st.title('Time Sheet App')
st.subheader('Formulário de cadastro')

col1, col2 = st.columns(2)
with col1:
    st.date_input('Data de cadastro', format='DD/MM/YYYY',
                  help='Inclua uma data para o cadastro de ponto')
with col2:
    st.time_input('Hora de cadastro', value='now', step=60,
                  help='Inclua um horário para o cadastro de ponto')

st.selectbox('Período diário', placeholder='Escolha uma opção',
             options=['Início', 'Almoço', 'Término'])
st.checkbox('Período de deploy')
st.button(label='Cadastrar', use_container_width=True)
