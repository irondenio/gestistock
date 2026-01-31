"""
Module de gestion des données Excel pour l'application de gestion de stock.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from openpyxl import Workbook, load_workbook
import os


class DataManager:
    """Gestionnaire des données Excel pour le stock."""
    
    def __init__(self, data_path: str = None):
        if data_path is None:
            data_path = Path(__file__).parent.parent / "data" / "stock_data.xlsx"
        self.data_path = Path(data_path)
        self._ensure_data_file_exists()
    
    def _ensure_data_file_exists(self):
        """Crée le fichier Excel s'il n'existe pas."""
        if not self.data_path.exists():
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            self._create_initial_excel()
    
    def _create_initial_excel(self):
        """Crée le fichier Excel initial avec les feuilles nécessaires."""
        wb = Workbook()
        
        # Feuille Produits
        ws_produits = wb.active
        ws_produits.title = "Produits"
        ws_produits.append([
            "ID", "Nom", "Catégorie", "Stock_Actuel", 
            "Stock_Sécurité", "Stock_Réappro", "Stock_Max", "Unité"
        ])
        # Données exemple
        ws_produits.append([1, "Ciment", "Matériaux", 100, 20, 50, 500, "Sacs"])
        ws_produits.append([2, "Fer à béton", "Métaux", 50, 10, 30, 200, "Barres"])
        ws_produits.append([3, "Peinture blanche", "Peintures", 25, 5, 15, 100, "Bidons"])
        
        # Feuille Entrées
        ws_entrees = wb.create_sheet("Entrées")
        ws_entrees.append(["ID", "Date", "Produit_ID", "Quantité", "Fournisseur", "Notes"])
        ws_entrees.append([1, datetime.now().strftime("%Y-%m-%d"), 1, 50, "Fournisseur A", "Livraison initiale"])
        
        # Feuille Sorties
        ws_sorties = wb.create_sheet("Sorties")
        ws_sorties.append(["ID", "Date", "Produit_ID", "Quantité", "Destination", "Notes"])
        ws_sorties.append([1, datetime.now().strftime("%Y-%m-%d"), 1, 10, "Chantier X", "Première sortie"])
        
        wb.save(self.data_path)
    
    # ============ PRODUITS ============
    
    def get_products(self) -> pd.DataFrame:
        """Récupère tous les produits."""
        try:
            df = pd.read_excel(self.data_path, sheet_name="Produits")
            return df
        except Exception:
            return pd.DataFrame(columns=[
                "ID", "Nom", "Catégorie", "Stock_Actuel", 
                "Stock_Sécurité", "Stock_Réappro", "Stock_Max", "Unité"
            ])
    
    def get_product_by_id(self, product_id: int) -> pd.Series:
        """Récupère un produit par son ID."""
        df = self.get_products()
        product = df[df["ID"] == product_id]
        if not product.empty:
            return product.iloc[0]
        return None
    
    def add_product(self, nom: str, categorie: str, stock_actuel: int,
                    stock_securite: int, stock_reappro: int, stock_max: int, unite: str):
        """Ajoute un nouveau produit."""
        df = self.get_products()
        new_id = df["ID"].max() + 1 if not df.empty else 1
        
        new_product = pd.DataFrame([{
            "ID": new_id,
            "Nom": nom,
            "Catégorie": categorie,
            "Stock_Actuel": stock_actuel,
            "Stock_Sécurité": stock_securite,
            "Stock_Réappro": stock_reappro,
            "Stock_Max": stock_max,
            "Unité": unite
        }])
        
        df = pd.concat([df, new_product], ignore_index=True)
        self._save_products(df)
        return new_id
    
    def update_product(self, product_id: int, **kwargs):
        """Met à jour un produit existant."""
        df = self.get_products()
        idx = df[df["ID"] == product_id].index
        if not idx.empty:
            for key, value in kwargs.items():
                if key in df.columns:
                    df.loc[idx[0], key] = value
            self._save_products(df)
            return True
        return False
    
    def delete_product(self, product_id: int):
        """Supprime un produit."""
        df = self.get_products()
        df = df[df["ID"] != product_id]
        self._save_products(df)
    
    def _save_products(self, df: pd.DataFrame):
        """Sauvegarde les produits dans Excel."""
        with pd.ExcelWriter(self.data_path, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Produits", index=False)
    
    def update_stock(self, product_id: int, quantity_change: int):
        """Met à jour le stock d'un produit."""
        df = self.get_products()
        idx = df[df["ID"] == product_id].index
        if not idx.empty:
            current_stock = df.loc[idx[0], "Stock_Actuel"]
            new_stock = current_stock + quantity_change
            df.loc[idx[0], "Stock_Actuel"] = max(0, new_stock)
            self._save_products(df)
            return True
        return False
    
    # ============ ENTRÉES ============
    
    def get_entries(self) -> pd.DataFrame:
        """Récupère toutes les entrées."""
        try:
            df = pd.read_excel(self.data_path, sheet_name="Entrées")
            return df
        except Exception:
            return pd.DataFrame(columns=["ID", "Date", "Produit_ID", "Quantité", "Fournisseur", "Notes"])
    
    def add_entry(self, produit_id: int, quantite: int, fournisseur: str, notes: str = ""):
        """Ajoute une nouvelle entrée et met à jour le stock."""
        df = self.get_entries()
        new_id = df["ID"].max() + 1 if not df.empty and not pd.isna(df["ID"].max()) else 1
        
        new_entry = pd.DataFrame([{
            "ID": int(new_id),
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Produit_ID": produit_id,
            "Quantité": quantite,
            "Fournisseur": fournisseur,
            "Notes": notes
        }])
        
        df = pd.concat([df, new_entry], ignore_index=True)
        self._save_entries(df)
        
        # Mettre à jour le stock
        self.update_stock(produit_id, quantite)
        return new_id
    
    def _save_entries(self, df: pd.DataFrame):
        """Sauvegarde les entrées dans Excel."""
        with pd.ExcelWriter(self.data_path, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Entrées", index=False)
    
    # ============ SORTIES ============
    
    def get_exits(self) -> pd.DataFrame:
        """Récupère toutes les sorties."""
        try:
            df = pd.read_excel(self.data_path, sheet_name="Sorties")
            return df
        except Exception:
            return pd.DataFrame(columns=["ID", "Date", "Produit_ID", "Quantité", "Destination", "Notes"])
    
    def add_exit(self, produit_id: int, quantite: int, destination: str, notes: str = ""):
        """Ajoute une nouvelle sortie et met à jour le stock."""
        # Vérifier le stock disponible
        product = self.get_product_by_id(produit_id)
        if product is None:
            return None, "Produit non trouvé"
        
        if product["Stock_Actuel"] < quantite:
            return None, f"Stock insuffisant. Disponible: {product['Stock_Actuel']}"
        
        df = self.get_exits()
        new_id = df["ID"].max() + 1 if not df.empty and not pd.isna(df["ID"].max()) else 1
        
        new_exit = pd.DataFrame([{
            "ID": int(new_id),
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Produit_ID": produit_id,
            "Quantité": quantite,
            "Destination": destination,
            "Notes": notes
        }])
        
        df = pd.concat([df, new_exit], ignore_index=True)
        self._save_exits(df)
        
        # Mettre à jour le stock
        self.update_stock(produit_id, -quantite)
        return new_id, None
    
    def _save_exits(self, df: pd.DataFrame):
        """Sauvegarde les sorties dans Excel."""
        with pd.ExcelWriter(self.data_path, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Sorties", index=False)
    
    # ============ STATISTIQUES ============
    
    def get_stock_summary(self) -> dict:
        """Récupère un résumé des stocks."""
        products = self.get_products()
        entries = self.get_entries()
        exits = self.get_exits()
        
        return {
            "total_produits": len(products),
            "total_entrees": entries["Quantité"].sum() if not entries.empty else 0,
            "total_sorties": exits["Quantité"].sum() if not exits.empty else 0,
            "valeur_stock": products["Stock_Actuel"].sum() if not products.empty else 0
        }
