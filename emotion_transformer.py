import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import pandas as pd

df = pd.read_csv("cleaned_comments_1.csv")

# Load the pre-trained model and tokenizer for emotion classification
model = AutoModelForSequenceClassification.from_pretrained(
    "cardiffnlp/twitter-roberta-base-emotion"
)
tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-emotion")

# Create an emotion analysis pipeline
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Process the texts in batches
batch_size = 100
emotions = []
cleaned_comments = []
for i in range(0, len(df["cleaned_comments"]), batch_size):
    batch = df["cleaned_comments"][i : i + batch_size].dropna().astype(str).tolist()
    batch = [comment for comment in batch if comment]
    if batch:
        results = classifier(batch)
        emotions.extend([result["label"] for result in results])
        cleaned_comments.extend(batch)

# Create a new DataFrame for the cleaned comments and their emotions
df_clean = pd.DataFrame({"cleaned_comments": cleaned_comments, "emotion": emotions})

# Merge the new DataFrame with the original DataFrame
df = df.merge(df_clean, on="cleaned_comments", how="left")

df.to_csv("emotion_analysis.csv", index=False)
