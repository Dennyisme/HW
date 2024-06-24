from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .LLM_Model import ChatGLM
from rest_framework.renderers import JSONRenderer
# from transformers import AutoTokenizer, AutoModel

class LLMView(APIView):
    # tokenizer = AutoTokenizer.from_pretrained("chatglm-6b", trust_remote_code=True)
    # model = AutoModel.from_pretrained("chatglm-6b", trust_remote_code=True).float()
    def post(self, request):
        history = []
        prompt_text = request.data.get("prompt","")
        print("prompt_text: ",prompt_text)
        if not prompt_text:
            return Response({"status": False, "message": "No prompt provided"}, status=400)
        
        try:
            model_instance = ChatGLM()
            response_text = model_instance(prompt_text, history)
            print("response_text: ",response_text)
            return Response({"status": True, "data": {"response": response_text}}, status=200)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=500)
        
# class LLMView(APIView):
#     def post(self, request):
#         prompt_text = request.data.get('prompt', '')
#         if not prompt_text:
#             return Response({"status": False, "message": "No prompt provided"}, status=400)
        
#         try:
#             model_instance = LLM_Model()
#             response_text = model_instance.forward(prompt_text)
#             return Response({"status": True, "data": {"response": response_text}}, status=200)
#         except Exception as e:
#             return Response({"status": False, "message": str(e)}, status=500)
