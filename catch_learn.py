
#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import os
import gym
import time

from stable_baselines3                  import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.callbacks import CallbackList
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.vec_env   import SubprocVecEnv
from stable_baselines3.common.monitor   import Monitor

from catch_env                          import CatchEnv
from catch                              import Catch


#---------------------------------------------------------
# CONSTANTS
#---------------------------------------------------------
# Number of parallel environments (match your CPU cores)
NUM_ENVS  = 4

# Number of timesteps to train/save
TIMESTEPS = 10000000
SAVE_FREQ = 500000
VERSION   = "V16_RPPO_TEST"

#---------------------------------------------------------
# CLASSES
#---------------------------------------------------------
class InfoLoggerCallback( BaseCallback ):

    def __init__( self, verbose=0 ):
        super( InfoLoggerCallback, self ).__init__( verbose )
        self.highest_score_ever = float('-inf')  # initialize to negative infinity

    def _on_step( self ) -> bool:
        # Assuming env is a VecEnv — get infos from all sub-envs
        infos = self.locals[ "infos" ]

        for info in infos:
            # Log everything returned from get_info()
            self.logger.record(" custom/object_speed", info[ "object_speed" ] )
            self.logger.record(" custom/object_count", info[ "object_count" ] )
            self.logger.record(" custom/episode_num",  info[ "episode_num" ] )

            # Track highest individual score ever seen
            current_score = info.get( "score", None )
            if current_score is not None:
                if current_score > self.highest_score_ever:
                    self.highest_score_ever = current_score
                self.logger.record( "custom/highest_score_ever", self.highest_score_ever )

        return ( True )

#---------------------------------------------------------
# VARIABLES
#---------------------------------------------------------
# Create directory for new model
models_dir = os.path.join( "models", VERSION, str( int( time.time() ) ) )
if not os.path.exists( models_dir ):
    os.makedirs( models_dir, exist_ok=True )

# Create directory for new logs
logdir = os.path.join( "logs", VERSION, str( int( time.time() ) ) )
if not os.path.exists( logdir ):
    os.makedirs( logdir, exist_ok=True )

# Instantiate custom checkpoint callback
checkpoint_callback = CheckpointCallback(
                                        save_freq=max( SAVE_FREQ // NUM_ENVS, 1 ),
                                                                        # Save every X steps
                                        save_path=models_dir,             # Path to save models
                                        name_prefix=f"catch_ppo_agent_{ VERSION }",    
                                                                        # Name prefix for model files
                                        save_replay_buffer=False,
                                        save_vecnormalize=False,
                                        )

# Instantiate custom logger callback
info_logger = InfoLoggerCallback()

# Combine callbacks
callbacks = CallbackList( [ checkpoint_callback, info_logger ] )

#---------------------------------------------------------
# PROCEDURES
#---------------------------------------------------------
# Function to create parallel environments
def make_env():
    env = CatchEnv( Catch() )
    return Monitor( env )

# Protect against environment exceptions
def safe_make_env():
    try:
        return make_env()
    except Exception as e:
        print(f"Error creating environment: {e}")
        return None

#---------------------------------------------------------
# EXECUTION
#---------------------------------------------------------
if __name__ == "__main__":

    import multiprocessing as mp
    mp.set_start_method("spawn")  # Explicitly set the start method

    # Create multiple environments with error handling
    envs = [ lambda: safe_make_env() for _ in range( NUM_ENVS ) ]
    envs = [ env for env in envs if env is not None ]  # Filter out failed envs
    env  = SubprocVecEnv( envs )

    # # Resume training of previous model version
    # prev_model = PPO.load( "models/V15_FULL_SEND/1745153387/catch_ppo_agent_V15_FULL_SEND_10000000_steps.zip", env=env, device="auto" )

    # # Grab the previous policies weights
    # policy_weights = prev_model.policy.state_dict()

    # Reinitialize a new model
    model = PPO( 
                "MultiInputPolicy", 
                env, 
                ent_coef=0.04,        # Increase entropy coefficient (default is usually 0.0)
                learning_rate=0.00025,# Increase from 0.0003 to 0.0005 or higher
                clip_range=0.3,       # Allow larger policy updates (default is 0.2)
                n_steps=4096,
                verbose=1, 
                tensorboard_log=logdir ,
                )


    # # Load the weights
    # model.policy.load_state_dict( policy_weights )

    # Train for TIMESTEPS
    model.learn( 
                total_timesteps=TIMESTEPS,      # Run for the full TIMESTEPS amount
                reset_num_timesteps=False,
                tb_log_name="PPO",
                callback=callbacks,             # Save every SAVE_REQ steps & log info
                )

    # Save model after training is complete
    model.save( f"{ models_dir }/{ TIMESTEPS }" )
        