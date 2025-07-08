import torch

MODEL_PATH = '../training/results'

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
        max_length=256,
    ).to(device)

    # Model inference
    with torch.no_grad():
        outputs = model(**inputs)

    # Convert logits to probabilities
    probabilities = torch.softmax(outputs.logits, dim=1).cpu().numpy()

    prediction = torch.argmax(outputs.logits, dim=1).item()
    return probabilities, 'llm related' if prediction == 1 else 'not llm related'

if __name__ == '__main__':
    tokenizer, model, device = load_model(MODEL_PATH)
    model.push_to_hub('AWCO/llm-text-classifier')

