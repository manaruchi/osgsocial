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
import datetime
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
    page_title="[SocialOIC] Edit Transactions",
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

    st.subheader("Edit Transactions")
    c.execute("SELECT * FROM transactions")
    transactions = c.fetchall()

    list_trans = [f'{i[0]}' for i in transactions]
    selected_trans = st.selectbox('Transactions', list_trans)

    with conn:
        c.execute("SELECT * FROM transactions WHERE transaction_id = :x", {'x': selected_trans})
    sel_trans_dict = c.fetchone()

    #st.write(sel_trans_dict)
    trans_type = sel_trans_dict[1]
    if(trans_type == 'Payment'):
        st.success("[{}] Transaction Type: {}".format(selected_trans, trans_type))
    else:
        st.error("[{}] Transaction Type: {}".format(selected_trans, trans_type))

    def_val = datetime.date(sel_trans_dict[5], sel_trans_dict[4], sel_trans_dict[3])
    date_of_transaction = st.date_input("Date of transaction", def_val)
    s_no = st.text_input("Service Number", sel_trans_dict[2])
    description = st.text_input("Description", sel_trans_dict[6])
    amount = st.number_input("Amount", value = sel_trans_dict[7])

    if st.button("Update Transaction"):

        with conn:
            c.execute("UPDATE transactions SET service_no = :ser, day = :day, month = :month, year = :year, description = :desc, amount = :amnt WHERE transaction_id = :transid;",
                      {'ser': s_no,
                      'day': int(str(date_of_transaction).split("-")[2]),
                      'month': int(str(date_of_transaction).split("-")[1]),
                      'year': int(str(date_of_transaction).split("-")[0]),
                      'desc': description,
                      'amnt': amount,
                      'transid': selected_trans})
        st.success(f"Transaction with ID *{selected_trans}* is updated!", icon="✅")

    if st.button("Delete Transaction"):

        try:
            with conn:
                c.execute("DELETE FROM transactions WHERE transaction_id = :t;",
                          {'t': selected_trans})
            st.success(f"Record with transaction ID *{selected_trans}* removed successfully!", icon="✅")
        except:
            st.warning('Something went wrong! Try Again.', icon="⚠️")
