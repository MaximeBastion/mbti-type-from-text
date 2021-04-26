import logging
import re
from argparse import ArgumentParser

import emot  # https://github.com/NeelShah18/emot
import nltk
import pandas as pd
from nltk.tokenize import word_tokenize


def group_messages_per_user(comments_df):
    messages_per_user_df = (
        comments_df.groupby("user_id").agg({"message": list}).rename(columns={"message": "message_list"})
    )
    messages_per_user_df["messages"] = messages_per_user_df["message_list"].apply(lambda l: " ".join(l))
    return messages_per_user_df


def compute_simple_messages_statistics(df):
    df["n_messages"] = df["message_list"].apply(len)
    df["character_count"] = df["messages"].apply(len)
    return df


def count_emojis_and_emoticons(text):
    # Note: emoticons count is partial: ^^ is not recognized for example
    _sum = 0
    for match_obj in [emot.emoji(text), emot.emoticons(text)]:
        if type(match_obj) is not list:  # apparently, when there are no matches, output is list
            _sum += len(match_obj["value"])
    return _sum


def remove_emojis(text):
    match_obj = emot.emoji(text)
    if type(match_obj) is list:
        return text

    unique_matches = set(match_obj["value"])
    for match in unique_matches:
        text = text.replace(match, " ")
    return text


def remove_emoticons(text):
    match_obj = emot.emoticons(text)
    if type(match_obj) is list:
        return text

    unique_matches = set(match_obj["value"])
    for match in unique_matches:
        text = text.replace(match, " ")
    return text


def handle_emojis_and_emoticons(df, messages_col_name: str):
    df["emoji_and_emoticon_count"] = df[messages_col_name].apply(count_emojis_and_emoticons)
    df[messages_col_name] = (
        df[messages_col_name].apply(remove_emoticons).apply(remove_emojis)
    )  # maybe we could keep emojis as tokens for vectorization?
    return df


def get_regexes_dict():
    # Note: will all be used case insensitively
    separated = r"\b(item)\b"
    return {
        "url": r"((https?)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)\b)",
        "line_break": r"(\n)",
        "i": separated.replace("item", "I"),  # I or i as single-letter word
        "you": separated.replace("item", "you|u"),
        "we": separated.replace("item", "we"),
        "they": separated.replace("item", "they"),
        "enneagram": separated.replace("item", "([1-9]w[1-9])|enneagram"),  # ignores single-digit enneagrams :/
        "cognitive_function": separated.replace("item", "([NSFJ][ie])|cognitive function"),
        "number_group": r"([0-9]+)",
        "hashtag": r"(#)[^#]",  # ignoring multiple
        "punctuation": r"([.;\:,!?])",
        "mbti_type": separated.replace("item", "(I|E|X)(S|N|X)(F|T|X)(J|P|X)"),
    }


def count_and_remove(df, messages_col_name: str, regexes_dict: {str: str}, regex_names: [str]):
    """
    For each regex, counts occurences from the specified col into a new column, and removes them
    """
    for regex_name, regex in regexes_dict.items():
        if regex_name in regex_names:
            df[f"{regex_name}_count"] = df[messages_col_name].apply(
                lambda m: len(re.findall(regex, m, flags=re.IGNORECASE))
            )  # counts
            df[messages_col_name] = df[messages_col_name].apply(
                lambda m: re.sub(regex, " ", m, flags=re.IGNORECASE)
            )  # removes
    return df


def clean_and_count_all_items(df, regexes_dict: {str: str}, messages_col_name: str):
    """
    For each regex, counts occurences from the specified col into a new column, and removes them
    Some are done before remove emojis/emoticons, some after
    Can be applied to any df having a column containing messages as string
    """
    to_do_before_emojis_and_emoticons = ["url"]

    df = count_and_remove(
        df=df,
        messages_col_name=messages_col_name,
        regexes_dict=regexes_dict,
        regex_names=to_do_before_emojis_and_emoticons,
    )

    df = handle_emojis_and_emoticons(df, messages_col_name)

    to_do_after_emojis_and_emoticons = [
        r for r in list(regexes_dict.keys()) if r not in to_do_before_emojis_and_emoticons
    ]
    df = count_and_remove(
        df=df,
        messages_col_name=messages_col_name,
        regexes_dict=regexes_dict,
        regex_names=to_do_after_emojis_and_emoticons,
    )

    return df


def compute_mean_statistics_per_message(df, messages_count_col: str, char_count_col: str, drop_count_cols: bool):
    for count_col in [c for c in df.columns if c.endswith("_count")]:
        mean_col_name = "{item}_message_mean".format(item=count_col[:-6])
        df[mean_col_name] = df[count_col] / df[messages_count_col]
        if count_col != "character_count":  # mean char per char is not super useful
            mean_col_name = "{item}_char_mean".format(item=count_col[:-6])
            df[mean_col_name] = df[count_col] / df[char_count_col]
    if drop_count_cols:
        df = df[[c for c in df.columns if not c.endswith("_count") or c == "character_count"]]
    return df


def clean_and_tokenize_text(text):
    text = text.lower()
    text = re.sub(r"\W|_", " ", text)  # removes special chars
    text = re.sub(r"\s+", " ", text)  # removes multiple spaces
    text = re.sub(r"^\s|\s$", "", text)  # removes space at the start or end of the string -> strip?
    # add before: replace abreviations by the full version: u for you, imo for in my opinion, bc

    tokens = word_tokenize(text)  # tokenizes

    stopwords = nltk.corpus.stopwords.words("english")  # are all messages in english?
    tokens = [token for token in tokens if token not in stopwords]  # removes stopwords
    tokens = [token for token in tokens if len(token) > 1]  # removes 1-char tokens

    wn = nltk.WordNetLemmatizer()
    tokens = [wn.lemmatize(token) for token in tokens]  # lematizes=roots words
    return tokens


def compute_token_statistics(df, tokens_col_name: str):
    df["tokens_count"] = df[tokens_col_name].apply(len)
    df["unique_tokens_count"] = df[tokens_col_name].apply(lambda tokens: len(set(tokens)))
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name="compute_statistics_and_tokens_per_user")

    parser = ArgumentParser()
    parser.add_argument(
        "--comments_feather_path",
        type=str,
        required=True,
        help="Path to the comments data (in the feather format)",
    )
    parser.add_argument(
        "--stats_per_user_path",
        type=str,
        required=True,
        help="Path where the statistics per user will be saved (in the feather format)",
    )
    parser.add_argument(
        "--tokens_per_user_path",
        type=str,
        required=True,
        help="Path where the tokens per user will be saved (in the feather format)",
    )
    args = parser.parse_args()

    logger.info("Load comments from '{}'".format(args.comments_feather_path))
    comments_df = pd.read_feather(args.comments_feather_path)

    logger.info("Group messages per user")
    messages_per_user_df = group_messages_per_user(comments_df=comments_df)

    logger.info("Compute simple statistics about the messages")
    messages_per_user_df = compute_simple_messages_statistics(df=messages_per_user_df)
    messages_per_user_df = messages_per_user_df.reset_index()
    messages_per_user_df = messages_per_user_df[["user_id", "n_messages", "character_count", "messages"]]

    logger.info("Start counting and removing items")
    messages_per_user_df["messages_raw"] = messages_per_user_df["messages"]  # keeping a copy of the original messages
    regexes_dict = get_regexes_dict()
    messages_per_user_df = clean_and_count_all_items(
        df=messages_per_user_df, regexes_dict=regexes_dict, messages_col_name="messages"
    )

    logger.info("Compute mean statistics per message")
    messages_per_user_df = compute_mean_statistics_per_message(
        df=messages_per_user_df, messages_count_col="n_messages", char_count_col="character_count", drop_count_cols=True
    )

    logger.info("Tokenize messages")
    messages_per_user_df["tokens"] = messages_per_user_df["messages"].apply(clean_and_tokenize_text)

    logger.info("Compute statistics about the tokens")
    messages_per_user_df = compute_token_statistics(df=messages_per_user_df, tokens_col_name="tokens")

    logger.info("Select the columns to keep")
    simple_statistics = ["n_messages", "character_count"]
    mean_statistics_per_message_columns = [c for c in messages_per_user_df.columns if c.endswith("_mean")]
    columns_to_select = (
        ["user_id"] + simple_statistics + mean_statistics_per_message_columns + ["tokens_count", "unique_tokens_count"]
    )
    stats_per_user_df = messages_per_user_df[columns_to_select].reset_index(drop=True)
    tokens_per_user_df = messages_per_user_df[["user_id", "tokens"]].reset_index(drop=True)

    logger.info("Save statistics per user to '{}'".format(args.stats_per_user_path))
    stats_per_user_df.to_feather(args.stats_per_user_path)
    logger.info("Save tokens per user to '{}'".format(args.tokens_per_user_path))
    tokens_per_user_df.to_feather(args.tokens_per_user_path)