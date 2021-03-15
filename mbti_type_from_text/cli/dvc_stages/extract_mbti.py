import logging
from argparse import ArgumentParser

import numpy as np
import pandas as pd


def unbold_text(string):
    if string is None:
        return None
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
    result_df = pd.DataFrame()
    result_df["user_id"] = df["id"]
    result_df["mbti_type_from_flair_text"] = df["flair_text"].str.upper().apply(unbold_text).str.extract(regex)[0]
    return result_df


def extract_mbti_from_messages(df):
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
    result_df["user_id"] = df["user_id"]
    for regex_name, regex_item in regex_dict.items():
        result_df["{}__on__title".format(regex_name)] = df["title"].str.extract(regex_item["regex"])[
            regex_item["group_index"]
        ]
        result_df["{}__on__content".format(regex_name)] = df["content"].str.extract(regex_item["regex"])[
            regex_item["group_index"]
        ]
    return result_df


def get_extracted_mbti_from_messages_if_exists(row):
    if row.last_valid_index() is None:
        return np.nan
    else:
        return row[row.last_valid_index()]


def merge_extracted_mbti(mbti_type_from_flair_text_df, mbti_type_from_messages_df):
    mbti_type_from_messages_by_user_df = (
        mbti_type_from_messages_df[~mbti_type_from_messages_df["mbti_type_from_messages"].isna()][
            ["user_id", "mbti_type_from_messages"]
        ]
        .groupby("user_id")["mbti_type_from_messages"]
        .unique()
    )
    # It is better to remove these users with ambiguous types
    mbti_type_from_messages_by_user_df = (
        mbti_type_from_messages_by_user_df[mbti_type_from_messages_by_user_df.str.len() == 1].str[0].reset_index()
    )

    # Merge the extracted types
    users_mbti_df = mbti_type_from_flair_text_df.merge(mbti_type_from_messages_by_user_df, on="user_id", how="left")

    # Let's take mbti_type_from_flair_text as a default value for the MBTI type of a user
    users_mbti_df["mbti_type"] = users_mbti_df["mbti_type_from_flair_text"]

    # However, if mbti_type_from_flair_text is not set, we use mbti_type_from_comments
    no_mbti_type_from_flair_text = users_mbti_df["mbti_type_from_flair_text"].isna()
    users_mbti_df.loc[no_mbti_type_from_flair_text, "mbti_type"] = users_mbti_df[no_mbti_type_from_flair_text][
        "mbti_type_from_messages"
    ]

    return users_mbti_df[["user_id", "mbti_type"]]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name="extract_mbti")

    parser = ArgumentParser()
    parser.add_argument(
        "--users_feather_path",
        type=str,
        required=True,
        help="Path to the users data (in the feather format)",
    )
    parser.add_argument(
        "--comments_feather_path",
        type=str,
        required=True,
        help="Path to the comments data (in the feather format)",
    )
    parser.add_argument(
        "--users_mbti_feather_path",
        type=str,
        required=True,
        help="Path to where the users MBTI profiles will be saved (in the feather format)",
    )
    args = parser.parse_args()

    logger.info("Load users from '{}'".format(args.users_feather_path))
    users_df = pd.read_feather(args.users_feather_path)
    logger.info("Load comments from '{}'".format(args.comments_feather_path))
    comments_df = pd.read_feather(args.comments_feather_path)

    logger.info("Extract MBTI from flair text")
    mbti_type_from_flair_text_df = extract_mbti_from_flair_text(df=users_df)
    n_found_mbti_type_from_flair_text = (~mbti_type_from_flair_text_df["mbti_type_from_flair_text"].isna()).sum()
    logger.debug("Found MBTI for {}/{} users".format(n_found_mbti_type_from_flair_text, len(users_df)))

    logger.info("Extract MBTI from messages")
    mbti_type_from_messages_df = extract_mbti_from_messages(df=comments_df)
    mbti_type_from_messages_df["mbti_type_from_messages"] = mbti_type_from_messages_df.drop("user_id", axis=1).apply(
        get_extracted_mbti_from_messages_if_exists, axis=1
    )
    mbti_type_from_messages_df = mbti_type_from_messages_df[["user_id", "mbti_type_from_messages"]]
    n_found_mbti_type_from_messages = (~mbti_type_from_messages_df["mbti_type_from_messages"].isna()).sum()
    logger.debug("Found MBTI for {}/{} comments".format(n_found_mbti_type_from_messages, len(comments_df)))

    logger.info("Merge extracted MBTI")
    users_mbti_df = merge_extracted_mbti(
        mbti_type_from_flair_text_df=mbti_type_from_flair_text_df, mbti_type_from_messages_df=mbti_type_from_messages_df
    )

    logger.info("Save users MBTI to '{}'".format(args.users_mbti_feather_path))
    users_mbti_df.to_feather(args.users_mbti_feather_path)
