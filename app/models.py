from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    MARKET_CHOICES = [
        ('US', 'US Market'),
        ('Indian', 'Indian Market')
    ]
    market = models.CharField(max_length=10, choices=MARKET_CHOICES)

    def __str__(self):
        return self.user.username

class StockPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=10)
    ALGORITHM_CHOICES = [
        ('algorithm1', 'Algorithm 1'),
        ('algorithm2', 'Algorithm 2')
    ]
    algorithm = models.CharField(max_length=20, choices=ALGORITHM_CHOICES)
    prediction_result = models.FloatField(null=True, blank=True)
    # prediction_result = models.DecimalField(max_digits=10, decimal_places=2)
    actual_result = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock_symbol} - {self.timestamp}"
