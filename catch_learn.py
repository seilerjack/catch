
import os
import gym
import time
from stable_baselines3                  import PPO
from stable_baselines3.common.callbacks import CheckpointCallback

from catch_env         import CatchEnv
from catch             import Catch

models_dir = f"models/{ int( time.time() ) }"
logdir     = f"logs/{ int( time.time() ) }"

if not os.path.exists( models_dir ):
    os.makedirs( models_dir )

if not os.path.exists( logdir ):
    os.makedirs( logdir )

GAME = Catch()
env  = CatchEnv( GAME )
env.reset()


checkpoint_callback = CheckpointCallback(save_freq=10000, save_path=models_dir,
                                         name_prefix="catch_ppo_model")

TIMESTEPS = 1000000

model = PPO( 
           "MultiInputPolicy", 
           env, 
           ent_coef=0.04 ,       # Increase entropy coefficient (default is usually 0.0)
           learning_rate=0.0005, # Increase from 0.0003 to 0.0005 or higher
           clip_range=0.3,       # Allow larger policy updates (default is 0.2)
           n_steps=4096,
           verbose=1, 
           tensorboard_log=logdir ,
           callback=checkpoint_callback
           )

# # Resume training of previous model version
# model = PPO.load("models/1743271288")
# model.set_env(env)  # Ensure you pass the same environment

for i in range( 1, 1000000 ):
    model.learn( total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="PPO" )
    model.save( f"{models_dir}/{TIMESTEPS * i}" )
