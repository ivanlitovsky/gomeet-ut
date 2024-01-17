#streamlit packages
import streamlit as st
#import streamlit_antd_components as sac

#other packages
import pandas as pd
import time

#custom functions
from tools import *

#OpenAI
import json
from openai import OpenAI
client = OpenAI(api_key=st.secrets.OPENAI_API_KEY,)



def get_user_info(db, index, match):
    progress_text = "Loading data..."
    my_bar = st.progress(0, text=progress_text)
    time.sleep(0.01)
    my_bar.progress(10, text=progress_text)


    ######
    ## Show what readers have in commong
    ######

    summary_reader_v1 = find_email_in_db(db.table("summaries"), st.session_state['reader'])
    my_bar.progress(20, text=progress_text)
    summary_reader_v2 = find_email_in_db(db.table("summaries"), match['matched_email'])
    my_bar.progress(30, text=progress_text)
    
    #Call chatGPT
    prompt = f"<<Primary reader>>\n {summary_reader_v1['paragraph']} \n\n <<Secondary reader>>\n {summary_reader_v2['paragraph']}"
    system_prompt = '''
        Explain in 1 or 2 sentences what these 2 Uncharted territory readers have in common.\n
        Do not mention anything about uncharted territory or UT.\n
        Explain what specifically in their experience, interest or hobbies they have in common. \n\n
        --Output Format--\n
        1. Start with 'You both ...'
        2. Very important: Mark the important keywords representing what these 2 readers have in common, by surrounding them with double asterisks (**)
    '''

    # Call the OpenAI API to generate a summary
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    for percent_complete in range(30,100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()


    st.write(response.choices[0].message.content)

    ######
    ## Display readers info
    ######

    survey_data = find_email_in_db(db.table("survey_answers"), match['matched_email'])

    # Distance
    #d_labels = distance_label(match['distance'])
    #sac.tags([sac.Tag(label=d_labels['label'], color=d_labels['color'], bordered=True)], key = f"Match #{index+1}")

    #Shared interests
    #shared_int_raw = db.table('shared_interests').select("*").eq("reader_1",st.session_state['reader']).eq("reader_2", match['matched_email']).execute()
    #shared_int = shared_int_raw.data

    #if len(shared_int) > 0:
    #    st.write(shared_int[0]['shared_interests'])

    # Summary
    st.write(" ")
    st.write(" ")
    #st.divider()
    with st.expander(f"More about reader {index+1} 👤"):
    #with st.expander(summaries['summary_v2']):
        st.write(f"**Gender**: {survey_data['gender']}")
        st.write(f"**Experience**: {survey_data['experience']}")
        st.write(f"**Interests**: {survey_data['interests']}")
        st.write(f"**Hobbies**: {survey_data['hobbies']}")
        #st.caption(f"💡 This is auto-generated from the reader's survey.")


    # Contact Form
    email_history_raw = db.table('intro_emails').select("*").eq("sender", st.session_state['reader']).eq("receiver", match['matched_email']).execute()

    last_email_sent = ""
    if len(email_history_raw.data) > 0:
        last_email_sent = email_history_raw.data[0]['content']

    if last_email_sent != "":
        st.divider()
        st.write("✅ You sent a message to this reader!")
        st.write(f"Content: {last_email_sent}")
        st.caption(f"You wrote it on: {email_history_raw.data[0]['created_at']}")
        st.caption("💡 We are sending email intros manually for now, expect 1 or 2 days delay")

    if last_email_sent == "":
        st.write(" ")
        st.write(" ")
        with st.form(f"contact_form_{index+1}"):
            st.write("Contact this other reader!")
            st.caption("Write an intro message, we'll send it to the other reader's email. If they accept, we'll put you both in touch!")
        
            message_input = st.text_area("Your message", height=100, placeholder="Hey! we are a match on UT! I'd love to grab a virtual coffee for a casual chat")

            # Every form must have a submit button.
            submitted = st.form_submit_button("Send")
            if submitted:
                if (message_input == ""):
                    st.write("❌ Please write a message!")
                else:
                    db.table('intro_emails').insert({'sender': st.session_state['reader'], 'receiver': match['matched_email'], 'content': message_input}).execute()
                    st.rerun()

