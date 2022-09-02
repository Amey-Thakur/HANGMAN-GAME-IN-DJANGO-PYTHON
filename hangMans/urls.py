"""hangMans URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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

from hangMansApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Start, name='starting'),
    path('update/word', views.updateWord, name='updated-word-game'),
    path('<uuid:uui>', views.playShare, name='play-game-share'),
    path('generate/word', views.generateWord, name='generate-word'),
]
