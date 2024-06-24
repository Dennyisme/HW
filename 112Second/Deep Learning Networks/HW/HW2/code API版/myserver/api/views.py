from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
# from .utils import model_instance
from .utils import LLM
from rest_framework.renderers import JSONRenderer


class LLMView(APIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request):
        # 示例返回JSON数据
        data = {"message": "This is a JSON response"}
        return Response(data)
    
    def post(self, request, *args, **kwargs):
        prompt_text = request.data.get('prompt', '')
        if not prompt_text:
            return Response({"status": False, "message": "No prompt provided"}, status=400)
        
        try:
            response_text = LLM(prompt_text)
            print("response_text: ",response_text)
            return Response({"status": True, "data": {"response": response_text}}, status=200)
        except Exception as e:
            return Response({"status": False, "failed": str(e)}, status=500)
