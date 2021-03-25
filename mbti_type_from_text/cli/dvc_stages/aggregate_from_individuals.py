import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pandas as pd

absolute_path_to_project_root = Path(__file__).parent.absolute().parent.parent.parent
sys.path.append(str(absolute_path_to_project_root))  # enables running the script from a terminal
from mbti_type_from_text.utils import add_dichotomies


def aggregate_from_individuals(stats_per_user, by: [str], drop_na_classes: bool, out_index: [str] = None):
    """
    Groups individuals by the specified column(s)
    """

    def aggregate_by_one_col(by: str):
        df = stats_per_user
        aggregation = {
            **{"user_id": len, "n_messages": [sum, "mean"], "character_count": sum},
            **{mean_c: np.mean for mean_c in [c for c in df.columns if c.endswith("_mean")]},  # add std?
        }

        df_per_type = df.groupby(by, dropna=drop_na_classes).agg(aggregation)

        # flattens the multi_index
        df_per_type.columns = ["_".join(x) for x in df_per_type.columns.ravel()]
        df_per_type.columns = [
            c.replace("_mean_mean", "_mean").replace("_count_count", "_count") for c in df_per_type.columns
        ]
        df_per_type = df_per_type.rename(
            columns={
                "character_count_sum": "characters",
                "user_id_len": "individuals",
                "n_messages_sum": "messages",
                "n_messages_mean": "messages_per_individual",
            }
        )
        return df_per_type

    if len(by) == 1:
        return aggregate_by_one_col(by=by[0])
    else:
        out_df = pd.concat([aggregate_by_one_col(by=e) for e in by])
        # order of index is False, True, NaN
        if out_index is None:
            out_index = (
                pd.Series(pd.Series([[f"is_not_{e}", f"is_{e}"] for e in by]).sum())
                .str.replace("not_is", "not")
                .str.replace("is_is", "is")
            )
        out_df.index = out_index
        return out_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name="aggregate_from_individuals")

    parser = ArgumentParser()
    parser.add_argument(
        "--stats_per_user_path",
        type=str,
        required=True,
        help="Path to the statistics per user (in the feather format)",
    )
    parser.add_argument(
        "--users_mbti_feather_path",
        type=str,
        required=False,
        help="Path to the users MBTI profiles (in the feather format)",
    )
    parser.add_argument(
        "--mbti_grouped_feather_path",
        type=str,
        required=False,
        help="Path to where the group by MBTI type will be saved (in the feather format)",
    )
    parser.add_argument(
        "--dichotomy_grouped_feather_path",
        type=str,
        required=False,
        help="Path to where the group by dichotomy will be saved (in the feather format)",
    )
    args = parser.parse_args()

    logger.info("Load statistics per user from '{}'".format(args.stats_per_user_path))
    stats_per_user_df = pd.read_feather(args.stats_per_user_path)
    logger.info("Load users MBTI from '{}'".format(args.users_mbti_feather_path))
    users_mbti_df = pd.read_feather(args.users_mbti_feather_path)

    logger.info("Join statistics with MBTI types")
    stats_per_user_with_mbti_df = stats_per_user_df.merge(users_mbti_df, on="user_id")
    logger.info("Add dichotomies")
    stats_per_user_with_labels_df = add_dichotomies(df=stats_per_user_with_mbti_df)  # might need to copy

    logger.info("Group by MBTI type")
    grouped_by_mbti_type = aggregate_from_individuals(
        stats_per_user=stats_per_user_with_mbti_df, by=["mbti_type"], drop_na_classes=False
    )

    logger.info("Group by dichotomy")
    dichotomies = [f"is_{letter}" for letter in list("ESTJ")]
    grouped_by_dichotomy = aggregate_from_individuals(
        stats_per_user=stats_per_user_with_labels_df,
        by=dichotomies,
        drop_na_classes=True,
        out_index=[f"is_{letter}" for letter in list("IENSFTPJ")]
        # have to reverse by pair as out indexes are False then True
    )

    logger.info("Save grouped by MBTI type to '{}'".format(args.mbti_feather_path))
    grouped_by_mbti_type.to_feather(args.mbti_feather_path)
    logger.info("Save grouped by dichotomy to '{}'".format(args.dichotomy_feather_path))
    grouped_by_mbti_type.to_feather(args.dichotomy_feather_path)

    """
    stats_per_user = pd.read_feather("../../../data/processed/stats_per_user.feather")
    stats_per_user = stats_per_user\
        .merge(pd.read_feather("../../../data/processed/mbti_per_user.feather"), on="user_id")
    stats_per_user = add_dichotomies(df=stats_per_user)
    o_df = aggregate_from_individuals(
        stats_per_user=stats_per_user,
        by=["mbti_type"],
        drop_na_classes=False
    )

    dichotomies = [f"is_{letter}" for letter in list("ESTJ")]
    all_dichotomies = [f"is_{letter}" for letter in list("EISNTFJP")]
    o_df_ = aggregate_from_individuals(
        stats_per_user=stats_per_user,
        by=dichotomies,
        drop_na_classes=True,
        out_index=[f"is_{letter}" for letter in list("IENSFTPJ")] # have to reverse by pair as indexes are False then True
    )

    print()
    """
