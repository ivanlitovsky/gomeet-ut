import streamlit as st
import pandas as pd
import os



def on_optin_change(db):
    print("NEW OPTIN CHANGE")
    print(st.session_state['optin'])
    db.table('survey_answers').upsert({'email': st.session_state['reader'], 'optin': st.session_state['optin']}).execute()
    return

def on_email_change(db):
        if st.session_state['current_input'] != st.session_state['reader']:
            # if the on_change function is called with a new email input

            print("NEW EMAIL INPUT")
            print("new input: ", st.session_state['current_input'])

            if st.session_state['current_input'] is not None and st.session_state['current_input'] != "":
                survey_data = find_email_in_db(db.table('survey_answers'), st.session_state['current_input'])
                
                if len(survey_data) == 0:
                    st.session_state['reader'] = None
                    db.table('login').insert({'email': st.session_state['current_input'], 'type': "NEW_LOGIN", 'success': False}).execute()
                else:
                    st.session_state['reader'] = st.session_state['current_input']
                    st.session_state['survey_data'] = survey_data
                    
                    optin = get_optin(db, st.session_state['current_input'], survey_data)
                    
                    st.session_state['optin'] = optin
                    db.table('login').insert({'email': st.session_state['current_input'], 'type': "NEW_LOGIN", 'success': True, 'optin': optin}).execute()
            
        
    




def init_states():    
    st.session_state['optin'] = False
    st.session_state['reader'] = None
    st.session_state['survey_data'] = None
    st.session_state['matches'] = None

def reformat_match_list(match_list):
    reformatted_data = []
    for i in range(1, 10):
        data = {
            'match_email': match_list[f'pair_name_{i}'],
            'paragraph': match_list[f'paragraph_{i}'],
            'distance': match_list[f'distance_{i}']
        }
        reformatted_data.append(data)
    return reformatted_data


def distance_label(d):
    result = {'label': '', 'color': ''}
    if d <= 0.3:
        result = {'label': 'Top 10% fit!', 'color': 'green'}
    elif d <= 0.5:
        result = {'label': 'Top 30% fit!', 'color': 'blue'}
    else:
        result = {'label': 'Top 50% fit!', 'color': 'orange'}

    return result


#### Database functions

def find_email_in_db(db_table, email):

    survey_data = db_table.select("*").eq("email", email).execute()
    if len(survey_data.data) == 0:
        return []
    else:
        return survey_data.data[0]


def get_optin(db, email, data):
    survey_data = data

    if survey_data == None:
        survey_data = find_email_in_db(db.table('survey_answers'), email)

    optin = False

    if survey_data is not None and len(survey_data) > 0:
        optin = survey_data['optin']
        if optin == None:
            answer_a = "Professional"
            answer_b = "In-person social"
            answer_c = "Remote social"
            answer_d = "Open to anything and everything"
            answer_e = "I want to be part of the social graph"

            optin = (
                answer_a in survey_data['expected_relationships']
                or answer_b in survey_data['expected_relationships']
                or answer_c in survey_data['expected_relationships']
                or answer_d in survey_data['expected_relationships']
                or answer_e in survey_data['expected_relationships']
            )

    return optin


