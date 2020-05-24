from django.contrib import admin
from django.contrib.auth.models import User
from .models import ServerState
from .models import StockCode
from .models import StockPrice
from .models import Profile


admin.site.register(ServerState)
admin.site.register(StockCode)
admin.site.register(StockPrice)
admin.site.register(Profile)
