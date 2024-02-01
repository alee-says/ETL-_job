import praw
from prawcore.exceptions import PrawcoreException
import time
import pandas as pd
from datetime import datetime
from config import reddit_config


max_retries = 20


def authenticate_with_retry():
    for retry in range(max_retries):
        try:
            reddit = praw.Reddit(
                client_id=reddit_config["client_id"],
                client_secret=reddit_config["client_secret"],
                user_agent=reddit_config["user_agent"],
                password=reddit_config["password"],
                username=reddit_config["username"],
            )

            return reddit

        except PrawcoreException as e:
            print(f"PrawcoreException: {e}")

        except Exception as e:
            print(f"Exception: {e}")

        print(f"Retry attempt {retry + 1}/{max_retries}")
        time.sleep(60)

    print("All retry attempts failed. Exiting.")
    return None


reddit = authenticate_with_retry()

if reddit:
    subreddit_name = "Artificial"
    subreddit = reddit.subreddit(subreddit_name)
    hot_posts = subreddit.hot(limit=100)

    data_list = [
        {
            "Title": post.title,
            "Author": getattr(post.author, "name", None),
            "Score": post.score,
            "Date": datetime.utcfromtimestamp(post.created_utc).strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            ),
        }
        for post in hot_posts
    ]

    df = pd.DataFrame.from_records(data_list)

    print(df)

df.to_csv("reddit_hot_100_posts.csv", index=False)
