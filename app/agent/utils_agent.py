import numpy as np
import pandas as pd
import random
import joblib
import os

from agent.agent_model_handler import StrategyModelHandler

model_handler = StrategyModelHandler()

def valeur_carte(carte):
    if carte in ['J', 'Q', 'K']:
        return 10
    else:
        return carte

def valeur_main(main_joueur):
    total = 0
    ace_count = 0

    for card in main_joueur:
        v = valeur_carte(card)
        if v == 11:
            ace_count += 1
        total += v

    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1

    return total

def is_soft(main):
    total = sum(valeur_carte(c) for c in main)
    ace_count = main.count(11)

    adjusted_aces = ace_count
    while total > 21 and adjusted_aces > 0:
        total -= 10
        adjusted_aces -= 1

    return adjusted_aces > 0

def surrender(main_joueur, main_dealer, true_count):
    carte_dealer = main_joueur[0]
    is_hard = not is_soft(main_joueur)
    if carte_dealer in [9, 10, 11]:
        if is_hard and (np.sum(main_joueur) == 16):
            return 1
        elif is_hard and ((np.sum(main_joueur) == 15) and (carte_dealer == 10)):
            return 1
        else:
            return 0
    else:
        return 0

def agent_split(main_joueur, main_dealer, is_DAS = True):

    total_joueur = valeur_main(main_joueur)
    carte_dealer = valeur_carte(main_dealer[0])

    if(main_joueur == [11, 11]):
        total_joueur = 22

    action = model_handler.predict("split", [total_joueur, carte_dealer])

    if action == "Y/N":
        if is_DAS:
            action = "Y"
        else:
            action = "N"

    if action == "Y":
        return True
    else:
        return False

def agent_stand_hit_double(main_joueur, main_dealer):

    double_possible = (len(main_joueur) == 2)
    is_soft_ = is_soft(main_joueur)

    total_joueur = valeur_main(main_joueur)
    carte_dealer = valeur_carte(main_dealer[0])

    action = model_handler.predict("stand_hit_double", [total_joueur, carte_dealer, is_soft_])

    if double_possible:
        if action == "Ds":
            action = 'D'
    else:
        if action == "Ds":
            action = 'S'
        if action == 'D':
            action = 'H'
        
    return action