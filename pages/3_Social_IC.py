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
    page_title="OSG Socials: Social OIC Information",
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

with conn:
    #c.execute("SELECT * FROM pbook WHERE person = :name", {'name': 'Manu'})
    c.execute("SELECT * FROM socialoicinfor")
out = c.fetchone()

if(len(out) == 0):
    st.error("No Social OIC defined!!")
    with conn:
        c.execute("INSERT INTO socialoicinfor VALUES (:name, :contact_info, :upi, :rmks, :handle)",
                  {'name': "To be defined",
                  'contact_info': "To be defined",
                  'upi': "To be defined",
                  'rmks': "To be defined",
                  'handle': "001"
              })

if st.session_state["authentication_status"]:
    st.sidebar.success(f'Welcome *{st.session_state["name"]}*')
    authenticator.logout('Logout', 'sidebar', key='unique_key')
    add_page("Home.py", "Add_Officer")
    add_page("Home.py", "Add_Spending")
    add_page("Home.py", "Add_Payment")
    add_page("Home.py", "Show_Transactions")
    add_page("Home.py", "Edit_Officers")
    add_page("Home.py", "Edit_Transaction")

    st.info("Edit Social IC Information")
    name = st.text_input("Name", out[0])
    contact_info = st.text_input("Contact Information", out[1])
    upi = st.text_input("UPI ID", out[2])
    remarks = st.text_input("Remarks", out[3])

    if st.button("Update Social OIC"):
        with conn:
            c.execute("UPDATE socialoicinfor SET name = :name, contact_info = :contact_info, upi = :upi, remarks = :rmks WHERE handle = :hndl;",
                      {'name': name,
                      'contact_info': contact_info,
                      'upi': upi,
                      'rmks': remarks,
                      'hndl': "001",
                      })
        st.success("Social OIC information updated!")
elif st.session_state["authentication_status"] is False:
    st.sidebar.error('Username/password is incorrect')
    delete_page("Home.py", "Add_Officer")
    delete_page("Home.py", "Add_Spending")
    delete_page("Home.py", "Add_Payment")
    delete_page("Home.py", "Show_Transactions")
    delete_page("Home.py", "Edit_Officers")
    delete_page("Home.py", "Edit_Transaction")

    st.subheader("👨‍💼 Socials OIC Info")
    st.markdown(f"""
        ##### 🧑🏻 Name
        **{out[0]}**

        ##### 📱 Contact Information
        {out[1]}

        ##### 💳 UPI ID
        {out[2]}

        ##### 📋 Remarks
        {out[3]}
    """)
elif st.session_state["authentication_status"] is None:
    delete_page("Home.py", "Add_Officer")
    delete_page("Home.py", "Add_Spending")
    delete_page("Home.py", "Add_Payment")
    delete_page("Home.py", "Show_Transactions")
    delete_page("Home.py", "Edit_Officers")
    delete_page("Home.py", "Edit_Transaction")


    st.subheader("👨‍💼 Socials OIC Info")
    st.markdown(f"""
        ##### 🧑🏻 Name
        **{out[0]}**

        ##### 📱 Contact Information
        {out[1]}

        ##### 💳 UPI ID
        {out[2]}

        ##### 📋 Remarks
        {out[3]}
    """)
