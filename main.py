import math
import random
from dataclasses import dataclass

import pygame


LARGURA_TELA = 960
ALTURA_TELA = 600
ALTURA_PAINEL = 54
ALTURA_VISAO = ALTURA_TELA - ALTURA_PAINEL
HORIZONTE = ALTURA_VISAO // 2
CAMPO_VISAO = math.pi / 3
QUANTIDADE_RAIOS = 320
DISTANCIA_MAXIMA_RAIO = 20
LIMITE_DEMONIOS_ATIVOS = 3
POSICAO_INICIAL_JOGADOR = (2.5, 2.5)
PONTOS_INIMIGOS = (
    (12.5, 2.5), (8.5, 2.5), (13.5, 5.5), (2.5, 9.5),
    (10.5, 9.5), (6.5, 11.5), (12.5, 10.5),
)
MAPA = (
    "################",
    "#..............#",
    "#..##......#...#",
    "#..............#",
    "#.....####.....#",
    "#..............#",
    "#..#.......##..#",
    "#..#..........#",
    "#......##......#",
    "#..............#",
    "#...##.........#",
    "#..............#",
    "################",
)


@dataclass
class Demonio:
    x: float
    y: float
    vida: int = 2
    tempo_ataque: float = 1.0


class Mundo:
    def __init__(self, blocos):
        self.blocos = blocos
        self.altura = len(blocos)
        self.largura = len(blocos[0])

    def eh_parede(self, x, y):
        bloco_x, bloco_y = int(x), int(y)
        return (
            bloco_x < 0
            or bloco_y < 0
            or bloco_x >= self.largura
            or bloco_y >= self.altura
            or self.blocos[bloco_y][bloco_x] == "#"
        )

    def tem_visao_direta(self, inicio, fim):
        diferenca_x = fim[0] - inicio[0]
        diferenca_y = fim[1] - inicio[1]
        distancia = math.hypot(diferenca_x, diferenca_y)
        quantidade_passos = max(1, int(distancia * 12))
        for passo in range(1, quantidade_passos):
            progresso = passo / quantidade_passos
            if self.eh_parede(inicio[0] + diferenca_x * progresso, inicio[1] + diferenca_y * progresso):
                return False
        return True

    def lancar_raio(self, origem, angulo_raio):
        direcao_x = math.cos(angulo_raio)
        direcao_y = math.sin(angulo_raio)
        distancia = 0.025
        while distancia < DISTANCIA_MAXIMA_RAIO:
            impacto_x = origem[0] + direcao_x * distancia
            impacto_y = origem[1] + direcao_y * distancia
            if self.eh_parede(impacto_x, impacto_y):
                return distancia, impacto_x, impacto_y
            distancia += 0.025
        return (
            DISTANCIA_MAXIMA_RAIO,
            origem[0] + direcao_x * DISTANCIA_MAXIMA_RAIO,
            origem[1] + direcao_y * DISTANCIA_MAXIMA_RAIO,
        )


class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("DOOM // INFERNO NA TERRA")
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.Font(None, 28)
        self.fonte_pequena = pygame.font.Font(None, 20)
        self.fonte_grande = pygame.font.Font(None, 54)
        self.mundo = Mundo(MAPA)
        self.reiniciar()

    def reiniciar(self):
        self.jogador_x, self.jogador_y = POSICAO_INICIAL_JOGADOR
        self.angulo = math.pi / 2
        self.vida = 100
        self.municao = 30
        self.abates = 0
        self.onda = 1
        self.inimigos_pendentes = 0
        self.clarao_disparo = 0.0
        self.clarao_dano = 0.0
        self.mensagem = ""
        self.tempo_mensagem = 0.0
        self.fim_de_jogo = False
        self.demonios = []
        self.iniciar_onda()

    @property
    def posicao_jogador(self):
        return self.jogador_x, self.jogador_y

    def criar_demonio(self):
        posicao_jogador = self.posicao_jogador
        pontos_disponiveis = [
            ponto
            for ponto in PONTOS_INIMIGOS
            if math.dist(ponto, posicao_jogador) >= 3.0
            and all(math.dist(ponto, (demonio.x, demonio.y)) >= 1.5 for demonio in self.demonios)
        ]
        if not pontos_disponiveis:
            pontos_disponiveis = [
                (x + 0.5, y + 0.5)
                for y, linha in enumerate(self.mundo.blocos)
                for x, bloco in enumerate(linha)
                if bloco != "#"
                and math.dist((x + 0.5, y + 0.5), posicao_jogador) >= 2.0
                and all(math.dist((x + 0.5, y + 0.5), (demonio.x, demonio.y)) >= 1.0
                        for demonio in self.demonios)
            ]
        if not pontos_disponiveis:
            return False
        x, y = random.choice(pontos_disponiveis)
        self.demonios.append(Demonio(x, y, tempo_ataque=random.uniform(1.5, 2.5)))
        return True

    def iniciar_onda(self):
        quantidade_inimigos = 3 + self.onda
        while len(self.demonios) < min(LIMITE_DEMONIOS_ATIVOS, quantidade_inimigos):
            quantidade_anterior = len(self.demonios)
            if not self.criar_demonio() or len(self.demonios) == quantidade_anterior:
                break
        self.inimigos_pendentes = quantidade_inimigos - len(self.demonios)
        self.exibir_mensagem(f"ONDA {self.onda}", 2.0)

    def avancar_onda(self):
        if self.demonios or self.inimigos_pendentes:
            return
        self.onda += 1
        self.vida = min(100, self.vida + 25)
        self.municao += 10
        self.iniciar_onda()

    def executar(self):
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        try:
            executando = True
            while executando:
                tempo_decorrido = min(self.relogio.tick(60) / 1000, 0.05)
                executando = self.tratar_eventos()
                self.atualizar(tempo_decorrido)
                self.desenhar()
        finally:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            pygame.quit()

    def tratar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                if self.fim_de_jogo and evento.key == pygame.K_r:
                    self.reiniciar()
                elif not self.fim_de_jogo and evento.key == pygame.K_SPACE:
                    self.atirar()
            if (
                not self.fim_de_jogo
                and evento.type == pygame.MOUSEBUTTONDOWN
                and evento.button == 1
            ):
                self.atirar()
        return True

    def atualizar(self, tempo_decorrido):
        self.clarao_disparo = max(0.0, self.clarao_disparo - tempo_decorrido)
        self.clarao_dano = max(0.0, self.clarao_dano - tempo_decorrido)
        self.tempo_mensagem = max(0.0, self.tempo_mensagem - tempo_decorrido)
        if self.fim_de_jogo:
            return
        self.atualizar_jogador(tempo_decorrido)
        self.atualizar_demonios(tempo_decorrido)

    def atualizar_jogador(self, tempo_decorrido):
        teclas = pygame.key.get_pressed()
        self.angulo += (teclas[pygame.K_RIGHT] - teclas[pygame.K_LEFT]) * 2.2 * tempo_decorrido
        movimento_mouse_x, _ = pygame.mouse.get_rel()
        self.angulo += movimento_mouse_x * 0.0025

        frente = (
            teclas[pygame.K_w] + teclas[pygame.K_UP]
            - teclas[pygame.K_s] - teclas[pygame.K_DOWN]
        )
        lateral = teclas[pygame.K_d] - teclas[pygame.K_a]
        tamanho_movimento = math.hypot(frente, lateral)
        if tamanho_movimento == 0:
            return

        frente /= tamanho_movimento
        lateral /= tamanho_movimento
        velocidade = 2.8 * tempo_decorrido
        deslocamento_x = (math.cos(self.angulo) * frente - math.sin(self.angulo) * lateral) * velocidade
        deslocamento_y = (math.sin(self.angulo) * frente + math.cos(self.angulo) * lateral) * velocidade
        self.mover_jogador(deslocamento_x, deslocamento_y)

    def mover_jogador(self, deslocamento_x, deslocamento_y):
        raio_jogador = 0.2
        inicio_x, inicio_y = self.posicao_jogador
        for fracao in (0.5, 1.0):
            proximo_x = inicio_x + deslocamento_x * fracao
            if not any(self.mundo.eh_parede(proximo_x, inicio_y + margem) for margem in (-raio_jogador, raio_jogador)):
                self.jogador_x = proximo_x
        for fracao in (0.5, 1.0):
            proximo_y = inicio_y + deslocamento_y * fracao
            if not any(self.mundo.eh_parede(self.jogador_x + margem, proximo_y) for margem in (-raio_jogador, raio_jogador)):
                self.jogador_y = proximo_y

    def atualizar_demonios(self, tempo_decorrido):
        for demonio in self.demonios:
            demonio.tempo_ataque -= tempo_decorrido
            diferenca_x = self.jogador_x - demonio.x
            diferenca_y = self.jogador_y - demonio.y
            distancia = math.hypot(diferenca_x, diferenca_y)
            if distancia > 0.85 and self.mundo.tem_visao_direta((demonio.x, demonio.y), self.posicao_jogador):
                passo = min(1.0, 0.5 * tempo_decorrido / distancia)
                deslocamento_x = diferenca_x * passo
                deslocamento_y = diferenca_y * passo
                if not self.mundo.eh_parede(demonio.x + deslocamento_x, demonio.y):
                    demonio.x += deslocamento_x
                if not self.mundo.eh_parede(demonio.x, demonio.y + deslocamento_y):
                    demonio.y += deslocamento_y
            if (
                distancia < 0.95
                and demonio.tempo_ataque <= 0
                and self.mundo.tem_visao_direta((demonio.x, demonio.y), self.posicao_jogador)
            ):
                self.vida -= 7
                self.clarao_dano = 0.2
                demonio.tempo_ataque = 1.5
                if self.vida <= 0:
                    self.fim_de_jogo = True
        self.avancar_onda()

    def atirar(self):
        if self.municao <= 0:
            self.exibir_mensagem("SEM MUNIÇÃO", 0.9)
            return
        self.municao -= 1
        self.clarao_disparo = 0.14
        alvo = self.encontrar_alvo()
        if alvo is None:
            return
        alvo.vida -= 1
        if alvo.vida <= 0:
            self.demonios.remove(alvo)
            self.abates += 1
            if self.inimigos_pendentes > 0 and len(self.demonios) < LIMITE_DEMONIOS_ATIVOS:
                if self.criar_demonio():
                    self.inimigos_pendentes -= 1
            self.exibir_mensagem("DEMÔNIO DERROTADO", 0.8)

    def encontrar_alvo(self):
        alvos = []
        for demonio in self.demonios:
            diferenca_x = demonio.x - self.jogador_x
            diferenca_y = demonio.y - self.jogador_y
            distancia = math.hypot(diferenca_x, diferenca_y)
            angulo_relativo = self.diferenca_angulos(math.atan2(diferenca_y, diferenca_x), self.angulo)
            if (
                abs(angulo_relativo) < 0.09
                and distancia < 9
                and self.mundo.tem_visao_direta(self.posicao_jogador, (demonio.x, demonio.y))
            ):
                alvos.append((distancia, demonio))
        return min(alvos, default=(0, None), key=lambda alvo: alvo[0])[1]

    @staticmethod
    def diferenca_angulos(primeiro, segundo):
        return (primeiro - segundo + math.pi) % (2 * math.pi) - math.pi

    def exibir_mensagem(self, mensagem, duracao):
        self.mensagem = mensagem
        self.tempo_mensagem = duracao

    def desenhar(self):
        self.desenhar_mundo()
        self.desenhar_demonios()
        self.desenhar_arma()
        self.desenhar_painel()
        self.desenhar_efeitos()
        pygame.display.flip()

    def desenhar_mundo(self):
        self.tela.fill((17, 15, 22))
        pygame.draw.rect(self.tela, (40, 37, 43), (0, 0, LARGURA_TELA, HORIZONTE))
        pygame.draw.rect(self.tela, (53, 37, 31), (0, HORIZONTE, LARGURA_TELA, ALTURA_VISAO - HORIZONTE))
        self.desenhar_grade_chao()
        self.profundidades_paredes = []
        largura_coluna = LARGURA_TELA / QUANTIDADE_RAIOS
        for indice_raio in range(QUANTIDADE_RAIOS):
            angulo_raio = self.angulo - CAMPO_VISAO / 2 + CAMPO_VISAO * indice_raio / QUANTIDADE_RAIOS
            distancia_raio, impacto_x, impacto_y = self.mundo.lancar_raio(self.posicao_jogador, angulo_raio)
            distancia_corrigida = max(0.08, distancia_raio * math.cos(angulo_raio - self.angulo))
            self.profundidades_paredes.append(distancia_corrigida)
            altura_parede = min(ALTURA_TELA * 1.5, ALTURA_TELA / distancia_corrigida)
            cor = self.cor_parede(impacto_x, impacto_y, distancia_corrigida)
            posicao_coluna_x = int(indice_raio * largura_coluna)
            pygame.draw.rect(
                self.tela,
                cor,
                (posicao_coluna_x, HORIZONTE - altura_parede / 2, math.ceil(largura_coluna) + 1, altura_parede),
            )

    def desenhar_grade_chao(self):
        for linha in range(1, 9):
            y = HORIZONTE + int((ALTURA_VISAO - HORIZONTE) * linha / 9)
            pygame.draw.line(self.tela, (59, 41, 34), (0, y), (LARGURA_TELA, y), 1)

    @staticmethod
    def cor_parede(impacto_x, impacto_y, distancia):
        borda = min(impacto_x % 1, 1 - impacto_x % 1, impacto_y % 1, 1 - impacto_y % 1)
        bloco = int(impacto_y if abs(impacto_x - round(impacto_x)) < abs(impacto_y - round(impacto_y)) else impacto_x)
        cor_base = (154, 67, 45) if bloco % 2 else (119, 51, 39)
        sombra = max(0.18, 1 - distancia / 13)
        if borda < 0.035:
            sombra *= 0.48
        return tuple(int(channel * sombra) for channel in cor_base)

    def desenhar_demonios(self):
        demonios_por_distancia = sorted(
            self.demonios,
            key=lambda demonio: math.dist(self.posicao_jogador, (demonio.x, demonio.y)),
            reverse=True,
        )
        for demonio in demonios_por_distancia:
            diferenca_x = demonio.x - self.jogador_x
            diferenca_y = demonio.y - self.jogador_y
            distancia = math.hypot(diferenca_x, diferenca_y)
            angulo_relativo = self.diferenca_angulos(math.atan2(diferenca_y, diferenca_x), self.angulo)
            if abs(angulo_relativo) > CAMPO_VISAO * 0.7 or distancia < 0.2:
                continue
            posicao_tela_x = LARGURA_TELA / 2 + math.tan(angulo_relativo) / math.tan(CAMPO_VISAO / 2) * LARGURA_TELA / 2
            indice_raio = max(0, min(QUANTIDADE_RAIOS - 1, int(posicao_tela_x / LARGURA_TELA * QUANTIDADE_RAIOS)))
            if distancia * math.cos(angulo_relativo) > self.profundidades_paredes[indice_raio] + 0.15:
                continue
            self.desenhar_demonio(demonio, posicao_tela_x, distancia)

    def desenhar_demonio(self, demonio, posicao_tela_x, distancia):
        tamanho = min(ALTURA_TELA * 0.85, ALTURA_TELA * 0.72 / distancia)
        centro_x = int(posicao_tela_x)
        base_y = int(HORIZONTE + tamanho * 0.43)
        largura_corpo = int(tamanho * 0.44)
        altura_corpo = int(tamanho * 0.72)
        cor_chifre = (77, 28, 25)
        cor_corpo = (145, 35, 29) if demonio.vida == 2 else (190, 54, 35)
        chifres = (
            (centro_x - largura_corpo // 3, base_y - altura_corpo),
            (centro_x - largura_corpo // 2, base_y - altura_corpo - tamanho * 0.22),
            (centro_x, base_y - altura_corpo + tamanho * 0.08),
        )
        pygame.draw.polygon(self.tela, cor_chifre, chifres)
        pygame.draw.polygon(
            self.tela,
            cor_chifre,
            [(2 * centro_x - x, y) for x, y in chifres],
        )
        pygame.draw.ellipse(
            self.tela,
            cor_corpo,
            (centro_x - largura_corpo // 2, base_y - altura_corpo, largura_corpo, int(tamanho * 0.3)),
        )
        pygame.draw.rect(
            self.tela,
            (105, 35, 29),
            (centro_x - largura_corpo // 2, base_y - int(altura_corpo * 0.67), largura_corpo, int(altura_corpo * 0.56)),
        )
        posicao_braco_y = base_y - int(altura_corpo * 0.63)
        altura_braco = int(altura_corpo * 0.42)
        for posicao_braco_x in (centro_x - largura_corpo * 0.72, centro_x + largura_corpo * 0.47):
            pygame.draw.rect(self.tela, cor_corpo, (posicao_braco_x, posicao_braco_y, largura_corpo * 0.25, altura_braco))
        posicao_perna_y = base_y - int(altura_corpo * 0.16)
        for posicao_perna_x in (centro_x - largura_corpo * 0.35, centro_x + largura_corpo * 0.08):
            pygame.draw.rect(self.tela, (55, 36, 33), (posicao_perna_x, posicao_perna_y, largura_corpo * 0.27, int(altura_corpo * 0.2)))
        raio_olho = max(2, int(tamanho * 0.025))
        posicao_olho_y = int(base_y - altura_corpo + tamanho * 0.14)
        distancia_olhos = int(tamanho * 0.09)
        for posicao_olho_x in (centro_x - distancia_olhos, centro_x + distancia_olhos):
            pygame.draw.circle(self.tela, (255, 209, 65), (posicao_olho_x, posicao_olho_y), raio_olho)

    def desenhar_arma(self):
        recuo = int(self.clarao_disparo * 22)
        altura_arma = ALTURA_TELA - ALTURA_PAINEL - 110 + recuo
        pygame.draw.polygon(
            self.tela,
            (39, 39, 42),
            [(LARGURA_TELA * 0.39, ALTURA_TELA), (LARGURA_TELA * 0.43, altura_arma + 28),
             (LARGURA_TELA * 0.57, altura_arma + 28), (LARGURA_TELA * 0.62, ALTURA_TELA)],
        )
        pygame.draw.rect(self.tela, (91, 87, 78), (LARGURA_TELA * 0.455, altura_arma, LARGURA_TELA * 0.09, 115))
        pygame.draw.rect(self.tela, (24, 24, 27), (LARGURA_TELA * 0.475, altura_arma - 35, LARGURA_TELA * 0.05, 75))
        pygame.draw.rect(self.tela, (130, 112, 83), (LARGURA_TELA * 0.435, altura_arma + 58, LARGURA_TELA * 0.13, 18))
        if self.clarao_disparo > 0:
            pygame.draw.polygon(
                self.tela,
                (255, 204, 78),
                [(LARGURA_TELA / 2, altura_arma - 85), (LARGURA_TELA / 2 - 28, altura_arma - 20),
                 (LARGURA_TELA / 2, altura_arma - 38), (LARGURA_TELA / 2 + 25, altura_arma - 18)],
            )

    def desenhar_painel(self):
        posicao_painel_y = ALTURA_TELA - ALTURA_PAINEL
        pygame.draw.rect(self.tela, (18, 18, 20), (0, posicao_painel_y, LARGURA_TELA, ALTURA_PAINEL))
        pygame.draw.line(self.tela, (131, 47, 37), (0, posicao_painel_y), (LARGURA_TELA, posicao_painel_y), 3)
        atributos = (
            ("DOOM", (196, 52, 40), 22),
            (f"VIDA  {max(0, self.vida):03}", (223, 215, 190), 155),
            (f"MUNIÇÃO  {self.municao:02}", (223, 215, 190), 390),
            (f"ABATES  {self.abates:02}", (223, 215, 190), 605),
            (f"ONDA  {self.onda:02}", (223, 215, 190), 790),
        )
        for texto, cor, posicao_x in atributos:
            self.tela.blit(self.fonte.render(texto, True, cor), (posicao_x, posicao_painel_y + 12))
        texto_ajuda = "WASD mover  |  Setas/mouse mirar  |  Espaço/clique atirar  |  Esc sair"
        instrucao = self.fonte_pequena.render(texto_ajuda, True, (156, 148, 134))
        self.tela.blit(instrucao, (LARGURA_TELA // 2 - instrucao.get_width() // 2, ALTURA_TELA - 19))
        self.desenhar_mira()

    def desenhar_mira(self):
        cor = (235, 219, 181)
        pygame.draw.line(self.tela, cor, (LARGURA_TELA // 2 - 9, HORIZONTE), (LARGURA_TELA // 2 - 3, HORIZONTE), 2)
        pygame.draw.line(self.tela, cor, (LARGURA_TELA // 2 + 3, HORIZONTE), (LARGURA_TELA // 2 + 9, HORIZONTE), 2)
        pygame.draw.line(self.tela, cor, (LARGURA_TELA // 2, HORIZONTE - 9), (LARGURA_TELA // 2, HORIZONTE - 3), 2)
        pygame.draw.line(self.tela, cor, (LARGURA_TELA // 2, HORIZONTE + 3), (LARGURA_TELA // 2, HORIZONTE + 9), 2)

    def desenhar_efeitos(self):
        if self.clarao_dano:
            sobreposicao = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            sobreposicao.fill((190, 15, 10, int(90 * self.clarao_dano / 0.2)))
            self.tela.blit(sobreposicao, (0, 0))
        if self.tempo_mensagem:
            mensagem_renderizada = self.fonte.render(self.mensagem, True, (255, 207, 101))
            self.tela.blit(mensagem_renderizada, mensagem_renderizada.get_rect(center=(LARGURA_TELA // 2, 80)))
        if self.fim_de_jogo:
            self.desenhar_fim_de_jogo()

    def desenhar_fim_de_jogo(self):
        sobreposicao = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        sobreposicao.fill((0, 0, 0, 185))
        self.tela.blit(sobreposicao, (0, 0))
        titulo = self.fonte_grande.render("VOCÊ MORREU", True, (205, 46, 36))
        instrucao = self.fonte.render("Pressione R para recomeçar   |   Esc para sair", True, (230, 218, 190))
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 18)))
        self.tela.blit(instrucao, instrucao.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 30)))


def iniciar():
    Jogo().executar()


if __name__ == "__main__":
    iniciar()


