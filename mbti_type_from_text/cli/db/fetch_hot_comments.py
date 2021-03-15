import argparse
import logging

from praw import Reddit

from mbti_type_from_text.db_utils import create_connection, insert_or_update_submission

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name="fetch_hot_comments")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_path", type=str, required=True, help="Path to the database file")
    parser.add_argument(
        "--subreddit", type=str, required=True, help="Name of the subreddit from which hot comments will be fetched"
    )
    parser.add_argument("--submission_flairs", nargs="+", help="List of flairs to select", required=False)
    parser.add_argument("--n_hot", type=int, required=True, help="Number of hot submissions to fetch")
    parser.add_argument("--reddit_client_id", type=str, required=True, help="Client ID to use with Reddit's API")
    parser.add_argument(
        "--reddit_client_secret", type=str, required=True, help="Client secret to use with Reddit's API"
    )
    args = parser.parse_args()

    logger.info("Create connection to '{}'".format(args.db_path))
    db_connection = create_connection(db_path=args.db_path)

    logger.info("Connect to Reddit API")
    reddit = Reddit(
        user_agent="mbti-type-from-text:v0.0.1 (by /u/gcoter)",
        client_id=args.reddit_client_id,
        client_secret=args.reddit_client_secret,
    )

    logger.info("Start iterating over {} hot submissions of subreddit '{}'".format(args.n_hot, args.subreddit))
    for n, submission in enumerate(reddit.subreddit(args.subreddit).hot(limit=args.n_hot)):
        if (
            submission.is_self
            and submission.num_comments > 0
            and (submission.link_flair_text is None or submission.link_flair_text in args.submission_flairs)
        ):
            logger.info("Handle submission '{}' ({}/{})".format(submission.title, n + 1, args.n_hot))
            insert_or_update_submission(submission=submission, db_connection=db_connection)
