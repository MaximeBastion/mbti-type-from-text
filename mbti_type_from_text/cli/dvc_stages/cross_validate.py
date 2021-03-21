import logging
from argparse import ArgumentParser

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import KFold

from mbti_type_from_text.utils import get_object_from_string, load_json, save_json

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name="cross_validate_model")

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
        "--classifier_import_path",
        type=str,
        required=True,
        help="Import path of the class to use as classifier",
    )
    parser.add_argument(
        "--classifier_config_path",
        type=str,
        required=True,
        help="Path to a JSON config file to specify the classifier to use",
    )
    parser.add_argument(
        "--metrics_path",
        type=str,
        required=True,
        help="Path to a JSON config file where the metrics will be saved",
    )
    args = parser.parse_args()

    logger.info("Load statistics per user from '{}'".format(args.stats_per_user_path))
    stats_per_user_df = pd.read_feather(args.stats_per_user_path)
    logger.info("Load users MBTI from '{}'".format(args.users_mbti_feather_path))
    users_mbti_df = pd.read_feather(args.users_mbti_feather_path)
    users_mbti_df["mbti_type"] = users_mbti_df["mbti_type"].fillna(pd.NA)
    logger.info("Load classifier config from '{}'".format(args.classifier_config_path))
    classifier_config_dict = load_json(path=args.classifier_config_path)

    logger.info("Join statistics with MBTI types")
    stats_per_user_with_mbti_df = stats_per_user_df.merge(users_mbti_df, on="user_id")

    logger.info("Select users with an MBTI type")
    stats_per_user_with_mbti_df = stats_per_user_with_mbti_df[~stats_per_user_with_mbti_df["mbti_type"].isna()]
    stats_per_user_with_mbti_df = stats_per_user_with_mbti_df[
        ~stats_per_user_with_mbti_df["mbti_type"].str.contains("X")
    ]
    logger.info("Select {} users".format(len(stats_per_user_with_mbti_df)))

    logger.info("Start cross-validation")
    input_features_per_user_df = stats_per_user_with_mbti_df.drop(["user_id", "mbti_type"], axis=1)
    mbti_type_per_user_df = stats_per_user_with_mbti_df["mbti_type"]
    k_fold_splitter = KFold(n_splits=2)
    cross_validation_metrics_df = pd.DataFrame()
    for n, (train_indices, test_indices) in enumerate(k_fold_splitter.split(X=input_features_per_user_df)):
        logger.info("Start fold {}/{}".format(n + 1, k_fold_splitter.get_n_splits()))
        train_input_features_per_user_df = input_features_per_user_df.iloc[train_indices]
        train_mbti_type_per_user_df = mbti_type_per_user_df.iloc[train_indices]
        test_input_features_per_user_df = input_features_per_user_df.iloc[test_indices]
        test_mbti_type_per_user_df = mbti_type_per_user_df.iloc[test_indices]

        classifier = get_object_from_string(string=args.classifier_import_path)(
            hyper_parameters=classifier_config_dict["hyper_parameters"]
        )
        classifier.fit(
            input_features_per_user_df=train_input_features_per_user_df,
            mbti_type_per_user_df=train_mbti_type_per_user_df,
        )
        test_y_pred = classifier.predict(input_features_per_user_df=test_input_features_per_user_df)
        test_y_true = classifier.encode_labels(mbti_type_per_user_df=test_mbti_type_per_user_df)
        cross_validation_metrics_df = cross_validation_metrics_df.append(
            {
                "f_score": f1_score(y_true=test_y_true, y_pred=test_y_pred, average="weighted"),
                "accuracy": accuracy_score(y_true=test_y_true, y_pred=test_y_pred),
            },
            ignore_index=True,
        )

    mean_metrics = cross_validation_metrics_df.mean(axis=0).to_dict()

    logger.info("Write metrics to '{}'".format(args.metrics_path))
    save_json(obj=mean_metrics, path=args.metrics_path)
