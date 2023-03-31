# importation des bibliotheques necessaires
import pygame
from pygame.locals import *

### CONSTANTES DU JEU ###

# Reglage des couleurs
CYAN = (0, 165, 255)
WHITE = (255, 255, 255)

# Reglage de l'image
image_accueil = 'image_accueil.png'
largeur_ecran = 900
hauteur_ecran = 675
display_surf = pygame.display.set_mode((largeur_ecran, hauteur_ecran)) #création de l'image avec la
                                                                        # meilleure résoltion
# reglage du mouvement de l'image
fps_clock = pygame.time.Clock()  # creation d'un objet pour suivre le temps
fps = 60  # Nombre d'image par seconde

# réglage du son

pygame.mixer.init()

songs = ['Arcanoide.mp3', 'arcanoid_villera.mp3']
son_rebond = pygame.mixer.Sound('rebond.mp3')
son_perdu = pygame.mixer.Sound('bip.wav')
son_gagne = pygame.mixer.Sound('win.mp3')

# son_jeu = pygame.mixer.music.load('son_jeu.mp3')

pygame.font.init()
font_obj = pygame.font.Font('freesansbold.ttf', 16)
text1 = font_obj.render('volume : augmenter : i ', True, WHITE)
text2 = font_obj.render('diminuer : d ', True, WHITE)
text3 = font_obj.render('arrêter : s ', True, WHITE)
text4 = font_obj.render('quitter : echap ', True, WHITE)
text1_rect, text2_rect, text3_rect, text4_rect = text1.get_rect(), text1.get_rect(), text1.get_rect(), text4.get_rect()
text1_rect.center = (largeur_ecran - 110, 20)  #On positionne les différents texte en fond d'écran
text2_rect.center = (largeur_ecran - 40, 40)  #On utilise la largeur de l'ecran pour les positionner bien à droite
text3_rect.center = (largeur_ecran - 40, 60)
text4_rect.center = (90, 20)


### CLASSES DU JEU ###

# Créarion de la super class game qui permettra d'afficher l'écran de jeu et de mettre le tout en mouvement
class Game():
    def __init__(self, ep_trait=10, speed=5):
        self.ep_trait = ep_trait
        self.speed = speed
        self.score = 0
        self.highscore = 0

        self.__init_ball()
        self.__init_paddle()
        # score :
        self.scoreboard = Scoreboard() #on inttroduit l'attribut scoreboard dans Game on pourra ensuite
                                        #changer le score avec la fonction update

    #initialisation de la balle
    def __init_ball(self):
        ball_x = int(largeur_ecran / 2)  # On place la balle au centre de l'écran initialement mais cela est anécdotique
        ball_y = int(hauteur_ecran / 2)
        self.ball = Ball(ball_x, ball_y, self.ep_trait,
                         self.ep_trait, self.speed)

    # initialisation du paddle
    def __init_paddle(self):
        self.paddles = {}  # dictionnaire contenant les paddles
        paddle_hauteur = 60
        paddle_largeur = self.ep_trait
        user_paddle_decalage = 7  # décalage par rapport au bord de l'image
        computer_paddle_decalage = largeur_ecran - paddle_largeur - user_paddle_decalage
        self.paddles['user'] = Paddle(user_paddle_decalage,
                                      paddle_largeur, paddle_hauteur)
        self.paddles['computer'] = AutoPaddle(computer_paddle_decalage,
                                              paddle_largeur, paddle_hauteur,
                                              self.ball, self.speed)

    ##création de l'arene du jeu
    def draw_arena(self):
        # couleur de l'arene
        display_surf.fill(CYAN)
        # contour de l'arene
        pygame.draw.rect(display_surf, WHITE,
                         ((0, 0), (largeur_ecran, hauteur_ecran)),
                         self.ep_trait)  # couleur position du contour taille du contour, epaisseur
        display_surf.blit(text1, text1_rect)  # Creation des zones de
        display_surf.blit(text2, text2_rect)  # de texte correpondant
        display_surf.blit(text3, text3_rect)  # au reglage du volume
        display_surf.blit(text4, text4_rect)  # sonore

    ##mise a jour du jeu pour créer le mouvement des différents élements (balle, paddles,scorreboard)
    # la plupart des fonctions appelées dans la fonction update seront définit plus tard
    def update(self):
        self.ball.move()
        self.paddles['computer'].move()

        if self.ball.hit_paddle(self.paddles['computer']):
            son_rebond.play()
            self.ball.bounce('x') #rebon symétrique à l'axe x
        elif self.ball.hit_paddle(self.paddles['user']):
            son_rebond.play()
            self.ball.bounce('x')
            self.score += 1
            if self.highscore <= self.score :
                self.highscore = self.score
        elif self.ball.pass_computer():
            self.score += 15           # si la balle passe l'ordinateur le joueur gagne +15 points
            son_gagne.play(0,100)
            if self.highscore <= self.score :
                self.highscore = self.score     #définition du highscore
        elif self.ball.pass_player():
            son_perdu.play(0, 100)
            self.score = 0

        self.draw_arena()
        self.ball.draw()
        self.paddles['user'].draw()
        self.paddles['computer'].draw()
        self.scoreboard.display(self.score,self.highscore)


class Paddle(pygame.sprite.Sprite):  # classe paddle hérité de la class de base
    # de pygame nommée Sprite qui se rapporte aux objets visible
    def __init__(self, x, lar, h):  # x = abscisse, lar = largeur, h = hauteur
        super().__init__()  #Paddle hérite l'initialisation de la class Sprite
        self.x = x
        self.lar = lar
        self.h = h
        self.y = int(hauteur_ecran / 2) # on ,initialise le paddle à peu près au centre de l'écran
        # Creation de rectangle avec pygame
        self.rect = pygame.Rect(self.x, self.y, self.lar, self.h)

    # Creation du paddle
    def draw(self):
        # limite haute du paddle
        if self.rect.bottom > hauteur_ecran - self.lar:
            self.rect.bottom = hauteur_ecran - self.lar
        # Limite bas du paddle
        elif self.rect.top < self.lar:
            self.rect.top = self.lar
        # Creation paddle
        pygame.draw.rect(display_surf, WHITE, self.rect)

    # deplacements du paddle
    def move(self, pos):
        self.rect.y = pos[1] #le 2ème élément de la liste pos correspond à la coordonnées selon y de la souris


class AutoPaddle(Paddle):
    def __init__(self, x, lar, h, ball, speed):
        super().__init__(x, lar, h)   #AutoPaddle hérite des attributs de Paddle (pour l'initialisation)
        self.ball = ball
        self.speed = speed

    def move(self, **kwargs):
        # si le ballon s'éloigne remettre le paddle au centre
        if self.ball.dir_x == -1:
            if self.rect.centery < int(hauteur_ecran / 2):
                self.rect.y += self.speed-0.5  #on prend une vitesse assez faible pour que le paddle reste
                                                #bien au centre et qu'il ne tremble pas au milieu à cause
                                                #de variations de position trop grande
            elif self.rect.centery > int(hauteur_ecran / 2):
                self.rect.y -= self.speed-0.5
        # si la balle est proche du paddle il doit suivre son mouvement
        elif self.ball.dir_x == 1:
            if self.rect.centery < self.ball.rect.centery:
                self.rect.y += self.speed-0.5  # On donne au paddle de l'ordinateur une vitesse plus faible
            else:                               # pour que l'ordinateur ne rattrape pas toutes les balles
                self.rect.y -= self.speed-0.5


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, lar, h, speed):
        super().__init__()
        self.x = x
        self.y = y
        self.lar = lar
        self.h = h
        self.speed = speed
        self.dir_x = 1  # 1 vers la gauche et -1 vers la droite
        self.dir_y = 1  # 1 vers le haut et -1 vers le bas

        self.rect = pygame.Rect(self.x, self.y, self.lar, self.h)

    # Creation de la balle
    def draw(self):
        pygame.draw.rect(display_surf, WHITE, self.rect)

    # deplacement de la balle
    def move(self):
        self.rect.x += (self.dir_x * self.speed)
        self.rect.y += (self.dir_y * self.speed)

        # rebond de la balle lors d'une collision
        if self.hit_plafond() or self.hit_sol():
            self.bounce('y')
        if self.hit_mur():
            self.bounce('x')

    def bounce(self, axe):
        if axe == 'x':
            self.dir_x *= -1 #On inverse la direction de la balle après un rebond en fonction du type de rebond
        elif axe == 'y':
            self.dir_y *= -1

#test si balle tape le paddle
    def hit_paddle(self, paddle):
        if pygame.sprite.collide_rect(self, paddle):
            return True
        else:
            return False

#test si la balle tape le mur
    def hit_mur(self):
        if ((self.dir_x == -1 and self.rect.left <= self.lar) or
                (self.dir_x == 1 and self.rect.right >= largeur_ecran - self.lar)):
            return True
        else:
            return False

#test si la balle tape le plafond
    def hit_plafond(self):
        if self.dir_y == -1 and self.rect.top <= self.lar:
            return True
        else:
            return False

#test si la balle tape le sol
    def hit_sol(self):
        if self.dir_y == 1 and self.rect.bottom >= hauteur_ecran - self.lar:
            return True
        else:
            return False

#test si la balle n'est pas rattrapé par le joueur
    def pass_player(self):
        if self.rect.left <= self.lar:
            return True
        else:
            return False

#test si la balle n'est pas rattrapé par l'ordinateur
    def pass_computer(self):
        if self.rect.right >= largeur_ecran - self.lar:
            return True
        else:
            return False

#xréation de la class scoreboard pour mettre le score et le meilleur score
class Scoreboard():
    def __init__(self, score=0, highscore=0, x=largeur_ecran / 2 - 50, y=10, font_size=20):
        self.score = score
        self.highscore = highscore
        self.x = x
        self.y = y
        self.font = pygame.font.Font('freesansbold.ttf', font_size) #ceux-ci seront placé dans le fond d'écran

    # Création du scoreboard
    def display(self, score, highscore):
        self.score = score
        self.highscore = highscore
        result_surf = self.font.render('Score = %s' % (self.score), True, WHITE) #zone de texte mise dans le fond d'écran
        best_result_surf = self.font.render('HighScore = %s' % (self.highscore), True, WHITE)
        rect = result_surf.get_rect() #positionnement au centre en haut de l'écran
        rect2 = best_result_surf.get_rect() #création d'un rectangle pour y mettre les zones de texte
        rect.topleft = (self.x, self.y) #placement de la zone de texte au centre de l'ecran
        rect2.topleft = (self.x -20, self.y +20)
        display_surf.blit(result_surf, rect) #affichage sur l'écran de jeu
        display_surf.blit(best_result_surf, rect2)


### FONCTION PRINCIPALE ###

def main():
    pygame.init()  # initialisation de pygame
    fenetre = pygame.display.set_mode((900, 675))
    pygame.display.set_caption('Pong game')  # creation du titre de la fenetre
    pygame.mouse.set_visible(False)  # 0 pour mettre le curseur invisible
    highscore_niveau1=0 #initialisation du highscore pour les différents niveaux
    highscore_niveau2=0
    vol=0.1
    continuer = 1
    game=Game(speed=5) #On implémente initialement Game avec une vitesse de 5 choisi aléatoirement, pour pouvoir
             #utiliser la classe game en dehors des boucle qui implémente Game pour les différentes vitesse de jeu
            #comme pour l'appel de la fonction update de Game à la fin du main


    while continuer:  # boucle principale
        # chargement son d'accueil
        pygame.mixer.music.load(songs[0])
        pygame.mixer.music.play(-1)

        # chargement de l'image d'acceuil
        accueil = pygame.image.load(image_accueil).convert()
        fenetre.blit(accueil, (0, 0))
        fenetre.blit(text4, text4_rect)
        pygame.display.flip()

        continuer_jeu = 1
        continuer_accueil = 1
        pygame.time.Clock().tick(30)
        while continuer_accueil:
            for event in pygame.event.get():  # On parcours la liste de tous les événements reçus
                # Si l'utilisateur quitte, on met les variables
                # de boucle à 0 pour n'en parcourir aucune et fermer

                if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.mixer.music.stop()


                    continuer_accueil = 0
                    continuer_jeu = 0
                    continuer = 0
                # Variable de choix du niveau
                elif event.type == KEYDOWN and (event.key == K_F1 or event.key == K_F2):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(songs[1])
                    pygame.mixer.music.play(-1)
                    vol = 0.1
                    pygame.mixer.music.set_volume(vol)
                    # Lancement du jeu
                    if event.key == K_F1:
                        continuer_accueil = 0  # On quitte l'accueil
                        game = Game(speed=4)
                        game.highscore = highscore_niveau1 #Au lancement d'un niveau on donne au highscore la dernière
                                            #valeur prise par celui-ci lors de la dernière partie pour le meme niveau


                    elif event.key == K_F2 :
                        continuer_accueil = 0  # On quitte l'accueil

                        game = Game(speed=7)
                        game.highscore = highscore_niveau2

            pygame.time.Clock().tick(30)
        while continuer_jeu:  # boucle principale
            for event in pygame.event.get():  # On parcours la liste de tous les événements reçus
                if event.type == QUIT:  # Si un de ces événements est de type QUIT
                    pygame.mixer.music.stop()

                    continuer = 0  # On arrête la boucle
                    continuer_jeu = 0
                # commande du paddle user avec pygame
                elif event.type == MOUSEMOTION:
                    game.paddles['user'].move(event.pos)
                    # si l'on appui sur echap au revient au menu
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        continuer_jeu = 0
                    if event.key == K_s:
                        vol *= 0
                        pygame.mixer.music.set_volume(vol)
                    if event.key == K_d:
                        vol -= 0.02
                        pygame.mixer.music.set_volume(vol)
                    if event.key == K_i:
                        vol += 0.02
                        pygame.mixer.music.set_volume(vol)
                if game.speed == 4 :
                    highscore_niveau1 = game.highscore #On stock la valeur du highscore en fonction du niveau
                elif game.speed == 7 :
                    highscore_niveau2 = game.highscore
                    #le high score est propre à un niveau et ne se perd pas à part si on quitte totalement le jeu

            game.update()
            pygame.display.update()  # rafaraichissement de la fenetre
            fps_clock.tick(fps)  #on met une fréquence d'image qui permet d'avoir une vitesse de jeu convenable


if __name__ == '__main__':
    main()