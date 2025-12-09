import streamlit as st
import pandas as pd
import numpy as np
import os
import numpy as np
import sqlite3

# Importations des fichiers séparés
from fscraper import scrape_web_pages, save_to_sql_db, laod_from_sql_db
from navigation import render_sidebar, URLS, URL_KOBO_COL, URL_GOOGLE_F # Sidedarr and urls


# ==== Chemins des Fichiers CSV pour l'Option 2 ====
DATA_PATHS = {
    "1 Chiens": "data/coinafrica_chiens_ok.csv",
    "2 Moutons": "data/coinafrica_moutons_ok.csv",
    "3 Poules palin-pigeon": "data/coinafrica_poules_lap_pi_ok.csv",
    "4 Autres animaux": "data/coinafrica_autres_ani_ok.csv",
}

# ===== Initialisation Session =====
if 'action_status' not in st.session_state:
    st.session_state.action_status = ""
if 'current_choice' not in st.session_state:
    st.session_state.current_choice = "1. Scrape data"
if 'scraped_df' not in st.session_state:
    st.session_state.scraped_df = None
if 'selected_url_key' not in st.session_state:
    st.session_state.selected_url_key = list(URLS.keys())[0]
if 'scrape_pending' not in st.session_state: # Ajouté pour le scraping asynchrone
    st.session_state.scrape_pending = False
if 'download_key' not in st.session_state: # Ajouté pour l'option 2
    st.session_state.download_key = None 

# Converting DataFrame to csv
@st.cache_data
def convert_df_to_csv(dataf):
    return dataf.to_csv(index=False).encode('utf-8')

# Loarding data
@st.cache_data
def load_data_from_csv(file_path):
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return pd.DataFrame()
    return pd.read_csv(file_path)

# ===== Configurations of the navigation page =====
st.set_page_config(
    page_title="Dashboard Dynamique",
    layout="wide"
)

#st.markdown("<h4 style='text-align: center; color: black;'>PROJECT4 DATA COLLECTION APP</h4>", unsafe_allow_html=True)
st.markdown("""
This app allows you to download scraped data on animals from Coinafrique.
* **Python libraries:** base64, pandas, streamlit, fscraper
* **Data source:** [Coinafrique](https://sn.coinafrique.com/).
""")

# ===== call function of sidebar to update the user choice =====
choice = render_sidebar() 
st.session_state.current_choice = choice

# ===== Application content ===== 
#st.title(f"Option : {st.session_state.current_choice}")
#st.markdown("---")


## ===== 🚀 Option 1 : Scrape data) ==== 
if st.session_state.current_choice == "1. Scrape data" and st.session_state.scrape_pending:
    
    st.session_state.scrape_pending = False 
    
    start_page = st.session_state.start_page
    end_page = st.session_state.end_page
    base_url_to_scrape = URLS[st.session_state.selected_url_key]

    with st.spinner(f"Scraping of '{st.session_state.selected_url_key}' in progress, please wait ..."):
        
        try:
            # ====  Call fonction scraping from fscraper.py file ==== 
            df_result = scrape_web_pages( 
                base_url=base_url_to_scrape,
                start_page=start_page,
                end_page=end_page
            )
            
            st.session_state.scraped_df = df_result
            st.session_state.action_status = "scraping_complete"
            
        except Exception as e:
            st.error(f"Error in scraping : {e}")
            st.session_state.action_status = "scraping_error"

## 📊 Section 2 : Affichage des Résultats (Toutes les Options)

# ==== display for option 4
if st.session_state.action_status == "kobo_clicked":
    st.success("✅ KoboCollect form is opened in new tab !")
    st.markdown(f"**Action In progress :** Pelease fill the [Kobocollect Form]({URL_KOBO_COL})")

elif st.session_state.action_status == "google_clicked":
    st.success("✅ Google Form opened in new tab !")
    st.markdown(f"**Action in progress :** Please fll the [Google Form]({URL_GOOGLE_F})")


# === display according to the choices

if st.session_state.current_choice == "1. Scrape data":
    st.header("1. Web Scraping results :")
    
    if st.session_state.action_status == "scraping_complete" and st.session_state.scraped_df is not None:
        df = st.session_state.scraped_df
        st.subheader(f"Resultats ({len(df)} lines)")
        st.dataframe(df.head(50)) # displat=ying only 50 rows
        
        # ==== Downloding the CSV file =======
        csv = convert_df_to_csv(df)

    elif st.session_state.action_status == "scraping_requested":
        st.info("Scraping in progress.... A loading indicator should appear above")
    
    elif st.session_state.action_status in ["url_selected", ""]:
        st.info("Select the source URL and page settings in the sidebar and click “🚀 Start scraping”.")
    
    elif st.session_state.action_status == "scraping_error":
        st.error("The scraping failed. Check the console for error details.")
        
# ---

elif st.session_state.current_choice == "2. Download data already scraped":
    st.header("2. Download data :")
    
    if st.session_state.download_key:
        dl_key = st.session_state.download_key
        
        # ===== displating the header =====
        st.subheader(f"Dowload Dataset : {dl_key}")
        st.info(f"Click the button below to download the pre-collected data for **{dl_key}**.")
        
        # ===== Loading data for download =====
        file_path = DATA_PATHS.get(dl_key)
        if file_path:
            try:
                data_to_dl = load_data_from_csv(file_path)
                csv = convert_df_to_csv(data_to_dl)
                
                # Dowloard 
                st.download_button(
                    label=f"📥 Download {dl_key.replace(' ', '_')}.csv",
                    data=csv,
                    file_name=f'{dl_key.replace(" ", "_")}.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            
                st.markdown(f"**Data shape :** {data_to_dl.shape[0]} lines, {data_to_dl.shape[1]} columns.")
                st.dataframe(data_to_dl.head(5))
                
            except Exception as e:
                st.error(f"Erre while loarding : {e}")
        else:
            st.error(f"File path not defined fo {dl_key}. please check DATA_PATHS.")
            
    else:
        st.info("Please select the dataset to download from the sidebar.")
# ---

elif st.session_state.current_choice == "3. View a dashboard of data":
    
    st.header("3. Tableau de Bord et Statistiques")
    #st.warning("This section will be implemented at a later date.")
    #st.info("Here, you will display graphs, statistical summaries (mean, median, distribution), and KPIs based on CSV data.")
    
    # Exemple de statistiques futures:
    # df_chiens = load_data_from_csv(DATA_PATHS['1 Chiens'])
    if not df_chiens.empty:
         st.subheader("Statistiques sur les Chiens")
         st.write(df_chiens.describe())
         st.bar_chart(df_chiens['prix_col']) # Exemple

# ---
elif st.session_state.current_choice == "4. Fill in an app evaluation":
    st.header("4. Application evaluation")
    st.info("Links to the KoboCollect and Google Form forms are available in the sidebar..")
