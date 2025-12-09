import streamlit as st
from requests import get
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import sqlite3

# sidebar / navigation content

# ==== URLS for scraping (Doit rester ici pour être accessible aux boutons du sidebar) ====
URLS = { 
    "1 Chiens": "https://sn.coinafrique.com/categorie/chiens?p=",
    "2 Moutons": "https://sn.coinafrique.com/categorie/moutons?p=",
    "3 Poules palin-pigeon": "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons?p=",
    "4 Autres animaux": "https://sn.coinafrique.com/categorie/autres-animaux?p=",
}

# ==== URLS des formulaires (Doit rester ici pour st.link_button) ====
URL_KOBO_COL = "https://ee.kobotoolbox.org/x/6jJY3cS1"
URL_GOOGLE_F = "https://docs.google.com/forms/d/e/1FAIpQLScJ1DTN0b6OIWgKyK55t5fF1B0Du7jznbSwqQCKYuFRtBZybQ/viewform?usp=header"

def render_sidebar():

    with st.sidebar:
        st.header("⚙️ Parameters & Actions")
        #st.markdown("### Select an action :")
        choice = st.selectbox('',
            [
                "1. Scrape data",
                "2. Download data already scraped",
                "3. View a dashboard of data",
                "4. Fill in an app evaluation"
            ],
            key="main_select"
        )
        st.session_state.current_choice = choice
        
        #st.markdown("---")
        
        # === 2. OPTION 1 : SCRAPE DATA  ===
        if choice == "1. Scrape data":
            st.markdown("#### Scraping parameters")
            
            # === Choix de l'url ====
            st.write("Choose one URL :")
            url_cols = st.columns(2)
            
            for i, url_key in enumerate(URLS.keys()):
                with url_cols[i % 2]:
                    if st.button(url_key, key=f"btn_url_{i}_s", use_container_width=True):
                        st.session_state.selected_url_key = url_key
                        st.session_state.scraped_df = None
                        st.session_state.action_status = "url_selected"
                        
            st.info(f"Selected URL: **{st.session_state.selected_url_key}**")

            # B. Plage de pages
            st.number_input("Input start web page number:", min_value=1, value=1, key="start_page")
            st.number_input("Imput end web page number:", min_value=1, value=5, key="end_page")
            
            st.markdown("---")

            # C. Bouton Lancer
            if st.button("🚀 Start the scraping", key="btn_scrape_launch_s", use_container_width=True):
                if st.session_state.start_page > st.session_state.end_page:
                    st.error("Start page number must be less or equal to the end page number.")
                else:
                    st.session_state.scrape_pending = True
                    st.session_state.action_status = "scraping_requested" 

        # --- OPTION 2 : DOWNLOAD DATA ---
        elif choice == "2. Download data already scraped":
            st.markdown("#### Download options")
            st.write("Choose the dataset to download:")
            
            dl_cols = st.columns(2)
            for i, dl_key in enumerate(URLS.keys()):
                 with dl_cols[i % 2]:
                    if st.button(dl_key, key=f"btn_dl_{i}_s", use_container_width=True):
                        st.session_state.download_key = dl_key 
                        st.session_state.action_status = "download_selected"
        
        # --- 4. OPTION 3 : DASHBOARD ---
        elif choice == "3. View a dashboard of data":
            st.markdown("#### Dashboard Parameters")
            st.write("No parameters needed for now.")
            
        # --- 5. OPTION 4 : EVALUATION ---
        elif choice == "4. Fill in an app evaluation":
            st.markdown("#### Evaluation Platform")
            st.warning("Select the platform:")
            
            if st.link_button("➡️ Open KoboCollect Form", url=URL_KOBO_COL, use_container_width=True):
                st.session_state.action_status = "kobo_clicked"
                
            if st.link_button("➡️ Open Google Form", url=URL_GOOGLE_F, use_container_width=True):
                st.session_state.action_status = "google_clicked"
    return choice