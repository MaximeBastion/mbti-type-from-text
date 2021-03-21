import numpy as np
import pandas as pd


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
            .apply(lambda mbti: np.nan if pd.isna(mbti) else (1 if mbti[i] == letter else 0))
            .astype(pd.Int32Dtype())
        )
        if all_8:
            opposite_letter = opposite_letters[i]
            df[f"is_{opposite_letter}"] = (
                df[f"is_{letter}"]
                .apply(lambda boolean_as_int: np.nan if pd.isna(boolean_as_int) else (1 if boolean_as_int == 0 else 0))
                .astype(pd.Int32Dtype())
            )

    return df
