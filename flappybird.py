import pygame
import os
import random

WIDTH = 500
HEIGHT = 800

# Carrega os sprites do jogo
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('sprites', 'red-pipe.png')))
FLOOR_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('sprites', 'base.png')))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('sprites', 'bg-night.png')))
BIRD_IMG = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('sprites', 'redbird-1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('sprites', 'redbird-2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('sprites', 'redbird-3.png'))),
]

pygame.font.init()
FONT = pygame.font.SysFont('comicsansms', 50)


class Bird:
    IMGS = BIRD_IMG
    # Variáveis para manipular animações do pássaro
    MAX_ROTATION = 25
    ROTATION_SPEED = 20
    TIME_FRAME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.speed = -10.5  # Movimentando o pássaro para cima
        self.time = 0
        self.height = self.y

    def move(self):
        # Faz o cálculo do movimento do pássaro
        self.time += 1  # Janela de tempo
        movement = 1.5 * (self.time ** 2) + self.speed * self.time

        # Restringe o movimento para não ultrapassar os limites de aceleramento
        if movement > 16:
            movement = 16
        elif movement < 0:
            movement -= 2

        # Faz o movimento do pássaro
        self.y += movement

        # Estabelece regras para o ângulo do pássaro durante o movimento
        if movement < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_SPEED

    def draw(self, screen):
        # Faz a seleção da animação do pássaro
        self.img_count += 1

        if self.img_count < self.TIME_FRAME:  # Asa pra cima
            self.img = self.IMGS[0]
        elif self.img_count < self.TIME_FRAME * 2:  # Asa pro meio
            self.img = self.IMGS[1]
        elif self.img_count < self.TIME_FRAME * 3:  # Asa pra baixo
            self.img = self.IMGS[2]
        elif self.img_count < self.TIME_FRAME * 4:  # Asa pro meio
            self.img = self.IMGS[1]
        elif self.img_count >= self.TIME_FRAME * 4 + 1:  # Volta pro início
            self.img = self.IMGS[0]
            self.img_count = 0

        # Em caso de o pássaro cair, as asas não batem
        if self.angle <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.TIME_FRAME * 2

        # Desenha as imagens na tela
        rotate_image = pygame.transform.rotate(self.img, self.angle)
        image_position = self.img.get_rect(topleft=(self.x, self.y)).center
        rect = rotate_image.get_rect(center=image_position)
        screen.blit(rotate_image, rect.topleft)

    # Máscara do pássaro para identificar sua colisão corretamente
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    DISTANCE = 200  # Distância entre pipes
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_position = 0
        self.base_position = 0
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMG, False, True)  # Inverte o pipe no eixo Y
        self.BASE_PIPE = PIPE_IMG
        self.passed = False
        self.define_height()

    # Altura dos pipes
    def define_height(self):
        self.height = random.randrange(50, 450)
        self.top_position = self.height - self.TOP_PIPE.get_height()
        self.base_position = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    # Desenha os pipes na tela
    def draw(self, screen):
        screen.blit(self.TOP_PIPE, (self.x, self.top_position))
        screen.blit(self.BASE_PIPE, (self.x, self.base_position))

    def colide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        base_mask = pygame.mask.from_surface(self.BASE_PIPE)

        # Distância do pássaro pro topo ou pra base do pipe
        top_distance = (self.x - bird.x, self.top_position - round(bird.y))
        base_distance = (self.x - bird.x, self.base_position - round(bird.y))

        # Checa se os pixels colidiram
        top = bird_mask.overlap(top_mask, top_distance)
        base = bird_mask.overlap(base_mask, base_distance)

        if top or base:
            return True
        else:
            return False


class Floor:
    SPEED = 5
    WIDTH = FLOOR_IMG.get_width()
    IMG = FLOOR_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED

        # Checa se o chão 1 ou o chão 2 sairam da tela
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # Desenha os pipes na tela
    def draw(self, screen):
        screen.blit(self.IMG, (self.x1, self.y))
        screen.blit(self.IMG, (self.x2, self.y))


def draw_screen(screen, birds, pipes, floor, points):
    screen.blit(BG_IMG, (0, 0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)

    text = FONT.render(f"Pontos: {points}", True, (255, 255, 255))
    screen.blit(text, (WIDTH - 10 - text.get_width(), 10))
    floor.draw(screen)
    pygame.display.update()


def main():
    birds = [Bird(230, 350)]
    floor = Floor(730)
    pipes = [Pipe(500)]
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    points = 0
    clock = pygame.time.Clock()

    running = True
    while running:
        # 30 fps
        clock.tick(30)
        for event in pygame.event.get():
            # Se fechar a tela, para o jogo
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                # Se pressionar a barra de espaço, pula
                if event.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()

        # Movimenta o chão e o pássaro
        for bird in birds:
            bird.move()
        floor.move()

        new_pipe = False
        remove_pipe = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                # Verifica se o pássaro bateu em algum cano e tira ele da lista
                if pipe.colide(bird):
                    birds.pop(i)
                # Se não passou do cano mas o X do pássaro é maior, cria outro cano
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    new_pipe = True

            pipe.move()

            # Verifica se cano já pode ser removido da tela
            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                remove_pipe.append(pipe)

        if new_pipe:
            points += 1
            pipes.append(Pipe(600))

        for pipe in remove_pipe:
            pipes.remove(pipe)

        # Exclui o pássaro caso ele vá além do limite de altura
        for i, bird in enumerate(birds):
            if (bird.y + bird.img.get_height()) > floor.y or bird.y < 0:
                birds.pop(i)

        draw_screen(screen, birds, pipes, floor, points)


if __name__ == '__main__':
    main()
