from django.db import models
from datetime import date

# Field type: https://docs.djangoproject.com/en/3.0/ref/models/fields/#model-field-types

class ServerState(models.Model):
  state_id = models.IntegerField(default=0, unique=True)  # 0: primary server state
  last_update_date = models.DateField(default=date(2018, 12, 31))  # Starting from 2019-01-01


class StockCode(models.Model):
  code = models.CharField(max_length=10, unique=True)
  industry = models.CharField(max_length=100, default="")

  def __str__(self):
    return self.code + " | " + self.industry


class StockPrice(models.Model):
  code = models.ForeignKey(StockCode, on_delete=models.CASCADE)
  date = models.DateField()
  price = models.FloatField()  # Close price.

  class Meta:
    unique_together = ("code", "date")  # No duplicate <code, date> pair

  def __str__(self):
    return str(self.code) + " | " + str(self.date) + " | " + str(self.price)
