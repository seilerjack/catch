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
                # This will represent the direction the agent can move, stay, left or right
                "direction" : spaces.Discrete( 3 ),

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


    def reset( self ):
        """ Reset to the episode instance.

        Call to the in-game function restart that resets the
        player's location, enemy's location, score, and clears
        all falling objects. This will also return an observation
        of this reset state for the start of a new episode.

        Args:
            argument_1 (CatchEnv): Reference to self, CatchEnv.

        Returns:
            spaces.Dict: returns an oberservation of the reset
                         state.
        """
        self.game.restart()
        return ( self._get_obs() )
    

    def _get_obs( self ):
        """ Private getter for current state's observation.

        Collects the following information and normalizes the
        values for further manipulation: player position (x,y),
        enemy position (x,y), falling object position(s) [(x,y)].

        Args:
            argument_1 (CatchEnv): Reference to self, CatchEnv.

        Returns:
            spaces.Dict: returns an oberservation of the current
                         state.
        """
        # Normalize player position (x / SCREEN_WIDTH, y / SCREEN_HEIGHT)
        player_obs = np.array( [
                               ( self.game.player_x / ( SCREEN_WIDTH - PLAYER_WIDTH ) ),
                               ( PLAYER_Y / SCREEN_HEIGHT )
                               ] )

        # Normalize enemy position
        enemy_x_norm = self.game.enemy_x / ( SCREEN_WIDTH - ENEMY_WIDTH )
        enemy_y_norm = ( self.game.enemy_y - ( SCREEN_HEIGHT // 3 ) ) / ( ( SCREEN_HEIGHT * 2 ) // 3 )

        enemy_obs    = np.array( [ 
                                 enemy_x_norm, 
                                 enemy_y_norm 
                                 ] )

        # Normalize projectile positions and pad as needed
        projectiles_obs = []
        for obj in self.game.falling_objects[ : MAX_PROJECTILES ]:
            proj_x = obj.x / ( SCREEN_WIDTH - OBJECT_WIDTH )
            proj_y = obj.y / SCREEN_HEIGHT

            projectiles_obs.append( np.array( [ 
                                              proj_x, 
                                              proj_y 
                                              ] ) )
        
        # Pad with normalized (-1, -1) if fewer projectiles than MAX_PROJECTILES
        while len( projectiles_obs ) < MAX_PROJECTILES:
            projectiles_obs.append( np.array( [ 
                                              -1.0, 
                                              -1.0 
                                              ] ) )

        # Create normalized observation dictionary
        observation = {
                      "player"     : player_obs,
                      "enemy"      : enemy_obs,
                      "projectiles": np.array( projectiles_obs ),
                      }

        return ( observation )

    # Should just be one full 'move' by the agent.
    # Record an observation after the action has been applied
    # and a reward calculated 
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
    # GAME.run_game()
