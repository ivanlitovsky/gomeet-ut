#streamlit packages
import streamlit as st
#import streamlit_antd_components as sac

#other packages
import pandas as pd

#custom functions
from tools import *
from map import *
from sidebar import *
from match_info import *
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

st.header('Uncharted Territories Network')

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
    url = "https://docs.google.com/forms/d/e/1FAIpQLSfdX1OYcs4nK5y7MKq4LpP8kwZU6YHqgI7fw3koh1PV4HKdIA/viewform"
    st.markdown(f"If you didn't fill the survey, you can do it here: [Survey Link]({url})", unsafe_allow_html=True)
    st.caption("Note: once you filled the survey, it takes around 24h to be processed.")
             
else:
    active_reader = st.session_state['reader']

    matched_user_data = supabase.table('top_matches').select("*").eq("email", active_reader).execute()
    matched_user_info = None
    if len(matched_user_data.data) > 0:
        matched_user_info = json.loads(matched_user_data.data[0]['top_matches'])

    if matched_user_info is not None:
        #show map
        plot_map(st.session_state['reader'], supabase)
        st.divider()

        #load matched users data
        db_filter = []
        for i, match in enumerate(matched_user_info):
            db_filter.append(match['matched_email'])

        all_matches_survey_data = supabase.table('survey_answers').select("*").in_('email', db_filter).execute()

        #remove opt-out users
        st.session_state['matches_survey_data'] = []
        for i, match in enumerate(all_matches_survey_data.data):
            optin = get_optin(match)
            if optin == True:
                st.session_state['matches_survey_data'].append(match)

        #display tabs
        tabs_list = []
        matched_email_list = [st.session_state['reader']]

        for i, match in enumerate(st.session_state['matches_survey_data']):
            count = i+1
            parts_to_print = f"👤 reader {count}"
            tabs_list.append(parts_to_print)
            matched_email_list.append(match['email'])

        #load all summaries of matched emails
        summaries_list_full = supabase.table('summaries').select("*").in_('email', matched_email_list).execute()

        st.markdown(f"Meet <span style='color:red;'><b>{len(tabs_list)}</b></span> other UT readers similar to you: ", unsafe_allow_html=True)

        tabs = st.tabs(tabs_list)

        for i, match in enumerate(st.session_state['matches_survey_data']):
            with tabs[i]:
                get_user_info(supabase, i, match, summaries_list_full.data)


