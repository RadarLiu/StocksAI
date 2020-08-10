import logging
import yfinance as yf
import datetime

from django.db import IntegrityError
from django.db import transaction
from django.db.models import Max
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.template import loader
from datetime import date
from datetime import datetime as dt
from .models import *
from .forms import *
from operator import itemgetter
from time import time

class ServerStateCache:
  last_update_date = date(2018, 12, 31)

  def __init__(self):
    pass  # Do not access DB here, may result in table not found error upon starting.

server_state_cache = ServerStateCache()

price_cache = dict()
price_refreshed_time_sec = time()

# See settings.py: "name of logger"
logger = logging.getLogger("stocksai")
def logInfo(s):
  logger.info("INFO: %s: %s" % (dt.now().strftime("'%Y-%m-%d' %H:%M:%S"), s))

def logWarning(s):
  logger.info("WARNING: %s: %s" % (dt.now().strftime("'%Y-%m-%d' %H:%M:%S"), s))

def logError(s):
  logger.info("ERROR: %s: %s" % (dt.now().strftime("'%Y-%m-%d' %H:%M:%S"), s))


# Helper function to get the latest stock price from local DB.
# Used for showing estimated earning.
# Do NOT use for purchasing (use the yfinance API instead).
def get_latest_stock_price(code=""):
  if code == "":
    return 0
  d = date(2018, 12, 31)
  price = 0.0
  prices = StockPrice.objects.filter(code__code=code)  # Filter by the "code" field of Foreign key "code".
  for p in prices:
    if p.date > d:
      d = p.date
      price = p.price
  return price


# Home page after use login.
@login_required
def index(request):
  r = refresh_stock_prices()

  # Hide data update info.
  # if r is None:
  #   return HttpResponse("Hello, world. You're at the index.")
  # else:
  #   return r

  # Default: GET
  context = {}
  user = request.user

  # Basic info
  context["first_name"] = user.first_name
  context["last_name"] = user.last_name
  context["email"] = user.email
  profile = get_object_or_404(Profile, user__username=user.username)
  context["registration_date"] = profile.registration_date
  context["cash_usd"] = "$" + str(round(profile.cash_usd, 2))

  # Stocks holding info: basic
  holdings = Holding.objects.filter(user=user)
  stock_table = {}  # Map from stock_code_str to a list of holdings
  for h in holdings:
    code = h.code.code
    if not code in stock_table:
      stock_table[code] = []  # list of holdings
    info = [h.purchase_date, h.purchase_unit_price, h.volume]
    stock_table[code].append(info)

  # Stocks holding info: derived
  total_wealth = 0.0
  for code in stock_table:
    stock_table[code] = sorted(stock_table[code], key=itemgetter(0), reverse=True)  # Sort by purchase_date desc.
    # Get current price
    current_price = get_latest_stock_price(code)
    for info in stock_table[code]:
      info.append("$" + str(round((current_price - info[1]) * info[2], 2)))  # earning
      info.append(str(round((current_price - info[1]) / info[1] * 100, 2)) + "%")  # earning percentage
      total_wealth += current_price * info[2]
      info[1] = "$" + str(round(info[1], 2))  # format: purchase _unit_price
      info[2] = str(round(info[2], 3))  # format: volume

  context["stock_table"] = stock_table  # info format: purchase_date, purchase_unit_price, volume, earning, earning percentage
  context["total_wealth"] = "$" + str(round(total_wealth + profile.cash_usd, 2))
  return render(request, "stocksai/index.html", context)


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
      start_date = (server_state_cache.last_update_date).strftime("%Y-%m-%d")
      end_date = dt.now().strftime("%Y-%m-%d")  # Not inclusive.

      # Remote API call.
      data = yf.download(codes, start=start_date, end=end_date)

      for code in code_list:
        stock_code = StockCode.objects.get(code=code)
        save_prices(data=data, stock_code=stock_code)

      # Update state
      o = ServerState.objects.get(state_id=0)
      o.last_update_date = today
      o.save()
      server_state_cache.last_update_date = today
      return HttpResponse("Data updated.")
  return None


# Helper function to save stock prices.
@transaction.atomic
def save_prices(data=None, stock_code=None):
  if data is None:
    return "data is None"
  if stock_code is None:
    return "code is None"
  f = data.loc[:, "Close"]
  try:
    f = f.loc[:, stock_code.code]
  except Exception:
    f = data.loc[:, "Close"] # yfinance API does not return the "code" dimension when there is only one company.
  for d, p in f.iteritems():
    cp = data.loc[:, "Close"]
    try:
      cp = cp.loc[:, stock_code.code]
    except Exception:
      cp = data.loc[:, "Close"]
    close_price = cp.loc[d]
    price = StockPrice(code=stock_code, date=d, price=close_price)
    try:
      price.save()
    except IntegrityError:
      pass # Ignore duplicate data


# Dev only
# def clear_all_stock_prices(request):
#   StockPrice.objects.all().delete()
#   return HttpResponse("All stock prices deleted.")


@transaction.atomic
def edit_company(request):
  add_err = ""
  add_success = ""
  del_err = ""
  del_success = ""

  print(request.method, request.path)

  if request.method == "POST" and "add_company" in request.path:
    form = AddCompanyForm(request.POST)
    if form.is_valid():  # This line is required to generate cleaned_data.
      code = form.cleaned_data["code"].upper()
      industry = form.cleaned_data["industry"]
      if StockCode.objects.filter(code=code).exists():
        add_err = "Company code %s already exists!" % code
      else:
        data = yf.download(code, start="2019-01-01", end=dt.now().strftime("%Y-%m-%d"))  # end date is not inclusive.
        if data.size == 0:
          add_err = "No data available for company code: %s" % code
        else:
          stock_code = StockCode(code=code, industry=industry)
          stock_code.save()
          save_prices(data=data, stock_code=stock_code)
    else:
      add_err = "Invalid Company Code!"

  if request.method == "POST" and "delete_company" in request.path:
    form = DelCompanyForm(request.POST)
    if form.is_valid():
      code = form.cleaned_data["code"].upper()
      try:
        StockCode.objects.filter(code=code).delete()
        StockPrice.objects.filter(code=code).delete()
      except Exception as e:
        del_err = "Deletion failed: %s" % str(e)
      del_success = "%s deleted!" % code

  # Render
  companies = StockCode.objects.all()
  context = {
      "companies": companies,
      "add_company_form": AddCompanyForm(),
      "add_success": add_success,
      "add_err": add_err,
      "del_success": del_success,
  }
  return render(request, "stocksai/edit_company.html", context)


@transaction.atomic
def register(request):
  context = {}

  if request.method == "GET":
    context["form"] = RegistrationForm()
    return render(request, "stocksai/register.html", context)

  form = RegistrationForm(request.POST)
  context["form"] = form
  if not form.is_valid():
    return render(request, "stocksai/register.html", context)

  # Cross-field validations that cannot be done in Django form.
  if form.cleaned_data["password"] != form.cleaned_data["password_repeat"]:
    context["t_errors"] = "Passwords did not match!"
    return render(request, "stocksai/register.html", context)

  user = User.objects.create_user(
    username=form.cleaned_data["username"],
    first_name=form.cleaned_data["first_name"],
    last_name=form.cleaned_data["last_name"],
    email=form.cleaned_data["email"],
    password=form.cleaned_data["password"],
    is_active=True,
  )
  user.save()

  profile = Profile(user=user, registration_date=date.today(), cash_usd = 10000.00)
  profile.save()
  return redirect(reverse("login"))


@login_required
@transaction.atomic
def edit_user_info(request):
  context = {}
  user = request.user

  if request.method == "GET":
    data = {
      "old_password": "******",
      "password": "******",
      "password_repeat": "******",
      "first_name": user.first_name,
      "last_name": user.last_name,
      "email": user.email,
    }
    context["form"] = EditUserInfoForm(data)
    context["username"] = user.username
    return render(request, "stocksai/edit_user_info.html", context)

  form = EditUserInfoForm(request.POST)
  context["form"] = form
  if not form.is_valid():
    return render(request, "stocksai/edit_user_info.html", context)

  if len(form.cleaned_data["password"]) > 0 and form.cleaned_data["password"] != form.cleaned_data["password_repeat"]:
    context["t_errors"] = "Passwords did not match!"
    return render(request, "stocksai/edit_user_info.html", context)

  if not user.check_password(form.cleaned_data["old_password"]):
    context["t_errors"] = "Invalid old password!"
    return render(request, "stocksai/edit_user_info.html", context)

  user.first_name = form.cleaned_data["first_name"]
  user.last_name = form.cleaned_data["last_name"]
  user.email = form.cleaned_data["email"]
  if len(form.cleaned_data["password"]) > 0:
    user.set_password(form.cleaned_data["password"])
  user.save()
  context["form"] = form
  context["username"] = user.username
  context["info"] = "Info Updated!"
  return render(request, "stocksai/edit_user_info.html", context)


@login_required
def sell(request):
  return HttpResponse("Sell page")

@login_required
def purchase(request):
  context = {}
  profile = get_object_or_404(Profile, user__username=request.user.username)

  if request.method == "GET":
    context["cash_usd"] = "$" + str(round(profile.cash_usd, 2))

    stock_table = {}
    for i in StockCode.objects.all():
      latest_price = None
      try:
        latest_price = PriceCache.objects.get(code=i)
      except PriceCache.DoesNotExist:
        latest_price = PriceCache(code=i, last_update_second=0)
      if time() - latest_price.last_update_second > 10 * 60:
        latest_price.price = yf.Ticker(i.code).info["regularMarketPrice"]  # real-time prices
        latest_price.last_update_second = time()
        latest_price.save()
      stock_table[i.code] = latest_price.price
    context["stock_table"] = stock_table

    return render(request, "stocksai/purchase_page.html", context)



  return HttpResponse(request.POST["code"])
