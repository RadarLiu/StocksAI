import logging
import yfinance as yf
import datetime

from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from datetime import date
from datetime import datetime as dt
from .models import StockCode, StockPrice, ServerState

class ServerStateCache:
  last_update_date = date(2018, 12, 31)

  def __init__(self):
    pass  # Do not access DB here, may result in table not found error upon starting.

server_state_cache = ServerStateCache()

# See settings.py: "name of logger"
logger = logging.getLogger("stocksai")
def logInfo(s):
  logger.info("INFO: %s: %s" % (dt.now().strftime("'%Y-%m-%d' %H:%M:%S"), s))

def logWarning(s):
  logger.info("WARNING: %s: %s" % (dt.now().strftime("'%Y-%m-%d' %H:%M:%S"), s))

def logError(s):
  logger.info("ERROR: %s: %s" % (dt.now().strftime("'%Y-%m-%d' %H:%M:%S"), s))


def index(request):
  r = refresh_stock_prices()
  if r is None:
    return HttpResponse("Hello, world. You're at the index.")
  else:
    return r


# Execute upon loading homepage if data looks stale.
def refresh_stock_prices():
  global server_state_cache
  today = date.today()
  if today > server_state_cache.last_update_date:
    logInfo("Cache could be stale: got last update: %s" % server_state_cache.last_update_date)
    if not ServerState.objects.filter(state_id=0).exists():
      ServerState(state_id=0, last_update_date=date(2018, 12, 31)).save()
      server_state_cache.last_update_date = date(2018, 12, 31)
    else:
      server_state_cache.last_update_date = ServerState.objects.get(state_id=0).last_update_date
    if today > server_state_cache.last_update_date:
      logWarning("Stale data: last update: %s, today: %s" % (server_state_cache.last_update_date, today))

      # Update latest stock prices for all companies.
      code_list = [i.code for i in StockCode.objects.all()]
      codes = " ".join(code_list)
      start_date = (server_state_cache.last_update_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
      end_date = dt.now().strftime("%Y-%m-%d")  # Not inclusive.

      # Remote API call.
      data = yf.download(codes, start=start_date, end=end_date)

      for code in code_list:
        stock_code = StockCode.objects.get(code=code)
        for d, p in data.loc[:, "Close"].loc[:, code].iteritems():
          close_price = data.loc[:, "Close"].loc[:, code].loc[d]
          price = StockPrice(code=stock_code, date=d, price=close_price)
          try:
            price.save()
          except IntegrityError:
            pass # Ignore duplicate data

      # Update state
      o = ServerState.objects.get(state_id=0)
      o.last_update_date = today
      o.save()
      server_state_cache.last_update_date = today
      return HttpResponse("Data updated.")
  return None


# Dev only
def clear_all_stock_prices(request):
  StockPrice.objects.all().delete()
  return HttpResponse("All stock prices deleted.")


def edit_company(request):
  companies = StockCode.objects.all()
  template = loader.get_template('stocksai/edit_company.html')
  context = {
      'companies': companies,
  }
  return HttpResponse(template.render(context, request))
