from sklearn.ensemble import RandomForestClassifier

from mbti_type_from_text.models.base import MBTIByDichotomyClassifier, MBTITypeClassifier


class RandomForestMBTITypeClassifier(MBTITypeClassifier):
    def instantiate_classifier(self):
        return RandomForestClassifier(**self.hyper_parameters)


class RandomForestMBTIByDichotomyClassifier(MBTIByDichotomyClassifier):
    def instantiate_classifier(self):
        return RandomForestClassifier(**self.hyper_parameters)
