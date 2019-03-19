from alien.prediction import Predictor, Prediction
from random import randint


# def test_prediction_predict():
#     prediction = Prediction()
#     prediction.add_predictor(Predictor(2, 2), 1)
#     prediction.add_predictor(Predictor(0, 2), 1)
#     prediction.add_predictor(Predictor(), 1)
#     prediction.add_predictor(Predictor(1, 3), 1)
#     prediction.add_predictor(Predictor(2, 0.5), 0)
#     assert 1 == prediction.predict()
#
#
# def test_prediction_fit():
#     prediction = Prediction()
#     predictors = [Predictor(), Predictor()]
#     prediction.add_predictor(predictors[0], 1)
#     prediction.fit(2)
#     assert 2 == predictors[0].coefficient  # it won't be like that
#     assert 1 == predictors[0].confidence
#     prediction.fit(4)
#     assert 3 == predictors[0].coefficient
#     assert 2 == predictors[0].confidence
#     prediction.add_predictor(predictors[1], 1)
#     prediction.fit(6)
#     assert 4 == predictors[0].coefficient
#     assert 3 == predictors[0].confidence
#     assert 6 == predictors[1].coefficient  # it won't be like that
#     assert 1 == predictors[1].confidence
#
#
# def test_prediction_fit_predict():
#     learning_trials_count = 50
#     testing_trials_count = 10
#
#     predictors = [Predictor() for _ in range(5)]
#
#     for _ in range(learning_trials_count):
#         prediction = Prediction()
#         true_value = None
#         for predictor in predictors:
#             activation = randint(0, 1)
#             if predictor == predictors[0]:
#                 true_value = activation
#             if activation:
#                 prediction.add_predictor(predictor, 1)
#         prediction.fit(true_value)
#
#     for _ in range(testing_trials_count):
#         prediction = Prediction()
#         true_value = None
#         for predictor in predictors:
#             activation = randint(0, 1)
#             if predictor == predictors[0]:
#                 true_value = activation
#             if activation:
#                 prediction.add_predictor(predictor, 1)
#         assert true_value == prediction.predict()
#         prediction.fit(true_value)


def test_base_predictor_same():
    assert Predictor(5, 4, 2).same(Predictor(5, 4, 1))
    assert not Predictor(5, 3, 2).same(Predictor(5, 4, 1))
