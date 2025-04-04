
import os
import gym
import time
from stable_baselines3                  import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.vec_env   import DummyVecEnv

from catch_env                          import CatchEnv
from catch                              import Catch

# Number of parallel environments (match your CPU cores)
NUM_ENVS = 2

# Number of timesteps to train/save
TIMESTEPS = 2000000
SAVE_FREQ = 500000

models_dir = f"models/baseline/{ int( time.time() ) }"
logdir     = f"logs/baseline/{ int( time.time() ) }"

checkpoint_callback = CheckpointCallback( save_freq=SAVE_FREQ, save_path=models_dir,
                                         name_prefix="catch_ppo_model" )

if not os.path.exists( models_dir ):
    os.makedirs( models_dir, exist_ok=True )

if not os.path.exists( logdir ):
    os.makedirs( logdir, exist_ok=True )

# Function to create parallel environments
def make_env():
    return CatchEnv( Catch() )

def safe_make_env():
    try:
        return make_env()
    except Exception as e:
        print(f"Error creating environment: {e}")
        return None

# Function to linearly decay the learning rate
def linear_schedule( initial_value ):
    def schedule( progress_remaining ):
        return initial_value * progress_remaining  # Linearly decreases
    return schedule


if __name__ == "__main__":

    # Create multiple environments
    # env = DummyVecEnv( [ lambda: safe_make_env() for _ in range( NUM_ENVS ) ] )
    
    GAME = Catch()
    env  = CatchEnv( GAME )
    env.reset()

    model = PPO( 
           "MultiInputPolicy", 
           env, 
           ent_coef=0.04 ,       # Increase entropy coefficient (default is usually 0.0)
           learning_rate=linear_schedule( 0.0005 ), 
                                 # Increase from 0.0003 to 0.0005 or higher
           clip_range=0.3,       # Allow larger policy updates (default is 0.2)
           n_steps=4096,
           verbose=1, 
           tensorboard_log=logdir ,
           )
    
    # # Resume training of previous model version
    # model = PPO.load("models/basic_objective_completion/1743271288/1000000.zip")
    # model.set_env(env)  # Ensure you pass the same environment

    # Modify specific hyperparameters
    # model.learning_rate = 0.0005  # Reduce learning rate
    # model.clip_range    = 0.3     # Adjust clipping
    # model.ent_coef      = 0.06    # Increase entropy for more exploration
    
    for i in range( 1, 1000000 ):
        model.learn( 
                total_timesteps=TIMESTEPS, 
                reset_num_timesteps=False, 
                tb_log_name="PPO", 
                callback=checkpoint_callback 
                )
        if ( TIMESTEPS * i ) % 1000000 == 0: 
            model.save( f"{models_dir}/{TIMESTEPS * i}" )
