import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd

import env.utils_env as utils_env
from agent.agent_BJ import agent_BJ

NB_SIMULATIONS = 999
HIT_SOFT_17 = True

def partie_BJ():
    historique_df = pd.DataFrame(columns=[
        'main_joueur',
        'main_dealer',
        'actions',
        'total_joueur',
        'total_dealer',
        'true_count',
        'résultat',
        'bj_joueur',
        'bj_dealer',
        'mise_initiale',
        'résultat_mise',
        'is_split',
        'is_surrender',
        'id_sabot'
    ])

    id_sabot = 0

    for _ in range(NB_SIMULATIONS):
        running_count = 0
        sabot = utils_env.creer_sabot()

        print("simu ", _)

        while len(sabot) > (utils_env.NUM_DECKS * 52 * 0.25):
            all_mains, main_dealer, running_count, sabot, mise_initiale = tour_BJ(sabot, running_count, historique_df)

            for main_joueur, action_stack in all_mains:
                historique_df = utils_env.fin_de_tour(
                    main_dealer,
                    main_joueur,
                    action_stack,
                    running_count,
                    sabot,
                    historique_df,
                    id_sabot,
                    mise_initiale
                )

        id_sabot += 1

    utils_env.df_stransform_n_save(historique_df)

def tour_BJ(sabot, running_count, historique_df):

    mise_initiale = agent_BJ(0, [], [], [], running_count, sabot)

    main_joueur, main_dealer, running_count = utils_env.distribution_initial(sabot, running_count)

    # Si le croupier a blackjack, on retourne une seule main
    if utils_env.blackjack(main_dealer):
        return [(main_joueur.copy(), [])], main_dealer, running_count, sabot, mise_initiale
    
    # Proposer surrender à l'agent
    if agent_BJ(2, [], main_joueur, main_dealer, running_count, sabot):
        return [(main_joueur.copy(), ["SU"])], main_dealer, running_count, sabot, mise_initiale

    # Jouer toutes les mains du joueur avec pile
    all_mains, running_count, sabot = gerer_toutes_les_mains(main_joueur.copy(), main_dealer, running_count, sabot)

    # Jouer le dealer
    main_dealer, running_count, sabot = jouer_main_dealer(main_dealer, running_count, sabot)

    return all_mains, main_dealer, running_count, sabot, mise_initiale

def jouer_main_dealer(main_dealer, running_count, sabot):
    while True:
        total = utils_env.valeur_main(main_dealer)
        is_soft_ = utils_env.is_soft(main_dealer)  # à créer si tu ne l’as pas encore

        if total > 17:
            break
        elif total == 17:
            if not HIT_SOFT_17:
                break
            elif not is_soft_:
                break

        # piocher
        card = sabot.pop()
        main_dealer.append(card)
        running_count = utils_env.update_running_count(card, running_count)

    return main_dealer, running_count, sabot

def jouer_une_main(main, main_dealer, action_stack, running_count, sabot):

    main = main.copy()
    action_stack = action_stack.copy()
    while True:
        if utils_env.valeur_main(main) > 21:
            break

        action = agent_BJ(4, action_stack, main, main_dealer, running_count, sabot)

        if action == 'H':
            action_stack.append('H')
            main, running_count, sabot = utils_env.hit_double_management(main, running_count, sabot)
        elif action == 'D':
            action_stack.append('D')
            main, running_count, sabot = utils_env.hit_double_management(main, running_count, sabot)
            break
        elif action == 'S':
            action_stack.append('S')
            break

    return main, action_stack, running_count, sabot

def gerer_toutes_les_mains(main_joueur, main_dealer, running_count, sabot):

    main_queue = [{
        "main": main_joueur.copy(),
        "action_stack": [],
        "security": False
    }]

    all_mains = []

    while main_queue:
        current = main_queue.pop(0)
        main = current["main"].copy()
        action_stack = current["action_stack"].copy()
        security = current["security"]

        if security or utils_env.valeur_main(main) > 21:
            all_mains.append((main.copy(), action_stack.copy()))
            continue

        if utils_env.is_pair(main) and agent_BJ(3, action_stack, main, main_dealer, running_count, sabot):
            action_stack.append("SP")

            main_1, main_2, running_count, sabot = utils_env.split_management(main.copy(), running_count, sabot)

            main_queue.append({
                "main": main_1.copy(),
                "action_stack": action_stack.copy(),
                "security": sorted([utils_env.valeur_carte(c) for c in main_1]) == [11, 11]
            })
            main_queue.append({
                "main": main_2.copy(),
                "action_stack": action_stack.copy(),
                "security": sorted([utils_env.valeur_carte(c) for c in main_2]) == [11, 11]
            })

            continue

        main, action_stack, running_count, sabot = jouer_une_main(main, main_dealer, action_stack, running_count, sabot)
        all_mains.append((main.copy(), action_stack.copy()))

    return all_mains, running_count, sabot

partie_BJ()