import sqlite3
import sys
from datetime import timedelta, datetime

import pandas as pd
import streamlit as st
from streamlit import runtime
from streamlit.web import cli

conn = sqlite3.connect('timesheet.db')
cursor = conn.cursor()
df_config = {'0': 'Data', '1': 'Início - Trabalho', '2': 'Início - Almoço',
             '3': 'Término - Almoço', '4': 'Término - Trabalho',
             '5': 'Início - Extra', '6': 'Término - Extra', '7': 'Observações'}


def database_healthcheck():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TIMESHEET (REGISTER_DATE TEXT NOT NULL PRIMARY KEY, 
        BEGIN_TIME TEXT, BEGIN_LUNCH TEXT, END_LUNCH TEXT, END_TIME TEXT, 
        BEGIN_EXTRA TEXT, END_EXTRA TEXT, OBSERVATIONS TEXT)
        """)


def select_all_data(period_flag):
    database_healthcheck()
    if period_flag:
        param = datetime.now().date().strftime('%Y-%m')
        return conn.execute("""SELECT * FROM TIMESHEET WHERE REGISTER_DATE LIKE ? 
            ORDER BY REGISTER_DATE""", (f'{param}%',)).fetchall()
    return conn.execute("SELECT * FROM TIMESHEET ORDER BY REGISTER_DATE").fetchall()


def select_by_date(form_date):
    return conn.execute("SELECT * FROM TIMESHEET WHERE REGISTER_DATE = :date",
                        {'date': form_date}).fetchone()


def set_register_date(form_date, form_time, form_obs):
    result = select_by_date(form_date)
    if not result:
        conn.execute("""INSERT INTO TIMESHEET (REGISTER_DATE, BEGIN_TIME, OBSERVATIONS) 
        VALUES (?, ?, ?)""", (str(form_date), str(form_time), form_obs))
    else:
        conn.execute("""UPDATE TIMESHEET SET BEGIN_TIME = ?, OBSERVATIONS = ? 
            WHERE REGISTER_DATE = ?""", (str(form_time), form_obs, str(form_date)))
    conn.commit()
    st.toast(':green[O dia está começando]')


def set_end_date(form_date, form_time, form_obs):
    result = select_by_date(form_date)
    if not result:
        conn.execute("""INSERT INTO TIMESHEET (REGISTER_DATE, END_TIME, OBSERVATIONS) 
        VALUES (?, ?, ?)""", (str(form_date), str(form_time), form_obs))
    else:
        conn.execute("""UPDATE TIMESHEET SET END_TIME = ?, OBSERVATIONS = ? 
            WHERE REGISTER_DATE = ?""", (str(form_time), form_obs, str(form_date)))
    conn.commit()
    st.toast(':green[Sextou, casseta!]')


def set_lunch_time(form_date, form_time, form_obs):
    result = select_by_date(form_date)
    begin_lunch = str(form_time)
    end_lunch = str(datetime.strptime(str(form_time), '%H:%M:%S') + timedelta(hours=1))[11:19]

    if not result:
        conn.execute("""INSERT INTO TIMESHEET (REGISTER_DATE, BEGIN_LUNCH, END_LUNCH, OBSERVATIONS) 
            VALUES (?, ?, ?, ?)""", (str(form_date), begin_lunch, end_lunch, form_obs))
    else:
        conn.execute("""UPDATE TIMESHEET SET BEGIN_LUNCH = ?, END_LUNCH = ?, OBSERVATIONS = ? 
            WHERE REGISTER_DATE = ?""", (begin_lunch, end_lunch, form_obs, str(form_date)))
    conn.commit()
    st.toast(':orange[Volto em uma hora]')


def set_begin_extra(form_date, form_time, form_obs):
    result = select_by_date(form_date)
    if not result:
        conn.execute("""INSERT INTO TIMESHEET (REGISTER_DATE, BEGIN_EXTRA, OBSERVATIONS) 
            VALUES (?, ?, ?, ?)""", (str(form_date), str(form_time), form_obs))
    else:
        conn.execute("""UPDATE TIMESHEET SET BEGIN_EXTRA = ?, OBSERVATIONS = ? 
            WHERE REGISTER_DATE = ?""", (str(form_time), form_obs, str(form_date)))
    conn.commit()
    st.toast(':red[Hora do trabalho noturno]')


def set_end_extra(form_date, form_time, form_obs):
    result = select_by_date(form_date)
    if not result:
        conn.execute("""INSERT INTO TIMESHEET (REGISTER_DATE, END_EXTRA, OBSERVATIONS) 
            VALUES (?, ?, ?, ?)""", (str(form_date), str(form_time), form_obs))
    else:
        conn.execute("""UPDATE TIMESHEET SET END_EXTRA = ?, OBSERVATIONS = ? 
            WHERE REGISTER_DATE = ?""", (str(form_time), form_obs, str(form_date)))
    conn.commit()
    st.toast(':red[A noite é uma criança!]')


def main():
    @st.cache_data
    def download_report(df):
        return df.to_csv().encode('utf-8')

    st.set_page_config(page_title='Folha de Ponto', layout='wide')
    st.markdown("""<style>
        div.block-container{ padding: 1rem; }
        [data-testid="stElementToolbar"] { display: none; }
        </style>""", unsafe_allow_html=True)

    st.title('Folha de Ponto')
    st.subheader('Formulário de cadastro')

    with st.expander(':red[Clique para expandir ou recuar o formulário]', expanded=True):
        with st.form('registration_form', clear_on_submit=True, border=0):
            col1, col2 = st.columns(2)
            date = col1.date_input('Data de cadastro', format='DD/MM/YYYY',
                                   help='Inclua uma data para o cadastro de ponto')
            time = col2.time_input('Hora de cadastro', value='now', step=60,
                                   help='Inclua um horário para o cadastro de ponto')

            period = st.selectbox('Período diário', placeholder='Escolha uma opção',
                                  options=['Início', 'Almoço', 'Término'])
            deploy = st.checkbox('Período extra')
            obs = st.text_input('Observações')
            submit = st.form_submit_button(label='Cadastrar', use_container_width=True)

        if submit:
            if period == 'Início' and not deploy:
                set_register_date(date, time, obs)
            elif period == 'Início' and deploy:
                set_begin_extra(date, time, obs)
            elif period == 'Almoço':
                set_lunch_time(date, time, obs)
            elif period == 'Término' and not deploy:
                set_end_date(date, time, obs)
            elif period == 'Término' and deploy:
                set_end_extra(date, time, obs)

    st.divider()

    st.subheader('Espelho de ponto')

    with st.expander(':red[Clique para expandir ou recuar o relatório]', expanded=False):
        row1, row2 = st.columns([3, 1])
        flag = row1.checkbox('Mensal', value=True)
        content = select_all_data(flag)

        if content:
            with st.container(height=450):
                st.dataframe(content, use_container_width=True, column_config=df_config)
        else:
            st.error('Nenhum registro cadastrado!')

        csv = download_report(pd.DataFrame(content, columns=list(df_config.values()))
                              .set_index(df_config.get("0")))
        filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        row2.download_button('Baixar CSV', type='primary', data=csv,
                             mime="text/csv", file_name=f'{filename}.csv')


if __name__ == '__main__':
    if runtime.exists():
        main()
    else:
        sys.argv = ['streamlit', 'run', sys.argv[0]]
        sys.exit(cli.main())
