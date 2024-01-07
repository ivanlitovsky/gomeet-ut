import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

    

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


def on_optin_change():
    return

def on_email_change():
    return



#### Firestore functions

def find_email_in_firestore(collection_name, email):
    db = firestore.client()
    query = db.collection(collection_name).where('email', '==', email).limit(1)
    matches = query.get()
    if matches:
        return matches[0].to_dict()
    else:
        return None


def update_firestore(collection_name, document_id, data):
    if not document_id:
        return
    else:
        db = firestore.client()
        doc_ref = db.collection(collection_name).document(document_id)
        if doc_ref.get().exists:
            doc_ref.update(data)


