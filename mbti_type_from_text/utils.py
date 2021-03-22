import json
from pathlib import Path

import pandas as pd


def get_object_from_string(string):
    components = string.split(".")
    object_name = components[-1]
    module_path = ".".join(components[:-1])
    module = __import__(module_path, fromlist=[object_name])
    return getattr(module, object_name)


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(obj, path):
    parent_folder = Path(path).parent.absolute()
    Path(parent_folder).mkdir(parents=True, exist_ok=True)  # create parent directory if it doesn't exist
    with open(path, "w") as f:
        json.dump(obj, f)


def add_dichotomies(df: pd.DataFrame, mbti_type_col: str = "mbti_type", all_8: bool = False) -> pd.DataFrame:
    """
    Adds the dichotomies to the df ("is_E", "is_S"...)
    all_8: add all 8 letters even though 4 of them already provides all the information
    Note: to have nullable ints, the output df uses the pd.Int32Dtype() type
    """
    primary_letters = list("ESTJ")
    opposite_letters = list("INFP")

    for i, letter in enumerate(primary_letters):
        df[f"is_{letter}"] = (
            df[mbti_type_col]
            .apply(lambda mbti: pd.NA if pd.isna(mbti) else (1 if mbti[i] == letter else 0))
            .astype(pd.Int32Dtype())
        )
        if all_8:
            opposite_letter = opposite_letters[i]
            df[f"is_{opposite_letter}"] = (
                df[f"is_{letter}"]
                .apply(lambda boolean_as_int: pd.NA if pd.isna(boolean_as_int) else (1 if boolean_as_int == 0 else 0))
                .astype(pd.Int32Dtype())
            )

    return df
