from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_checkpoint = "sentence-transformers/all-MiniLM-L6-v2"

def init_model_and_tokenizer(num_labels, label2id, id2label):
    global model_checkpoint
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint, num_labels=num_labels, label2id=label2id, id2label=id2label)

    return tokenizer, model