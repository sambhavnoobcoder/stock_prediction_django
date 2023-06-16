from django.urls import path,include
from django.contrib.auth import views as auth_views
from app import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('predict/', views.predict, name='predict'),
    path('history/', views.history, name='history'),
    # path('prediction_chart/', views.prediction_chart, name='prediction_chart'),
    path('prediction/<int:prediction_id>/chart', views.prediction_chart, name='prediction_chart'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),  # <-- here
    path('api/register/',views.UserRegistrationAPIView.as_view(),name='register'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('settings/password/', views.password, name='password'),
]
