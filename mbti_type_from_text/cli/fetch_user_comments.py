import argparse
import logging
import os

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
    parser.add_argument(
        "--user_ids_file_path",
        type=str,
        required=False,
        help="Path to a text file containing the user IDs to treat (one per line)",
    )
    parser.add_argument(
        "--progress_file_path",
        type=str,
        required=False,
        help="Path to a text file where the treated user IDs will be saved. They are skipped in the next executions of this command.",
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

    logger.info("List users to treat")
    if args.user_ids_file_path is None:
        user_names = get_all_user_names(db_connection=db_connection)
    else:
        logger.info("Read users to treat from '{}'".format(args.user_ids_file_path))
        with open(args.user_ids_file_path, "r") as f:
            user_names = f.readlines()
    if args.progress_file_path is not None and os.path.exists(args.progress_file_path):
        logger.info("Read users to not treat from '{}'".format(args.progress_file_path))
        with open(args.progress_file_path, "r") as f:
            already_treated_user_names = f.readlines()
        user_names = [user_name for user_name in user_names if user_name not in already_treated_user_names]

    logger.info("Start iterating over users")
    for n, user_name in enumerate(user_names):
        logger.info("Handle user '{}' ({}/{})".format(user_name, n + 1, len(user_names)))
        user = reddit.redditor(name=user_name)
        insert_or_update_user_submissions(user=user, n_hot=args.n_hot, db_connection=db_connection)
        insert_or_update_user_comments(user=user, n_hot=args.n_hot, db_connection=db_connection)
        if args.progress_file_path is not None:
            logger.debug("Write user ID to '{}'".format(args.progress_file_path))
            with open(args.progress_file_path, "a") as f:
                f.write(user_name)
