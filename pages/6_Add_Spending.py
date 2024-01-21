import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from streamlit.source_util import (
    page_icon_and_name,
    calc_md5,
    get_pages,
    _on_pages_changed
)
import sqlite3
#Set Up Database
conn = sqlite3.connect("socials.db")
c = conn.cursor()
c.execute("""
        CREATE TABLE IF NOT EXISTS officers (rank TEXT,
                      full_name TEXT,
                      designation TEXT,
                      service_no TEXT,
                      date_of_birth TEXT,
                      address TEXT,
                      lat TEXT,
                      lon TEXT,
                      contact_numbers TEXT,
                      spouse_name TEXT,
                      date_of_marriage TEXT,
                      date_of_birth_spouse TEXT,
                      child1_name TEXT,
                      child1_dob TEXT,
                      child2_name TEXT,
                      child2_dob TEXT,
                      child3_name TEXT,
                      child3_dob TEXT);
""")
c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (transaction_id TEXT,
                      transaction_type TEXT,
                      service_no TEXT,
                      day INT,
                      month INT,
                      year INT,
                      description TEXT,
                      amount FLOAT
                      );
""")
c.execute("""
        CREATE TABLE IF NOT EXISTS events (service_no TEXT,
                      day INT,
                      month INT,
                      year INT,
                      description TEXT,
                      type TEXT
                      );
""")

c.execute("""
        CREATE TABLE IF NOT EXISTS socialoicinfor (name TEXT,
                      contact_info TEXT,
                      upi TEXT,
                      remarks TEXT,
                      handle TEXT
                      );
""")

st.set_page_config(
    page_title="[SocialOIC] Add Spendings",
    page_icon="🤠",
)

#hashed_passwords = stauth.Hasher(['abc', 'def']).generate()


with open('.streamlit/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

#Function to add or remove page
def delete_page(main_script_path_str, page_name):

    current_pages = get_pages(main_script_path_str)
    for key, value in current_pages.items():
        if value['page_name'] == page_name:
            del current_pages[key]
            break
        else:
            pass
    _on_pages_changed.send()

def add_page(main_script_path_str, page_name):

    pages = get_pages(main_script_path_str)
    main_script_path = Path(main_script_path_str)
    pages_dir = main_script_path.parent / "pages"
    script_path = [f for f in pages_dir.glob("*.py") if f.name.find(page_name) != -1][0]
    script_path_str = str(script_path.resolve())
    pi, pn = page_icon_and_name(script_path)
    psh = calc_md5(script_path_str)
    pages[psh] = {
        "page_script_hash": psh,
        "page_name": pn,
        "icon": pi,
        "script_path": script_path_str,
    }
    _on_pages_changed.send()

def generate_new_transaction_id():
    c.execute("SELECT * FROM transactions")
    trans_list = c.fetchall()
    trans_id_list = [f'{i[0]}' for i in trans_list]
    if len(trans_id_list) > 0:
        num_vals = [int(x[3:]) for x in trans_id_list]
        return f"TRN{str(max(num_vals) + 1).zfill(7)}"
    else:
        return f"TRN{str(1).zfill(7)}"
#-----------------------------------------------------------------------------
#Page Content Starts Here...

st.header("OSG Socials")

name, authentication_status, username = authenticator.login('Login', 'sidebar')



if st.session_state["authentication_status"] is False:
    st.sidebar.error('Username/password is incorrect')
    delete_page("Home.py", "Add_Officer")
    delete_page("Home.py", "Add_Spending")
    delete_page("Home.py", "Add_Payment")
    delete_page("Home.py", "Show_Transactions")
    delete_page("Home.py", "Edit_Officers")
    delete_page("Home.py", "Edit_Transaction")
    st.warning("Not authorised to access this page until logged in.")
elif st.session_state["authentication_status"] is None:
    delete_page("Home.py", "Add_Officer")
    delete_page("Home.py", "Add_Spending")
    delete_page("Home.py", "Add_Payment")
    delete_page("Home.py", "Show_Transactions")
    delete_page("Home.py", "Edit_Officers")
    delete_page("Home.py", "Edit_Transaction")
    st.warning("Not authorised to access this page until logged in.")
elif st.session_state["authentication_status"]:
    st.sidebar.success(f'Welcome *{st.session_state["name"]}*')
    authenticator.logout('Logout', 'sidebar', key='unique_key')
    add_page("Home.py", "Add_Officer")
    add_page("Home.py", "Add_Spending")
    add_page("Home.py", "Add_Payment")
    add_page("Home.py", "Show_Transactions")
    add_page("Home.py", "Edit_Officers")
    add_page("Home.py", "Edit_Transaction")

    st.subheader("Add Spendings")

    c.execute("SELECT * FROM officers")
    offr_names = c.fetchall()
    list_offr_names = [f'[{i[3]}] {i[0]} {i[1]}' for i in offr_names]
    selected_offr = st.multiselect('Select Officer(s)', list_offr_names, list_offr_names)

    selected_service_nos = [x[1:6] for x in selected_offr]


    date_of_transaction = st.date_input("Date of Transaction")
    description = st.text_input("Description")
    amount = st.number_input("Amount")

    if st.button('Add Spending'):
        with st.spinner('Adding to Database.. Please Wait..'):
            for i, ser in enumerate(selected_service_nos):
                trans_id = generate_new_transaction_id()

                with conn:
                    c.execute("INSERT INTO transactions VALUES (:tid, :ttype, :ser, :day, :mon, :year, :desc, :amnt);",
                              {'tid': trans_id,
                              'ttype': 'Spending',
                              'ser': ser,
                              'day': int(str(date_of_transaction).split("-")[2]),
                              'mon': int(str(date_of_transaction).split("-")[1]),
                              'year': int(str(date_of_transaction).split("-")[0]),
                              'desc': description,
                              'amnt': amount})
        st.success("Records added successfully!!")
