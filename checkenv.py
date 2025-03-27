from stable_baselines3.common.env_checker import check_env
from catch_env                            import CatchEnv
from catch                                import Catch

GAME = Catch()
env = CatchEnv( GAME )
# This will check the custom environment and output additional warnings if needed
check_env( env )
