import praw
import prawcore.exceptions
import logging
import time
from datetime import datetime
import pandas as pd
from config import reddit_config

# Configure logging
logging.basicConfig(level=logging.INFO)


class RedditScraper:
    """
    A class for scraping comments from Reddit using PRAW library.
    """

    def __init__(self, reddit_config):
        """
        Initializes the RedditScraper object.

        Args:
            reddit_config (dict): Configuration parameters for Reddit API.

        """
        self.reddit_config = reddit_config
        self.reddit = self.authenticate_with_retry()

    def authenticate_with_retry(self):
        """
        Authenticates with Reddit API using the provided credentials.

        Returns:
            praw.Reddit: Authenticated Reddit API object.

        """
        max_retries = 5
        for retry in range(max_retries):
            try:
                reddit = praw.Reddit(
                    client_id=self.reddit_config["client_id"],
                    client_secret=self.reddit_config["client_secret"],
                    user_agent=self.reddit_config["user_agent"],
                    password=self.reddit_config["password"],
                    username=self.reddit_config["username"],
                )
                return reddit
            except prawcore.exceptions.ResponseException as e:
                logging.error(f"ResponseException during authentication: {e}")
                return None
            except Exception as e:
                logging.error(f"Exception during authentication: {e}")
                time.sleep(60)

        logging.error("All retry attempts failed during authentication. Exiting.")
        return None

    def fetch_comments(self, url):
        """
        Fetches comments from a Reddit submission.

        Args:
            url (str): URL of the Reddit submission.

        Returns:
            list: List of dictionaries containing comment data.

        """
        if not self.reddit:
            return []

        submission = self.reddit.submission(url=url)
        try:
            submission.comments.replace_more(
                limit=None
            )  # Remove limit to fetch all comments
        except prawcore.exceptions.TooManyRequests as e:
            logging.warning(f"Too many requests: {e}")
            retry_after = e.response.headers.get("Retry-After")
            if retry_after:
                logging.info(f"Waiting for {retry_after} seconds before retrying...")
                time.sleep(int(retry_after) + 1)  # Add 1 second buffer
            else:
                logging.info("Waiting for 60 seconds before retrying...")
                time.sleep(60)
            # Retry fetching comments
            return self.fetch_comments(url)

        data_list = []

        for comment in submission.comments.list():
            data_list.append(
                {
                    "comment_author": getattr(comment.author, "name", None),
                    "comment_body": comment.body,
                    "comment_score": comment.score,
                    "comment_date": datetime.utcfromtimestamp(
                        comment.created_utc
                    ).strftime("%Y-%m-%d %H:%M:%S UTC"),
                }
            )

        return data_list


def main():
    """
    Main function to execute the RedditScraper.

    """
    url = "https://www.reddit.com/r/AskReddit/comments/12rk46t/there_is_a_greek_proverb_a_society_grows_great/"  # Add url here

    scraper = RedditScraper(reddit_config)
    data = scraper.fetch_comments(url)
    csv_file = "reddit_comments_test.csv"  # Add file name here
    if data:
        df = pd.DataFrame.from_records(data)
        df.to_csv(csv_file, index=False)
        logging.info(f"Comments fetched and saved to {csv_file}")
    else:
        logging.error("Failed to fetch comments.")


if __name__ == "__main__":
    main()
