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
    url = "https://www.reddit.com/r/AskReddit/comments/12rk46t/there_is_a_greek_proverb_a_society_grows_great/"
    submission = reddit.submission(url=url)
    submission.comments.replace_more(limit=0)  # Remove limit to fetch all comments

    data_list = []

    for comment in submission.comments.list():
        data_list.append(
            {
                "comment_author": getattr(comment.author, "name", None),
                "comment_body": comment.body,
                "comment_score": comment.score,
                "comment_date": datetime.utcfromtimestamp(comment.created_utc).strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                ),
            }
        )

    df = pd.DataFrame.from_records(data_list)

    print(df.head())

    df.to_csv("reddit_comments_1.csv", index=False)
