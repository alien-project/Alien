from alien.prediction import Predictor, Estimator
from random import shuffle


# def test_estimator_fit():
#     predictors = [Predictor() for _ in range(3)]
#     for _ in range(4):
#         Estimator.fit([predictors[0]], 0)
#     for _ in range(2):
#         Estimator.fit(predictors[0:2], 4)
#     for _ in range(2):
#         Estimator.fit(predictors, 12)
#     assert 4 == predictors[0].mean
#     assert 24 == predictors[0].variance
#     assert 8 == predictors[0].confidence
#     assert 8 == predictors[1].mean
#     assert 16 == predictors[1].variance
#     assert 4 == predictors[1].confidence
#     assert 12 == predictors[2].mean
#     assert 0 == predictors[2].variance
#     assert 2 == predictors[2].confidence


def test_estimator_fit_predict():
    # Estimator.a = 0.5
    # Estimator.b = 2
    # Estimator.mean_mad_ratio = 0.5

    predictors = [Predictor() for _ in range(5)]
    x = []

    for _ in range(100):
        x.append((predictors, 12))
    for _ in range(100):
        x.append((predictors[1:5], 0))
    for _ in range(100):
        x.append((predictors[2:5], 0))
    for _ in range(100):
        x.append((predictors[3:5], 0))
    for _ in range(100):
        x.append(([predictors[4]], 0))
    for _ in range(100):
        x.append((predictors[0:4], 12))
    for _ in range(100):
        x.append(([predictors[0]], 12))
    for _ in range(100):
        x.append(([predictors[4]], 0))

    shuffle(x)

    for a in x:
        Estimator.fit(a[0], a[1])

    # for _ in range(100):
    #     Estimator.fit(predictors, 12)
    # for _ in range(100):
    #     Estimator.fit(predictors[1:5], 0)
    # for _ in range(100):
    #     Estimator.fit(predictors[2:5], 0)
    # for _ in range(100):
    #     Estimator.fit(predictors[3:5], 0)
    # for _ in range(100):
    #     Estimator.fit([predictors[4]], 0)
    # for _ in range(100):
    #     Estimator.fit(predictors[0:4], 12)
    # for _ in range(100):
    #     Estimator.fit([predictors[0]], 12)
    # for _ in range(100):
    #     Estimator.fit([predictors[4]], 0)

    assert Estimator.predict(predictors[2:5]) < 6
    assert Estimator.predict(predictors[0:3]) > 7
    assert Estimator.predict([predictors[4]]) < 4
    assert Estimator.predict([predictors[0]]) > 8


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
    assert Predictor(5).same(Predictor(5))
    assert not Predictor(4).same(Predictor(5))
