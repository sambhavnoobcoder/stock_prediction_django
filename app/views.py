from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, StockPredictionForm
from .models import UserProfile, StockPrediction
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from django.contrib.auth.models import User
from django.http import Http404
import yfinance as yf
import numpy as np
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from social_django.models import UserSocialAuth

class SettingsView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            github_login = user.social_auth.get(provider='github')
            print("github is logged in")
        except UserSocialAuth.DoesNotExist:
            github_login = None

        try:
            twitter_login = user.social_auth.get(provider='twitter')
        except UserSocialAuth.DoesNotExist:
            twitter_login = None

        try:
            facebook_login = user.social_auth.get(provider='facebook')
        except UserSocialAuth.DoesNotExist:
            facebook_login = None

        can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

        return render(request, 'settings.html', {
            'github_login': github_login,
            'twitter_login': twitter_login,
            'facebook_login': facebook_login,
            'can_disconnect': can_disconnect
        })


@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'password.html', {'form': form})

class UserRegistrationAPIView(APIView):
    def get(self, request):
        form = UserRegistrationForm(request.data)
        return render( request,'register.html',{'form': form})  # Redirect to the register.html page for GET requests

    def post(self, request):
        form = UserRegistrationForm(request.data)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if password != confirm_password:
                return Response({'error': "Passwords do not match."}, status=400)

            user = User.objects.create_user(username=username, email=email, password=password)

            # return Response({'message': "Registration successful."}, status=201)
            return redirect('login')
        else:
            # return Response(form.errors, status=400)
            form = UserRegistrationForm()

            return render(request, 'register.html', {'form': form})

@login_required
def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if password != confirm_password:
                # Handle password mismatch error
                return render(request, 'register.html', {'form': form, 'error': "Passwords do not match."})

            # Create new user instance
            user = User.objects.create_user(username=username, email=email, password=password)

            # Redirect to login or home page
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def predict(request):
    if request.method == 'POST':
        form = StockPredictionForm(request.POST)
        if form.is_valid():
            prediction = form.save(commit=False)
            prediction.user = request.user
            prediction.save()

            stock_symbol = prediction.stock_symbol
            algorithm = prediction.algorithm

            # Perform stock price prediction based on the selected algorithm
            stock_data = get_stock_data(stock_symbol)
            predicted_prices = None

            if algorithm == 'algorithm1':
                predicted_prices = linear_regression_prediction(stock_data)
            elif algorithm == 'algorithm2':
                predicted_prices = random_forest_prediction(stock_data)

            # Convert the predicted prices to a dictionary for rendering
            predicted_prices_dict = {
                str(day): price for day, price in enumerate(predicted_prices)
            }

            # Render the prediction results in table and line chart
            return render(request, 'prediction_chart.html', {
                'prediction': prediction,
                'predicted_prices': predicted_prices_dict
            })
    else:
        form = StockPredictionForm()
    return render(request, 'predict.html', {'form': form})

@login_required
def history(request):
    predictions = StockPrediction.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'history.html', {'predictions': predictions})


def linear_regression_prediction(stock_data):
    # Perform linear regression prediction using stock data
    # ...

    # Return the predicted prices
    X = np.array(range(len(stock_data))).reshape(-1, 1)
    y = stock_data['Close'].values

    model = LinearRegression()
    model.fit(X, y)

    # Predict future prices
    future_X = np.array(range(len(stock_data), len(stock_data) + 30)).reshape(-1, 1)
    predicted_prices = model.predict(future_X)
    return predicted_prices


def random_forest_prediction(stock_data):
    # Perform random forest prediction using stock data
    # ...

    # Return the predicted prices
    X = np.array(range(len(stock_data))).reshape(-1, 1)
    y = stock_data['Close'].values

    model = RandomForestRegressor()
    model.fit(X, y)

    # Predict future prices
    future_X = np.array(range(len(stock_data), len(stock_data) + 30)).reshape(-1, 1)
    predicted_prices = model.predict(future_X)
    return predicted_prices

def get_stock_data(symbol):
    # Retrieve stock data using yfinance
    stock = yf.Ticker(symbol)

    # Get historical stock prices
    historical_data = stock.history(period='1y')  # Adjust the period as per your requirement

    # Perform any necessary data preprocessing or feature engineering
    # ...

    return historical_data

@login_required
def prediction_chart(request, prediction_id):
    prediction = get_object_or_404(StockPrediction, id=prediction_id)

    # Retrieve stock data for the given symbol using Yahoo Finance or any other source
    stock_symbol = prediction.stock_symbol
    stock_data = get_stock_data(stock_symbol)  # Implement this function to retrieve stock data

    # Check if the algorithm is linear regression
    if prediction.algorithm == 'algorithm1':
        predicted_prices = linear_regression_prediction(stock_data)
    else:
        predicted_prices = random_forest_prediction(stock_data)

    # Get the past stock prices for the chart
    past_stock_prices = stock_data['Close'].values[-30:]

    # Prepare the data for the line chart
    stock_prices_json = past_stock_prices.tolist()
    predicted_prices_json = predicted_prices.tolist()

    # Generate a line chart of predicted vs actual prices
    actual_prices = stock_data['Close'].values

    plt.plot(range(len(actual_prices)), actual_prices, marker='o', label='Actual')
    plt.plot(range(len(actual_prices), len(actual_prices) + len(predicted_prices)), predicted_prices, marker='o', label='Predicted')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Stock Price Prediction')
    plt.legend()
    plt.grid(True)

    # Save the chart as an image
    chart_path = f'prediction_chart_{prediction_id}.png'
    plt.savefig(chart_path)
    plt.close()

    return render(request, 'prediction_chart.html', {
        'prediction': prediction,
        'stock_prices_json': json.dumps(stock_prices_json),
        'predicted_prices_json': json.dumps(predicted_prices_json),
        'chart_path': chart_path
    })

@login_required
def logout_view(request):
    # logout(request)
    return redirect('home')
