#streamlit packages
import streamlit as st
#import streamlit_antd_components as sac

#other packages
import pandas as pd

#custom functions
from tools import *
from sidebar import get_sidebar
from match_info import get_user_info
# Initialize DB
import os
import json
from supabase import create_client, Client

url: str = st.secrets.SUPABASE_URL
key: str = st.secrets.SUPABASE_KEY
supabase: Client = create_client(url, key)

# Initialize session states
if 'current_input' not in st.session_state:
    st.session_state['current_input'] = None
if 'new_optin' not in st.session_state:
    print("here")
    st.session_state['new_optin'] = None
if 'optin' not in st.session_state:
    st.session_state['optin'] = False
if 'reader' not in st.session_state:
    st.session_state['reader'] = None

matched_user_info = None

print("--------------------")
print("NEW LOAD")
print("reader: ", st.session_state['reader'])
print("current_input: ", st.session_state['current_input'])
print("optin: ", st.session_state['optin'])


## --------------------------------
## HEADER
## --------------------------------

st.header('Uncharted Territory Network')

## --------------------------------
## SIDEBAR
## --------------------------------

get_sidebar(supabase)

print("ACTIVE STATES:")
print("reader: ", st.session_state['reader'])
print("current_input: ", st.session_state['current_input'])
print("optin: ", st.session_state['optin'])

## --------------------------------
## Main
## --------------------------------


reformated_list = None


if st.session_state['reader'] is None or st.session_state['optin'] == False:
    st.write('Please enter your email and opt-in using the left panel')
             
else:
    active_reader = st.session_state['reader']
    st.write(f"Welcome {active_reader}!")

    matched_user_data = supabase.table('top_matches').select("*").eq("email", active_reader).execute()
    matched_user_info = None
    if len(matched_user_data.data) > 0:
        matched_user_info = json.loads(matched_user_data.data[0]['top_matches'])

    if matched_user_info is not None:

        #remove opt-out users
        optin_matched_users = []
        for i, match in enumerate(matched_user_info):
            optin = get_optin(supabase, match['matched_email'], None)
            if optin == True:
                optin_matched_users.append(match)

        tabs_list = []

        for i, match in enumerate(optin_matched_users):
            count = i+1
            parts_to_print = f"👤 reader {count}"
            tabs_list.append(parts_to_print)

        st.markdown(f"Meet <span style='color:red;'><b>{len(tabs_list)}</b></span> other UT readers similar to you: ", unsafe_allow_html=True)

        tabs = st.tabs(tabs_list)

        for i, match in enumerate(optin_matched_users):
            with tabs[i]:
                get_user_info(supabase, i, match)


