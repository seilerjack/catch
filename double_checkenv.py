from catch_env import CatchEnv
from catch     import Catch

GAME = Catch()

env = CatchEnv( GAME )

episodes = 1
for episode in range( episodes ):
    done = False
    obs  = env.reset()

    while not done:
        action = env.action_space.sample()
        print( f"Action: {action}" )

        obs, reward, done, truncated, info = env.step( action )
        print( f"Reward: {reward}" )
        print( "\n" )
