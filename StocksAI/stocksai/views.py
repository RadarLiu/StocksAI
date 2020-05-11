import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Max
from datetime import date
from datetime import datetime

from .models import StockCode, StockPrice

# Global variable to cache the last day on which stock price data was updated.
lastUpdate = date(1999, 12, 31)

# See settings.py: "name of logger"
logger = logging.getLogger("stocksai")
def logInfo(s):
	logger.info("INFO: %s: %s" % (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), s))

def logWarning(s):
	logger.info("WARNING: %s: %s" % (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), s))

def logError(s):
	logger.info("ERROR: %s: %s" % (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), s))


def index(request):
    # Update stock price data is stale.
    # lastUpdate = UpdateDate.objects.aggregate(Max("date"))["date__max"]
    global lastUpdate
    if date.today() > lastUpdate:
        logWarning("Stale data: last update: %s, today: %s" % (lastUpdate, date.today()))
        return HttpResponse("Stale data: last update: %s, today: %s" % (lastUpdate, date.today()))
    return HttpResponse("Hello, world. You're at the index.")


#def backfillStockPrices():
