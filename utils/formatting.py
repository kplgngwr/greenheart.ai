import streamlit as st
from PIL import Image
import os

def display_uploaded_image(image):
    st.image(image, caption="Uploaded Image", use_container_width=True)

def format_project():
    st.markdown("""
    <style>
        .css-18e3th9 {
            padding: 5rem 1rem 1rem 1rem;
        }
        .main {
            background-color: #0C0C0C;
            font-family: 'Sans-Serif';
        }
    </style>
    """, unsafe_allow_html=True)

def intro():
    # Using relative path instead of absolute path
    heading = Image.open("assets/title-greenheart.png")
    st.image(heading)

    st.write("""
    **Welcome to the Leaf Disease Analyzer!**
    Upload a leaf image, and our advanced AI model will analyze it for potential diseases and suggest corrective measures.
    
    ### Features:
    - 🧠 **AI-powered Analysis** for detecting diseases, infestations, or deficiencies.
    - 📈 **Detailed Report** with actionable insights.
    - 🌿 **Sustainable Recommendations** for long-term plant health.

    Please upload a clear image of the leaf for an accurate analysis.
    """)

def outro():
    # Using relative path instead of absolute path
    heading = Image.open("assets/thankyou.png")
    st.image(heading)