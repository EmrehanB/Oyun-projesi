import raylibpy as rl
import random

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

MAX_FALLING_ROCKS = 70
FRAME_HOLD = 6

PLATFORM_COUNT = 100
PLATFORM_WIDTH_RANGE = (60, 90)
PLATFORM_HEIGHT_GAP = (100, 150)
HORIZONTAL_VARIANCE = 120
COLLISION_TOLERANCE_X = 10
COLLISION_TOLERANCE_Y = 10

def generate_platforms():
    platforms = []
    x = 100
    y = 900
    for i in range(PLATFORM_COUNT):
        width = random.randint(*PLATFORM_WIDTH_RANGE)
        x = max(0, min(x + random.randint(-HORIZONTAL_VARIANCE, HORIZONTAL_VARIANCE), 800 - width))
        platforms.append(rl.Rectangle(x, y, width, 10))
        y -= random.randint(*PLATFORM_HEIGHT_GAP)
    return platforms

def main():
    screen_width = 800
    screen_height = 450

    rl.init_window(screen_width, screen_height, "Zor Zıplama Oyunu - Astronot ve Meteorlar")
    rl.set_target_fps(60)

    # Sprite yükleme
    idle_frames = [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(0, 8)]
    walk_right_frames = [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(9, 16)]
    walk_left_frames = [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(25, 31)]

    # Meteor görseli
    meteor_texture = rl.load_texture("assets/Meteor1.png")
    meteor_width = meteor_texture.width - 45
    meteor_height = meteor_texture.height - 40

    sprite_w = idle_frames[0].width
    sprite_h = idle_frames[0].height

    platforms = generate_platforms()
    first_plat = platforms[0]
    player = Player(
        rl.Vector2(first_plat.x + first_plat.width/2 - sprite_w/2, first_plat.y - sprite_h),
        3.0
    )

    gravity = 0.5
    velocity_y = 0
    goal = rl.Vector2(platforms[-1].x + 30, platforms[-1].y)

    camera = rl.Camera2D()
    camera.offset = (screen_width/2, screen_height/2)
    camera.zoom = 1.0

    game_finished = False
    player_hit = False
    falling_rocks = []
    rock_spawn_timer = 0
    frame_counter = 0

    while not rl.window_should_close():
        if not game_finished and not player_hit:
            moving = False

            # Yatay hareket
            if rl.is_key_down(rl.KEY_RIGHT):
                player.position.x += player.speed
                player.facing_right = True
                moving = True
            elif rl.is_key_down(rl.KEY_LEFT):
                player.position.x -= player.speed
                player.facing_right = False
                moving = True

            # Zıplama
            if rl.is_key_pressed(rl.KEY_SPACE) and player.can_jump:
                velocity_y = -10
                player.can_jump = False

            # Yerçekimi
            velocity_y += gravity
            player.position.y += velocity_y

            # Platform çarpışması
            player.can_jump = False
            player_rect = rl.Rectangle(player.position.x, player.position.y, sprite_w, sprite_h)
            for plat in platforms:
                ext_x = plat.x - COLLISION_TOLERANCE_X
                ext_y = plat.y - COLLISION_TOLERANCE_Y
                ext_w = plat.width + 2 * COLLISION_TOLERANCE_X
                ext_h = plat.height + COLLISION_TOLERANCE_Y
                extended_plat = rl.Rectangle(ext_x, ext_y, ext_w, ext_h)
                if velocity_y >= 0 and rl.check_collision_recs(player_rect, extended_plat):
                    player.position.y = plat.y - sprite_h
                    velocity_y = 0
                    player.can_jump = True
                    break

            # Hedef ve düşme kontrolü
            if player.position.y <= goal.y:
                game_finished = True
            if player.position.y > platforms[0].y + 200:
                player_hit = True

            # Meteor üretme
            rock_spawn_timer += 1
            if rock_spawn_timer > 60:
                if len(falling_rocks) < MAX_FALLING_ROCKS:
                    rx = player.position.x + random.randint(-HORIZONTAL_VARIANCE, HORIZONTAL_VARIANCE)
                    ry = player.position.y - 300
                    rock_rect = rl.Rectangle(rx, ry, meteor_width, meteor_height)
                    falling_rocks.append(FallingRock(rock_rect, random.randint(3, 6)))
                rock_spawn_timer = 0

            for rock in falling_rocks[:]:
                rock.rect.y += rock.speed
                if rl.check_collision_recs(player_rect, rock.rect):
                    player_hit = True
                if rock.rect.y > player.position.y + screen_height:
                    falling_rocks.remove(rock)

            # Animasyon güncelle
            frame_counter += 1
            if frame_counter >= FRAME_HOLD:
                frame_counter = 0
                if moving:
                    player.frame_index = (player.frame_index + 1) % len(walk_right_frames)
                else:
                    player.frame_index = (player.frame_index + 1) % len(idle_frames)

        camera.target = player.position

        # Çizim
        rl.begin_drawing()
        rl.clear_background(rl.SKYBLUE)
        rl.begin_mode2d(camera)

        for plat in platforms:
            rl.draw_rectangle_rec(plat, rl.DARKGRAY)

        rl.draw_circle_v(goal, 10, rl.RED)
        rl.draw_text("HEDEF", int(goal.x) - 20, int(goal.y) - 30, 10, rl.RED)

        # Meteorları çiz
        for rock in falling_rocks:
            rl.draw_texture(meteor_texture, int(rock.rect.x), int(rock.rect.y), rl.WHITE)

        # Oyuncu sprite çizimi
        if not player.can_jump:
            frame = idle_frames[player.frame_index % len(idle_frames)]
        else:
            if rl.is_key_down(rl.KEY_RIGHT):
                frame = walk_right_frames[player.frame_index % len(walk_right_frames)]
            elif rl.is_key_down(rl.KEY_LEFT):
                frame = walk_left_frames[player.frame_index % len(walk_left_frames)]
            else:
                frame = idle_frames[player.frame_index % len(idle_frames)]

        rl.draw_texture(frame, int(player.position.x), int(player.position.y), rl.WHITE)

        rl.end_mode2d()

        if player_hit:
            rl.draw_text("DÜŞTÜN veya METEORA ÇARPTIN! Oyun Bitti.", screen_width//2 - 200, screen_height//2, 20, rl.RED)
        elif game_finished:
            rl.draw_text("TEBRİKLER! Yukarı Ulaştın!", screen_width//2 - 150, screen_height//2, 20, rl.DARKGREEN)

        rl.end_drawing()

    # Belleği temizle
    for tex in idle_frames + walk_right_frames + walk_left_frames:
        rl.unload_texture(tex)
    rl.unload_texture(meteor_texture)
    rl.close_window()

if __name__ == "__main__":
    main()
