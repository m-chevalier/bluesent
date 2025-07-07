from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
from transformers import TrainingArguments, Trainer

from training_producer.scripts.training.data_preparation import connect_to_mongodb_and_load_data
from training_producer.scripts.training.llm_text_dataset import LLMTextDataset
from training_producer.scripts.training.setup import init_model_and_tokenizer

import numpy as np
import evaluate

if __name__ == "__main__":
    df = connect_to_mongodb_and_load_data("is_llm_related")

    df = df.head(5000)
    df = df[['text', 'is_llm_related']]

    num_labels = 2
    id2label = {0: "Negative", 1: "Positive"}
    label2id = {"Negative": 0, "Positive": 1}

    tokenizer, model = init_model_and_tokenizer(num_labels, label2id, id2label)

    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['is_llm_related'])

    train_dataset = LLMTextDataset(train_df, tokenizer)
    test_dataset = LLMTextDataset(test_df, tokenizer)

    train_dataloader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    test_dataloader = DataLoader(test_dataset, batch_size=16, shuffle=False)

    print("\n--- Sample from Training Dataset ---")
    sample_item = train_dataset[0]
    print(sample_item)
    print("Input IDs shape:", sample_item['input_ids'].shape)

    output_dir = "./results"

    training_arguments = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        eval_strategy="epoch",
        eval_steps=50,
        save_strategy="epoch",
        save_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        save_total_limit=2,
        greater_is_better=True
    )

    accuracy_metric = evaluate.load('accuracy')
    f1_metric = evaluate.load('f1')

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        f1 = f1_metric.compute(predictions=predictions, references=labels, average="weighted")
        accuracy = accuracy_metric.compute(predictions=predictions, references=labels)
        return {
            "accuracy": accuracy['accuracy'],
            "f1": f1['f1']
        }

    trainer = Trainer(
        model=model,
        args=training_arguments,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )


    # Train the model
    trainer.train()

    # Save the best model
    trainer.save_model(output_dir=output_dir)
