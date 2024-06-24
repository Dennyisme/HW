from django.urls import path
# from . import views
from .views import LLMView

urlpatterns = [
    path('llm/', LLMView.as_view(), name='llm-api'),
]


