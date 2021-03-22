from abc import abstractmethod

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder


class MBTIBaseClassifier(object):
    def __init__(self, hyper_parameters, tokens_tfidf_vectorizer_parameters=None):
        self.hyper_parameters = hyper_parameters
        self.tokens_tfidf_vectorizer_parameters = tokens_tfidf_vectorizer_parameters
        self.label_encoder = LabelEncoder()
        self.tfidf_vectorizer = None

    def encode_labels(self, mbti_type_per_user_df):
        return self.label_encoder.transform(y=mbti_type_per_user_df.values)

    def prepare_X(self, input_features_per_user_df):
        X_stats = input_features_per_user_df.drop("tokens", axis=1).values
        if self.tokens_tfidf_vectorizer_parameters is None:
            return X_stats
        else:
            raw_documents = input_features_per_user_df["tokens"].apply(lambda token_list: " ".join(token_list)).tolist()
            if self.tfidf_vectorizer is None:
                self.tfidf_vectorizer = TfidfVectorizer(**self.tokens_tfidf_vectorizer_parameters)
                self.tfidf_vectorizer.fit(raw_documents=raw_documents)
            X_token_vectors = self.tfidf_vectorizer.transform(raw_documents=raw_documents).todense()
            return np.concatenate([X_stats, X_token_vectors], axis=1)

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
    def __init__(self, hyper_parameters, tokens_tfidf_vectorizer_parameters=None):
        super().__init__(
            hyper_parameters=hyper_parameters, tokens_tfidf_vectorizer_parameters=tokens_tfidf_vectorizer_parameters
        )
        self.classifier = self.instantiate_classifier()

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
    def __init__(self, hyper_parameters, tokens_tfidf_vectorizer_parameters=None):
        super().__init__(
            hyper_parameters=hyper_parameters, tokens_tfidf_vectorizer_parameters=tokens_tfidf_vectorizer_parameters
        )
        self.dichotomy_dicts = [
            {"letter": "E", "classifier": self.instantiate_classifier()},
            {"letter": "S", "classifier": self.instantiate_classifier()},
            {"letter": "T", "classifier": self.instantiate_classifier()},
            {"letter": "J", "classifier": self.instantiate_classifier()},
        ]

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
