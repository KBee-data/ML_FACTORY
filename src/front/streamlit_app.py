# src/front/streamlit_app.py

import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("URL_PREDICT_DOCKER")

st.title("Iris Prediction App")

st.write("Enter flower measurements")

sepal_length = st.number_input("Sepal length")
sepal_width = st.number_input("Sepal width")
petal_length = st.number_input("Petal length")
petal_width = st.number_input("Petal width")

if st.button("Predict"):
    payload = {
        "sepal_length": sepal_length,
        "sepal_width": sepal_width,
        "petal_length": petal_length,
        "petal_width": petal_width
    }

    response = requests.post(API_URL, json=payload)

    if response.status_code == 200:
        result = response.json()

        st.success(f"Species: {result['species']}")
        st.write(f"Predicted class: {result['prediction']}")
        #st.write(f"Prediction probability: {result['probabilities']}")
        st.write("Model version:", result["model_version"])

    else:
        st.error(f"API error, API response = {response.status_code}")

        