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
import pandas as pd

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
    page_title="OSG Socials: Bills",
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

def color_type(val):
    color = 'red' if val=='Spending' else 'green'
    return f'background-color: {color}'

def calculate_bill(x):
    total_bill = 0
    for v in x:
        if(v[1] == 'Spending'):
            total_bill = total_bill + v[7]
        elif(v[1] == 'Payment'):
            total_bill = total_bill - v[7]
    return total_bill

def parse_date(d):
    year = d.split("-")[2]
    month = d.split("-")[1].zfill(2)
    day = d.split("-")[0].zfill(2)
    mval = ""
    if month == '01': mval = "Jan"
    if month == '02': mval = 'Feb'
    if month == '03': mval = 'Mar'
    if month == '04': mval = "Apr"
    if month == '05': mval = "May"
    if month == '06': mval = 'Jun'
    if month == '07': mval = 'Jul'
    if month == '08': mval = "Aug"
    if month == '09': mval = 'Sep'
    if month == '10': mval = 'Oct'
    if month == '11': mval = "Nov"
    if month == '12': mval = "Dec"

    return f"{day} {mval} {year[2:]}"
#-----------------------------------------------------------------------------
#Page Content Starts Here...

st.header("OSG Socials")

name, authentication_status, username = authenticator.login('Login', 'sidebar')


if st.session_state["authentication_status"]:
    st.sidebar.success(f'Welcome *{st.session_state["name"]}*')
    authenticator.logout('Logout', 'sidebar', key='unique_key')
    add_page("Home.py", "Add_Officer")
    add_page("Home.py", "Add_Spending")
    add_page("Home.py", "Add_Payment")
    add_page("Home.py", "Show_Transactions")
    add_page("Home.py", "Edit_Officers")
    add_page("Home.py", "Edit_Transaction")
elif st.session_state["authentication_status"] is False:
    st.sidebar.error('Username/password is incorrect')
    delete_page("Home.py", "Add_Officer")
    delete_page("Home.py", "Add_Spending")
    delete_page("Home.py", "Add_Payment")
    delete_page("Home.py", "Show_Transactions")
    delete_page("Home.py", "Edit_Officers")
    delete_page("Home.py", "Edit_Transaction")
elif st.session_state["authentication_status"] is None:
    delete_page("Home.py", "Add_Officer")
    delete_page("Home.py", "Add_Spending")
    delete_page("Home.py", "Add_Payment")
    delete_page("Home.py", "Show_Transactions")
    delete_page("Home.py", "Edit_Officers")
    delete_page("Home.py", "Edit_Transaction")


st.subheader("🧾 Bills Info")
c.execute("SELECT * FROM officers")
offr_names = c.fetchall()
officer_dict = {}
for offr in offr_names:
    officer_dict[f'{offr[3]}'] = f"{offr[0]} {offr[1]}"
list_offr_names = [f'[{i[3]}] {i[0]} {i[1]}' for i in offr_names]
selected_offr = st.selectbox('Select Officer', list_offr_names)

with conn:
    c.execute("SELECT * FROM transactions WHERE service_no = :name", {'name': selected_offr[1:6]})
    #c.execute("SELECT * FROM pbook")
final_list = c.fetchall()

st.metric(label = "Amount to be paid", value = f"₹{round(calculate_bill(final_list), 2)}")


df = pd.DataFrame({'Date': [parse_date(f"{x[3]}-{x[4]}-{x[5]}") for x in final_list],
                   'Transaction ID': [f"{x[0]}" for x in final_list],
                   'Officer': [f"{officer_dict[x[2]]}" for x in final_list],
                   'Description': [f"{x[6]}" for x in final_list],
                   'Type': [f"{x[1]}" for x in final_list],
                   'Amount': [f"₹{x[7]}" for x in final_list]})

st.table(df.sort_values(by=['Transaction ID'], ascending=False).style.applymap(color_type, subset=['Type']))
