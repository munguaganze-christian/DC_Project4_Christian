from requests import get
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import numpy as np
import sqlite3

def scrape_web_pages(base_url: str, start_page: int, end_page: int) -> pd.DataFrame:
    # create a empty dataframe df
    dataf = pd.DataFrame()

    # loop over pages indexes
    for index_page in range(start_page,end_page+1) :
        #url = f'https://sn.coinafrique.com/categorie/chiens?page={index_page}'
        url = f'{base_url}{index_page}'
        res = get(url)
        soup = bs(res.content,'html.parser')

        # get all containers
        containers = soup.find_all('div','col s6 m4 l3')

        df= []

        for container in containers: # Loop over containers in each page
            try:
                name = container.find('p','ad__card-description').a.text.replace('CFA','')
                price1 = container.find('p','ad__card-price').text.replace('CFA','')
                price = price1.replace(' ','')
                #location = container.find('i','material-icons') #ad__card-location
                adress =container.find('p','ad__card-location').text.replace('location_on','') #ad__card-location
                image_link = container.find('img','ad__card-img')['src']

                dict = {
                    "name":name,
                    "price":price,
                    "adress":adress,
                    "image_link":image_link
                }
                df.append(dict)
            except:
                pass
        DF = pd.DataFrame(df)
        dataf = pd.concat([dataf,DF], axis = 0).reset_index(drop = True) 
        return dataf

def save_to_sql_db(dataf, t_animals):
    conn = sqlite3.connect('coinafrica_database.db')
    c = conn.cursor()
    dataf.to_sql(t_animals,c, if_existe='replace', index=false)
    c.close()

def laod_from_sql_db(t_animals):
    conn = sqlite3.connect('coinafrica_database.db')
    c = conn.cursor()
    df_from_sql = pd.read_sql(f'SELECT * FROM {t_animals}',c)
    c.close()
    return df_from_sql

