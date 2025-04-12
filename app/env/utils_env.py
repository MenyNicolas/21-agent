import random
import numpy as np
import pandas as pd

# === CONFIGURATION SIMULATEUR ===
NUM_DECKS = 6

def is_soft(main):
    total = sum(valeur_carte(c) for c in main)
    ace_count = main.count(11)

    adjusted_aces = ace_count
    while total > 21 and adjusted_aces > 0:
        total -= 10
        adjusted_aces -= 1

    return adjusted_aces > 0

def creer_sabot(num_decks=NUM_DECKS):
    deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 11] * 4 * num_decks
    random.shuffle(deck)
    return deck


def update_running_count(card, count):
    if card in [2, 3, 4, 5, 6]:
        return count + 1
    elif card in [10, 'J', 'Q', 'K', 11]:
        return count - 1
    else:
        return count


def distribution_initial(deck, running_count):
    player = []
    dealer = []
    for _ in range(2):
        for hand in [player, dealer]:
            card = deck.pop()
            hand.append(card)
            running_count = update_running_count(card, running_count)
    return player.copy(), dealer.copy(), running_count

def blackjack(main):
    return len(main) == 2 and valeur_main(main) == 21

def is_pair(main_joueur):
    return len(main_joueur) == 2 and main_joueur[0] == main_joueur[1]

def split_management(main_joueur, running_count, sabot):
    carte1 = sabot.pop()
    carte2 = sabot.pop()

    main_1 = [main_joueur[0], carte1]
    main_2 = [main_joueur[1], carte2]

    running_count = update_running_count(carte1, running_count)
    running_count = update_running_count(carte2, running_count)

    return main_1.copy(), main_2.copy(), running_count, sabot

def hit_double_management(main_joueur, running_count, sabot):
    carte = sabot.pop()
    main_joueur.append(carte)
    running_count = update_running_count(carte, running_count)

    return main_joueur.copy(), running_count, sabot

def valeur_carte(carte):
    return 10 if carte in ['J', 'Q', 'K'] else carte

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


def resultat(main_dealer, main_joueur, is_doubled, is_split, is_surrender):

    if is_surrender:
        return -0.5

    mise = 2 if is_doubled else 1

    joueur_bj = blackjack(main_joueur)
    dealer_bj = blackjack(main_dealer)

    # ✅ Cas 1 : Blackjack joueur
    if joueur_bj:
        if dealer_bj:
            return 0  # Égalité
        else:
            return mise if is_split else 1.5 * mise  # BJ après split = 1:1

    # ✅ Cas 2 : Dealer a blackjack
    if dealer_bj:
        return -mise

    # ✅ Cas 3 : Busts ou comparaison de valeurs
    total_joueur = valeur_main(main_joueur)
    total_dealer = valeur_main(main_dealer)

    if total_joueur > 21:
        return -mise
    elif total_dealer > 21:
        return mise
    elif total_joueur > total_dealer:
        return mise
    elif total_joueur == total_dealer:
        return 0
    else:
        return -mise


def fin_de_tour(main_dealer, main_joueur, action_stack, running_count, sabot, historique_df, id_sabot, mise_initiale):
    is_doubled = action_stack[-1] == 'D' if action_stack else False
    is_split = action_stack[0] == 'SP' if action_stack else False
    is_surrender = action_stack[0] == 'SU' if action_stack else False

    true_count = (running_count / (len(sabot) / 52)) if len(sabot) > 0 else 0
    resultat_main = resultat(main_dealer, main_joueur, is_doubled, is_split, is_surrender)

    total_joueur = valeur_main(main_joueur)
    total_dealer = valeur_main(main_dealer)

    series_resultat = pd.Series({
        'main_joueur': main_joueur.copy(),
        'main_dealer': main_dealer.copy(),
        'actions': action_stack.copy(),
        'total_joueur': total_joueur,
        'total_dealer': total_dealer,
        'true_count': true_count,
        'résultat': resultat_main,
        'bj_joueur': blackjack(main_joueur),
        'bj_dealer': blackjack(main_dealer),
        'mise_initiale': mise_initiale,
        'résultat_mise': resultat_main * mise_initiale,
        'is_split': is_split,
        'is_surrender': is_surrender,
        'id_sabot': id_sabot
    })

    return pd.concat([historique_df, series_resultat.to_frame().T], ignore_index=True)

def df_stransform_n_save(df):

    # Création des nouvelles colonnes pour main_joueur
    for i in range(1, 7):
        df[f'main_joueur_{i}'] = df['main_joueur'].apply(lambda x: x[i-1] if len(x) >= i else None)

    # Création des nouvelles colonnes pour main_dealer
    for i in range(1, 7):
        df[f'main_dealer_{i}'] = df['main_dealer'].apply(lambda x: x[i-1] if len(x) >= i else None)

    # Création des nouvelles colonnes pour actions
    for i in range(1, 7):
        df[f'actions_{i}'] = df['actions'].apply(lambda x: x[i-1] if len(x) >= i else None)
    
    df.to_csv('historique_BJ.csv', index=False)