#streamlit packages
import streamlit as st
import streamlit_antd_components as sac

#other packages
import pandas as pd

#custom functions
from tools import *


def get_sidebar(db):
    with st.sidebar:
        input = st.text_input(
            "Your email",
            label_visibility="visible",
            disabled=False,
            placeholder="email used in survey",
            on_change = on_email_change(db),
            key = "current_input" 
        )

        if st.session_state['reader'] is None:
            survey_url = "https://docs.google.com/forms/d/e/1FAIpQLSfdX1OYcs4nK5y7MKq4LpP8kwZU6YHqgI7fw3koh1PV4HKdIA/viewform"
            st.markdown(f"""
                <small>Use the same email you used in the <a href="{survey_url}">survey</a></small>
                """, unsafe_allow_html=True)
        else:            
            st.divider()

            st.write('Opt-in')

            st.toggle(
                    label = "Opt-in",
                    #value = st.session_state['optin'],
                    on_change = on_optin_change(db),
                    key = "optin"
            )

            st.caption('To see other UT members, you need to opt-in first. By opting-in, you accept that your email will be shared with other UT members.')


            st.divider()

            with st.form(f"feedback_form", border = False):
                st.write("Help us improve!")
                st.caption("This is an experimental Product, so your feedback is invaluable!")
                feedback_input = st.text_area("Send us feedback", key =  f"feedback_sidebar", height=50)
                button_send = st.form_submit_button("Send")
                if button_send:
                    db.table('feedback').insert({'reader': st.session_state['reader'], 'content': feedback_input}).execute()
                    st.write(f"✅ You feedback has been sent!")