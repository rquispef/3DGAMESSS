import pygame
import random
import math

# Inicializar Pygame
pygame.init()

# Constantes
GAME_WIDTH = 800
GAME_HEIGHT = 600
PLAYER_SIZE = 50
ZOMBIE_SIZE = 40
BULLET_SIZE = 10
INITIAL_HEALTH = 100
MAX_HEALTH = 100  # Nueva constante para límite máximo de salud
MAX_AMMO = 30
ZOMBIE_DAMAGE = 20
PLAYER_SPEED = 5
BULLET_SPEED = 10
RELOAD_TIME = 1000  # 1 segundo en milisegundos
ZOMBIE_SPAWN_RATE = 2000  # Tiempo en milisegundos para generar zombies
ZOMBIE_SPEED = 1  # Velocidad de los zombies (más lento)
ZOMBIE_SPACING = 60  # Distancia mínima entre zombies

# Colores
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Clase del jugador
class Player:
    def __init__(self):
        self.rect = pygame.Rect(GAME_WIDTH // 2, GAME_HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
        self.health = INITIAL_HEALTH
        self.ammo = MAX_AMMO
        self.score = 0
        self.direction = (0, 0)  # Dirección de disparo (dx, dy)
        self.reloading = False
        self.reload_start_time = 0
        self.current_wave = 1  # Nueva variable para seguimiento de oleadas

# Clase de los zombies
class Zombie:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, GAME_WIDTH - ZOMBIE_SIZE), random.randint(0, GAME_HEIGHT - ZOMBIE_SIZE), ZOMBIE_SIZE, ZOMBIE_SIZE)

# Clase de las balas
class Bullet:
    def __init__(self, x, y, dx, dy):
        self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
        self.dx = dx
        self.dy = dy

# Función para generar zombies con espaciado
def spawn_zombies(zombie_list, count, existing_zombies=None):
    if existing_zombies is None:
        existing_zombies = zombie_list

    attempts = 0
    max_attempts = 100  # Prevenir bucle infinito
    while len(zombie_list) < count and attempts < max_attempts:
        new_zombie = Zombie()
        
        # Verificar espaciado con zombies existentes
        too_close = False
        for zombie in existing_zombies:
            distance = math.sqrt(
                (new_zombie.rect.centerx - zombie.rect.centerx)**2 + 
                (new_zombie.rect.centery - zombie.rect.centery)**2
            )
            if distance < ZOMBIE_SPACING:
                too_close = True
                break
        
        # Verificar espaciado con el jugador
        if not too_close:
            zombie_list.append(new_zombie)
        
        attempts += 1

# Función para mostrar la pantalla de inicio
def show_start_screen(screen):
    font = pygame.font.Font(None, 74)
    title_text = font.render("Zombie Shooter", True, WHITE)
    start_text = font.render("Press Enter to Start", True, WHITE)
    
    screen.fill(BLACK)
    screen.blit(title_text, (GAME_WIDTH // 2 - title_text.get_width() // 2, GAME_HEIGHT // 2 - 50))
    screen.blit(start_text, (GAME_WIDTH // 2 - start_text.get_width() // 2, GAME_HEIGHT // 2 + 20))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False

# Función para mostrar la pantalla de Game Over
def show_game_over_screen(screen):
    font = pygame.font.Font(None, 74)
    game_over_text = font.render("Game Over", True, RED)
    retry_text = font.render("Press R to Retry", True, WHITE)
    
    screen.fill(BLACK)
    screen.blit(game_over_text, (GAME_WIDTH // 2 - game_over_text.get_width() // 2, GAME_HEIGHT // 2 - 50))
    screen.blit(retry_text, (GAME_WIDTH // 2 - retry_text.get_width() // 2, GAME_HEIGHT // 2 + 20))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False

# Función principal del juego
def main():
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    pygame.display.set_caption("Zombie Shooter")
    clock = pygame.time.Clock()

    player = Player()
    zombies = []
    bullets = []
    game_over = False
    last_spawn_time = pygame.time.get_ticks()
    last_space_press_time = 0  # Para controlar el tiempo entre disparos

    # Generar zombies iniciales
    spawn_zombies(zombies, 4)

    show_start_screen(screen)  # Mostrar pantalla de inicio

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        keys = pygame.key.get_pressed()
        if not game_over:
            # Movimiento del jugador
            player.direction = (0, 0)  # Reiniciar dirección
            if keys[pygame.K_w]:
                player.rect.y -= PLAYER_SPEED
                player.direction = (0, -1)
            if keys[pygame.K_s]:
                player.rect.y += PLAYER_SPEED
                player.direction = (0, 1)
            if keys[pygame.K_a]:
                player.rect.x -= PLAYER_SPEED
                player.direction = (-1, 0)
            if keys[pygame.K_d]:
                player.rect.x += PLAYER_SPEED
                player.direction = (1, 0)

            # Disparar con la barra espaciadora (una bala por toque)
            if keys[pygame.K_SPACE]:
                current_time = pygame.time.get_ticks()
                if current_time - last_space_press_time >= 200:  # Esperar 200 ms entre disparos
                    if player.ammo > 0:
                        dx = BULLET_SPEED * player.direction[0]
                        dy = BULLET_SPEED * player.direction[1]
                        bullets.append(Bullet(player.rect.centerx, player.rect.centery, dx, dy))
                        player.ammo -= 1
                        last_space_press_time = current_time

            # Disparar en todas las direcciones con 'E'
            if keys[pygame.K_e]:
                current_time = pygame.time.get_ticks()
                if current_time - last_spawn_time >= 500 and player.ammo >= 10:  # Cooldown de 500ms
                    for angle in range(0, 360, 36):  # Disparar en 10 direcciones
                        angle_rad = math.radians(angle)
                        dx = BULLET_SPEED * math.cos(angle_rad)
                        dy = BULLET_SPEED * math.sin(angle_rad)
                        bullets.append(Bullet(player.rect.centerx, player.rect.centery, dx, dy))
                    player.ammo -= 10
                    last_spawn_time = current_time

            # Recargar con la tecla 'R'
            if keys[pygame.K_r] and not player.reloading:
                player.reloading = True
                player.reload_start_time = pygame.time.get_ticks()

            # Mover balas
            for bullet in bullets[:]:
                bullet.rect.x += bullet.dx
                bullet.rect.y += bullet.dy

            # Colisiones de balas con zombies
            for bullet in bullets[:]:
                for zombie in zombies[:]:
                    if bullet.rect.colliderect(zombie.rect):
                        bullets.remove(bullet)
                        zombies.remove(zombie)
                        player.score += 10
                        # Regenerar salud al matar un zombie
                        player.health = min(player.health + 2, MAX_HEALTH)
                        break

            # Verificar si la oleada está completada
            if len(zombies) == 0:
                # Aumentar el número de zombies en cada oleada
                spawn_count = 4 * player.current_wave
                spawn_zombies(zombies, spawn_count)
                player.current_wave += 1

            # Mover zombies y verificar colisiones con el jugador
            for zombie in zombies[:]:
                if zombie.rect.x < player.rect.x:
                    zombie.rect.x += ZOMBIE_SPEED
                if zombie.rect.x > player.rect.x:
                    zombie.rect.x -= ZOMBIE_SPEED
                if zombie.rect.y < player.rect.y:
                    zombie.rect.y += ZOMBIE_SPEED
                if zombie.rect.y > player.rect.y:
                    zombie.rect.y -= ZOMBIE_SPEED

                # Verificar colisión con el jugador
                if zombie.rect.colliderect(player.rect):
                    player.health -= ZOMBIE_DAMAGE
                    zombies.remove(zombie)  # Eliminar el zombie al tocar al jugador
                    if player.health <= 0:
                        game_over = True

            # Verificar si el jugador está recargando
            current_time = pygame.time.get_ticks()
            if player.reloading:
                if current_time - player.reload_start_time >= RELOAD_TIME:
                    player.ammo = MAX_AMMO
                    player.reloading = False

            # Verificar si el juego ha terminado
            if game_over:
                show_game_over_screen(screen)  # Mostrar pantalla de Game Over
                player = Player()  # Reiniciar jugador
                zombies.clear()  # Limpiar zombies
                bullets.clear()  # Limpiar balas
                spawn_zombies(zombies, 4)  # Generar zombies iniciales
                game_over = False  # Reiniciar estado de juego

        # Dibujar en la pantalla
        screen.fill(BLACK)
        pygame.draw.rect(screen, BLUE, player.rect)  # Dibujar jugador
        for zombie in zombies:
            pygame.draw.rect(screen, GREEN, zombie.rect)  # Dibujar zombies
        for bullet in bullets:
            pygame.draw.rect(screen, YELLOW, bullet.rect)  # Dibujar balas

        # Mostrar salud y puntaje
        font = pygame.font.Font(None, 36)
        health_text = font.render(f'Health: {player.health}', True, WHITE)
        score_text = font.render(f'Score: {player.score}', True, WHITE)
        ammo_text = font.render(f'Ammo: {player.ammo}', True, WHITE)
        wave_text = font.render(f'Wave: {player.current_wave}', True, WHITE)
        screen.blit(health_text, (10, 10))
        screen.blit(score_text, (10, 40))
        screen.blit(ammo_text, (10, 70))
        screen.blit(wave_text, (10, 100))

        # Verificar si el juego ha terminado
        if game_over:
            game_over_text = font.render('Game Over', True, RED)
            screen.blit(game_over_text, (GAME_WIDTH // 2 - game_over_text.get_width() // 2, GAME_HEIGHT // 2 - 20))

        pygame.display.flip()
        clock.tick(60)

# Ejecutar el juego
if __name__ == "__main__":
    main()