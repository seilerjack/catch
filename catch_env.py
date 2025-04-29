#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import numpy     as np

from gymnasium   import spaces, Env


#---------------------------------------------------------
# CONSTANTS
#---------------------------------------------------------
# Screen settings
SCREEN_WIDTH    = 500
SCREEN_HEIGHT   = 720
FPS             = 60

# Game settings
PLAYER_WIDTH    = 100
PLAYER_HEIGHT   = 20

# Player/Enemy settings
PLAYER_Y        = 580
ENEMY_WIDTH     = 60
ENEMY_HEIGHT    = 40

# Projectile settings
OBJECT_WIDTH    = 20
OBJECT_HEIGHT   = 20
SPEED_MULT      = 1.25
MAX_PROJECTILES = 10
MAX_SPEED       = 5
PIXEL_BUFFER    = 7

#---------------------------------------------------------
# CLASSES
#---------------------------------------------------------
class CatchEnv( Env ):
 
    def __init__( self, game ):
        super().__init__()

        # Game instance to apply Environment on
        self.game = game

        # Initialize the step state and reward
        self.done           = False
        self.reward_val     = 0
        self.last_player_x  = ( SCREEN_WIDTH // 2 ) - ( PLAYER_WIDTH // 2 ) # Initialize to middle of the screen
        
        # Metrics used for difficulty scaling during training
        self.episode_num                      = 0

        self.info_logs = {
                         "episode_num"          : self.episode_num,
                         "object_speed"         : self.game.object_speed,
                         "object_count"         : self.game.max_num_objects,
                         "score"                : self.game.score,
                         "terminal_observation" : {}
                         }

        # Action space - Need representations for direction (L/R)
        self.action_space = spaces.Discrete( 3 )

        # Observation space - Need position of the following: The Player, Falling Projectiles, Enemy(?)
        self.observation_space = spaces.Dict(
            {
                # This will represent the location of the player (x, y)
                "player" : spaces.Box(                #  X coord range                                   Y coord range
                                     low   = np.array( [ 0,                                              PLAYER_Y ] ),
                                     high  = np.array( [ ( SCREEN_WIDTH - PLAYER_WIDTH ),                PLAYER_Y ] ),
                                     dtype = float,
                                     ),

                # This will represent the locations of the falling projectiles [(x, y)]
                "projectiles" : spaces.Box(               #    X coord range                    Y coord range                           Num proj to track
                                          low  = np.array( [ [ 0,                               0                                 ] ] * MAX_PROJECTILES ),
                                          high = np.array( [ [ ( SCREEN_WIDTH - OBJECT_WIDTH ), ( SCREEN_HEIGHT - OBJECT_HEIGHT ) ] ] * MAX_PROJECTILES ),
                                          dtype= float,
                                          ),

                # This will represent whether or not the projectile is 'in use'.
                "mask": spaces.Box(  # Binary mask to indicate active/inactive projectiles
                                   low   = 0,
                                   high  = 1,
                                   shape = ( MAX_PROJECTILES , ),
                                   dtype = np.int64,
                                   ),
            }
        )


    def reset( self, seed=None ):
        """ Reset to the episode instance.

        Call to the in-game function restart that resets the
        player's location, enemy's location, score, and clears
        all falling objects. This will also return an observation
        of this reset state for the start of a new episode.

        Args:
            arguement_1 (CatchEnv): Reference to self, CatchEnv.
            arguement_2 (int): Seed for the RNG.

        Returns:
            spaces.Dict: returns an oberservation of the reset
                         state.
        """
        # We need the following line to seed self.np_random
        super().reset( seed=seed )
        
        # Reset relevant CatchEnv attributes
        self.done           = False
        self.reward_val     = 0
        self.last_player_x  = ( SCREEN_WIDTH // 2 ) - ( PLAYER_WIDTH // 2 )

        # Reset relevant Catch attributes
        self.game.restart()

        # Increment episode based settings
        self.episode_num += 1
        self.info_logs[ "episode_num" ] = self.episode_num

        return ( self._get_obs(), self._get_info() )
    

    def _get_info( self ):
        """ Private getter for extra relevant game info.

        Return relevant attributes to give the gym
        environment extra context for observation/reward processes.
        
        Args:
            arguement_1 (CatchEnv): Reference to self, CatchEnv.

        Returns:
            spaces.Dict: returns a observation of the game's current
                         score, episode count, object count, object speed,
                         and average score.
        """
        return ( self.info_logs )
    

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
        # Collect the player's current position.
        player_obs = np.array( [
                               self.game.player_x,
                               PLAYER_Y
                               ] )

        # Collect position data for any active falling objects and
        # mask off 'active' projectiles for futher processing.
        projectiles_obs = []
        mask            = []
        for obj in self.game.falling_objects[ : MAX_PROJECTILES ]:
            proj_x = obj.x
            proj_y = obj.y

            projectiles_obs.append( np.array( [ 
                                              proj_x, 
                                              proj_y 
                                              ] ) )
            mask.append( 1 ) # Mark object as active
        
        # Pad with normalized (0, 0) if fewer projectiles than MAX_PROJECTILES
        while len( projectiles_obs ) < MAX_PROJECTILES:
            projectiles_obs.append( np.array( [ 
                                              0, 
                                              0 
                                              ] ) )
            mask.append( 0 ) # Mark object as inactive

        # Create normalized observation dictionary
        observation = {
                      "player"     : player_obs,
                      "projectiles": np.array( projectiles_obs ),
                      "mask"       : np.array( mask ),
                      }

        return ( observation )


    # Should just be one full 'move' by the agent.
    # Record an observation after the action has been applied
    # and a reward calculated 
    def step( self, action ):

        # Grab the agent's action and corresponding move
        # Call game's run method to updated based on the action
        self.game.run_game( action=action )

        # Check if the action resulted in the game ending
        if self.game.running == False:
            # Set the flag alerting the episode has finished
            self.info_logs[ "score" ] = self.game.score
            self.done                 = True

        # Take an observation of the game state after the action
        observation = self._get_obs()

        # Calculate a reward based on the action
        self.reward_val = self.reward( observation )

        # Grab any other information
        info      = self._get_info()
        truncated = False

        return ( observation, self.reward_val, self.done, truncated, info )


    def reward( self, obs ):
        # Base reward initialization
        reward = 0

        # Calculate player's center position
        # Grab the x position of the player
        player_x = obs[ "player" ][ 0 ] # Index 0 because that correspond 
                                        # to the X coordinate
        player_center_x = player_x + ( PLAYER_WIDTH // 2 )
        player_center_y = PLAYER_Y - ( PLAYER_HEIGHT // 2 )

        # Loop through falling objects to find the closest one
        active_projectiles = []

        # Grab array indicies of the active projectiles
        for index, mask in enumerate( obs[ "mask" ] ):
            if mask:
                active_projectiles.append( index )

        coord_pairs_of_actv_proj = []
        for index in active_projectiles:
            coord_pairs_of_actv_proj.append( obs[ "projectiles" ][ index ] )

        # If there are no falling objects return a reward of 0
        if not coord_pairs_of_actv_proj:
            return reward
        # Else sort by the second element of each sublist
        else: coord_pairs_of_actv_proj.sort( reverse=True, key=lambda x: x[ 1 ] )

        # Grab the closest object that isn't aleady below the player
        closest_obj = ( 0, 0 )
        for index, pair in enumerate( coord_pairs_of_actv_proj ):

            # Make sure the object is already below the player
            if( PLAYER_Y > pair[ 1 ] ):
                closest_obj = pair
                break
            else: continue

        # Calculate the center of the falling object
        obj_center_x = closest_obj[ 0 ] + ( OBJECT_WIDTH // 2 )
        obj_center_y = closest_obj[ 1 ] - ( OBJECT_HEIGHT // 2 )

        # Compute separate x and y distances
        x_distance = abs( player_center_x - obj_center_x ) / SCREEN_WIDTH
        # y_distance = abs( player_center_y - obj_center_y ) / SCREEN_HEIGHT

        # Shaping reward: prioritize X alignment
        reward += 1.0 - x_distance  # closer is better

        # Bonus if proactively standing under an object (before it reaches player Y)
        if abs( player_center_x - obj_center_x ) < OBJECT_WIDTH and obj_center_y < PLAYER_Y:
            reward += 0.3  # proactive bonus

        # Penalize excessive movement (efficiency)
        movement_penalty = abs(player_x - self.last_player_x) / SCREEN_WIDTH
        reward -= 0.5 * movement_penalty

        if self.game.temp_collision_det == True:
            reward                       = 10               # Full reward for catching the object
            self.game.temp_collision_det = False            # Reset the collision flag
            return ( reward )                               # Return immediately if an object is caught

        # Save last player position for next step
        self.last_player_x = player_x

        return ( reward )
