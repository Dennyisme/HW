from gpt4all import GPT4All
import torch
import torch.nn as nn



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
    
model = LLMModel()
input = "你好嗎？"
output = model(input)
print(output)
    
# model = GPT4All("gpt4all-13b-snoozy-q4_0.gguf")
# # output = model.generate("The capital of Taiwan is?", max_tokens=100)
# # print(output)


# while True:
#     # 獲取用戶輸入
#     user_input = input("輸入：\n ")
#     print("輸入內容：", user_input)
#     # 檢查是否為退出指令
#     if user_input.lower() == "exit":
#         print("退出LLM！")
#         break

#     # 像模型發送prompt，並獲得輸出
#     try:
#         output = model.generate(user_input, max_tokens=100)
#         print(output)
#     except Exception as e:
#         print(f"生程文本出現錯誤: {e}")
#         break