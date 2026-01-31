# Application de Gestion de Stock

Application de gestion de stock avec Python, Streamlit et Excel.

## Installation

1. Installer les dépendances :

```bash
pip install -r requirements.txt
```

1. Lancer l'application :

```bash
streamlit run app.py
```

## Fonctionnalités

- 📦 Gestion des produits (ajout, modification, suppression)
- 📥 Enregistrement des entrées de stock
- 📤 Enregistrement des sorties de stock
- 🚨 Alertes automatiques (stock de sécurité, réapprovisionnement, surstock)
- 📊 Tableau de bord avec graphiques

## Structure des données

Les données sont stockées dans `data/stock_data.xlsx` avec 3 feuilles :

- **Produits** : liste des produits et leurs seuils
- **Entrées** : historique des entrées
- **Sorties** : historique des sorties
