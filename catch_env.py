#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import numpy as np

from catch   import Catch
from gym     import spaces, Env


#---------------------------------------------------------
# CONSTANTS
#---------------------------------------------------------
# Screen settings
SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 720
FPS           = 60

# Game settings
PLAYER_WIDTH  = 100
PLAYER_HEIGHT = 20

# Player/Enemy settings
PLAYER_Y      = 580
ENEMY_WIDTH   = 60
ENEMY_HEIGHT  = 40

# Projectile settings
OBJECT_WIDTH    = 20
OBJECT_HEIGHT   = 20
SPEED_MULT      = 1.25
MAX_PROJECTILES = 10

#---------------------------------------------------------
# CLASSES
#---------------------------------------------------------
class CatchEnv( Env ):
 
    def __init__( self, game ):
        super().__init__()

        # Game instance to apply Environment on
        self.game = game

        # Action space - Need representations for direction (L/R) and distance to move (pixels)
        self.action_space = spaces.Dict(
            {
                # This will represent the direction the agent can move, left or right
                "direction" : spaces.Discrete( 2 ),

                # This will represent how far the agent moves in selected direction (pixels)
                "distance" : spaces.Box(
                                        low  = 0,                               # Min value (0px)
                                        high = ( SCREEN_WIDTH - PLAYER_WIDTH ), # Max value (540px)
                                        dtype= int
                                        ),
            }
        )

        # Observation space - Need position of the following: The Player, Falling Projectiles, Enemy(?)
        self.observation_space = spaces.Dict(
            {
                # This will represent the location of the player (x, y)
                "player" : spaces.Box(                #  X coord range                    Y coord range
                                     low   = np.array( [ 0,                               PLAYER_Y ] ),
                                     high  = np.array( [ ( SCREEN_WIDTH - PLAYER_WIDTH ), PLAYER_Y ] ),
                                     dtype = int,
                                     ),

                # This will represent the location of the enemy (x, y)
                "enemy" : spaces.Box(                #  X coord range                   Y coord range
                                    low   = np.array( [ 0,                              ( SCREEN_HEIGHT // 3 ) ] ),
                                    high  = np.array( [ ( SCREEN_WIDTH - ENEMY_WIDTH ), SCREEN_HEIGHT          ] ),
                                    dtype = int,
                                    ),

                # This will represent the locations of the falling projectiles [(x, y)]
                "projectiles" : spaces.Box(               #    X coord range                  Y coord range       Num proj to track
                                          low  = np.array( [ [ 0,                           0             ] ] * MAX_PROJECTILES ),
                                          high = np.array( [ [ SCREEN_WIDTH - OBJECT_WIDTH, SCREEN_HEIGHT ] ] * MAX_PROJECTILES ),
                                          dtype= int,
                                          )
            }
        )


    def _get_obs( self ):
        pass

    def reset( self ):
        pass

    def step( self ):
        pass

    def reward( self ):
        pass


#---------------------------------------------------------
# EXECUTION
#---------------------------------------------------------
if __name__ == "__main__":
    GAME = Catch()
    env = CatchEnv( GAME )
    GAME.run_game()
