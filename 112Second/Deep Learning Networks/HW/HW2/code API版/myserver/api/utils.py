import torch
import torch.nn as nn

from gpt4all import GPT4All

# class LLMModel():
#     def __init__(self):
#         self.model = GPT4All("gpt4all-13b-snoozy-q4_0.gguf")

#     def process_prompt(self, prompt):
#         print("prompt: ",prompt)
#         outputs = self.model.generate(prompt, max_tokens=100)
#         print("回答: ",outputs)
#         return outputs

class LLMModel(nn.Module):
    def __init__(self):
        super(LLMModel, self).__init__()
        self.model = GPT4All("gpt4all-13b-snoozy-q4_0.gguf")
    
    def forward(self, input):
        try:
            output = self.model.generate(input, max_tokens=100)
            # print(output)
        except Exception as e:
            print(f"生程文本出現錯誤: {e}")
        return output
    
LLM = LLMModel()