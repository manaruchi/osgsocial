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
from datetime import datetime, timedelta

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
    page_title="OSG Socials: Homepage",
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


def parse_date(d,month):
    month = str(month).zfill(2)
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

    return f"{str(d).zfill(2)} {mval}"

def calcth(yr):
    cur_yr = datetime.now().year
    yr_diff = cur_yr - yr
    if(yr_diff == 1 or yr_diff == 21 or yr_diff == 31 or yr_diff == 41 or yr_diff == 51 or yr_diff == 61 or yr_diff == 71 or yr_diff == 81 or yr_diff == 91):
        return f"{yr_diff}st"
    elif(yr_diff == 2 or yr_diff == 22 or yr_diff == 32 or yr_diff == 42 or yr_diff == 52 or yr_diff == 62 or yr_diff == 72 or yr_diff == 82 or yr_diff == 92):
        return f"{yr_diff}nd"
    elif(yr_diff == 3 or yr_diff == 23 or yr_diff == 33 or yr_diff == 43 or yr_diff == 53 or yr_diff == 63 or yr_diff == 73 or yr_diff == 83 or yr_diff == 93):
        return f"{yr_diff}rd"
    else:
        return f"{yr_diff}th"

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

with conn:
    #c.execute("SELECT * FROM pbook WHERE person = :name", {'name': 'Manu'})
    c.execute("SELECT * FROM events")
out = c.fetchall()


st.subheader("Today's Event(s)")
with st.spinner("Generating List..."):
    tdate = int(datetime.now().day)
    tmon = int(datetime.now().month)
    events_in_month = 0
    for v in out:
        if(v[1] == tdate and v[2] == tmon):
            events_in_month = events_in_month + 1
            if(v[5] == "BD"):
                st.info(f"🎂 **{calcth(v[3])} {v[4]}**")
            if(v[5] == "AN"):
                st.warning(f"💑 **{calcth(v[3])} {v[4]}**")
    if(events_in_month == 0):
        st.info(f"*No events today..*")
st.subheader("Upcoming Event(s)")
with st.spinner("Generating List..."):
    upcoming_events = 0
    for i in range(1,10):
        new_date = datetime.today() + timedelta(days = i)
        tdate = int(new_date.day)
        tmon = int(new_date.month)
        for v in out:
            if(v[1] == tdate and v[2] == tmon):
                upcoming_events = upcoming_events + 1
                if(v[5] == "BD"):
                    st.info(f"[{i} days to go] {parse_date(v[1], v[2])} 🎂 **{calcth(v[3])} {v[4]}**")
                if(v[5] == "AN"):
                    st.warning(f"[{i} days to go] {parse_date(v[1], v[2])} 💑 **{calcth(v[3])} {v[4]}**")
    if(upcoming_events == 0):
        st.info(f"*No events in next 10 days...*")

st.subheader("Stats")
with st.spinner("Calculating Stats..."):
    col1, col2, col3 = st.columns(3)
    c.execute("SELECT * FROM officers")
    offr_names = c.fetchall()
    col1.metric("Officers", len(offr_names))
    col2.metric("Events", len(out))


    c.execute("SELECT * FROM transactions")
    trans_list = c.fetchall()
    if len(trans_list) > 0:
        tot_bal = 0
        for t in trans_list:
            if(t[1] == 'Payment'):
                tot_bal = tot_bal + t[7]
            else:
                tot_bal = tot_bal - t[7]
        if(trans_list[-1][1] == 'Payment'):
            delta_text = f"₹{round(trans_list[-1][7], 2)}"
        else:
            delta_text = f"-₹{round(trans_list[-1][7],2)}"
        col3.metric("Total Balance", f"₹{round(tot_bal, 2)}", delta_text)
