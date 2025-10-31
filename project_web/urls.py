"""
URL configuration for project_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home),
    path('home/', views.home),
	path('home/news1/', views.news1),
	path('home/news2/', views.news2),
	path('home/news3/', views.news3),
	path('home/news4/', views.news4),
    path('adduser/', views.adduser),
    path('login/', views.login),
	path('logout/', views.logout),
    path('userupdate/', views.userupdate),
	path('userforget/', views.userforget),
    path('order/', views.order),
    path('checkout/', views.checkout),
    path('checkout/detial/', views.checkout_detial),
    path('reserve/', views.reserve),
	path('reserve/booking/', views.booking),
	path('reserve/detial/', views.reserve_detial),
    path('food/', views.food),
	
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
