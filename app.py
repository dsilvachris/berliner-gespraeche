import streamlit as st
import subprocess
import sys

# Redirect to the actual Streamlit app
st.write("Redirecting to Berliner Gespräche...")
exec(open('streamlit_app.py').read())