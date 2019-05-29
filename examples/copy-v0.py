from gym import make
from alien import RLAgent, Action, ActionAtom, StateAtom, Condition
from alien import ConditionalStatement, Procedure
from numpy import array

create_storithm_types = [
    {ActionAtom: 16, StateAtom: 8},
    {Condition: 16},
    {ConditionalStatement: 70, Procedure: 160}
]
actions = []
for i in range(2):
    for j in range(2):
        for k in range(5):
            actions.append(Action((i, j, k)))
agent = RLAgent(
    (1,),
    actions,
    1,
    0,
    return_discount_factor=1,
    horizon=5,
    time_importance_factor=1,
    create_storithm_types=create_storithm_types,
    max_predictors_count=70,
    softmax_temperature=14,
    internal_actions=[],
    memory_tapes_count=0
)

env = make('Copy-v0')
env.reset()
env.render()
observation = 5
reward = 0
return_ = 0
done = False
for _ in range(3000):
    action = agent.act(array([observation]), reward)
    observation, reward, done, _ = env.step(action.id)
    env.render()
    if done:
        env.reset()
for _ in range(1000):
    action = agent.act(array([observation]), reward)
    observation, reward, done, _ = env.step(action.id)
    return_ += reward
    env.render()
    if done:
        env.reset()
env.close()
print("return: " + str(return_))


"""
storithms like this should have positive coefficient:
if observation = 5 then move right without prediction and then if observation = 0 then write A
if observation = 5 then move right without prediction and then if observation = 1 then write B
...

s_0_5 a_(1, 0, ...) s_0_0 a_(..., 1, 0) <-- that should be good

there are no storithms like that so you should increase the number of created storithms
"""