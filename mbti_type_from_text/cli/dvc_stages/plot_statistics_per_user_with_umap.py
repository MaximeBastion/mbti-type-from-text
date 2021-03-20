import logging
from argparse import ArgumentParser

import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from umap import UMAP

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name="plot_statistics_per_user_with_umap")

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
        required=True,
        help="Path to the users MBTI profiles (in the feather format)",
    )
    parser.add_argument(
        "--plot_path",
        type=str,
        required=True,
        help="Path where the plot will be saved (in the HTML format)",
    )
    args = parser.parse_args()

    logger.info("Load statistics per user from '{}'".format(args.stats_per_user_path))
    stats_per_user_df = pd.read_feather(args.stats_per_user_path)
    logger.info("Load users MBTI from '{}'".format(args.users_mbti_feather_path))
    users_mbti_df = pd.read_feather(args.users_mbti_feather_path)

    logger.info("Join statistics with MBTI types")
    stats_per_user_with_mbti_df = stats_per_user_df.merge(users_mbti_df, on="user_id")

    logger.info("Standardize statistics")
    stats_columns = stats_per_user_with_mbti_df.columns.difference(["user_id", "mbti_type"]).tolist()
    scaler = StandardScaler()
    standardized_stats = scaler.fit_transform(X=stats_per_user_with_mbti_df[stats_columns].values)

    logger.info("Reduce statistics to 2 dimensions with UMAP")
    reducer = UMAP(n_components=2)
    standardized_stats_2d = reducer.fit_transform(X=standardized_stats)

    logger.info("Prepare plot")
    plot_df = pd.DataFrame()
    plot_df["user_id"] = stats_per_user_with_mbti_df["user_id"]
    plot_df["mbti_type"] = stats_per_user_with_mbti_df["mbti_type"].fillna("NA")
    plot_df["umap_x"] = standardized_stats_2d[:, 0]
    plot_df["umap_y"] = standardized_stats_2d[:, 1]
    fig = px.scatter(
        plot_df, x="umap_x", y="umap_y", color="mbti_type", hover_data=["user_id", "umap_x", "umap_y", "mbti_type"]
    )

    logger.info("Save plot to '{}'".format(args.plot_path))
    fig.write_html(args.plot_path)
