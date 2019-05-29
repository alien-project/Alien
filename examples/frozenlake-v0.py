from gym import make
from alien import RLAgent, Action, ActionAtom, StateAtom, Condition
from alien import ConditionalStatement
from numpy import array

create_storithm_types = [
    {ActionAtom: 2, StateAtom: 2},
    {Condition: 2},
    {ConditionalStatement: 4}
]
agent = RLAgent(
    (1,),
    [Action(i) for i in range(4)],
    return_discount_factor=1,
    horizon=10,
    time_importance_factor=1,
    create_storithm_types=create_storithm_types,
    max_predictors_count=70,
    softmax_temperature=14,
    internal_actions=[],
    memory_tapes_count=0
)

env = make('FrozenLake-v0', is_slippery=False)
env.reset()
env.render()
observation = array([1])
reward = 0

for _ in range(10000):
    action = agent.act(array([observation]), reward)
    observation, reward, done, _ = env.step(action.id)
    env.render()
    if done:
        env.reset()
alien_return = 0
for _ in range(1000):
    action = agent.act(array([observation]), reward)
    observation, reward, done, _ = env.step(action.id)
    env.render()
    alien_return += reward
    if done:
        env.reset()

random_return = 0
for _ in range(1000):
    observation, reward, done, _ = env.step(env.action_space.sample())
    random_return += reward
    if done:
        env.reset()
env.close()

print("Alien agent result: " + str(alien_return))
print("Random agent result: " + str(random_return))
