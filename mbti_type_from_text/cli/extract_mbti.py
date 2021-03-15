import logging
from argparse import ArgumentParser

import numpy as np
import pandas as pd

from mbti_type_from_text.db_utils import create_connection


def unbold_text(string):
    unbolded_string = ""
    for c in string:
        int_code = ord(c)
        if int_code >= ord("𝐀") and int_code <= ord("𝐙"):
            unbolded_string += chr(int_code - 119743)
        else:
            unbolded_string += c
    return unbolded_string


def extract_mbti_from_flair_text(df):
    regex = r"((I|E|X)(S|N|X)(F|T|X)(J|P|X))"
    return df["flair_text"].str.upper().apply(unbold_text).str.extract(regex)[0]


def extract_mbti_from_message(df):
    mbti_regex = "(I|E|X)(S|N|X)(F|T|X)(J|P|X)"
    regex_dict = {
        "i_am_mbti_regex": {"regex": "I('m| am)(?: (an|a))? ({})".format(mbti_regex), "group_index": 2},
        "my_mbti_regex": {"regex": "(M|m)y ({}) (personality|experience)".format(mbti_regex), "group_index": 1},
        "mbti_here_regex": {"regex": "({})(?: \((m|f)\))? here".format(mbti_regex), "group_index": 0},
        "fellow_mbti_regex": {"regex": "(F|f)ellow ({})".format(mbti_regex), "group_index": 1},
        "i_mbti_regex": {"regex": "(Me|I)(?: )?\(({})\)".format(mbti_regex), "group_index": 1},
        "looking_for_regex": {"regex": "({}) looking for".format(mbti_regex), "group_index": 0},
    }
    result_df = pd.DataFrame()
    for regex_name, regex_item in regex_dict.items():
        result_df["{}__on__title".format(regex_name)] = df["title"].str.extract(regex_item["regex"])[
            regex_item["group_index"]
        ]
        result_df["{}__on__content".format(regex_name)] = df["content"].str.extract(regex_item["regex"])[
            regex_item["group_index"]
        ]
    return result_df


def get_extracted_mbti_if_exists(row):
    if row.last_valid_index() is None:
        return np.nan
    else:
        return row[row.last_valid_index()]


def merge_extracted_mbti(users_df, comments_df):
    extracted_mbti_by_user_df = (
        comments_df[~comments_df["extracted_mbti"].isna()][["user_id", "extracted_mbti"]]
        .groupby("user_id")["extracted_mbti"]
        .unique()
    )

    # It is better to remove these users with ambiguous types
    extracted_mbti_by_user_df = extracted_mbti_by_user_df[extracted_mbti_by_user_df.str.len() == 1].str[0].reset_index()

    users_df = users_df.merge(extracted_mbti_by_user_df, left_on="id", right_on="user_id", how="left")
    users_df = users_df.rename(
        columns={"mbti_type": "mbti_type_from_flair_text", "extracted_mbti": "mbti_type_from_comments"}
    )

    # Let's take mbti_type_from_flair_text as a default value for the MBTI type of a user
    users_df["mbti_type"] = users_df["mbti_type_from_flair_text"]

    # However, if mbti_type_from_flair_text is not set, we use mbti_type_from_comments
    no_mbti_type_from_flair_text = users_df["mbti_type_from_flair_text"].isna()
    users_df.loc[no_mbti_type_from_flair_text, "mbti_type"] = users_df[no_mbti_type_from_flair_text][
        "mbti_type_from_comments"
    ]

    return users_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name="extract_mbti")

    parser = ArgumentParser()
    parser.add_argument("--db_path", type=str, required=True, help="Path to where the database file will be saved")
    parser.add_argument(
        "--users_feather_path",
        type=str,
        required=True,
        help="Path to where the users will be saved (in the feather format)",
    )
    args = parser.parse_args()

    logger.info("Create connection to '{}'".format(args.db_path))
    db_connection = create_connection(db_path=args.db_path)

    logger.info("Load comments from DB")
    comments_df = pd.read_sql(sql="SELECT * FROM Comments", con=db_connection)
    logger.info("Load users from DB")
    users_df = pd.read_sql(sql="SELECT * FROM Users", con=db_connection)

    logger.info("Extract MBTI from flair text")
    users_df["mbti_type"] = extract_mbti_from_flair_text(df=users_df)

    logger.info("Extract MBTI from messages")
    extract_mbti_from_message_df = extract_mbti_from_message(comments_df)
    comments_df["extracted_mbti"] = extract_mbti_from_message_df.apply(get_extracted_mbti_if_exists, axis=1)

    logger.info("Merge extracted MBTI")
    users_df = merge_extracted_mbti(users_df, comments_df)
    users_df = users_df[["id", "name", "mbti_type"]]

    # saving the users_df with mbti_types as a feather file
    logger.info("Save users to '{}'".format(args.users_feather_path))
    users_df.to_feather(args.users_feather_path)
