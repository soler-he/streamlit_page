import streamlit as st

from page_config import setup

setup()

st.title("SOLER Catalogues")

st.markdown('The [SOLER](https://soler-horizon.eu) project provides three interlinked catalogues focusing on different aspects of energetic solar eruptions: solar flares, coronal mass ejections (CME), and solar energetic particles (SEP).')

st.write('Select the catalogue you want to explore:')

st.page_link("pages/cme_catalogue.py", label="CME catalogue", icon="1️⃣")
st.page_link("pages/flare_catalogue.py", label="Flare catalogue", icon="2️⃣")
st.page_link("pages/sep_catalogue.py", label="SEP catalogue", icon="3️⃣")

# st.write('Open the sidebar (">>" in the top left) for options.')


st.markdown("""
            #### Acknowledgement

            <img hspace="10px" align="right" height="80px" src="https://github.com/user-attachments/assets/28c60e00-85b4-4cf3-a422-6f0524c42234" alt="EU flag">
            <img align="right" height="80px" src="https://github.com/user-attachments/assets/5bec543a-5d80-4083-9357-f11bc4b339bd" alt="SOLER logo">

            These catalogues are developed within the SOLER (*Energetic Solar Eruptions: Data and Analysis Tools*) project. SOLER has received funding from the European Union’s Horizon Europe programme under grant agreement No 101134999.

            The catalogues reflects only the authors’ view and the European Commission is not responsible for any use that may be made of the information it contains.
            """, unsafe_allow_html=True)
