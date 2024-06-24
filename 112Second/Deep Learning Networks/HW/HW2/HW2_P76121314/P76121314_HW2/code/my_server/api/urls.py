from django.urls import path
# from . import views
from .views import LLMView

urlpatterns = [
    path('chat/', LLMView.as_view(), name='chat'),
]


