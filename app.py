#streamlit packages
import streamlit as st
import streamlit_antd_components as sac

#other packages
import pandas as pd

#custom functions
from tools import *



if 'optin' not in st.session_state:
    st.session_state['optin'] = False
if 'reader' not in st.session_state:
    st.session_state['reader'] = None
match_list = None



st.write('Go meet with the')
st.header('Uncharted Territory Network')


with st.sidebar:
    input = st.text_input(
        "Your email",
        label_visibility="visible",
        disabled=False,
        placeholder="email used in survey",
        on_change = on_email_change
    )
    st.session_state['reader'] = input
    
    match_list = find_email_in_firestore('readers', st.session_state['reader'])
    if match_list is None:
        st.session_state['optin'] = False
        st.session_state['reader'] = None

        st.caption('email not found')
    else:

        if match_list['optin'] == True:
            st.session_state['optin'] = True
        else:
            st.session_state['optin'] = False

    st.empty()
    st.divider()

    if st.session_state['reader'] is not None:
        st.write('Opt-in')
        val = st.session_state['optin']
        switch = sac.switch(
            value = val,
            on_change = on_optin_change,
            key = "new_optin"
        )
        st.caption('To see other UT members, you need to opt-in first. By opting-in, you accept that your email will be shared with other UT members.')
        st.session_state['optin'] = switch

        update_firestore('readers', st.session_state['reader'], {'optin': st.session_state['optin']})



reformated_list = None


if st.session_state['reader'] is None or st.session_state['optin'] == False:
    st.write('Please enter your email and opt-in')
             
else:
    st.write('Top 10 UT readers matched with: ', st.session_state['reader'])

    if match_list is not None:
        for i, match in enumerate(match_list['matches']):
            st.write('')
            st.divider()

            if match['distance'] <= 0.3:
                sac.tags([sac.Tag(label="Very Strong Fit!", color='green', bordered=True)], key = f"Match #{i+1}")
            elif match['distance'] <= 0.5:
                sac.tags([sac.Tag(label="Good Fit", color='blue', bordered=True)], key = f"Match #{i+1}")
            else:
                sac.tags([sac.Tag(label="Medium Fit", color='orange', bordered=True)], key = f"Match #{i+1}")

            st.write(match['paragraph'])
            st.caption(match['match_email'])

    ##########
    # For debug
    #st.divider()

    #st.write(match_list)
