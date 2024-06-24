import requests

# # 用戶輸入 prompt
# user_prompt = input("請輸入妳的prompt: ")

# # 創建 JSON 格式
# prompt_json = {
#     "prompt": user_prompt
# }

# # 發送 POST 請求
# response = requests.post(
#     "http://127.0.0.1:8000/api/llm/",
#     json=prompt_json
# )

# 輸出結果
# print(response.json())

while True:
    # 用戶輸入 prompt
    user_prompt = input("請輸入妳的prompt: ")
    
    # 檢查是否為退出指令
    if user_prompt.lower() == "exit":
        print("退出聊天！")
        break
    
    try:
        # 創建 JSON 格式
        prompt_json = {
            "prompt": user_prompt
        }

        # 發送 POST 請求
        response = requests.post(
            "http://127.0.0.1:8000/api/llm/",
            json=prompt_json
        )
        
        # 輸出結果
        print(response.json())
        
    except Exception as e:
        print(f"生程文本出現錯誤: {e}")
        break