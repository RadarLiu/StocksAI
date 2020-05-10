from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Max

from .models import UpdateDate, StockCode, StockPrice
from datetime import date


def index(request):
	# Update stock price data is stale.
	lastUpdate = UpdateDate.objects.aggregate(Max("date"))
	if lastUpdate["date__max"] == None or date.today() > lastUpdate["date__max"]:
		return HttpResponse("Stale data: last update: %s, today: %s" % (lastUpdate["date__max"], date.today()))
	return HttpResponse("Hello, world. You're at the index.")


#def backfillStockPrices():
