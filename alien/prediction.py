from .helpers import AutoIncrementId


class BasePredictor:
    def __init__(self, id_=None, storithm=None, distance=None):
        self.storithm = storithm
        self.distance = distance
        self.id = AutoIncrementId.generate(id_)
        self._hash_cache = None

    def importance(self):
        raise NotImplementedError

    # def confidence(self):
    #     raise NotImplementedError

    def same(self, other):
        a_dict = self.__dict__.copy()
        b_dict = other.__dict__.copy()
        a_dict.pop('id')
        b_dict.pop('id')
        return (
            self.__class__ == other.__class__ and
            a_dict == b_dict
        )

    def __lt__(self, other):
        return self.importance() < other.importance()

    def __gt__(self, other):
        return self.importance() > other.importance()

    def __eq__(self, other):
        if self.storithm and other.storithm:
            return (
                self.storithm == other.storithm and
                self.distance == other.distance
            )
        return self.same(other)

    def __hash__(self):
        return self.id


class BaseEstimator:
    @staticmethod
    def fit(predictors, value, sample_weight=1):
        raise NotImplementedError

    @staticmethod
    def predict(predictors):
        raise NotImplementedError


# class Predictor(BasePredictor):
#     def __init__(self, mean=0, variance=0, confidence=0, id_=None):
#         self.mean = mean
#         self.variance = variance
#         self.confidence = confidence
#         self.sum = self.variance * self.confidence
#         super().__init__(id_)
#
#     def variance_value(self):
#         if self.confidence == 0:
#             return Estimator.MEAN_VARIANCE_RATIO
#         variance_confidence = min(
#             (
#                 Estimator.VARIANCE_CONFIDENCE_MULTIPLIER *
#                 log(
#                     self.confidence,
#                     Estimator.VARIANCE_CONFIDENCE_BASE
#                 )
#             ),
#             Estimator.ALMOST_ONE
#         )
#         return (
#             (
#                 variance_confidence *
#                 self.variance /
#                 max(self.mean ** 2, Estimator.ALMOST_ONE)
#             ) +
#             (
#                 (1 - variance_confidence) *
#                 Estimator.MEAN_VARIANCE_RATIO
#             )
#         )
#
#     def importance(self):
#         return 0
#
#     # def confidence(self):
#     #     return self.confidence_
#
#
# class Estimator(BaseEstimator):
#     VARIANCE_CONFIDENCE_MULTIPLIER = 0.5
#     VARIANCE_CONFIDENCE_BASE = 2
#     MEAN_VARIANCE_RATIO = 0.9
#     ALMOST_ZERO = 0.01
#     ALMOST_ONE = 0.99
#
#     @staticmethod
#     def fit(predictors, value, sample_weight=1):
#         for predictor in predictors:
#             old_mean = predictor.mean
#             predictor.mean = (
#                 (
#                     predictor.mean * predictor.confidence +
#                     value * sample_weight
#                 ) /
#                 (predictor.confidence + sample_weight)
#             )
#             predictor.confidence += sample_weight
#             predictor.sum += (
#                 (value - old_mean) *
#                 (value - predictor.mean) *
#                 sample_weight
#             )
#             predictor.variance = predictor.sum / predictor.confidence
#
#     @staticmethod
#     def predict(predictors):
#         top = 0
#         bottom = 0
#         for predictor in predictors:
#             top += (
#                 predictor.mean * predictor.confidence /
#                 predictor.variance_value()
#             )
#             bottom += predictor.confidence / predictor.variance_value()
#         return top / bottom if bottom > 0 else 0


class Predictor(BasePredictor):
    def __init__(self, coefficient=0, id_=None, storithm=None, distance=None):
        self.coefficient = coefficient
        super().__init__(id_, storithm, distance)

    def importance(self):
        return abs(self.coefficient)


class Estimator(BaseEstimator):
    LEARNING_RATE = 0.05
    bias = 0

    @staticmethod
    def fit(predictors, value, sample_weight=1, change_bias=True):
        prediction = Estimator.predict(predictors)
        error = prediction - value
        if change_bias:
            Estimator.bias -= Estimator.LEARNING_RATE * error
        for predictor in predictors:
            predictor.coefficient -= Estimator.LEARNING_RATE * error

    @staticmethod
    def predict(predictors):
        return (
            sum([predictor.coefficient for predictor in predictors]) +
            Estimator.bias
        )
