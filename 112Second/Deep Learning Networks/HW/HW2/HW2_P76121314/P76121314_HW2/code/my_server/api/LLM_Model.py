import torch
import torch.nn as nn
import os
import platform
import signal
from transformers import AutoTokenizer, AutoModel
from django.apps import apps
from .load_weight import model, tokenizer
# from gpt4all import GPT4All

# class LLMModel():
#     def __init__(self):
#         self.model = GPT4All("gpt4all-13b-snoozy-q4_0.gguf")

#     def process_prompt(self, prompt):
#         print("prompt: ",prompt)
#         outputs = self.model.generate(prompt, max_tokens=100)
#         print("回答: ",outputs)
#         return outputs

# class LLM_Model(nn.Module):
#     def __init__(self):
#         super(LLM_Model, self).__init__()
#         self.model = GPT4All("gpt4all-13b-snoozy-q4_0.gguf")
    
#     def forward(self, input):
#         try:
#             output = self.model.generate(input, max_tokens=100)
#             return output
#         except Exception as e:
#             print(f"生程文本出現錯誤: {e}")
#             return ""



class ChatGLM(nn.Module):
    def __init__(self):
        super(ChatGLM, self).__init__()
        # self.tokenizer = AutoTokenizer.from_pretrained("chatglm-6b", trust_remote_code=True)
        # self.model = AutoModel.from_pretrained("chatglm-6b", trust_remote_code=True).float().eval()
        self.tokenizer = tokenizer
        self.model = model
    def forward(self, input, history):
        try:
            output = self.model.stream_chat(self.tokenizer, input)
            # print("gggg",output[0])
            # print("llll",output[0][-1])
            responses = []
            for response in output:
                responses.append(response)
            # print("responses形狀: ",len(responses))
            # for idx, response in enumerate(responses):
            #     print(f"响应 {idx+1} 的长度（如果是字符串或列表）:", len(response))
            #     print(f"响应 {idx+1} 的内容:", response)
            response = responses[-1][0]
            
            return response
        except Exception as e:
            print(f"生程文本出現錯誤: {e}")
            return 
            
            