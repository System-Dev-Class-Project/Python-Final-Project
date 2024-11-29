import pygame
pygame.mixer.init()
new_game_sound = pygame.mixer.Sound('Python-Final-Project/Sound_Effects/new_game.mp3')
ticking_sound = pygame.mixer.Sound('Python-Final-Project/Sound_Effects/ticking.mp3')
victory_sound = pygame.mixer.Sound('Python-Final-Project/Sound_Effects/victory.mp3')
wrong_move_sound = pygame.mixer.Sound('Python-Final-Project/Sound_Effects/wrong_move.mp3')


def play_new_game():
    pygame.mixer.Channel(1).play(new_game_sound)

def play_ticking():
    pygame.mixer.Channel(2).play(ticking_sound, loops=-1)

def play_victory():
    pygame.mixer.stop()
    pygame.mixer.Channel(1).play(victory_sound)

def play_wrong_move():
    pygame.mixer.Channel(3).play(wrong_move_sound)
