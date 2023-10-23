import tkinter as tk
import random
import time
from threading import Lock


# Liste des couleurs utilisées pour les tétriminos
COULEURS = ['gray', 'lightgreen', 'pink', 'blue', 'orange', 'purple']


# Classe principale pour le jeu Tetris
class Tetris():
    HAUTEUR_CHAMP = 20
    LARGEUR_CHAMP = 20
    SCORE_PAR_LIGNES_ELIMINEES = (0, 40, 100, 300, 1200)
    # Les différentes formes des pièces de Tetris
    TETROMINOS = [
        [(0, 0), (0, 1), (1, 0), (1,1)], # O
        [(0, 0), (0, 1), (1, 1), (2,1)], # L
        [(0, 1), (1, 1), (2, 1), (2,0)], # J 
        [(0, 1), (1, 0), (1, 1), (2,0)], # Z
        [(0, 1), (1, 0), (1, 1), (2,1)], # T
        [(0, 0), (1, 0), (1, 1), (2,1)], # S
        [(0, 1), (1, 1), (2, 1), (3,1)], # I
    ]
    
    def __init__(self):
        # Initialisation du champ de jeu
        self.champ = [[0 for c in range(Tetris.LARGEUR_CHAMP)] for r in range(Tetris.HAUTEUR_CHAMP)]
        self.score = 0
        self.niveau = 0
        self.total_lignes_eliminees = 0
        self.partie_terminee = False
        self.verrou_deplacement = Lock()
        self.tetromino_index = 0
        self.reinitialiser_tetromino()
        self.reinitialiser_tetromino()

    def reinitialiser_tetromino(self):
        # Sélection aléatoire d'un nouveau Tetris et couleur
        self.tetromino = random.choice(Tetris.TETROMINOS)[:]
        self.couleur_tetromino = random.randint(1, len(COULEURS) - 1)
        self.decalage_tetromino = [-2, random.randint(0, Tetris.LARGEUR_CHAMP - 1)]
        self.tetromino_index = random.randint(0, len(Tetris.TETROMINOS) - 1)


    def afficher_prochain_tetromino(self):
        # Effacer l'affichage du prochain Tetris
        self.next_piece_canvas.delete("all")
        # Affichage du prochain Tetris
        next_tetromino = Tetris.TETROMINOS[self.tetromino_index]
        next_color = self.couleur_tetromino
        for (r, c) in next_tetromino:
            x, y = c * 30 + 15, r * 30 + 15
            self.next_piece_canvas.create_rectangle(x, y, x + 30, y + 30, fill=COULEURS[next_color])


    #Pour obtenir des coordonnées des pièces
    def obtenir_coordonnees_tetromino(self):
        return [(r + self.decalage_tetromino[0], c + self.decalage_tetromino[1]) for (r, c) in self.tetromino]

    #Pour l'élimination des lignes complètes et met à jour le score et le niveau
    def appliquer_tetromino(self):
        for (r, c) in self.obtenir_coordonnees_tetromino():
            self.champ[r][c] = self.couleur_tetromino

        nouveau_champ = [ligne for ligne in self.champ if any(carreau == 0 for carreau in ligne)]
        lignes_eliminees = len(self.champ) - len(nouveau_champ)
        self.total_lignes_eliminees += lignes_eliminees
        self.champ = [[0] * Tetris.LARGEUR_CHAMP for x in range(lignes_eliminees)] + nouveau_champ
        self.score += Tetris.SCORE_PAR_LIGNES_ELIMINEES[lignes_eliminees] * (self.niveau + 1)
        self.niveau = self.total_lignes_eliminees // 10
        self.reinitialiser_tetromino()

    #Pour obtenir la couleur
    def obtenir_couleur(self, r, c):
        return self.couleur_tetromino if (r, c) in self.obtenir_coordonnees_tetromino() else self.champ[r][c]

    # vérifie si la case à la position (r, c) est libre
    def est_case_libre(self, r, c):
        return r < Tetris.HAUTEUR_CHAMP and 0 <= c < Tetris.LARGEUR_CHAMP and (r < 0 or self.champ[r][c] == 0)

    #permet de déplacer le tétrimino en spécifiant le décalage (dr, dc).
    def deplacer(self, dr, dc):
        with self.verrou_deplacement:
            if self.partie_terminee:
                return

            if all(self.est_case_libre(r + dr, c + dc) for (r, c) in self.obtenir_coordonnees_tetromino()):
                self.decalage_tetromino = [self.decalage_tetromino[0] + dr, self.decalage_tetromino[1] + dc]
            elif dr == 1 and dc == 0:
                self.partie_terminee = any(r < 0 for (r, c) in self.obtenir_coordonnees_tetromino())
                if not self.partie_terminee:
                    self.appliquer_tetromino()

    # Faire pivoter
    def faire_pivoter(self):
        with self.verrou_deplacement:
            if self.partie_terminee:
                self.__init__()
                return

            ys = [r for (r, c) in self.tetromino]
            xs = [c for (r, c) in self.tetromino]
            taille = max(max(ys) - min(ys), max(xs)-min(xs))
            tetromino_fait_pivoter = [(c, taille - r) for (r, c) in self.tetromino]
            decalage_wallkick = self.decalage_tetromino[:]
            coordonnees_tetromino = [(r + decalage_wallkick[0], c + decalage_wallkick[1]) for (r, c) in tetromino_fait_pivoter]
            min_x = min(c for r, c in coordonnees_tetromino)
            max_x = max(c for r, c in coordonnees_tetromino)
            max_y = max(r for r, c in coordonnees_tetromino)
            decalage_wallkick[1] -= min(0, min_x)
            decalage_wallkick[1] += min(0, Tetris.LARGEUR_CHAMP - (1 + max_x))
            decalage_wallkick[0] += min(0, Tetris.HAUTEUR_CHAMP - (1 + max_y))

            coordonnees_tetromino = [(r + decalage_wallkick[0], c + decalage_wallkick[1]) for (r, c) in tetromino_fait_pivoter]
            if all(self.est_case_libre(r, c) for (r, c) in coordonnees_tetromino):
                self.tetromino, self.decalage_tetromino = tetromino_fait_pivoter, decalage_wallkick

# Classe pour l'interface utilisateur
class Application(tk.Frame):
    # Initialisation de l'application
    def __init__(self, master=None):
        super().__init__(master)
        self.tetris = Tetris()
        self.pack()
        self.creer_widgets()
        self.actualiser_horloge()

    #Méthode pour mettre à jour le jeu à intervalles réguliers
    def actualiser_horloge(self):
        self.tetris.deplacer(1, 0)
        self.afficher_prochain_tetromino()
        self.update()
        self.master.after(int(1000*(0.66**self.tetris.niveau)), self.actualiser_horloge)

    # méthode pour créer les interfaces du jeu de Tetris
    def creer_widgets(self):
        TAILLE_PIECE = 30

        self.canvas = tk.Canvas(self, height=TAILLE_PIECE * self.tetris.HAUTEUR_CHAMP,
                                width=TAILLE_PIECE * self.tetris.LARGEUR_CHAMP, bg="black", bd=0)
        self.canvas.bind('<Left>', lambda _: (self.tetris.deplacer(0, -1), self.update()))
        self.canvas.bind('<Right>', lambda _: (self.tetris.deplacer(0, 1), self.update()))
        self.canvas.bind('<Down>', lambda _: (self.tetris.deplacer(1, 0), self.update()))
        self.canvas.bind('<Up>', lambda _: (self.tetris.faire_pivoter(), self.update()))
        self.canvas.focus_set()
        self.rectangles = [
            self.canvas.create_rectangle(c * TAILLE_PIECE, r * TAILLE_PIECE, (c + 1) * TAILLE_PIECE, (r + 1) * TAILLE_PIECE)
            for r in range(self.tetris.HAUTEUR_CHAMP) for c in range(self.tetris.LARGEUR_CHAMP)
        ]
        self.canvas.pack(side="left")

        self.next_piece_canvas = tk.Canvas(self, width=5 * TAILLE_PIECE, height=5 * TAILLE_PIECE, bg="black", bd=0)
        self.next_piece_canvas.pack(side="left")

        self.message_statut = tk.Label(self, anchor='w', width=11, font=("Courier", 24))
        self.message_statut.pack(side="bottom")
        self.message_partie_terminee = tk.Label(self, anchor='w', width=11, font=("Courier", 24), fg='red')
        self.message_partie_terminee.pack(side="bottom")
        self.message_name = tk.Label(self, anchor='w', width=11, font=("Courier", 24))
        self.message_name.pack(side="top")

    #permet d'affihcer la prochaine pièce de Tétris
    def afficher_prochain_tetromino(self):
        self.next_piece_canvas.delete("all")
        next_tetromino = self.tetris.TETROMINOS[self.tetris.tetromino_index]
        next_color = self.tetris.couleur_tetromino
        for (r, c) in next_tetromino:
            x, y = c * 30 + 15, r * 30 + 15
            self.next_piece_canvas.create_rectangle(x, y, x + 30, y + 30, fill=COULEURS[next_color])

    #Méthode pour mettre à jour l'affichage du champ de jeu
    def update(self):
        for i, _id in enumerate(self.rectangles):
            numero_couleur = self.tetris.obtenir_couleur(i // self.tetris.LARGEUR_CHAMP, i % self.tetris.LARGEUR_CHAMP)
            self.canvas.itemconfig(_id, fill=COULEURS[numero_couleur])

        self.message_statut['text'] = "Score : {}\nNiveau : {}".format(self.tetris.score, self.tetris.niveau)
        self.message_partie_terminee['text'] = "PARTIE TERMINEE.\nAppuyez sur UP\npour réinitialiser" if self.tetris.partie_terminee else ""
        self.message_name['text'] = "Bienvenue"


root = tk.Tk()
app = Application(master=root)
app.mainloop()
