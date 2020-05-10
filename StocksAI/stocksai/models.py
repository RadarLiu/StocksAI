from django.db import models

# Field type: https://docs.djangoproject.com/en/3.0/ref/models/fields/#model-field-types

class UpdateDate(models.Model):
	date = models.DateField()


class StockCode(models.Model):
	code = models.CharField(max_length=10)

	def __str__(self):
		return self.code


class StockPrice(models.Model):
    code = models.ForeignKey(StockCode, on_delete=models.CASCADE)
    date = models.DateField()
    open_price = models.FloatField()
    close_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()

    def __str__(self):
        return (self.code + "|" + str(self.date) + "|" + str(self.open_price) + "|" +
        	str(self.close_price) + "|" + str(self.high_price) + "|" + str(self.low_price))
