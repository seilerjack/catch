import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode( ( SCREEN_WIDTH, SCREEN_HEIGHT ) )
pygame.display.set_caption( "Catch the Objects!" )

# Colors
WHITE = ( 255, 255, 255 )
BLACK = ( 0, 0, 0 )
RED   = ( 255, 0, 0 )
BLUE  = ( 0, 0, 255 )

# Game settings
PLAYER_WIDTH  = 100
PLAYER_HEIGHT = 20
PLAYER_Y      = 580
player_x      = ( SCREEN_WIDTH // 2 ) - ( PLAYER_WIDTH // 2 )
player_speed  = 7

ENEMY_WIDTH   = 60
ENEMY_HEIGHT  = 40
enemy_x       = random.randint( 0, SCREEN_WIDTH - ENEMY_WIDTH )
enemy_y       = random.randint( 0, SCREEN_HEIGHT // 3 )
enemy_speed_x = 3
enemy_speed_y = 2

OBJECT_WIDTH    = 20
OBJECT_HEIGHT   = 20
falling_objects = []
object_speed    = 5

SPEED_MULT  = 1.25
score = 0
font  = pygame.font.SysFont(None, 48)
clock = pygame.time.Clock()
FPS   = 60

# Functions
def draw_player():
    pygame.draw.rect( screen, BLUE, ( player_x, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT ) )

def draw_enemy():
    pygame.draw.ellipse( screen, RED, ( enemy_x, enemy_y, ENEMY_WIDTH, ENEMY_HEIGHT ) )

def draw_falling_objects():
    for obj in falling_objects:
        pygame.draw.rect( screen, BLACK, obj )

def show_score():
    score_text = font.render( f"Score: { score }", True, BLACK )
    screen.blit( score_text, ( 10, 10 ) )

def check_collision( player_rect, obj_rect ):
    return player_rect.colliderect( obj_rect )

# Main game loop
running = True
while running:
    screen.fill( WHITE )

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[ pygame.K_a]  and player_x > 0:
        player_x -= player_speed
    if keys[ pygame.K_d ] and player_x < SCREEN_WIDTH - PLAYER_WIDTH:
        player_x += player_speed

    # Enemy movement, speed up when score increments by 10
    speed_multiplier = SPEED_MULT if score % 10 == 0 else 1
    enemy_x += enemy_speed_x * speed_multiplier
    enemy_y += enemy_speed_y * speed_multiplier

    if enemy_x <= 0 or enemy_x >= SCREEN_WIDTH - ENEMY_WIDTH:
        enemy_speed_x *= -1
    if enemy_y <= 0 or enemy_y >= SCREEN_HEIGHT // 3:
        enemy_speed_y *= -1

    # Drop objects periodically
    if random.randint( 1, 40 ) == 1:
        falling_objects.append( pygame.Rect( enemy_x + ENEMY_WIDTH // 2, enemy_y + ENEMY_HEIGHT, OBJECT_WIDTH, OBJECT_HEIGHT ) )

    # Update falling objects
    for obj in falling_objects[ : ]:
        obj.y += object_speed
        if obj.y >= SCREEN_HEIGHT:
            running = False
            print( "Game Over!" )
        if check_collision( pygame.Rect( player_x, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT ), obj ):
            falling_objects.remove( obj )
            score += 1

    # Drawing
    draw_player()
    draw_enemy()
    draw_falling_objects()
    show_score()

    # Refresh the screen
    pygame.display.flip()
    clock.tick( FPS )

pygame.quit()
sys.exit()
