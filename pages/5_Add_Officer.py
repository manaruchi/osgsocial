import streamlit as st
import streamlit_authenticator as stauth
import yaml
import sqlite3
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
    page_title="[SocialOIC] Add Officers",
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

    #Main content of the page--------------------------------------------------
    st.subheader("Add Officer")
    st.info('Donot leave field blank. Enter NA if no value available...')
    service_no = st.text_input("Service Number (without suffix)", max_chars=5)
    rank = st.text_input("Rank")
    full_name = st.text_input("Full Name")
    designation = st.text_input("Designation")
    date_of_birth = st.date_input("Date of Birth")
    address = st.text_input("Address")
    address_lat = st.text_input("Address Latitude")
    address_lon = st.text_input("Address Longitude")
    contact_numbers = st.text_input("Contact Numbers")
    spouse_name = st.text_input("Spouse Name", "NA")
    date_of_marriage = st.date_input("Date of Marriage")
    date_of_birth_spouse = st.date_input("Date of Birth of Spouse")
    child1_name = st.text_input("Child 1 Name", "NA")
    child1_dob = st.date_input("Child 1 Date of Birth")
    child2_name = st.text_input("Child 2 Name", "NA")
    child2_dob = st.date_input("Child 2 Date of Birth")
    child3_name = st.text_input("Child 3 Name", "NA")
    child3_dob = st.date_input("Child 3 Date of Birth")

    if st.button('Add Officer'):
        c.execute("SELECT * FROM officers")
        offr_names = c.fetchall()
        list_offr_names = [f'{i[3]}' for i in offr_names]
        if(service_no in list_offr_names):
            st.warning("Officer of same Service Number already exists!!!")
        else:
            try:
                with conn:
                    c.execute("INSERT INTO officers VALUES (:rank, :fn, :des, :ser, :dob, :add, :lat, :lon, :con, :spn, :dom, :spnb, :c1n, :c1dob, :c2n, :c2dob, :c3n, :c3dob)",
                              {'rank': rank,
                              'fn': full_name,
                              'des': designation,
                              'ser': service_no,
                              'dob': date_of_birth,
                              'add': address,
                              'lat': address_lat,
                              'lon': address_lon,
                              'con': contact_numbers,
                              'spn': spouse_name,
                              'dom': date_of_marriage,
                              'spnb': date_of_birth_spouse,
                              'c1n': child1_name,
                              'c1dob': child1_dob,
                              'c2n': child2_name,
                              'c2dob': child2_dob,
                              'c3n': child3_name,
                              'c3dob': child3_dob,
                              })
                    # Lets add birthday of the Officer
                    c.execute("INSERT INTO events VALUES (:ser, :day, :mon, :year, :desc, :type)",
                              {'ser': service_no,
                              'day': int(str(date_of_birth).split("-")[2]),
                              'mon': int(str(date_of_birth).split("-")[1]),
                              'year': int(str(date_of_birth).split("-")[0]),
                              'desc': f"Birthday of {rank} {full_name}",
                              'type': 'BD'
                              })

                    if(spouse_name != 'NA'):
                        c.execute("INSERT INTO events VALUES (:ser, :day, :mon, :year, :desc, :type)",
                                  {'ser': service_no,
                                  'day': int(str(date_of_marriage).split("-")[2]),
                                  'mon': int(str(date_of_marriage).split("-")[1]),
                                  'year': int(str(date_of_marriage).split("-")[0]),
                                  'desc': f"Anniversary of {rank} {full_name} and {spouse_name}",
                                  'type': 'AN'
                                  })
                        c.execute("INSERT INTO events VALUES (:ser, :day, :mon, :year, :desc, :type)",
                                  {'ser': service_no,
                                  'day': int(str(date_of_birth_spouse).split("-")[2]),
                                  'mon': int(str(date_of_birth_spouse).split("-")[1]),
                                  'year': int(str(date_of_birth_spouse).split("-")[0]),
                                  'desc': f"Birthday of {spouse_name}, P/O {rank} {full_name}",
                                  'type': 'BD'
                                  })
                    if(child1_name != "NA"):
                        c.execute("INSERT INTO events VALUES (:ser, :day, :mon, :year, :desc, :type)",
                                  {'ser': service_no,
                                  'day': int(str(child1_dob).split("-")[2]),
                                  'mon': int(str(child1_dob).split("-")[1]),
                                  'year': int(str(child1_dob).split("-")[0]),
                                  'desc': f"Birthday of {child1_name}, C/O {rank} {full_name}",
                                  'type': 'BD'
                                  })
                    if(child2_name != "NA"):
                        c.execute("INSERT INTO events VALUES (:ser, :day, :mon, :year, :desc, :type)",
                                  {'ser': service_no,
                                  'day': int(str(child2_dob).split("-")[2]),
                                  'mon': int(str(child2_dob).split("-")[1]),
                                  'year': int(str(child2_dob).split("-")[0]),
                                  'desc': f"Birthday of {child2_name}, C/O {rank} {full_name}",
                                  'type': 'BD'
                                  })
                    if(child3_name != "NA"):
                        c.execute("INSERT INTO events VALUES (:ser, :day, :mon, :year, :desc, :type)",
                                  {'ser': service_no,
                                  'day': int(str(child3_dob).split("-")[2]),
                                  'mon': int(str(child3_dob).split("-")[1]),
                                  'year': int(str(child3_dob).split("-")[0]),
                                  'desc': f"Birthday of {child3_name}, C/O {rank} {full_name}",
                                  'type': 'BD'
                                  })
                st.success(f"[{service_no}] {rank} {full_name} is added to the Database!", icon="✅")
            except:
                st.warning('Something went wrong while adding the officer! Try Again.', icon="⚠️")
