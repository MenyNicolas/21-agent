import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
import random

import agent.utils_agent as utils_agent


def agent_BJ(id_action, action_stack, main_joueur, main_dealer, running_count, sabot):

    true_count = int(running_count / (len(sabot) / 52))

    # gestion de la mise initiale
    if(id_action == 0):
        if true_count >= 5:
            return 100
        if true_count >= 3:
            return 60
        if true_count >= 1:
            return 20
        return 10

    # gestion de l'assurance
    if(id_action == 1):
        if true_count > 2:
            return 'A'
        else:
            return 'N'

    # gestion du surrender
    if(id_action == 2):
        return utils_agent.surrender(main_joueur, main_dealer, true_count)
    
    # gestion des splits
    if(id_action == 3):
        return utils_agent.agent_split(main_joueur, main_dealer)
    
    # gestion stand hit double
    if(id_action == 4):
        return utils_agent.agent_stand_hit_double(main_joueur, main_dealer)
    
    return 0