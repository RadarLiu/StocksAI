from django.contrib import admin
from .models import ServerState, StockCode, StockPrice, Profile, Holding

admin.site.register(ServerState)
admin.site.register(StockCode)
admin.site.register(StockPrice)
admin.site.register(Profile)
admin.site.register(Holding)
