from django.contrib import admin
from .models import StockPrediction
# import models

class StockPredictionAdmin(admin.ModelAdmin):
    list_display = ('stock_symbol', 'algorithm', 'get_result', 'get_date')
    list_filter = ('algorithm',)



    def get_result(self, obj):
        return obj.result
    get_result.admin_order_field = 'result'
    get_result.short_description = 'Result'

    def get_date(self, obj):
        return obj.date
    get_date.admin_order_field = 'date'
    get_date.short_description = 'Date'

admin.site.register(StockPrediction, StockPredictionAdmin)
