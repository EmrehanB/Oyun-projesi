import raylibpy as rl
import random

# Sabitler
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
MAX_FALLING_ROCKS = 70
FRAME_HOLD = 6
SCALE = 1.25

PLATFORM_WIDTH_RANGE = (60, 90)
PLATFORM_HEIGHT_GAP = (100, 150)
HORIZONTAL_VARIANCE = 120
COLLISION_TOLERANCE_X = 10
COLLISION_TOLERANCE_Y = 10
PLATFORM_COUNTS = [10, 10, 10, 10, 10]

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

def generate_platforms(platform_count):
    platforms = []
    y = 0
    for _ in range(platform_count):
        width = random.randint(*PLATFORM_WIDTH_RANGE)
        x = SCREEN_WIDTH // 2 - width // 2 + random.randint(-HORIZONTAL_VARIANCE // 2, HORIZONTAL_VARIANCE // 2)
        x = max(0, min(x, SCREEN_WIDTH - width))
        platforms.append(rl.Rectangle(x, y, width, 10))
        y -= random.randint(*PLATFORM_HEIGHT_GAP)
    return platforms

def reset_game(level, sprite_w, sprite_h):
    platforms = generate_platforms(PLATFORM_COUNTS[level])
    first_plat = platforms[0]
    player = Player(
        rl.Vector2(first_plat.x + first_plat.width / 2 - sprite_w / 2, first_plat.y - sprite_h),
        3.0
    )
    return {
        "platforms": platforms,
        "player": player,
        "velocity_y": 0,
        "goal": rl.Vector2(platforms[-1].x + 30, platforms[-1].y),
        "falling_rocks": [],
        "rock_spawn_timer": 0,
        "frame_counter": 0,
        "game_finished": False,
        "player_hit": False,
        "start_y": first_plat.y,
        "level": level
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

    game_state = reset_game(0, sprite_w, sprite_h)
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
            rl.draw_texture_pro(
                menu_background,
                rl.Rectangle(0, 0, menu_background.width, menu_background.height),
                rl.Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
                rl.Vector2(0, 0),
                0.0,
                rl.WHITE
            )

            rl.draw_text(" Meteor Escape ", center_x - 200, center_y - 120, 30, rl.YELLOW)
            rl.draw_text("Press [SPACE] to start", center_x - 180, center_y + 75, 16, rl.YELLOW)
            rl.draw_text("Press [ESC] to quit", center_x - 180, center_y + 100, 16, rl.YELLOW)

            if rl.is_key_pressed(rl.KEY_SPACE):
                game_state = reset_game(0, sprite_w, sprite_h)
                menu_active = False
        else:
            player = game_state["player"]

            # --- SABİT OYUN ARKAPLANI ---
            rl.draw_texture_pro(
                game_background,
                rl.Rectangle(0, 0, game_background.width, game_background.height),
                rl.Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
                rl.Vector2(0, 0),
                0.0,
                rl.WHITE
            )

            # --- HAREKETLİ NESNELERİ KAMERA TAKİBİYLE ÇİZ ---
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

                if player.position.y <= game_state["goal"].y:
                    if game_state["level"] < 4:
                        game_state = reset_game(game_state["level"] + 1, sprite_w, sprite_h)
                    else:
                        game_state["game_finished"] = True

                if player.position.y > game_state["platforms"][0].y + 200:
                    game_state["player_hit"] = True

                game_state["rock_spawn_timer"] += 1
                if game_state["rock_spawn_timer"] > 60:
                    if len(game_state["falling_rocks"]) < MAX_FALLING_ROCKS:
                        rx = player.position.x + random.randint(-HORIZONTAL_VARIANCE, HORIZONTAL_VARIANCE)
                        ry = player.position.y - 300
                        game_state["falling_rocks"].append(
                            FallingRock(rl.Rectangle(rx, ry, meteor_width, meteor_height), random.randint(3, 6))
                        )
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

            for plat in game_state["platforms"]:
                rl.draw_rectangle_rec(plat, rl.DARKGRAY)

            goal = game_state["goal"]
            rl.draw_texture(ship_texture, int(goal.x - ship_texture.width / 2), int(goal.y - ship_texture.height / 2), rl.WHITE)

            for rock in game_state["falling_rocks"]:
                rl.draw_texture(meteor_texture, int(rock.rect.x), int(rock.rect.y), rl.WHITE)

            # Oyuncu sprite'ı
            if not player.can_jump:
                frame = idle_frames[player.frame_index % len(idle_frames)]
            elif rl.is_key_down(rl.KEY_RIGHT):
                frame = walk_right_frames[player.frame_index % len(walk_right_frames)]
            elif rl.is_key_down(rl.KEY_LEFT):
                frame = walk_left_frames[player.frame_index % len(walk_left_frames)]
            else:
                frame = idle_frames[player.frame_index % len(idle_frames)]

            rl.draw_texture_ex(frame, rl.Vector2(player.position.x, player.position.y), 0.0, SCALE, rl.WHITE)
            rl.end_mode2d()

            # Arayüz
            score = int(game_state["start_y"] - player.position.y)
            rl.draw_text(f"Score: {score} m", 20, 20, 20, rl.WHITE)

            if game_state["player_hit"]:
                rl.draw_text(" GAME OVER.", center_x - 140, center_y, 24, rl.YELLOW)
                rl.draw_text("[R] to Restart", center_x - 120, center_y + 40, 18, rl.YELLOW)
            elif game_state["game_finished"]:
                rl.draw_text("CONGRATULATIONS!", center_x - 170, center_y, 24, rl.YELLOW)
                rl.draw_text("[R] to Restart", center_x - 120, center_y + 40, 18, rl.YELLOW)

            if rl.is_key_pressed(rl.KEY_R):
                game_state = reset_game(0, sprite_w, sprite_h)
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
