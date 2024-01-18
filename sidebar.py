#streamlit packages
import streamlit as st
#import streamlit_antd_components as sac

#other packages
import pandas as pd

#custom functions
from tools import *

import time


def get_sidebar(db):
    with st.sidebar:
        with st.form(f"login_form"):
            st.subheader("Your email")
            survey_url = "https://docs.google.com/forms/d/e/1FAIpQLSfdX1OYcs4nK5y7MKq4LpP8kwZU6YHqgI7fw3koh1PV4HKdIA/viewform"

            email_input = st.text_input(
                "The same email you used in the survey",
                label_visibility="visible",
                disabled=False,
                placeholder="hello@mail.com",
                #on_change = on_email_change(db),
                #key = "current_input" 
            )

            #st.markdown(f"""
            #    <small>Survey <a href="{survey_url}">link</a></small>
            #    """, unsafe_allow_html=True)
                      

            st.write(' ')

            optin_button = st.toggle(
                    label = "Opt-in",
                    value = False,
                    #value = st.session_state['optin'],
                    #on_change = on_optin_change(db),
                    #key = "optin"
            )

            st.caption('By opting-in you accept to become visible to other UT members.')

            login_button = st.form_submit_button("Load", type="primary")

            if login_button:
                progress_text = "Loading data..."
                my_bar = st.progress(0, text=progress_text)
                time.sleep(0.01)
                my_bar.progress(10, text=progress_text)
                time.sleep(0.01)

                if (email_input == ""):
                    my_bar.progress(100, text=progress_text)
                    time.sleep(0.5)
                    my_bar.empty()
                    st.write("❌ Please write your email!")
                else:
                    my_bar.progress(20, text=progress_text)
                    survey_data = find_email_in_db(db.table('survey_answers'), email_input)
                    my_bar.progress(70, text=progress_text)
                    time.sleep(0.1)
                    if len(survey_data) == 0:
                        db.table('login').insert({'email': email_input, 'type': "NEW_LOGIN", 'success': False}).execute()
                        my_bar.progress(100, text=progress_text)
                        time.sleep(1)
                        my_bar.empty()
                        st.write("❌ Email not found")
                    else:
                        my_bar.progress(85, text=progress_text)
                        time.sleep(0.1)
                        st.session_state['survey_data'] = survey_data
                        st.session_state['reader'] = email_input
                        if optin_button == False:
                            db.table('login').insert({'email': email_input, 'type': "NEW_LOGIN", 'success': True, 'optin': False}).execute()
                            db.table('survey_answers').upsert({'email': email_input, 'optin': False}).execute()
                            st.session_state['optin'] = False
                            
                            my_bar.progress(100, text=progress_text)
                            time.sleep(1)
                            my_bar.empty()
                            
                            st.write("❌ Please opt-in to see other UT members!")
                        else:
                            db.table('login').insert({'email': email_input, 'type': "NEW_LOGIN", 'success': True, 'optin': True}).execute()
                            db.table('survey_answers').upsert({'email': email_input, 'optin': True}).execute()
                            st.session_state['optin'] = True

                            my_bar.progress(100, text=progress_text)
                            time.sleep(1)
                            my_bar.empty()

                            st.write(f"✅ Welcome back {email_input}")


        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        with st.form(f"feedback_form", border = False):
            st.write("Help us improve!")
            st.caption("This is an experimental Product, so your feedback is invaluable!")
            feedback_input = st.text_area("Send us feedback", key =  f"feedback_sidebar", height=50)
            button_send = st.form_submit_button("Send")
            if button_send:
                db.table('feedback').insert({'reader': st.session_state['reader'], 'content': feedback_input}).execute()
                st.write(f"✅ You feedback has been sent!")