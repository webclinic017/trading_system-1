#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

#%%
def scrape(tickers):

    financial_dir_cy = {}
    financial_dir_py = {}
    financial_dir_py2 = {}

    for ticker in tickers:
        try:
            print("Scraping financial statement data for:",ticker)
            temp_dir = {}
            temp_dir2 = {}
            temp_dir3 = {}

            #getting balance sheet data from yahoo finance for the given ticker
            url = 'https://sg.finance.yahoo.com/quote/'+ticker+'/balance-sheet?p='+ticker
            page = requests.get(url)
            page_content = page.content
            soup = BeautifulSoup(page_content,'html.parser')
            tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
            for t in tabl:
                rows = t.find_all("div", {"class" : "rw-expnded"})
                for row in rows:
                    temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[1]
                    temp_dir2[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[2]
                    temp_dir3[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[3]

            #getting income statement data from yahoo finance for the given ticker
            url = 'https://sg.finance.yahoo.com/quote/'+ticker+'/financials?p='+ticker
            page = requests.get(url)
            page_content = page.content
            soup = BeautifulSoup(page_content,'html.parser')
            tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
            for t in tabl:
                rows = t.find_all("div", {"class" : "rw-expnded"})
                for row in rows:
                    temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[1]
                    temp_dir2[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[2]
                    temp_dir3[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[3]

            #getting cashflow statement data from yahoo finance for the given ticker
            url = 'https://sg.finance.yahoo.com/quote/'+ticker+'/cash-flow?p='+ticker
            page = requests.get(url)
            page_content = page.content
            soup = BeautifulSoup(page_content,'html.parser')
            tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
            for t in tabl:
                rows = t.find_all("div", {"class" : "rw-expnded"})
                for row in rows:
                    temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[1]
                    temp_dir2[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[2]
                    temp_dir3[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[3]

        except:
            print("Problem scraping data for ",ticker)

        financial_dir_cy[ticker] = temp_dir
        financial_dir_py[ticker] = temp_dir2
        financial_dir_py2[ticker] = temp_dir3

    return financial_dir_cy, financial_dir_py, financial_dir_py2



#%%
tickers = ["AXP","AAPL","BA","CAT","CVX","CSCO","DIS","DOW", "XOM",
           "HD","IBM","INTC","JNJ","KO","MCD","MMM","MRK","MSFT",
           "NKE","PFE","PG","TRV","UTX","UNH","VZ","V","WMT","WBA"]

curr_year, past_year, past_year2 = scrape(tickers)

# %%
#storing information in pandas dataframe
combined_financials_cy = pd.DataFrame(curr_year)
#combined_financials_cy.dropna(axis=1,inplace=True) #dropping columns with NaN values
combined_financials_py = pd.DataFrame(past_year)
#combined_financials_py.dropna(axis=1,inplace=True)
combined_financials_py2 = pd.DataFrame(past_year2)
#combined_financials_py2.dropna(axis=1,inplace=True)
tickers = combined_financials_cy.columns #updating the tickers

# %%
combined_financials_cy.to_csv("./data/current_year.csv")
combined_financials_py.to_csv("./data/past_year.csv")
combined_financials_py2.to_csv("./data/past_year2.csv")
# %%
