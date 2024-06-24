from django.apps import AppConfig
from transformers import AutoTokenizer, AutoModel
import os
from .load_weight import load_weight

class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
    
    
    tokenizer = None
    model = None

    def ready(self):
        load_weight()
        print("Model and tokenizer have been loaded.")
