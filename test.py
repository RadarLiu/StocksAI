import yfinance as yf

msft = yf.Ticker("MSFT")
goog = yf.Ticker("GOOG")

# get stock info
# print(msft.info)

# # get historical market data
#hist = goog.history(period="1mo", interval="1d")
#print(hist)
# print(type(hist))  # pandas.core.frame.DataFrame
# https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html
# print(hist["Open"])
# print(hist[["Open", "Close"]])
# print(hist.loc["2020-04-30"])
# print(hist.loc["2020-04-29":"2020-05-01"])
# print(hist.loc["2020-04-30"]["Open"])



data = yf.download("MSFT GOOG", start="2020-01-01", end="2020-04-30")
print(type(data))
print(data)  # pandas.core.frame.DataFrame
print(data.loc[:, "Close"].loc[:, "GOOG"])
print(type(data.loc[:, "Close"].loc[:, "GOOG"]))  # pandas.core.series.Series
#for d, price in data.loc[:, "Close"].loc[:, "GOOG"].iteritems():
#	print(d.to_pydatetime(), type(d.to_pydatetime()), price, type(price))  # datetime.datetime  and  float
for d, price in data.loc[:, "Open"].loc[:, "GOOG"].iteritems():
	print(d.to_pydatetime(), data.loc[:, "Open"].loc[:, "GOOG"].loc[d], data.loc[:, "Close"].loc[:, "GOOG"].loc[d])  # datetime.datetime  and  float



# # show actions (dividends, splits)
# msft.actions

# # show dividends
# msft.dividends

# # show splits
# msft.splits

# # show financials
# msft.financials
# msft.quarterly_financials

# # show major holders
# stock.major_holders

# # show institutional holders
# stock.institutional_holders

# # show balance heet
# msft.balance_sheet
# msft.quarterly_balance_sheet

# # show cashflow
# msft.cashflow
# msft.quarterly_cashflow

# # show earnings
# msft.earnings
# msft.quarterly_earnings

# # show sustainability
# msft.sustainability

# # show analysts recommendations
# msft.recommendations

# # show next event (earnings, etc)
# msft.calendar

# # show ISIN code - *experimental*
# # ISIN = International Securities Identification Number
# msft.isin

# # show options expirations
# msft.options

# # get option chain for specific expiration
# opt = msft.option_chain('YYYY-MM-DD')
# # data available via: opt.calls, opt.puts