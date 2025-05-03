import raylibpy as rl
import random

class Player:
    def __init__(self, position, speed):
        self.position = position
        self.speed = speed
        self.can_jump = False
        self.direction = "idle"    # "idle", "right", "left"
        # Her animasyon için ayrı frame index
        self.idle_idx = 0
        self.right_idx = 0
        self.left_idx = 0
        # Tüm animasyonlar için ortak frame counter / speed
        self.frame_counter = 0
        self.frame_speed = 8
        self.is_jumping = False

MAX_FALLING_ROCKS = 50

def main():
    screen_width = 800
    screen_height = 450

    rl.init_window(screen_width, screen_height, "Zıplama Oyunu - Astronot ve Düşen Taşlar")
    rl.set_target_fps(60)

    # Animasyon sprite'ları
    idle_frames      = [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(0, 9)]
    walk_right_frames= [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(9, 16)]
    walk_left_frames = [rl.load_texture(f"assets/spriteSplitted/{i}_Astronaut Player.png") for i in range(25, 31)]

    camera = rl.Camera2D()
    camera.offset = (screen_width/2, screen_height/2)
    camera.zoom   = 1.0

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
    player_hit    = False

    falling_rocks = []
    rock_spawn_timer = 0

    while not rl.window_should_close():
        # 1) INPUT + PHYSICS + LOGIC
        if not game_finished and not player_hit:
            # yönü başta idle yap
            player.direction = "idle"

            # yatay hareket
            if rl.is_key_down(rl.KEY_RIGHT):
                player.position.x += player.speed
                player.direction = "right"
            elif rl.is_key_down(rl.KEY_LEFT):
                player.position.x -= player.speed
                player.direction = "left"

            # zıplama
            if rl.is_key_pressed(rl.KEY_SPACE) and player.can_jump:
                velocity_y = -10
                player.can_jump = False
                player.is_jumping = True

            # yerçekimi
            velocity_y += gravity
            player.position.y += velocity_y

            # platform çarpışması
            player.can_jump = False
            for plat in platforms:
                pr = rl.Rectangle(player.position.x, player.position.y, idle_frames[0].width, idle_frames[0].height)
                if rl.check_collision_recs(pr, plat) and velocity_y >= 0:
                    player.position.y = plat.y - idle_frames[0].height
                    velocity_y = 0
                    player.can_jump = True
                    player.is_jumping = False

            # hedef kontrolü
            if player.position.y <= goal.y:         game_finished = True
            if player.position.y > goal.y + 600:    player_hit    = True

            # taş spawn
            rock_spawn_timer += 1
            if rock_spawn_timer > 180 and len(falling_rocks) < MAX_FALLING_ROCKS:
                rx = player.position.x + random.randint(-200,200)
                ry = player.position.y - 300
                falling_rocks.append((rl.Rectangle(rx, ry, 20, 20), random.randint(2,5)))
                rock_spawn_timer = 0

            # taş güncelle
            for rock, speed in falling_rocks[:]:
                rock.y += speed
                pr = rl.Rectangle(player.position.x, player.position.y, idle_frames[0].width, idle_frames[0].height)
                if rl.check_collision_recs(pr, rock):
                    player_hit = True
                if rock.y > player.position.y + screen_height:
                    falling_rocks.remove((rock, speed))

            # animasyon güncelle
            player.frame_counter += 1
            if player.frame_counter >= (60 // player.frame_speed):
                player.frame_counter = 0
                if player.direction == "right":
                    player.right_idx = (player.right_idx + 1) % len(walk_right_frames)
                elif player.direction == "left":
                    player.left_idx = (player.left_idx + 1) % len(walk_left_frames)
                else:
                    player.idle_idx = (player.idle_idx + 1) % len(idle_frames)

        # 2) Kamera
        camera.target = player.position

        # 3) Çizim
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        rl.begin_mode2d(camera)

        # karakteri çiz
        if   player.direction == "right":
            tex = walk_right_frames[player.right_idx]
        elif player.direction == "left":
            tex = walk_left_frames[player.left_idx]
        else:
            tex = idle_frames[player.idle_idx]

        rl.draw_texture(tex, int(player.position.x), int(player.position.y), rl.WHITE)

        # platformlar
        for plat in platforms:
            rl.draw_rectangle_rec(plat, rl.DARKGRAY)

        # hedef
        rl.draw_circle_v(goal, 10, rl.RED)
        rl.draw_text("Hedef Nokta", int(goal.x)-30, int(goal.y)-30, 10, rl.RED)

        # düşen taşlar
        for rock, _ in falling_rocks:
            rl.draw_rectangle_rec(rock, rl.MAROON)

        rl.end_mode2d()

        # oyun sonu mesajları
        if player_hit:
            rl.draw_text("TAŞA ÇARPTIN veya DÜŞTÜN! Oyun Bitti.", screen_width//2-150, screen_height//2, 20, rl.RED)
        elif game_finished:
            rl.draw_text("TEBRİKLER! Yukarı ulaştın!", screen_width//2-150, screen_height//2, 20, rl.DARKGREEN)

        rl.end_drawing()

    # temizleme
    for tex in idle_frames + walk_right_frames + walk_left_frames:
        rl.unload_texture(tex)
    rl.close_window()

if __name__ == "__main__":
    main()
