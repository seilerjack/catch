#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import sys
import random
import pygame


#---------------------------------------------------------
# CONSTANTS
#---------------------------------------------------------
# Colors
WHITE         = ( 255, 255, 255 )
BLACK         = ( 0, 0, 0 )
RED           = ( 255, 0, 0 )
BLUE          = ( 0, 0, 255 )

# Screen settings
# SCREEN_WIDTH  = 640
SCREEN_WIDTH  = 500
SCREEN_HEIGHT = 720
FPS           = 30
PIXEL_BUFFER  = 5

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
MAX_PROJECTILES = 1

#---------------------------------------------------------
# PROCEDURES
#---------------------------------------------------------
def game_exit():
    pygame.quit()
    sys.exit()

#---------------------------------------------------------
# CLASSES
#---------------------------------------------------------
class Catch( object ):

    def __init__( self ):
        # Initialize pygame
        pygame.init()

        # Player/Enemy/Projectile movement setup
        self.player_x           = ( SCREEN_WIDTH // 2 ) - ( PLAYER_WIDTH // 2 )
        self.player_speed       = 12

        self.enemy_x            = ( SCREEN_WIDTH // 2 ) - ( ENEMY_WIDTH // 2 )
        self.enemy_y            = ( SCREEN_HEIGHT // 6 ) - ( ENEMY_HEIGHT // 2 )
        self.enemy_speed_x      = random.choice( [ i for i in range( -3,3 ) if i not in [ 1, 0, 1 ] ] )
        self.enemy_speed_y      = random.choice( [ y for y in range( -2,2 ) if y not in [ -1, 0, 1 ] ] )
        self.speed_multiplier   = 1

        self.falling_objects    = []
        self.object_speed       = 3
        self.collision_detected = False
        self.temp_collision_det = False

        # Game environemnt settings
        self.running = False
        self.score   = 0
        self.font    = pygame.font.SysFont(None, 48)
        self.clock   = pygame.time.Clock()
        self.screen  = pygame.display.set_mode( ( SCREEN_WIDTH, SCREEN_HEIGHT ) )
        pygame.display.set_caption( "Catch the Objects!" )

    #---------------------------------------------------------
    # PROCEDURES
    #---------------------------------------------------------
    def draw_player( self ):
        pygame.draw.rect( self.screen, BLUE, ( self.player_x, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT ) )


    def draw_enemy( self ):
        pygame.draw.ellipse( self.screen, RED, ( self.enemy_x, self.enemy_y, ENEMY_WIDTH, ENEMY_HEIGHT ) )


    def draw_falling_objects( self ):
        for obj in self.falling_objects:
            pygame.draw.rect( self.screen, BLACK, obj )

    
    def draw_distance_to_obj( self ):
        for obj in self.falling_objects:
            # Draw a line from the center of the player to the center of the object
            player_center_x = self.player_x + PLAYER_WIDTH // 2
            player_center_y = PLAYER_Y + PLAYER_HEIGHT // 2
            obj_center_x    = obj.x + OBJECT_WIDTH // 2
            obj_center_y    = obj.y + OBJECT_HEIGHT // 2

            # Draw the line if the object's y-position is less than or equal to the player's y-position
            if obj.y <= PLAYER_Y:
                pygame.draw.line( self.screen, RED, ( player_center_x, player_center_y ), ( obj_center_x, obj_center_y ), 2 )


    def show_score( self ):
        score_text = self.font.render( f"Score: { self.score }", True, BLACK )
        self.screen.blit( score_text, ( 10, 10 ) )


    def check_collision( self, player_rect, obj_rect ):
        if( player_rect.colliderect( obj_rect ) ):
            self.collision_detected = True
            self.temp_collision_det = True
        return ( self.collision_detected )


    def get_key_press( self, action=None ):
        # Get the actual keys pressed by the user
        keys = pygame.key.get_pressed()

        # If an action is passed (0 = stay, 1 = left, 2 = right), mimic key presses:
        if action is not None:
            # Create a temporary keys list mimicking Pygame key behavior
            keys = list( keys )  # Convert to mutable list if it's a tuple-like object
            if action == 1:  # Left
                keys[ pygame.K_a ] = True
            elif action == 2:  # Right
                keys[ pygame.K_d ] = True

        # Handle left movement (player_x decreases) if 'a' or corresponding action is pressed
        if keys[ pygame.K_a ] and self.player_x > 0 + PIXEL_BUFFER:
            self.player_x -= self.player_speed
        # Handle right movement (player_x increases) if 'd' or corresponding action is pressed
        if keys[ pygame.K_d ] and self.player_x < SCREEN_WIDTH - PLAYER_WIDTH - PIXEL_BUFFER:
            self.player_x += self.player_speed
        # Handle game exit on ESC key press
        if keys[ pygame.K_ESCAPE ]:
            self.running = False
            game_exit()
    

    def draw( self ):
        # Drawing
        self.draw_player()
        self.draw_enemy()
        self.draw_falling_objects()
        self.draw_distance_to_obj()
        self.show_score()


    def update( self, action=None ):
        # Set the temporary collision flag to false
        self.temp_collision_det = False
        # Player movement and ESC key for exiting the game
        self.get_key_press( action )

        # Enemy movement, speed up when score increments by 10
        self.speed_multiplier = SPEED_MULT if self.score % 10 == 0 else 1
        self.enemy_x += self.enemy_speed_x * self.speed_multiplier
        self.enemy_y += self.enemy_speed_y * self.speed_multiplier

        if self.enemy_x <= 0 or self.enemy_x >= SCREEN_WIDTH - ENEMY_WIDTH:
            self.enemy_speed_x *= -1
        if self.enemy_y <= 0 or self.enemy_y >= ( SCREEN_HEIGHT - ENEMY_HEIGHT ) / 3:
            self.enemy_speed_y *= -1

        # Drop objects periodically
        if random.randint( 1, 75 ) == 1:
            if len( self.falling_objects ) < MAX_PROJECTILES:
                self.falling_objects.append( pygame.Rect( self.enemy_x + ENEMY_WIDTH // 2, self.enemy_y + ENEMY_HEIGHT, OBJECT_WIDTH, OBJECT_HEIGHT ) )

        # Update falling objects
        for obj in self.falling_objects[ : ]:
            # Reset collision_detected at the start of each frame
            self.collision_detected = False
            obj.y += self.object_speed
            if obj.y >= ( SCREEN_HEIGHT - OBJECT_HEIGHT - PIXEL_BUFFER ):
                if self.running:  # To prevent spamming "Game Over!"
                    print(f"Game Over! Score: { self.score }")
                self.running = False
            if self.check_collision( pygame.Rect( self.player_x, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT ), obj ):
                self.falling_objects.remove( obj )
                self.score += 1
                continue


    def restart( self ):
        self.running            = True
        self.score              = 0
        self.player_x           = ( SCREEN_WIDTH // 2 ) - ( PLAYER_WIDTH // 2 )
        self.enemy_x            = ( SCREEN_WIDTH // 2 ) - ( ENEMY_WIDTH // 2 )
        self.enemy_y            = ( SCREEN_HEIGHT // 6 ) - ( ENEMY_HEIGHT // 2 )
        self.enemy_speed_x      = random.choice( [ i for i in range( -3,3 ) if i not in [ 1, 0, 1 ] ] )
        self.enemy_speed_y      = random.choice( [ y for y in range( -2,2 ) if y not in [ -1, 0, 1 ] ] )
        self.speed_multiplier   = 1
        self.collision_detected = False
        self.temp_collision_det = False
        self.falling_objects.clear()


    def run_game( self, action=None ):
        # Main game loop
        # while True:
        # Only call restart if we are playing outside the RL environment
            # if action is None: self.restart()
            # while self.running:
        self.screen.fill( WHITE )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update all moving objects
        self.update( action )

        # Draw on screen
        self.draw()

        # Refresh the screen
        pygame.display.flip()
        self.clock.tick( FPS )

#---------------------------------------------------------
# EXECUTION
#---------------------------------------------------------
if __name__ == "__main__":
    game = Catch()
    game.run_game()
