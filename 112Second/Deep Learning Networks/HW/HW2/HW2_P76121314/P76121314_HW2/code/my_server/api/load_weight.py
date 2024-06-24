from transformers import AutoTokenizer, AutoModel

model = None
tokenizer = None

def load_weight():
    global model, tokenizer
    if model is None or tokenizer is None:
        model_identifier = "chatglm-6b"
        tokenizer = AutoTokenizer.from_pretrained("chatglm-6b", trust_remote_code=True)
        model = AutoModel.from_pretrained("chatglm-6b", trust_remote_code=True).float().eval()
        print("權重下載完畢")