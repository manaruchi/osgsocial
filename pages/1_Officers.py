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
#Database query to show all officers


st.set_page_config(
    page_title="OSG Socials: Officers",
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
def parse_date(d):
    year = d.split("-")[0]
    month = d.split("-")[1]
    day = d.split("-")[2]
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


st.subheader("🤵 Officers Info")
#Database Query to show all Officers
c.execute("SELECT * FROM officers")
offr_names = c.fetchall()
list_offr_names = [f'[{i[3]}] {i[0]} {i[1]}' for i in offr_names]
selected_offr = st.selectbox('Select Officer', list_offr_names)

if st.button("🔍 Show"):

    sel_service_no = selected_offr[1:6]
    if(sel_service_no == '38079'):
        st.success("👑 Developer of this application...")
    with conn:
        c.execute("SELECT * FROM officers WHERE service_no = :x", {'x': sel_service_no})
    sel_offr_dict = c.fetchone()

    st.subheader(selected_offr)
    st.info('🤵 Personal Information')
    st.markdown(f"""
        ##### Designation
        **{sel_offr_dict[2]}**

        ##### Address
        {sel_offr_dict[5]}

        [Show in Map](http://maps.google.com/maps?z=12&t=k&q=loc:{sel_offr_dict[6]}+{sel_offr_dict[7]})

        ##### Date of Birth
        {parse_date(sel_offr_dict[4])}

        ##### Contact Information
        {sel_offr_dict[8]}

    """)


    if(sel_offr_dict[9] != 'NA'):
        st.info("💑🏻 Spouse")
        st.markdown(f"""
            ##### Spouse
            {sel_offr_dict[9]}

            ##### Date of Marriage
            {parse_date(sel_offr_dict[10])}

            ##### Birthday of Spouse
            {parse_date(sel_offr_dict[11])}

        """)

    if(sel_offr_dict[12] != 'NA'):
        st.info("👨‍👨‍👧‍👦 Children")
        st.markdown(f"""
            ##### {sel_offr_dict[12]}
            Birthday: {parse_date(sel_offr_dict[13])}
        """)
        if(sel_offr_dict[14] != 'NA'):
            st.markdown(f"""
                ##### {sel_offr_dict[14]}
                Birthday: {parse_date(sel_offr_dict[15])}
            """)
            if(sel_offr_dict[16] != 'NA'):
                st.markdown(f"""
                    ##### {sel_offr_dict[16]}
                    Birthday: {parse_date(sel_offr_dict[17])}
                """)




    #st.write(sel_offr_dict)
