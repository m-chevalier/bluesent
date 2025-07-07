import torch

MODEL_PATH = '../training/results/checkpoint-1500'

def load_model(model_path: str, device: str = None):
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
    model.eval()
    return tokenizer, model, device


def predict(text: str, tokenizer, model, device: str):
    """Run model inference and return probabilities + predicted class"""
    # Tokenize input and move to device
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    ).to(device)

    # Model inference
    with torch.no_grad():
        outputs = model(**inputs)

    # Convert logits to probabilities
    probabilities = torch.softmax(outputs.logits, dim=1)
    return probabilities.cpu().numpy()


if __name__ == '__main__':
    tokenizer, model, device = load_model(MODEL_PATH)
    text = "Sometimes I really think that I would get myself in trouble if I used Claude for my assignment"
    probabilities = predict(text, tokenizer, model, device)
    print(probabilities)

