import subprocess
import sys

import random
import math

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


try:
    import pygame
except ImportError:
    print("pygame is not installed. Installing now...")
    install("pygame")
    import pygame

pygame.init()

FPS = 60

WIDTH,HEIGHT = 800,800
ROWS = 4
COLS = 4

RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (187,173,160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205,192,180)
FONT_COLOR = (119,110,101)

FONT = pygame.font.SysFont("arial",60, bold=True)
MOVE_VEL = 20

WINDOW = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("2048")

class Tile:
    COLORS = [   (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        ]

    def __init__(self,value,row,col):
        self.value = value
        self.row  = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color

    def draw(self,window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1 , FONT_COLOR)
        window.blit(
            text, 
            (self.x + (RECT_WIDTH/2 - text.get_width()/2 ),
            self.y + (RECT_HEIGHT / 2 - text.get_height()/2)
            ),
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil (self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor (self.x / RECT_WIDTH)

    def move(self,delta):
        self.x += delta[0]
        self.y += delta[1]

def draw_grid(window):
    for row in range(1,ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1,COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, ( x, 0), ( x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(window,OUTLINE_COLOR,(0,0, WIDTH , HEIGHT), OUTLINE_THICKNESS)


def draw(window,tiles):
    window.fill(BACKGROUND_COLOR)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)
    pygame.display.update()

def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles:
            break

    return row, col

def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()

    if direction == "left":
        sort_func = lambda x: x.col
        reverse = False
        delta = (-MOVE_VEL, 0)
        boundary_check = lambda tile : tile.col == 0
        get_next_tile = lambda tile : tiles.get(f"{tile.row}{tile.col -1}")
        merge_check = lambda tile, next_tile : tile.x > next_tile.x + MOVE_VEL
        move_check = lambda tile, next_tile : tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        ceil = True

    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile : tile.col == COLS -1
        get_next_tile = lambda tile : tiles.get(f"{tile.row}{tile.col  + 1}")
        merge_check = lambda tile, next_tile : tile.x < next_tile.x - MOVE_VEL
        move_check = lambda tile, next_tile : tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x 
        ceil = False

    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = ( 0, -MOVE_VEL)
        boundary_check = lambda tile : tile.row == 0
        get_next_tile = lambda tile : tiles.get(f"{tile.row-1}{tile.col}")
        merge_check = lambda tile, next_tile : tile.y > next_tile.y + MOVE_VEL
        move_check = lambda tile, next_tile : tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        ceil = True

    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = ( 0, MOVE_VEL)
        boundary_check = lambda tile : tile.row == ROWS -1
        get_next_tile = lambda tile : tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile : tile.y < next_tile.y - MOVE_VEL
        move_check = lambda tile, next_tile : tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i,tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif tile.value == next_tile.value and tile not in blocks and next_tile not in blocks:
                if merge_check(tile,next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)

            elif move_check(tile,next_tile):
                tile.move(delta)
            else:
                continue
            tile.set_pos(ceil)
            updated = True

        update_tiles(window,tiles, sorted_tiles)
    
    result = end_move(tiles, window)  

    
    if result == "restart":
        print("Game restarted due to full grid.")

def end_move(tiles,window):
    if len(tiles) == 16:
        # Create the 'Game Over' message
        game_over_font = pygame.font.SysFont("verdana", 52)  
        restart_msg_font = pygame.font.SysFont("verdana", 46)
        game_over_text = game_over_font.render("Game Over!!!", True, (32, 35, 36))  
        restart_msg_text = restart_msg_font.render("Press escape to Restart", True, (32, 35, 36)) 
        over_text_x = WIDTH / 2 - game_over_text.get_width() / 2
        over_text_y = HEIGHT / 2 - game_over_text.get_height() / 2
        restart_text_x = WIDTH / 2 - restart_msg_text.get_width() / 2
        restart_text_y = HEIGHT / 2 - restart_msg_text.get_height() / 2 + game_over_text.get_height() 

        # Draw the 'Game Over' message in the center of the screen
        #window.fill((0, 0, 0))  # Optional: fill the screen with black before displaying the message
        window.blit(game_over_text, (over_text_x, over_text_y))
        window.blit(restart_msg_text, (restart_text_x, restart_text_y))
        pygame.display.update()  # Update the display to show the game over message

        # Wait for the user to press the escape key
        waiting_for_escape = True
        while waiting_for_escape:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting_for_escape = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        restart_game(window, tiles)
        return "restart"
    
    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2,4]),row,col)
    return "continue"

def restart_game(window, tiles):
    # Clears existing tiles and generates new ones
    tiles.clear()
    initial_tiles = generate_tiles()
    for key, tile in initial_tiles.items():
        tiles[key] = tile
    draw(window, tiles)  # Redraw the initial game state

def update_tiles(window,tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    draw(window, tiles)

def generate_tiles():
    tiles = {}
    for _ in range(2):
        row , col = get_random_pos(tiles)
        tiles [ f"{row}{col}" ] = Tile(2,row,col)

    return tiles

def main(window):
    clock = pygame.time.Clock()
    run = True
    
    tiles = generate_tiles()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    restart_game(window, tiles)
                if event.key == pygame.K_LEFT:
                    move_tiles(window, tiles, clock, "left")
                if event.key == pygame.K_RIGHT:
                    move_tiles(window, tiles, clock, "right")
                if event.key == pygame.K_UP:
                    move_tiles(window, tiles, clock, "up")
                if event.key == pygame.K_DOWN:
                    move_tiles(window, tiles, clock, "down")
            
        draw(window, tiles)

if __name__ == "__main__":
    main(WINDOW)

# python -m PyInstaller --onefile --windowed scriptxy.py
