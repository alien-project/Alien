class Predictor:
    def __init__(self, coefficient=0, confidence=0):
        self.coefficient = coefficient
        self.confidence = confidence


class Prediction:
    def __init__(self):
        self._predictors = []
        self._activations = []
        self._estimation = 0

    def add_predictor(self, predictor, activation):
        self._predictors.append(predictor)
        self._activations.append(activation)
        self._estimation = None

    def fit(self, true_value, sample_weight=1):
        if self._estimation is None:
            self.predict()
        for key, predictor in self._predictors:
            predictor.coefficient = (
                (
                    predictor.coefficient * predictor.confidence +
                    predictor.coefficient * true_value / self._estimation *
                    self._activations[key] * sample_weight
                ) /
                (predictor.confidence + self._activations[key] * sample_weight)
            )
            predictor.confidence += self._activations[key] * sample_weight

    def predict(self):
        equation_top = 0
        equation_bottom = 0
        for key, predictor in enumerate(self._predictors):
            equation_top += (
                predictor.coefficient *
                predictor.confidence *
                self._activations[key]
            )
            equation_bottom += predictor.confidence * self._activations[key]
        self._estimation = (
            equation_top / equation_bottom if equation_bottom != 0 else 0
        )
        return self._estimation
