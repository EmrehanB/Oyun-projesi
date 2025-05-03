import raylibpy as rl
import random

class Player:
    def __init__(self, position, speed):
        self.position = position
        self.speed = speed
        self.can_jump = False
        self.direction = "idle"  # "right", "left", "idle"
        self.frame_index = 0
        self.frame_counter = 0
        self.frame_speed = 8

MAX_FALLING_ROCKS = 50

def main():
    screen_width = 800
    screen_height = 450

    rl.init_window(screen_width, screen_height, "Zıplama Oyunu - Astronot ve Düşen Taşlar")
    rl.set_target_fps(60)

    # Sprite animasyonları
    idle_frames = [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(0, 9)]
    walk_right_frames = [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(9, 16)]
    walk_left_frames = [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(25, 31)]

    camera = rl.Camera2D()
    camera.offset = (screen_width / 2, screen_height / 2)
    camera.zoom = 1.0

    player = Player(rl.Vector2(100, 800), 3.0)
    gravity = 0.5
    velocity_y = 0

    platforms = [
        rl.Rectangle(80, 850, 100, 10),
        rl.Rectangle(200, 750, 100, 10),
        rl.Rectangle(350, 650, 100, 10),
        rl.Rectangle(150, 550, 100, 10),
        rl.Rectangle(300, 450, 100, 10),
        rl.Rectangle(100, 350, 100, 10)
    ]

    goal = rl.Vector2(120, 300)
    game_finished = False
    player_hit = False

    falling_rocks = []
    rock_spawn_timer = 0

    while not rl.window_should_close():
        if not game_finished and not player_hit:
            player.direction = "idle"
            # Input
            if rl.is_key_down(rl.KEY_RIGHT):
                player.position.x += player.speed
                player.direction = "right"
            elif rl.is_key_down(rl.KEY_LEFT):
                player.position.x -= player.speed
                player.direction = "left"

            if rl.is_key_pressed(rl.KEY_SPACE) and player.can_jump:
                velocity_y = -10
                player.can_jump = False

            velocity_y += gravity
            player.position.y += velocity_y

            # Platform collision
            player.can_jump = False
            for plat in platforms:
                player_rect = rl.Rectangle(player.position.x, player.position.y, 40, 50)
                if rl.check_collision_recs(player_rect, plat):
                    if velocity_y >= 0:
                        player.position.y = plat.y - 50
                        velocity_y = 0
                        player.can_jump = True

            # Check goal
            if player.position.y <= goal.y:
                game_finished = True
            if player.position.y > goal.y + 600:
                player_hit = True

            # Spawn falling rocks
            rock_spawn_timer += 1
            if rock_spawn_timer > 180:
                if len(falling_rocks) < MAX_FALLING_ROCKS:
                    rock_x = player.position.x + random.randint(-200, 200)
                    rock_y = player.position.y - 300
                    rock = rl.Rectangle(rock_x, rock_y, 20, 20)
                    falling_rocks.append((rock, random.randint(2, 5)))
                rock_spawn_timer = 0

            # Update rocks
            for rock, speed in falling_rocks[:]:
                rock.y += speed
                player_rect = rl.Rectangle(player.position.x, player.position.y, 40, 50)
                if rl.check_collision_recs(player_rect, rock):
                    player_hit = True
                if rock.y > player.position.y + screen_height:
                    falling_rocks.remove((rock, speed))

            # Update animation frame
            player.frame_counter += 1
            if player.frame_counter >= (60 // player.frame_speed):
                player.frame_counter = 0
                player.frame_index += 1
                if player.direction == "right":
                    player.frame_index %= len(walk_right_frames)
                elif player.direction == "left":
                    player.frame_index %= len(walk_left_frames)
                else:
                    player.frame_index %= len(idle_frames)

        camera.target = player.position

        # Drawing
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        rl.begin_mode2d(camera)

        # Karakteri çiz
        if player.direction == "right":
            frame = walk_right_frames[player.frame_index]
        elif player.direction == "left":
            frame = walk_left_frames[player.frame_index]
        else:
            frame = idle_frames[player.frame_index]
        rl.draw_texture(frame, int(player.position.x), int(player.position.y), rl.WHITE)

        for plat in platforms:
            rl.draw_rectangle_rec(plat, rl.DARKGRAY)

        rl.draw_circle_v(goal, 10, rl.RED)
        rl.draw_text("Hedef Nokta", int(goal.x) - 30, int(goal.y) - 30, 10, rl.RED)

        for rock, _ in falling_rocks:
            rl.draw_rectangle_rec(rock, rl.MAROON)

        rl.end_mode2d()

        if player_hit:
            rl.draw_text("TAŞA ÇARPTIN veya DÜŞTÜN! Oyun Bitti.", screen_width // 2 - 150, screen_height // 2, 20, rl.RED)
        elif game_finished:
            rl.draw_text("TEBRİKLER! Yukarı ulaştın!", screen_width // 2 - 150, screen_height // 2, 20, rl.DARKGREEN)

        rl.end_drawing()

    for tex in idle_frames + walk_right_frames + walk_left_frames:
        rl.unload_texture(tex)
    rl.close_window()

if __name__ == "__main__":
    main()
