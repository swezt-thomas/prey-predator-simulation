import pygame, sys, pymunk
import numpy as np
from math import dist, atan2, degrees, cos, sin
import pymunk.pygame_util
from pymunk.vec2d import Vec2d
import matplotlib.pyplot as plt

endurance = [800, 900]
timer = [0, 300]
reproduction_timer = [200, 360]
size = 7
starting_population = [150, 80]
predator_max = 160
prey_max = 200
class Species:
    '''classe espèce'''
    def __init__(self, name, vision_range, field_of_view):
        '''attribut un nom, un distance et un angle de champ de vision à cette espèce'''
        self.name = name
        self.vision_range = vision_range
        self.field_of_view = field_of_view

prey_species = Species('prey', vision_range=50, field_of_view=240) #création de l'espèce proie
predator_species = Species('predator', vision_range=100, field_of_view=70) #création de l'espèce prédatrice

class Creature:
    '''classe créature'''
    def __init__(self, species, position=None, direction_corr = None, factor = None, strategy = None):
        
        self.species = species #l'espèce de la créature
        self.body = pymunk.Body(1, 100, body_type=pymunk.Body.DYNAMIC) #création du body
        if position: #seulement si la créature est l'enfant d'une autre
            self.body.position = position
        else: #si c'est une créature de la première génération
            self.body.position = (np.random.uniform(0, 1000), np.random.uniform(0, 1000)) #placement aléatoire
        self.shape = pymunk.Circle(self.body, size) #shape de la créaature (rond)
        self.shape.color = (154, 244, 114, 100) if self.species == prey_species else (255, 51, 51, 100) #rouge = prédateur, vert = proie
        space.add(self.body, self.shape)
        self.endurance = np.random.uniform(endurance[0], endurance[1]) if self.species == prey_species else np.random.uniform(endurance[0], endurance[1]) #quand l'endurance arrive à 0, al créature meurt ou est immobilisée
        self.timer = np.random.randint(timer[0], timer[1]) if species == prey_species else 0
        self.reproduction_timer = np.random.randint(reproduction_timer[0], reproduction_timer[1]) if species == prey_species else 0
        self.hunger = 0 if species == predator_species else None
        self.body.angle = np.random.uniform(0, 2 * np.pi)
        if direction_corr != None and factor != None:
            self.direction_corr =np.random.normal(direction_corr, min(direction_corr, 2*np.pi - direction_corr))
            self.factor = np.random.normal(factor, min(factor, 1.5- factor))
            self.strategy =np.random.normal(strategy, min(strategy, 1-strategy))
        else:
            self.direction_corr = np.random.uniform(0, 2*np.pi)
            self.factor = np.random.uniform(0.5, 1.5)
            self.strategy = np.random.uniform(0, 1)
        
    def detect_neighbors(self, creatures):
        '''détecte les créatures de l'autre espèce dans le champ de vision'''
        neighbors = []
        for creature in creatures: #dans la liste des créatures de l'autre espèce
            distance = dist(self.body.position, creature.body.position)
            if distance < self.species.vision_range: #si c'est assez proche
                angle = atan2(creature.body.position[1] - self.body.position[1],
                              creature.body.position[0] - self.body.position[0])
                angle_difference = abs(degrees(angle - self.body.angle))
                if angle_difference%(2*np.pi) < self.species.field_of_view / 2: #si c'est dans le champ de vision
                    neighbors.append((creature, distance))
                if self.species == predator_species and distance < 2*size: #vérifie si on peut manger
                    creature.die()
                    predator_population[predator_population.index(self)].eat()
        return neighbors
        
    def update_movement(self, neighbors):
        '''calcul le prochaine position en fonction de la liste des voisins'''
        if neighbors:
            d = 0
            pos_x = 0
            pos_y = 0
            for i in range (len(neighbors)):
                d += neighbors[i][1]
                pos_x+= neighbors[i][0].body.position[0]
                pos_y+= neighbors[i][0].body.position[1]
            d/=len(neighbors)
            pos_x/= len(neighbors)
            pos_y/= len(neighbors)
            neighbor = ((pos_x, pos_y), d)
            angle_to_neighbor = atan2(neighbor[0][1] - self.body.position[1],
                                      neighbor[0][0] - self.body.position[0])
            self.body.angle = angle_to_neighbor + self.direction_corr
            closest_neighbor = min(neighbors, key=lambda x: x[1])
            angle_to_closest_neighbor = atan2(closest_neighbor[0].body.position[1] - self.body.position[1],
                                                closest_neighbor[0].body.position[0] - self.body.position[0])
            
        else:
            self.body.angle += np.random.uniform(-np.pi/6, np.pi/6)
            neighbor = False
        if self.timer == 0 and self.species == prey_species:
            self.timer = timer[0]
            self.endurance = endurance[0]
        #repositionnement de l'autre côpté de l'écran
        XY = self.body.position
        if XY[0] < 0 or XY[1] < 0 or XY[0] >= 1000 or XY[1] >= 1000:
            self.body.position = (XY[0]%1000, XY[1]%1000)
        if self.endurance > 0:
            if neighbor == False:
                distance = (self.factor)**(1/1.5)
            else:
                distance = (self.factor*(self.species.vision_range/(neighbor[1]*self.strategy + closest_neighbor[1] * (1-self.strategy))))**(1/1.5)
            force = Vec2d(distance, 0).rotated(self.body.angle)
            self.body.velocity = 30*force
            self.endurance -= (force[0]**2 + force[1]**2)**(1/2)
        else:
            self.timer -=1
    def update_behavior(self):
        if self.species == prey_species:
            self.reproduction_timer -= 1
            if self.reproduction_timer <= 0 and len(prey_population) < prey_max:
                self.reproduce()
                self.reproduction_timer = np.random.randint(reproduction_timer[0], reproduction_timer[1])
        else:
            if self.endurance <= 0:
                self.die()
                
    def reproduce(self):
        """Duplique la créature avec de légères mutations"""
        new_child = Creature(self.species, position=self.body.position+(-cos(self.body.angle)*2*size, -sin(self.body.angle)*2*size))
        if self.species == predator_species:
            self.hunger = 0
            predator_population.append(new_child)
            all_creatures.append(new_child)
        else:
            prey_population.append(new_child)
            all_creatures.append(new_child)
        
    def eat(self):
        self.endurance = endurance[0]
        if self.species == predator_species:
            self.hunger += 1
            if self.hunger >= 2:
                self.hunger = 0
                if len(predator_population) < predator_max:
                    return self.reproduce()

    def die(self):
        if self.species == predator_species:
            predator_population.pop(predator_population.index(self))
            all_creatures.pop(all_creatures.index(self))
        else:
            prey_population.pop(prey_population.index(self))
            all_creatures.pop(all_creatures.index(self))
        space.remove(self.shape, self.body)

def draw(screen, space, draw_options):
    scaled_image = pygame.transform.scale(image, (int(image.get_width() * zoom_factor), int(image.get_height() * zoom_factor)))  # Ajuste la taille du fond en fonction du zoom
    screen.fill((220, 220, 220))
    screen.blit(scaled_image, (0 - screen_offset[0], 0 - screen_offset[1]))  # Dessine le fond avec le décalage de l'écran appliqué
    for creature in all_creatures:
        scaled_position = creature.body.position * zoom_factor  # Ajuste la position en fonction du zoom
        scaled_size = size * zoom_factor  # Ajuste la taille en fonction du zoom
        creature_image = pygame.transform.rotozoom(proie if creature.species == prey_species else predateur, -creature.body.angle*180/np.pi, 0.28 * zoom_factor)  # Ajuste la taille de l'image en fonction du zoom
        screen.blit(creature_image, (scaled_position[0] - creature_image.get_width() / 2 - screen_offset[0], scaled_position[1] - creature_image.get_height() / 2 - screen_offset[1]))

def zoom(event):
    global zoom_factor, screen_offset, selected_creature
    
    # Position de la souris lors du zoom
    zoom_pos = pygame.mouse.get_pos()
    
    # Ancien décalage de l'écran
    old_screen_offset = screen_offset.copy()
    
    # Facteur de zoom en fonction de la molette de la souris
    if event.button == 4:  # Molette vers le haut
        zoom_factor *= 1 + scroll_speed  # Zoom avant
    elif event.button == 5:  # Molette vers le bas
        zoom_factor /= 1 + scroll_speed  # Zoom arrière
    
    # Calcul du nouveau décalage de l'écran pour garder le point fixe sous la souris
    new_offset = ((zoom_pos[0] - old_screen_offset[0]) * (1 / zoom_factor - 1),
                  (zoom_pos[1] - old_screen_offset[1]) * (1 / zoom_factor - 1))
    
    # Soustraction des décalages
    screen_offset = [old_screen_offset[0] - new_offset[0], old_screen_offset[1] - new_offset[1]]
    print(zoom)
    





def move_screen(keys):
    global screen_offset
    if keys[pygame.K_UP]:
        screen_offset = [screen_offset[0], screen_offset[1] - move_speed]
    if keys[pygame.K_DOWN]:
        screen_offset = [screen_offset[0], screen_offset[1] + move_speed]
    if keys[pygame.K_LEFT]:
        screen_offset = [screen_offset[0] - move_speed, screen_offset[1]]
    if keys[pygame.K_RIGHT]:
        screen_offset = [screen_offset[0] + move_speed, screen_offset[1]]
    print(screen_offset)


selected_creature = None

def update_camera_position():
    global screen_offset, zoom_factor, selected_creature
    
    if selected_creature:
        # Obtenez la position de la créature sélectionnée
        creature_position = selected_creature.body.position
        
        # Ajustez le zoom pour que la moitié de la hauteur affichée soit égale au champ de vision de la créature
        zoom_factor = 3
        
        # Calculez le nouveau décalage de l'écran pour centrer la créature
        screen_offset = [creature_position[0]*zoom_factor-(500) ,
                         creature_position[1]*zoom_factor-(500)] 


def select_creature(event):
    global selected_creature, zoom_factor, screen_offset
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche de la souris
        # Obtenir les coordonnées de la souris dans le monde du jeu
        mouse_x, mouse_y = event.pos
        world_mouse_x = (mouse_x + screen_offset[0]) / zoom_factor
        world_mouse_y = (mouse_y + screen_offset[1]) / zoom_factor
        
        # Trouver la créature la plus proche des coordonnées de la souris
        closest_creature = None
        min_distance = float('inf')
        for creature in all_creatures:
            distance = dist(creature.body.position, (world_mouse_x, world_mouse_y))
            if distance < min_distance:
                min_distance = distance
                closest_creature = creature
        
        # Sélectionner la créature la plus proche
        selected_creature = closest_creature


def deselect_creature(event):
    global selected_creature, zoom_factor, screen_offset
    selected_creature = None  # Désélectionne la créature
    zoom_factor = 1
    screen_offset = [0, 0]







# Avant la boucle principale
screen_offset = [0, 0]


pygame.init()
screen_width = 1000  # Largeur de l'écran
screen_height = 1000  # Hauteur de l'écran
screen = pygame.display.set_mode((1000, 1000), flags = pygame.SCALED)
clock = pygame.time.Clock()
space = pymunk.Space()
draw_options = pymunk.pygame_util.DrawOptions(screen) 
image = pygame.image.load('textures/BG.png')
proie = pygame.image.load('textures/proie.png')
predateur = pygame.image.load('textures/chasseur.png')

#Création de la population
prey_population = [Creature(prey_species) for _ in range(starting_population[0])]
predator_population = [Creature(predator_species) for _ in range(starting_population[1])]
L_chasseur = [len(predator_population)]
L_proie = [len(prey_population)]
L_t = [1]
k = 1  


zoom_factor = 1.0
scroll_speed = 0.1
scroll_threshold = 0.5
move_speed = 40


play = True
while play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Molette vers le haut
                zoom(event)
            elif event.button == 5:  # Molette vers le bas
                zoom(event)
            elif event.button ==1:
                select_creature(event)
            elif event.button==3:
                deselect_creature(event)
        elif event.type == pygame.KEYDOWN:
            move_screen(pygame.key.get_pressed())
    
    all_creatures = prey_population + predator_population
    for creature in all_creatures:
        if creature.species == prey_species:
            neighbors = creature.detect_neighbors(predator_population)
        else:
            neighbors = creature.detect_neighbors(prey_population)
        creature.update_movement(neighbors)
        creature.update_behavior()
    # Dans la boucle principale, après la sélection de la créature
    
    update_camera_position()
    draw(screen, space, draw_options)
    space.step(1 / 30)
    pygame.display.update()
    clock.tick(60)
    k+=1
    L_t.append(k)
    L_chasseur.append(len(predator_population))
    L_proie.append(len(prey_population))
    
plt.figure()
plt.plot(L_t, L_chasseur, label = 'chasseur')
plt.plot(L_t, L_proie, label = 'proie')
plt.legend()
plt.show()

pygame.quit()
sys.exit()

