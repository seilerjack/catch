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
        self.player_x         = ( SCREEN_WIDTH // 2 ) - ( PLAYER_WIDTH // 2 )
        self.player_speed     = 7

        self.enemy_x          = ( SCREEN_WIDTH // 2 ) - ( ENEMY_WIDTH // 2 )
        self.enemy_y          = ( SCREEN_HEIGHT // 6 ) - ( ENEMY_HEIGHT // 2 )
        self.enemy_speed_x    = 3
        self.enemy_speed_y    = 2
        self.speed_multiplier = 1

        self.falling_objects  = []
        self.object_speed     = 5

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


    def show_score( self ):
        score_text = self.font.render( f"Score: { self.score }", True, BLACK )
        self.screen.blit( score_text, ( 10, 10 ) )


    def check_collision( self, player_rect, obj_rect ):
        return player_rect.colliderect( obj_rect )


    def update( self ):
        # Player movement and ESC key for exiting the game
        keys = pygame.key.get_pressed()
        if keys[ pygame.K_a]  and self.player_x > 0:
            self.player_x -= self.player_speed
        if keys[ pygame.K_d ] and self.player_x < SCREEN_WIDTH - PLAYER_WIDTH:
            self.player_x += self.player_speed
        if keys[pygame.K_ESCAPE]:
            game_exit()

        # Enemy movement, speed up when score increments by 10
        self.speed_multiplier = SPEED_MULT if self.score % 10 == 0 else 1
        self.enemy_x += self.enemy_speed_x * self.speed_multiplier
        self.enemy_y += self.enemy_speed_y * self.speed_multiplier

        if self.enemy_x <= 0 or self.enemy_x >= SCREEN_WIDTH - ENEMY_WIDTH:
            self.enemy_speed_x *= -1
        if self.enemy_y <= 0 or self.enemy_y >= SCREEN_HEIGHT // 3:
            self.enemy_speed_y *= -1

        # Drop objects periodically
        if random.randint( 1, 40 ) == 1:
            self.falling_objects.append( pygame.Rect( self.enemy_x + ENEMY_WIDTH // 2, self.enemy_y + ENEMY_HEIGHT, OBJECT_WIDTH, OBJECT_HEIGHT ) )

        # Update falling objects
        for obj in self.falling_objects[ : ]:
            obj.y += self.object_speed
            if obj.y >= SCREEN_HEIGHT:
                if self.running:  # To prevent spamming "Game Over!"
                    print("Game Over!")
                self.running = False
            if self.check_collision( pygame.Rect( self.player_x, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT ), obj ):
                self.falling_objects.remove( obj )
                self.score += 1


    def restart( self ):
        self.running          = True
        self.score            = 0
        self.player_x         = ( SCREEN_WIDTH // 2 ) - ( PLAYER_WIDTH // 2 )
        self.enemy_x          = ( SCREEN_WIDTH // 2 ) - ( ENEMY_WIDTH // 2 )
        self.enemy_y          = ( SCREEN_HEIGHT // 6 ) - ( ENEMY_HEIGHT // 2 )
        self.enemy_speed_x    = 3
        self.enemy_speed_y    = 2
        self.speed_multiplier = 1
        self.falling_objects.clear()


    def run_game( self ):
        # Main game loop
        while True:
            self.restart()
            while self.running:
                self.screen.fill( WHITE )

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # Update all moving objects
                self.update()

                # Drawing
                self.draw_player()
                self.draw_enemy()
                self.draw_falling_objects()
                self.show_score()

                # Refresh the screen
                pygame.display.flip()
                self.clock.tick( FPS )

#---------------------------------------------------------
# EXECUTION
#---------------------------------------------------------
if __name__ == "__main__":
    game = Catch()
    game.run_game()
