
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from emoji import demojize
from multiprocessing import Pool
import contractions
import spacy

stop_words = set(stopwords.words("english"))
nlp = spacy.load("en_core_web_sm")

def clean_comment(comment):
    """
    Clean a comment by performing various text preprocessing steps.

    Args:
        comment (str): The comment to be cleaned.

    Returns:
        str: The cleaned comment.
    """
    lemmatizer = WordNetLemmatizer()
    comment = comment.lower()
    comment = contractions.fix(comment)
    comment = re.sub(r"http\S+|www.\S+", "", comment)
    comment = demojize(comment)
    comment = re.sub(r"\W", " ", comment)
    comment = re.sub(r"\d", " ", comment)
    tokens = word_tokenize(comment)
    lemmatized_comment = [
        lemmatizer.lemmatize(word) for word in tokens if word not in stop_words
    ]
    doc = nlp(" ".join(lemmatized_comment))
    lemmatized_comment = [token.text for token in doc if token.ent_type_ == ""]
    lemmatized_comment = " ".join(lemmatized_comment)
    lemmatized_comment = re.sub(" +", " ", lemmatized_comment)
    return lemmatized_comment.strip()

df = pd.read_csv("reddit_comments_test.csv")
df = df[df["comment_body"] != "[deleted]"]
df_comments = df["comment_body"]

if len(df_comments) < 10000:
    cleaned_comments = df_comments.map(clean_comment)
else:
    with Pool(4) as p:
        cleaned_comments = p.map(clean_comment, df_comments)

cleaned_comments = pd.Series(cleaned_comments)
df["cleaned_comments"] = cleaned_comments
df.to_csv("cleaned_comments.csv", index=False)
