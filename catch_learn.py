
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


checkpoint_callback = CheckpointCallback(save_freq=100000, save_path=models_dir,
                                         name_prefix="catch_ppo_model")

TIMESTEPS = 500000

# model = PPO( 
#            "MultiInputPolicy", 
#            env, 
#            ent_coef=0.04 ,       # Increase entropy coefficient (default is usually 0.0)
#            learning_rate=0.0005, # Increase from 0.0003 to 0.0005 or higher
#            clip_range=0.3,       # Allow larger policy updates (default is 0.2)
#            n_steps=4096,
#            verbose=1, 
#            tensorboard_log=logdir ,
#            callback=checkpoint_callback
#            )

# Resume training of previous model version
model = PPO.load("models/basic_objective_completion/1743271288/1000000.zip")
model.set_env(env)  # Ensure you pass the same environment

# Modify specific hyperparameters
# model.learning_rate = 0.0005  # Reduce learning rate
# model.clip_range    = 0.3     # Adjust clipping
model.ent_coef      = 0.06    # Increase entropy for more exploration

for i in range( 1, 1000000 ):
    model.learn( total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="PPO", callback=checkpoint_callback )
    model.save( f"{models_dir}/{TIMESTEPS * i}" )
