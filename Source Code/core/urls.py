'''
***************************************************************************************************
* PROJ NAME: HANGMAN GAME IN DJANGO & PYTHON
* AUTHOR   : Amey Thakur ([GitHub](https://github.com/Amey-Thakur))
* CO-AUTHOR: Mega Satish ([GitHub](https://github.com/msatmod))
* REPO     : [GitHub Repository](https://github.com/Amey-Thakur/HANGMAN-GAME-IN-DJANGO-PYTHON)
* RELEASE  : September 2, 2022
* LICENSE  : MIT License (https://opensource.org/licenses/MIT)
* 
* DESCRIPTION:
* Centralized Routing Architecture. This module maps external HTTP request vectors 
* to internal controller logic (views), orchestrating the application's navigational 
* flow and resource accessibility.
***************************************************************************************************
'''

from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from hangman import views

# Routing Matrix: Mapping URIs to Business Logic
urlpatterns = [
    # Administrative Control Plane
    path('admin/', admin.site.urls),
    
    # Primary Entry Point: Game Initialization
    path('', views.start, name='starting'),
    
    # Asynchronous State Update Endpoint (AJAX Guesses)
    path('update/word', views.update_word, name='updated-word-game'),
    
    # Social Share Vector: Shareable UUID mapping
    path('<uuid:uuid>', views.play_share, name='play-game-share'),
    
    # Asynchronous Resource Generation (New Word for Share)
    path('generate/word', views.generate_word, name='generate-word'),
    
    # Error Handling Protocol: Explicit 404 access
    path('404/', TemplateView.as_view(template_name='404.html')),
]

# Global Exception Mapping: Routing for undefined paths
handler404 = 'hangman.views.handler404'

