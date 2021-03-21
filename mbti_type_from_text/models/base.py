from abc import abstractmethod

import pandas as pd
from sklearn.preprocessing import LabelEncoder


class MBTIBaseClassifier(object):
    def __init__(self, hyper_parameters):
        self.hyper_parameters = hyper_parameters
        self.label_encoder = LabelEncoder()

    def encode_labels(self, mbti_type_per_user_df):
        return self.label_encoder.transform(y=mbti_type_per_user_df.values)

    @abstractmethod
    def instantiate_classifier(self):
        raise NotImplementedError()

    @abstractmethod
    def fit(self, input_features_per_user_df, mbti_type_per_user_df):
        raise NotImplementedError()

    @abstractmethod
    def predict(self, input_features_per_user_df):
        raise NotImplementedError()


class MBTITypeClassifier(MBTIBaseClassifier):
    def __init__(self, hyper_parameters):
        super().__init__(hyper_parameters=hyper_parameters)
        self.classifier = self.instantiate_classifier()

    def prepare_X(self, input_features_per_user_df):
        return input_features_per_user_df.drop("tokens", axis=1).values

    def prepare_y(self, mbti_type_per_user_df):
        return self.encode_labels(mbti_type_per_user_df=mbti_type_per_user_df)

    def fit(self, input_features_per_user_df, mbti_type_per_user_df):
        self.label_encoder.fit(y=mbti_type_per_user_df.values)
        X = self.prepare_X(input_features_per_user_df=input_features_per_user_df)
        y = self.prepare_y(mbti_type_per_user_df=mbti_type_per_user_df)
        self.classifier.fit(X=X, y=y)

    def predict(self, input_features_per_user_df):
        X = self.prepare_X(input_features_per_user_df=input_features_per_user_df)
        return self.classifier.predict(X=X)


class MBTIByDichotomyClassifier(MBTIBaseClassifier):
    def __init__(self, hyper_parameters):
        super().__init__(hyper_parameters=hyper_parameters)
        self.dichotomy_dicts = [
            {"letter": "E", "classifier": self.instantiate_classifier()},
            {"letter": "S", "classifier": self.instantiate_classifier()},
            {"letter": "T", "classifier": self.instantiate_classifier()},
            {"letter": "J", "classifier": self.instantiate_classifier()},
        ]

    def prepare_X(self, input_features_per_user_df):
        return input_features_per_user_df.drop("tokens", axis=1).values

    def prepare_y(self, mbti_type_per_user_df, letter_index, letter):
        return (mbti_type_per_user_df.str[letter_index] == letter).values

    def fit(self, input_features_per_user_df, mbti_type_per_user_df):
        self.label_encoder.fit(y=mbti_type_per_user_df.values)
        X = self.prepare_X(input_features_per_user_df=input_features_per_user_df)
        for i, dichotomy_dict in enumerate(self.dichotomy_dicts):
            y = self.prepare_y(
                mbti_type_per_user_df=mbti_type_per_user_df, letter_index=i, letter=dichotomy_dict["letter"]
            )
            dichotomy_dict["classifier"].fit(X=X, y=y)

    def predict(self, input_features_per_user_df):
        X = self.prepare_X(input_features_per_user_df=input_features_per_user_df)
        predicted_dichotomies_df = pd.DataFrame()
        for i, dichotomy_dict in enumerate(self.dichotomy_dicts):
            predicted_dichotomies_df["is_{}".format(dichotomy_dict["letter"])] = dichotomy_dict["classifier"].predict(
                X=X
            )
        predicted_mbti_strings = (
            predicted_dichotomies_df["is_E"].replace(True, "E").replace(False, "I")
            + predicted_dichotomies_df["is_S"].replace(True, "S").replace(False, "N")
            + predicted_dichotomies_df["is_T"].replace(True, "T").replace(False, "F")
            + predicted_dichotomies_df["is_J"].replace(True, "J").replace(False, "P")
        )
        return self.label_encoder.transform(y=predicted_mbti_strings.values)
