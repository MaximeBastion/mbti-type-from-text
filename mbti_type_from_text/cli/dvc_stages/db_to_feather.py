import logging
from argparse import ArgumentParser

import numpy as np
import pandas as pd

from mbti_type_from_text.db_utils import create_connection


def preprocess_users(df):
    # apparently, feather treats "NaN" as "None", converting back to "NaN"
    df = df.fillna(np.nan)

    return df


def preprocess_comments(df):
    # apparently, feather treats "NaN" as "None", converting back to "NaN"
    df = df.fillna(np.nan)

    # replaces field that's entirely space (or empty) with NaN
    df["title"] = df.title.replace(r"^\s*$", np.nan, regex=True)

    # Concatenate title and content
    df["message"] = df["title"] + "\n" + df["content"]

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name="db_to_feather")

    parser = ArgumentParser()
    parser.add_argument("--db_path", type=str, required=True, help="Path to where the database file will be saved")
    parser.add_argument(
        "--users_feather_path",
        type=str,
        required=True,
        help="Path to where the users will be saved (in the feather format)",
    )
    parser.add_argument(
        "--comments_feather_path",
        type=str,
        required=True,
        help="Path to where the comments will be saved (in the feather format)",
    )
    args = parser.parse_args()

    logger.info("Create connection to '{}'".format(args.db_path))
    db_connection = create_connection(db_path=args.db_path)

    logger.info("Load users from DB")
    users_df = pd.read_sql(sql="SELECT * FROM Users", con=db_connection)
    logger.info("Load comments from DB")
    comments_df = pd.read_sql(sql="SELECT * FROM Comments", con=db_connection)

    logger.info("Preprocess users")
    users_df = preprocess_users(df=users_df)
    logger.info("Preprocess comments")
    comments_df = preprocess_comments(df=comments_df)

    logger.info("Save users to '{}'".format(args.users_feather_path))
    users_df.to_feather(args.users_feather_path)
    logger.info("Save comments to '{}'".format(args.comments_feather_path))
    comments_df.to_feather(args.comments_feather_path)
