
import os
import gym
import time
from stable_baselines3                  import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.vec_env   import SubprocVecEnv
from stable_baselines3.common.monitor   import Monitor

from catch_env                          import CatchEnv
from catch                              import Catch

# Number of parallel environments (match your CPU cores)
NUM_ENVS = 4

# Number of timesteps to train/save
TIMESTEPS = 10000000
SAVE_FREQ = 500000
VERSION   = "v3"

models_dir = os.path.join( "models", VERSION, str( int( time.time() ) ) )
logdir     = os.path.join( "logs", VERSION, str( int( time.time() ) ) )

checkpoint_callback = CheckpointCallback(
    save_freq=SAVE_FREQ,              # Save every X steps
    save_path=models_dir,             # Path to save models
    name_prefix=f"catch_ppo_agent_{ VERSION }",    
                                      # Name prefix for model files
    save_replay_buffer=False,
    save_vecnormalize=False,
)

if not os.path.exists( models_dir ):
    os.makedirs( models_dir, exist_ok=True )

if not os.path.exists( logdir ):
    os.makedirs( logdir, exist_ok=True )

# Function to create parallel environments
def make_env():
    env = CatchEnv( Catch() )
    return Monitor( env )

def safe_make_env():
    try:
        return make_env()
    except Exception as e:
        print(f"Error creating environment: {e}")
        return None

# Function to linearly decay the learning rate
def linear_schedule( initial_value, min_value=1e-5 ):
    def schedule( progress_remaining ):
        return max( initial_value * progress_remaining, min_value )
    return schedule


if __name__ == "__main__":

    import multiprocessing as mp
    mp.set_start_method("spawn")  # Explicitly set the start method

    # Create multiple environments with error handling
    envs = [ lambda: safe_make_env() for _ in range( NUM_ENVS ) ]
    envs = [ env for env in envs if env is not None ]  # Filter out failed envs
    env  = SubprocVecEnv( envs )
    
    # ## UNCOMMENT FOR SINGLE ENV TRAINING ###
    # GAME = Catch()
    # env  = CatchEnv( GAME )
    # env.reset()
    ########################################

    # Resume training of previous model version
    prev_model = PPO.load( "models/v2/1744025418/V2_60_FPS.zip", env=env, device="auto" )

    # Grab the previous policies weights
    policy_weights = prev_model.policy.state_dict()

    # Reinitialize a new model
    model = PPO( 
           "MultiInputPolicy", 
           env, 
           ent_coef=0.04 ,       # Increase entropy coefficient (default is usually 0.0)
           learning_rate=linear_schedule( 0.00025, 1e-5 ), 
                                 # Increase from 0.0003 to 0.0005 or higher
           clip_range=0.3,       # Allow larger policy updates (default is 0.2)
           n_steps=4096,
           verbose=1, 
           tensorboard_log=logdir ,
           )

    # Load the weights    
    model.policy.load_state_dict( policy_weights )

    # Train for TIMESTEPS
    model.learn( 
                total_timesteps=TIMESTEPS,      # Run for the full TIMESTEPS amount
                reset_num_timesteps=False,
                tb_log_name="PPO",
                callback=checkpoint_callback,   # Save every SAVE_REQ steps 
                )

    # Save model after training is complete
    model.save( f"{ models_dir }/{ TIMESTEPS }" )
            