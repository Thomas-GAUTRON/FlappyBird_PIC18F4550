import matplotlib
matplotlib.use('TkAgg')

import numpy as np
import matplotlib.pyplot as plt

# Ratios h/w à tester (hauteur du trou / taille de l’oiseau)
ratios = np.array([1.0, 1.2, 1.5, 2, 3, 4, 6])

# Paramètres de simulation
target_score = 30          # score cible : 30 tuyaux franchis
max_score = 50             # score maximum possible
base_learning_rate = 0.0004  # vitesse d'apprentissage de base

# Fonction simulant l'évolution du score moyen au fil des générations
def simulate_learning_curve(ratio):
    generations = np.arange(0, 3000, 50)
    learning_rate = base_learning_rate * ratio**1.4
    score = max_score / (1 + np.exp(-learning_rate * (generations - 1000)))
    noise = np.random.normal(0, 0.8, len(score))
    return generations, np.clip(score + noise, 0, max_score)

# Calcul du temps (en générations) pour atteindre le score cible
learning_times = []
for ratio in ratios:
    generations, scores = simulate_learning_curve(ratio)
    # Trouver la première génération où le score dépasse 30
    try:
        gen_to_reach_target = generations[np.where(scores >= target_score)[0][0]]
    except IndexError:
        gen_to_reach_target = np.nan  # si jamais le score n'est pas atteint
    learning_times.append(gen_to_reach_target)

# --- Figure 1 : évolution du score moyen ---
plt.figure(figsize=(9,5))
for ratio in ratios:
    generations, scores = simulate_learning_curve(ratio)
    plt.plot(generations, scores, label=f"h/w = {ratio}")
plt.title("Évolution du score moyen selon le rapport h/w")
plt.xlabel("Générations")
plt.ylabel("Score moyen (tuyaux franchis)")
plt.legend(title="Rapport h/w")
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Figure 2 : temps moyen pour atteindre le score cible ---
plt.figure(figsize=(7,5))
plt.plot(ratios, learning_times, 'o-', color='orange', linewidth=2, markersize=8)
plt.title(f"Temps moyen pour atteindre un score de {target_score} selon h/w")
plt.xlabel("Rapport h/w (hauteur du trou / taille de l'oiseau)")
plt.ylabel("Nombre de générations nécessaires")
plt.grid(True)
plt.tight_layout()
plt.show()
