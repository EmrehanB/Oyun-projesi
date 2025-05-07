# meteor_escape_game.py
import raylibpy as rl
import random

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
MAX_FALLING_ROCKS = 70
FRAME_HOLD = 6
SCALE = 1.50
PLATFORM_WIDTH_RANGE = (60, 90)
PLATFORM_HEIGHT_GAP = (100, 150)
HORIZONTAL_VARIANCE = 120
COLLISION_TOLERANCE_X = 10
COLLISION_TOLERANCE_Y = 10
PLATFORM_COUNT = 10

class Player:
    def __init__(self, position, speed):
        self.position = position
        self.speed = speed
        self.can_jump = True
        self.frame_index = 0
        self.facing_right = True

class FallingRock:
    def __init__(self, rect, speed):
        self.rect = rect
        self.speed = speed
        
def generate_platforms():
    platforms = []
    y = 0
    for _ in range(PLATFORM_COUNT):
        width = random.randint(*PLATFORM_WIDTH_RANGE)
        x = SCREEN_WIDTH // 2 - width // 2 + random.randint(-HORIZONTAL_VARIANCE // 2, HORIZONTAL_VARIANCE // 2)
        x = max(0, min(x, SCREEN_WIDTH - width))
        platforms.append(rl.Rectangle(x, y, width, 10))
        y -= random.randint(*PLATFORM_HEIGHT_GAP)
    return platforms

def reset_game(sprite_w, sprite_h, ship_texture):
    platforms = generate_platforms()
    first_plat = platforms[0]
    player = Player(
        rl.Vector2(first_plat.x + first_plat.width / 2 - sprite_w / 2, first_plat.y - sprite_h),
        3.0
    )
    last_platform = platforms[-1]
    goal = rl.Vector2(
        last_platform.x + last_platform.width / 2 - ship_texture.width / 2,
        last_platform.y - ship_texture.height - 20
    )
    return {
        "platforms": platforms,
        "player": player,
        "velocity_y": 0,
        "goal": goal,
        "falling_rocks": [],
        "rock_spawn_timer": 0,
        "frame_counter": 0,
        "game_finished": False,
        "player_hit": False,
        "start_y": first_plat.y
    }

def main():
    rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Meteor Escape")
    rl.set_target_fps(60)

    idle_frames = [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(0, 8)]
    walk_right_frames = [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(9, 16)]
    walk_left_frames = [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(25, 31)]

    meteor_texture = rl.load_texture("assets/Meteor1.png")
    ship_texture = rl.load_texture("assets/Ship2.png")
    game_background = rl.load_texture("assets/Background.png")
    menu_background = rl.load_texture("assets/Menu.png")

    sprite_w = idle_frames[0].width * SCALE
    sprite_h = idle_frames[0].height * SCALE
    meteor_width = meteor_texture.width - 45
    meteor_height = meteor_texture.height - 40

    game_state = reset_game(sprite_w, sprite_h, ship_texture)
    menu_active = True

    camera = rl.Camera2D()
    camera.offset = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    camera.zoom = 1.0

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.BLACK)

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        if menu_active:
            rl.draw_texture_pro(menu_background, rl.Rectangle(0, 0, menu_background.width, menu_background.height), rl.Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), rl.Vector2(0, 0), 0.0, rl.WHITE)
            
            rl.draw_text("Press [SPACE] to start", center_x - 150, center_y + 0, 25, rl.YELLOW)
            rl.draw_text("Press [ESC] to quit", center_x - 150, center_y + 25, 25, rl.YELLOW)
            if rl.is_key_pressed(rl.KEY_SPACE):
                game_state = reset_game(sprite_w, sprite_h, ship_texture)
                menu_active = False
        else:
            player = game_state["player"]
            rl.draw_texture_pro(game_background, rl.Rectangle(0, 0, game_background.width, game_background.height), rl.Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), rl.Vector2(0, 0), 0.0, rl.WHITE)
            camera.target = rl.Vector2(SCREEN_WIDTH // 2, player.position.y + sprite_h / 2)
            rl.begin_mode2d(camera)

            if not game_state["game_finished"] and not game_state["player_hit"]:
                moving = False
                if rl.is_key_down(rl.KEY_RIGHT):
                    player.position.x += player.speed
                    player.facing_right = True
                    moving = True
                elif rl.is_key_down(rl.KEY_LEFT):
                    player.position.x -= player.speed
                    player.facing_right = False
                    moving = True

                if rl.is_key_pressed(rl.KEY_SPACE) and player.can_jump:
                    game_state["velocity_y"] = -10
                    player.can_jump = False

                game_state["velocity_y"] += 0.5
                player.position.y += game_state["velocity_y"]
                player.can_jump = False
                player_rect = rl.Rectangle(player.position.x, player.position.y, sprite_w, sprite_h)

                for plat in game_state["platforms"]:
                    ext = rl.Rectangle(
                        plat.x - COLLISION_TOLERANCE_X,
                        plat.y - COLLISION_TOLERANCE_Y,
                        plat.width + 2 * COLLISION_TOLERANCE_X,
                        plat.height + COLLISION_TOLERANCE_Y
                    )
                    if game_state["velocity_y"] >= 0 and rl.check_collision_recs(player_rect, ext):
                        player.position.y = plat.y - sprite_h
                        game_state["velocity_y"] = 0
                        player.can_jump = True
                        break

                if player.position.y > game_state["platforms"][0].y + 200:
                    game_state["player_hit"] = True

                game_state["rock_spawn_timer"] += 1
                if game_state["rock_spawn_timer"] > 60:
                    if len(game_state["falling_rocks"]) < MAX_FALLING_ROCKS:
                        rx = player.position.x + random.randint(-HORIZONTAL_VARIANCE, HORIZONTAL_VARIANCE)
                        ry = player.position.y - 300
                        game_state["falling_rocks"].append(FallingRock(rl.Rectangle(rx, ry, meteor_width, meteor_height), random.randint(3, 6)))
                    game_state["rock_spawn_timer"] = 0

                for rock in game_state["falling_rocks"][:]:
                    rock.rect.y += rock.speed
                    if rl.check_collision_recs(player_rect, rock.rect):
                        game_state["player_hit"] = True
                    if rock.rect.y > player.position.y + SCREEN_HEIGHT:
                        game_state["falling_rocks"].remove(rock)

                game_state["frame_counter"] += 1
                if game_state["frame_counter"] >= FRAME_HOLD:
                    game_state["frame_counter"] = 0
                    player.frame_index += 1

                goal_rect = rl.Rectangle(game_state["goal"].x, game_state["goal"].y, ship_texture.width, ship_texture.height)
                if rl.check_collision_recs(player_rect, goal_rect):
                    game_state["game_finished"] = True

            for plat in game_state["platforms"]:
                rl.draw_rectangle_rec(plat, rl.DARKGRAY)

            goal = game_state["goal"]
            rl.draw_texture(ship_texture, int(goal.x), int(goal.y), rl.WHITE)

            for rock in game_state["falling_rocks"]:
                rl.draw_texture(meteor_texture, int(rock.rect.x), int(rock.rect.y), rl.WHITE)

            frame = idle_frames[player.frame_index % len(idle_frames)]
            if player.can_jump:
                if rl.is_key_down(rl.KEY_RIGHT):
                    frame = walk_right_frames[player.frame_index % len(walk_right_frames)]
                elif rl.is_key_down(rl.KEY_LEFT):
                    frame = walk_left_frames[player.frame_index % len(walk_left_frames)]

            rl.draw_texture_ex(frame, rl.Vector2(player.position.x, player.position.y), 0.0, SCALE, rl.WHITE)
            rl.end_mode2d()

            score = int(game_state["start_y"] - player.position.y)
            rl.draw_text(f"Score: {score} m", 20, 20, 20, rl.WHITE)

            if game_state["player_hit"]:
                rl.draw_text(" GAME OVER.", center_x - 140, center_y, 24, rl.YELLOW)
                rl.draw_text("[R] to Restart", center_x - 120, center_y + 40, 18, rl.YELLOW)

            elif game_state["game_finished"]:
                rl.draw_text(" YOU WIN! ", center_x - 120, center_y, 24, rl.GREEN)
                rl.draw_text("[R] to Restart", center_x - 120, center_y + 40, 18, rl.GREEN)

            if rl.is_key_pressed(rl.KEY_R):
                game_state = reset_game(sprite_w, sprite_h, ship_texture)
                menu_active = True

        rl.end_drawing()

    for tex in idle_frames + walk_right_frames + walk_left_frames:
        rl.unload_texture(tex)
    rl.unload_texture(meteor_texture)
    rl.unload_texture(ship_texture)
    rl.unload_texture(game_background)
    rl.unload_texture(menu_background)
    rl.close_window()

if __name__ == "__main__":
    main()
