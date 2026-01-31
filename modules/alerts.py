"""
Module de gestion des alertes pour l'application de gestion de stock.
"""

import pandas as pd
from typing import List, Dict
from enum import Enum


class AlertType(Enum):
    CRITICAL = "critical"       # Stock <= Stock de sécurité
    WARNING = "warning"         # Stock <= Stock de réapprovisionnement  
    OVERSTOCK = "overstock"     # Stock > Stock max


class AlertManager:
    """Gestionnaire des alertes de stock."""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_all_alerts(self) -> List[Dict]:
        """Récupère toutes les alertes actives."""
        products = self.data_manager.get_products()
        alerts = []
        
        for _, product in products.iterrows():
            product_alerts = self._check_product_alerts(product)
            alerts.extend(product_alerts)
        
        # Trier par priorité (critique > warning > overstock)
        priority_order = {AlertType.CRITICAL: 0, AlertType.WARNING: 1, AlertType.OVERSTOCK: 2}
        alerts.sort(key=lambda x: priority_order.get(x["type"], 99))
        
        return alerts
    
    def _check_product_alerts(self, product: pd.Series) -> List[Dict]:
        """Vérifie les alertes pour un produit donné."""
        alerts = []
        stock_actuel = product["Stock_Actuel"]
        stock_securite = product["Stock_Sécurité"]
        stock_reappro = product["Stock_Réappro"]
        stock_max = product["Stock_Max"]
        
        # Alerte critique : stock <= stock de sécurité
        if stock_actuel <= stock_securite:
            alerts.append({
                "type": AlertType.CRITICAL,
                "product_id": product["ID"],
                "product_name": product["Nom"],
                "message": f"⚠️ CRITIQUE: Stock très bas ({stock_actuel} {product['Unité']})",
                "details": f"Stock actuel: {stock_actuel} | Seuil sécurité: {stock_securite}",
                "color": "#FF4B4B",
                "icon": "🚨"
            })
        # Alerte réapprovisionnement : stock <= stock de réappro (mais > sécurité)
        elif stock_actuel <= stock_reappro:
            alerts.append({
                "type": AlertType.WARNING,
                "product_id": product["ID"],
                "product_name": product["Nom"],
                "message": f"⚡ RÉAPPRO: Commander bientôt ({stock_actuel} {product['Unité']})",
                "details": f"Stock actuel: {stock_actuel} | Seuil réappro: {stock_reappro}",
                "color": "#FFA500",
                "icon": "📦"
            })
        
        # Alerte surstock : stock > stock max
        if stock_actuel > stock_max:
            alerts.append({
                "type": AlertType.OVERSTOCK,
                "product_id": product["ID"],
                "product_name": product["Nom"],
                "message": f"📈 SURSTOCK: Capacité dépassée ({stock_actuel} {product['Unité']})",
                "details": f"Stock actuel: {stock_actuel} | Capacité max: {stock_max}",
                "color": "#1E90FF",
                "icon": "📊"
            })
        
        return alerts
    
    def get_alerts_count(self) -> Dict[str, int]:
        """Compte les alertes par type."""
        alerts = self.get_all_alerts()
        return {
            "critical": len([a for a in alerts if a["type"] == AlertType.CRITICAL]),
            "warning": len([a for a in alerts if a["type"] == AlertType.WARNING]),
            "overstock": len([a for a in alerts if a["type"] == AlertType.OVERSTOCK]),
            "total": len(alerts)
        }
    
    def get_product_status(self, product: pd.Series) -> Dict:
        """Retourne le statut d'un produit avec couleur."""
        stock_actuel = product["Stock_Actuel"]
        stock_securite = product["Stock_Sécurité"]
        stock_reappro = product["Stock_Réappro"]
        stock_max = product["Stock_Max"]
        
        if stock_actuel <= stock_securite:
            return {"status": "Critique", "color": "#FF4B4B", "emoji": "🔴"}
        elif stock_actuel <= stock_reappro:
            return {"status": "À réapprovisionner", "color": "#FFA500", "emoji": "🟠"}
        elif stock_actuel > stock_max:
            return {"status": "Surstock", "color": "#1E90FF", "emoji": "🔵"}
        else:
            return {"status": "Normal", "color": "#00C853", "emoji": "🟢"}
    
    def calculate_stock_health(self) -> float:
        """Calcule un score de santé du stock (0-100)."""
        products = self.data_manager.get_products()
        if products.empty:
            return 100.0
        
        total_score = 0
        for _, product in products.iterrows():
            stock_actuel = product["Stock_Actuel"]
            stock_securite = product["Stock_Sécurité"]
            stock_reappro = product["Stock_Réappro"]
            stock_max = product["Stock_Max"]
            
            # Score optimal entre réappro et max
            if stock_reappro < stock_actuel <= stock_max:
                total_score += 100
            elif stock_securite < stock_actuel <= stock_reappro:
                total_score += 60
            elif stock_actuel <= stock_securite:
                total_score += 20
            else:  # Surstock
                total_score += 70
        
        return total_score / len(products)
