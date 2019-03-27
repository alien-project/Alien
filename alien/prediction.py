from helpers import AutoIncrementId
from math import log


class BasePredictor:
    def __init__(self, id_=None):
        self.storithm = None
        self.distance = None
        self.id = AutoIncrementId.generate(id_)

    def importance(self):
        raise NotImplementedError

    # def confidence(self):
    #     raise NotImplementedError

    def __eq__(self, other):
        return self.same(other)

    def same(self, other):
        a_dict = self.__dict__.copy()
        b_dict = other.__dict__.copy()
        a_dict.pop('id')
        b_dict.pop('id')
        return (
            self.__class__ == other.__class__ and
            a_dict == b_dict
        )


class BaseEstimator:
    @staticmethod
    def fit(predictors, value, sample_weight=1):
        raise NotImplementedError

    @staticmethod
    def predict(predictors):
        raise NotImplementedError


class Predictor(BasePredictor):
    def __init__(self, mean=0, variance=0, confidence=0, id_=None):
        self.mean = mean
        self.variance = variance
        self.confidence = confidence
        self.sum = self.variance * self.confidence
        super().__init__(id_)

    def variance_value(self):
        if self.confidence == 0:
            return 0
        variance_confidence = min(
            Estimator.a * log(self.confidence, Estimator.b),
            Estimator.max_variance_confidence
        )
        return (
            variance_confidence * self.variance / self.mean ** 2 +
            (1 - variance_confidence) * Estimator.mean_variance_ratio
        )

    def importance(self):
        return 0

    # def confidence(self):
    #     return self.confidence_

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.__dict__ == other.__dict__
        )


class Estimator(BaseEstimator):
    a = 0.5
    b = 2
    mean_variance_ratio = 0.9
    max_variance_confidence = 0.99

    @staticmethod
    def fit(predictors, value, sample_weight=1):
        for predictor in predictors:
            old_mean = predictor.mean
            predictor.mean = (
                (
                    predictor.mean * predictor.confidence +
                    value * sample_weight
                ) /
                (predictor.confidence + sample_weight)
            )
            predictor.confidence += sample_weight
            predictor.sum += (
                (value - old_mean) *
                (value - predictor.mean) *
                sample_weight
            )
            predictor.variance = predictor.sum / predictor.confidence

    @staticmethod
    def predict(predictors):
        top = 0
        bottom = 0
        for predictor in predictors:
            top += (
                predictor.mean * predictor.confidence /
                predictor.variance_value()
            )
            bottom += predictor.confidence / predictor.variance_value()
        return top / bottom
