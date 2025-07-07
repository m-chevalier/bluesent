import torch
from torch.utils.data import Dataset

class LLMTextDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_length = 128):
        self.tokenizer = tokenizer
        self.max_length = max_length

        self.texts = dataframe['text'].tolist()
        self.labels = dataframe['is_llm_related'].tolist()

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }