import argparse
import logging

from praw import Reddit

from mbti_type_from_text.db_utils import (
    create_connection,
    get_all_user_names,
    insert_or_update_user_comments,
    insert_or_update_user_submissions,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name="fetch_user_comments")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_path", type=str, required=True, help="Path to the database file")
    parser.add_argument(
        "--n_hot", type=int, required=True, help="Number of hot submissions and comments to fetch for each user"
    )
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

    logger.info("Start iterating over users")
    all_user_names = get_all_user_names(db_connection=db_connection)
    for n, user_name in enumerate(all_user_names):
        logger.info("Handle user '{}' ({}/{})".format(user_name, n + 1, len(all_user_names)))
        user = reddit.redditor(name=user_name)
        insert_or_update_user_submissions(user=user, n_hot=args.n_hot, db_connection=db_connection)
        insert_or_update_user_comments(user=user, n_hot=args.n_hot, db_connection=db_connection)
