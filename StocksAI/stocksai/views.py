import logging
import yfinance as yf
import datetime

from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Max
from datetime import date
from datetime import datetime as dt
from .models import StockCode, StockPrice


# Global variable to cache the last day on which stock price data was updated.
last_update = date(2018, 12, 31)  # Since 2019

# See settings.py: "name of logger"
logger = logging.getLogger("stocksai")
def logInfo(s):
	logger.info("INFO: %s: %s" % (dt.now().strftime("'%Y-%m-%d' %H:%M:%S"), s))

def logWarning(s):
	logger.info("WARNING: %s: %s" % (dt.now().strftime("'%Y-%m-%d' %H:%M:%S"), s))

def logError(s):
	logger.info("ERROR: %s: %s" % (dt.now().strftime("'%Y-%m-%d' %H:%M:%S"), s))


def index(request):
	# Update stock price data is stale.
	# lastUpdate = UpdateDate.objects.aggregate(Max("date"))["date__max"]
	global last_update
	if date.today() > last_update:
		logWarning("Stale data: last update: %s, today: %s" % (last_update, date.today()))
		
		# Update latest stock prices for all companies.
		code_list = [i.code for i in StockCode.objects.all()]
		codes = " ".join(code_list)
		start_date = (last_update + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
		end_date = dt.now().strftime("%Y-%m-%d")  # Not inclusive.

		# Remote API call.
		data = yf.download(codes, start=start_date, end=end_date)

		for code in code_list:
			stock_code = StockCode.objects.get(code=code)
			for d, p in data.loc[:, "Open"].loc[:, code].iteritems():
				open_price = data.loc[:, "Open"].loc[:, code].loc[d]
				close_price = data.loc[:, "Close"].loc[:, code].loc[d]
				high_price = data.loc[:, "High"].loc[:, code].loc[d]
				low_price = data.loc[:, "Low"].loc[:, code].loc[d]
				price = StockPrice(code=stock_code, date=d, open_price=open_price, close_price=close_price, high_price=high_price, low_price=low_price)
				try:
					price.save()
				except IntegrityError:
					pass # Ignore duplicate data
		last_update = date.today()
		return HttpResponse("Data updated.")
	return HttpResponse("Hello, world. You're at the index.")



# Dev only
def clear_all_stock_prices(request):
	StockPrice.objects.all().delete()
	return HttpResponse("All stock prices deleted.")