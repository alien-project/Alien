class BasePredictor:
    next_id = 0

    def __init__(self, id_=None):
        self.id = self._auto_increment_id(id_)

    def _auto_increment_id(self, id_):
        if id_ is None:
            BasePredictor.next_id += 1
            return BasePredictor.next_id - 1
        if isinstance(id_, int):
            if id_ >= BasePredictor.next_id:
                BasePredictor.next_id = id_ + 1
        return id_

    def importance(self):
        raise NotImplementedError

    def confidence(self):
        raise NotImplementedError

    def same(self, other):
        a_dict = self.__dict__.copy()
        b_dict = self.__dict__.copy()
        a_dict.pop('id')
        b_dict.pop('id')
        return (
            self.__class__ == other.__class__ and
            a_dict == b_dict
        )


class Predictor(BasePredictor):
    def __init__(self, coefficient=0, confidence=0, id_=None):
        self.coefficient = coefficient
        self.confidence_ = confidence
        super().__init__(id_)

    def importance(self):
        return 0

    def confidence(self):
        return self.confidence_

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.__dict__ == other.__dict__
        )


class Prediction:
    def __init__(self):
        self.predictors = []
        self.activations = []
        self.estimation = 0

    def add_predictor(self, predictor, activation):
        self.predictors.append(predictor)
        self.activations.append(activation)
        self.estimation = None

    def fit(self, true_value, sample_weight=1):
        if self.estimation is None:
            self.predict()
        for key, predictor in self.predictors:
            predictor.coefficient = (
                (
                    predictor.coefficient * predictor.confidence +
                    predictor.coefficient * true_value / self.estimation *
                    self.activations[key] * sample_weight
                ) /
                (predictor.confidence + self.activations[key] * sample_weight)
            )
            predictor.confidence += self.activations[key] * sample_weight

    def predict(self):
        equation_top = 0
        equation_bottom = 0
        for key, predictor in enumerate(self.predictors):
            equation_top += (
                predictor.coefficient *
                predictor.confidence *
                self.activations[key]
            )
            equation_bottom += predictor.confidence * self.activations[key]
        self.estimation = (
            equation_top / equation_bottom if equation_bottom != 0 else 0
        )
        return self.estimation
