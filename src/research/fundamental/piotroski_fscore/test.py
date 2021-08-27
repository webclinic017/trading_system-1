#%%
import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import copy
import matplotlib.pyplot as plt

# %%
stats = ["Net income available to common shareholders",
         "Total assets",
         "Net cash provided by operating activities",
         "Long-term debt",
         "Other long-term liabilities",
         "Total current assets",
         "Total current liabilities",
         "Common stock",
         "Total revenue",
         "Gross profit"] # change as required

indx = ["NetIncome","TotAssets","CashFlowOps","LTDebt","OtherLTDebt",
        "CurrAssets","CurrLiab","CommStock","TotRevenue","GrossProfit"]

# %%
def info_filter(df,stats,indx):
    """function to filter relevant financial information for each
       stock and transforming string inputs to numeric"""
    tickers = df.columns
    all_stats = {}
    for ticker in tickers:
        try:
            temp = df[ticker]
            ticker_stats = []
            for stat in stats:
                ticker_stats.append(temp.loc[stat])
            all_stats['{}'.format(ticker)] = ticker_stats
        except:
            print("can't read data for ",ticker)

    all_stats_df = pd.DataFrame(all_stats,index=indx)

    # cleansing of fundamental data imported in dataframe
    all_stats_df[tickers] = all_stats_df[tickers].replace({',': ''}, regex=True)
    for ticker in all_stats_df.columns:
        all_stats_df[ticker] = pd.to_numeric(all_stats_df[ticker].values,errors='coerce')
    return all_stats_df
# %%
def piotroski_f(df_cy,df_py,df_py2):
    """function to calculate f score of each stock and output information as dataframe"""
    f_score = {}
    tickers = df_cy.columns
    for ticker in tickers:
        ROA_FS = int(df_cy.loc["NetIncome",ticker]/((df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2) > 0)
        CFO_FS = int(df_cy.loc["CashFlowOps",ticker] > 0)
        ROA_D_FS = int(df_cy.loc["NetIncome",ticker]/(df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2 > df_py.loc["NetIncome",ticker]/(df_py.loc["TotAssets",ticker]+df_py2.loc["TotAssets",ticker])/2)
        CFO_ROA_FS = int(df_cy.loc["CashFlowOps",ticker]/df_cy.loc["TotAssets",ticker] > df_cy.loc["NetIncome",ticker]/((df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2))
        LTD_FS = int((df_cy.loc["LTDebt",ticker] + df_cy.loc["OtherLTDebt",ticker])<(df_py.loc["LTDebt",ticker] + df_py.loc["OtherLTDebt",ticker]))
        CR_FS = int((df_cy.loc["CurrAssets",ticker]/df_cy.loc["CurrLiab",ticker])>(df_py.loc["CurrAssets",ticker]/df_py.loc["CurrLiab",ticker]))
        DILUTION_FS = int(df_cy.loc["CommStock",ticker] <= df_py.loc["CommStock",ticker])
        GM_FS = int((df_cy.loc["GrossProfit",ticker]/df_cy.loc["TotRevenue",ticker])>(df_py.loc["GrossProfit",ticker]/df_py.loc["TotRevenue",ticker]))
        ATO_FS = int(df_cy.loc["TotRevenue",ticker]/((df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2)>df_py.loc["TotRevenue",ticker]/((df_py.loc["TotAssets",ticker]+df_py2.loc["TotAssets",ticker])/2))
        f_score[ticker] = [ROA_FS,CFO_FS,ROA_D_FS,CFO_ROA_FS,LTD_FS,CR_FS,DILUTION_FS,GM_FS,ATO_FS]
    f_score_df = pd.DataFrame(f_score,index=["PosROA","PosCFO","ROAChange","Accruals","Leverage","Liquidity","Dilution","GM","ATO"])
    return f_score_df

# %%
current_year = pd.read_csv("./data/current_year.csv", index_col=0)
past_year = pd.read_csv("./data/past_year.csv", index_col=0)
past_year2 = pd.read_csv("./data/past_year2.csv", index_col=0)

#%%
# Selecting stocks with highest Piotroski f score
transformed_df_cy = info_filter(current_year,stats,indx)
transformed_df_py = info_filter(past_year,stats,indx)
transformed_df_py2 = info_filter(past_year2,stats,indx)

f_score_df = piotroski_f(transformed_df_cy,transformed_df_py,transformed_df_py2)
f_score_df.sum().sort_values(ascending=False)

# %%
######################### BACKTEST ############################
def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df["mon_ret"]).cumprod()
    n = len(df)/12 # using 12 since using monthly returns
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df["mon_ret"].std() * np.sqrt(12) # using 12 since using monthly returns
    return vol

def sharpe(DF,rf):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df) - rf)/volatility(df)
    return sr


def max_dd(DF):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df["mon_ret"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd


def portfolio(currentYearDf, pastYearDf, fortYearDf, x):
    tickers = []
    fScoreDf = piotroski_f(currentYearDf, pastYearDf, fortYearDf)

    for i in range(len(fScoreDf.columns)):
        currentTicker = fScoreDf.iloc[:, i]

        if (currentTicker.sum() >= x):
            tickers.append(currentTicker.name)

    return tickers

pf = portfolio(transformed_df_cy, transformed_df_py, transformed_df_py2, 6)

def monthlyReturn(pf, start, end, interval):
    ohlcv = {}
    portfolioMonthlyReturn = pd.DataFrame()
    cummulativeMonthlyReturn = [0]

    for ticker in pf:
        ohlcv[ticker] = yf.download(ticker, start, end, interval=interval)
        ohlcv[ticker].dropna(inplace=True,how="all")
        print("calculating monthly return for ",ticker)
        ohlcv[ticker]["mon_ret"] = ohlcv[ticker]["Adj Close"].pct_change()
        portfolioMonthlyReturn[ticker] = ohlcv[ticker]["mon_ret"]

    for i in range(1,len(portfolioMonthlyReturn)):
        cummulativeMonthlyReturn.append((portfolioMonthlyReturn.iloc[i,:].mean()))

    cummulativeDf = pd.DataFrame(np.array(cummulativeMonthlyReturn),columns=["mon_ret"])
    return [portfolioMonthlyReturn, cummulativeDf]

#%%
start = dt.datetime.today() - dt.timedelta(1825)
end = dt.datetime.today()
fScoreReturns = monthlyReturn(pf, start, end, '1mo')

#%%
CAGR(fScoreReturns[1])
sharpe(fScoreReturns[1], 0.025)
max_dd(fScoreReturns[1])

#%%
#calculating KPIs for Index buy and hold strategy over the same period
DJI = yf.download("^DJI",dt.date.today()-dt.timedelta(1825),dt.date.today(),interval='1mo')
DJI["mon_ret"] = DJI["Adj Close"].pct_change()
CAGR(DJI)
sharpe(DJI,0.025)
max_dd(DJI)

#%%
#visualization
fig, ax = plt.subplots()

# if investing $1 what will be the return
plt.plot((1+fScoreReturns[1]).cumprod())
plt.plot((1+DJI["mon_ret"][2:].reset_index(drop=True)).cumprod())
plt.title("Index Return vs Strategy Return")
plt.ylabel("cumulative return")
plt.xlabel("months")
ax.legend(["Strategy Return","Index Return"])
