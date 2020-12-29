import ugame
import stage

"""
Display is 160 pixels wide x 128 pixels high.
Tiles are 16x16, window is 10 tiles wide x 8 tiles high.
(0,0) is the top left of the screen.
Sprite locations are the top left point of the sprite image.
"""

# Movement, gravity, and refresh variables
MOVE_SPEED = 6 # How fast the game scrolls, values of 16+ could cause problems detecting collisions
FPS = 12 # Maximum frames per second


# State of the game: win, lose, or play
PLAY = 0
WIN = 1
LOSE = -1
game_state = PLAY

# Set up the main game display
game = stage.Stage(
    display=ugame.display, # initialized display parameter
    fps=FPS # Set maximum frame rate
)

# Load in the sprite and background images
bank = stage.Bank.from_bmp16("img/sprites.bmp")

# Set the background to tile a single 16x16 sprite from the bank
# Defaults to the first 16x16 image, but can use tile to change individual tiles
background = stage.Grid(bank, width=10, height=8)

# Create player character Blinka as a sprite
blinka = stage.Sprite(
    bank=bank, # Use the bank of images we already loaded
    frame=1, # Use the second image in the bank (0-indexed)
    x=72, # Set the x co-ordinate of the top-right corner of the sprite
    y=56, # set the y co-ordinate of the top-right corner of the sprite
)

# Set up the ground as obstacles we can't pass. Each piece of wall is a sprite.
# Create sprites the same way as for blinka
wall_sprites = []

# Add main floor
for x in range (0, 10*16, 16):
    wall_sprites.append(stage.Sprite(bank, frame=5, x=x, y=72))
# Skip a section for a pit
for x in range(12*16, 20*16, 16):
    wall_sprites.append(stage.Sprite(bank, frame=5, x=x, y=72))
# Add a platform to jump on
for x in range (8*16, 13*16, 16):
    wall_sprites.append(stage.Sprite(bank, frame=5, x=x, y=44))

# Put all sprites that aren't Blinka in a single list. This will make things easier later
world_sprites = wall_sprites #[goal_sprite] + enemy_sprites +  wall_sprites

# Create text object to display mesages
text = stage.Text(width=12, height=11)
        
# Set the text location
text.move(x=50, y=50)

# Create a list of layers to be displayed, from foreground to background
# Background should always be last or it will cover anything behind it
game.layers = [text, blinka] + world_sprites + [background]

# Update the display
game.render_block()

y_velocity = 0
jump_time = 0
max_jump_time = 3

# Game runs in a loop forever, refreshing the screen as often as fps allows
while True:

    # Info on how to make jumps: https://2dengine.com/?p=platformers#section_4
    jump_height = 3*16
    GRAVITY = 8
    INITIAL_VELOCITY = 28
    MAX_MOVE = 15
    

    # If control pad/joystick buttons are pressed, determine where to move
    dx = 0 # How far to move in x direction
    dy = 0 # How far to move in y direction

    # See which buttons are pressed (if any)
    keys = ugame.buttons.get_pressed()

    # ugame.K_RIGHT will be true if the right button is pressed
    if keys & ugame.K_RIGHT:
        dx = -MOVE_SPEED
    # ugame.K_LEFT will be true if the left button is pressed
    elif keys & ugame.K_LEFT:
        dx = MOVE_SPEED
    # ugame.K_UP will be true if the up button is pressed
    if keys & ugame.K_UP:
        if jump_time < max_jump_time:
            y_velocity = INITIAL_VELOCITY
            jump_time += 1

    y_velocity -= GRAVITY
    dy = y_velocity - GRAVITY
    dy = min(dy, MAX_MOVE) # Limit the speed
    dy = max(dy, -MAX_MOVE)

        
    # Keep Blinka from going through walls
    for sprite in wall_sprites:
        # Check if the movement in x direction would cause a collision
        x_collision = stage.collide(ax0=blinka.x + 1,   # Make Blinka 1 pixel smaller in each direction
                                    ay0=blinka.y + 1,   # to prevent issues with collisions on the
                                    ax1=blinka.x + 15,  # boundary line
                                    ay1=blinka.y + 15,
                                    bx0=sprite.x + dx,
                                    by0=sprite.y,
                                    bx1=sprite.x + dx + 16,
                                    by1=sprite.y + 16)

        # If x movement would cause a collision, limit movement so Blinka is next to wall
        # dx/abs(dx) gets whether dx is above or below 0, determines whether we add or subtract 16
        if x_collision and dx != 0: 
            dx = blinka.x - sprite.x - dx / abs(dx) * 16
        
        # Check if the movement in y direction would cause a collision
        y_collision = stage.collide(ax0=blinka.x + 1,   # Make Blinka 1 pixel smaller in each direction
                                    ay0=blinka.y + 1,   # to prevent issues with collisions on the
                                    ax1=blinka.x + 15,  # boundary line
                                    ay1=blinka.y + 15,
                                    bx0=sprite.x,
                                    by0=sprite.y + dy,
                                    bx1=sprite.x + 16,
                                    by1=sprite.y + dy + 16)

        # If y movement would cause a collision, limit movement so Blinka is next to wall
        # dy/abs(dy) gets whether dx is above or below 0, determines whether we add or subtract 16
        if y_collision and dy != 0: 
            dy = blinka.y - sprite.y - dy / abs(dy) * 16
            y_velocity = 0 # If we hit ground, stop falling
            jump_time = 0

    # Update the location on all world sprites. This keeps Blinka in the center and moves the world around her.
    for sprite in world_sprites:
        # Have to call update to store old location in temp variable, otherwise it may not erase properly
        sprite.update()
        sprite.move(x=sprite.x + dx, y=sprite.y + dy)

    # Animate Blinka by changing the frame
    # Add 1 to the current frame to move on to the next one
    # The modulo (%) operator lets us wrap back to the first frame number at the end
    blinka.set_frame(frame=blinka.frame % 4 + 1)

    # Update the display of all sprites in the list
    game.render_sprites([blinka] + world_sprites)

    # Wait for the start of the next frame (limited by fps set when creating game)
    game.tick()

