

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import pandas as pd
import tensorflow
from tensorflow import keras

df = pd.read_csv("cleaned_comments.csv")

# Load the pre-trained model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained(
    "cardiffnlp/twitter-roberta-base-sentiment"
)
tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")

# Create a sentiment analysis pipeline
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Process the texts in batches
batch_size = 100
sentiments = []
cleaned_comments = []
for i in range(0, len(df["cleaned_comments"]), batch_size):
    batch = df["cleaned_comments"][i : i + batch_size].dropna().astype(str).tolist()
    results = classifier(batch)
    sentiments.extend([result["label"] for result in results])
    cleaned_comments.extend(batch)

# Create a new DataFrame for the cleaned comments and their sentiments
df_clean = pd.DataFrame({"cleaned_comments": cleaned_comments, "sentiment": sentiments})

# Merge the new DataFrame with the original DataFrame
df = df.merge(df_clean, on="cleaned_comments", how="left")

df.to_csv("sentiment_analysis.csv", index=False)
