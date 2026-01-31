"""
Application de Gestion de Stock
Python + Streamlit + Excel
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Ajouter le chemin des modules
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_manager import DataManager
from modules.alerts import AlertManager, AlertType

# Configuration de la page
st.set_page_config(
    page_title="Gestion de Stock",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.image("assets/copyrights.png", width=75)

st.title("📦 Application de Gestion de Stock")

st.subheader("Auteur: Anthony DJOUMBISSI, adjoumbissi@gmail.com")

# Styles CSS personnalisés
st.markdown("""
<style>
    /* Variables de couleurs */
    :root {
        --primary-color: #6C63FF;
        --success-color: #00C853;
        --warning-color: #FFA500;
        --danger-color: #FF4B4B;
        --info-color: #1E90FF;
    }
    
    /* Cards métriques */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Alertes personnalisées */
    .alert-critical {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #F2994A 0%, #F2C94C 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 0.5rem;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Status badges */
    .status-critical { color: #FF4B4B; font-weight: bold; }
    .status-warning { color: #FFA500; font-weight: bold; }
    .status-ok { color: #00C853; font-weight: bold; }
    .status-overstock { color: #1E90FF; font-weight: bold; }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Form styling */
    .stForm {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation
@st.cache_resource
def get_data_manager():
    return DataManager()

dm = get_data_manager()
am = AlertManager(dm)


def show_dashboard():
    """Affiche le tableau de bord principal."""
    st.markdown('<div class="main-header"><h1>📦 Tableau de Bord</h1><p>Vue d\'ensemble de votre stock</p></div>', unsafe_allow_html=True)
    
    # Métriques principales
    summary = dm.get_stock_summary()
    alerts_count = am.get_alerts_count()
    health_score = am.calculate_stock_health()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Produits", summary["total_produits"])
    with col2:
        st.metric("📥 Total Entrées", int(summary["total_entrees"]))
    with col3:
        st.metric("📤 Total Sorties", int(summary["total_sorties"]))
    with col4:
        st.metric("🏥 Santé Stock", f"{health_score:.0f}%")
    
    st.divider()
    
    # Alertes actives
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 État des Stocks")
        products = dm.get_products()
        
        if not products.empty:
            # Graphique des stocks
            fig = go.Figure()
            
            colors = []
            for _, p in products.iterrows():
                status = am.get_product_status(p)
                colors.append(status["color"])
            
            fig.add_trace(go.Bar(
                x=products["Nom"],
                y=products["Stock_Actuel"],
                marker_color=colors,
                name="Stock Actuel"
            ))
            
            fig.add_trace(go.Scatter(
                x=products["Nom"],
                y=products["Stock_Sécurité"],
                mode='lines+markers',
                name="Seuil Sécurité",
                line=dict(color='red', dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=products["Nom"],
                y=products["Stock_Réappro"],
                mode='lines+markers',
                name="Seuil Réappro",
                line=dict(color='orange', dash='dot')
            ))
            
            fig.update_layout(
                title="Niveaux de Stock par Produit",
                xaxis_title="Produit",
                yaxis_title="Quantité",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun produit enregistré. Ajoutez des produits pour voir le graphique.")
    
    with col2:
        st.subheader("🚨 Alertes Actives")
        
        # Compteurs d'alertes
        if alerts_count["critical"] > 0:
            st.error(f"🔴 {alerts_count['critical']} alerte(s) critique(s)")
        if alerts_count["warning"] > 0:
            st.warning(f"🟠 {alerts_count['warning']} à réapprovisionner")
        if alerts_count["overstock"] > 0:
            st.info(f"🔵 {alerts_count['overstock']} en surstock")
        
        if alerts_count["total"] == 0:
            st.success("✅ Aucune alerte active")
        
        # Liste des alertes
        alerts = am.get_all_alerts()
        for alert in alerts[:5]:  # Afficher les 5 premières
            if alert["type"] == AlertType.CRITICAL:
                st.markdown(f"""<div class="alert-critical">
                    <strong>{alert['product_name']}</strong><br>
                    {alert['message']}
                </div>""", unsafe_allow_html=True)
            elif alert["type"] == AlertType.WARNING:
                st.markdown(f"""<div class="alert-warning">
                    <strong>{alert['product_name']}</strong><br>
                    {alert['message']}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="alert-info">
                    <strong>{alert['product_name']}</strong><br>
                    {alert['message']}
                </div>""", unsafe_allow_html=True)


def show_products():
    """Gestion des produits."""
    st.markdown('<div class="main-header"><h1>📦 Gestion des Produits</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Liste des Produits", "➕ Ajouter un Produit", "✏️ Modifier/Supprimer"])
    
    with tab1:
        products = dm.get_products()
        if not products.empty:
            # Ajouter colonne statut
            statuses = []
            for _, p in products.iterrows():
                status = am.get_product_status(p)
                statuses.append(f"{status['emoji']} {status['status']}")
            products["Statut"] = statuses
            
            st.dataframe(
                products,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Stock_Actuel": st.column_config.ProgressColumn(
                        "Stock Actuel",
                        min_value=0,
                        max_value=int(products["Stock_Max"].max()) if not products.empty else 100
                    )
                }
            )
        else:
            st.info("Aucun produit enregistré.")
    
    with tab2:
        with st.form("add_product_form"):
            st.subheader("Nouveau Produit")
            
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nom du produit *", placeholder="Ex: Ciment Portland")
                categorie = st.text_input("Catégorie", placeholder="Ex: Matériaux de construction")
                unite = st.text_input("Unité de mesure", value="Unités", placeholder="Ex: Kg, Litres, Pièces")
            
            with col2:
                stock_actuel = st.number_input("Stock initial", min_value=0, value=0)
                stock_securite = st.number_input("Stock de sécurité *", min_value=0, value=10,
                    help="Niveau minimum critique à ne pas dépasser")
                stock_reappro = st.number_input("Stock de réapprovisionnement *", min_value=0, value=30,
                    help="Seuil déclenchant une commande")
                stock_max = st.number_input("Stock maximum", min_value=1, value=100,
                    help="Capacité maximale de stockage")
            
            submitted = st.form_submit_button("➕ Ajouter le produit", use_container_width=True)
            
            if submitted:
                if nom and stock_securite < stock_reappro < stock_max:
                    new_id = dm.add_product(
                        nom=nom, categorie=categorie, stock_actuel=stock_actuel,
                        stock_securite=stock_securite, stock_reappro=stock_reappro,
                        stock_max=stock_max, unite=unite
                    )
                    st.success(f"✅ Produit '{nom}' ajouté avec succès (ID: {new_id})")
                    st.rerun()
                else:
                    st.error("⚠️ Vérifiez les données: Stock sécurité < Stock réappro < Stock max")
    
    with tab3:
        products = dm.get_products()
        if not products.empty:
            product_options = {f"{p['Nom']} (ID: {p['ID']})": p['ID'] for _, p in products.iterrows()}
            selected = st.selectbox("Sélectionner un produit", list(product_options.keys()))
            
            if selected:
                product_id = product_options[selected]
                product = dm.get_product_by_id(product_id)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✏️ Modifier")
                    with st.form("edit_product_form"):
                        new_nom = st.text_input("Nom", value=product["Nom"])
                        new_categorie = st.text_input("Catégorie", value=product["Catégorie"])
                        new_stock = st.number_input("Stock actuel", value=int(product["Stock_Actuel"]))
                        new_securite = st.number_input("Stock sécurité", value=int(product["Stock_Sécurité"]))
                        new_reappro = st.number_input("Stock réappro", value=int(product["Stock_Réappro"]))
                        new_max = st.number_input("Stock max", value=int(product["Stock_Max"]))
                        
                        if st.form_submit_button("💾 Sauvegarder", use_container_width=True):
                            dm.update_product(
                                product_id,
                                Nom=new_nom, Catégorie=new_categorie,
                                Stock_Actuel=new_stock, **{"Stock_Sécurité": new_securite},
                                **{"Stock_Réappro": new_reappro}, Stock_Max=new_max
                            )
                            st.success("✅ Produit mis à jour!")
                            st.rerun()
                
                with col2:
                    st.subheader("🗑️ Supprimer")
                    st.warning(f"Voulez-vous vraiment supprimer **{product['Nom']}** ?")
                    if st.button("🗑️ Confirmer la suppression", type="primary", use_container_width=True):
                        dm.delete_product(product_id)
                        st.success("Produit supprimé!")
                        st.rerun()
        else:
            st.info("Aucun produit à modifier.")


def show_entries():
    """Gestion des entrées de stock."""
    st.markdown('<div class="main-header"><h1>📥 Entrées de Stock</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Historique", "➕ Nouvelle Entrée"])
    
    with tab1:
        entries = dm.get_entries()
        products = dm.get_products()
        
        if not entries.empty and not products.empty:
            # Joindre le nom du produit
            entries_display = entries.merge(
                products[["ID", "Nom"]], 
                left_on="Produit_ID", 
                right_on="ID", 
                suffixes=("", "_prod")
            )
            entries_display = entries_display.rename(columns={"Nom": "Produit"})
            entries_display = entries_display[["ID", "Date", "Produit", "Quantité", "Fournisseur", "Notes"]]
            
            st.dataframe(entries_display, use_container_width=True, hide_index=True)
            
            # Graphique des entrées par produit
            fig = px.bar(entries_display, x="Produit", y="Quantité", color="Fournisseur",
                        title="Entrées par Produit et Fournisseur")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune entrée enregistrée.")
    
    with tab2:
        products = dm.get_products()
        
        if not products.empty:
            with st.form("add_entry_form"):
                st.subheader("Enregistrer une entrée")
                
                product_options = {f"{p['Nom']} (Stock: {p['Stock_Actuel']} {p['Unité']})": p['ID'] 
                                  for _, p in products.iterrows()}
                
                col1, col2 = st.columns(2)
                with col1:
                    selected_product = st.selectbox("Produit *", list(product_options.keys()))
                    quantite = st.number_input("Quantité *", min_value=1, value=1)
                
                with col2:
                    fournisseur = st.text_input("Fournisseur", placeholder="Nom du fournisseur")
                    notes = st.text_area("Notes", placeholder="Commentaires optionnels")
                
                if st.form_submit_button("📥 Enregistrer l'entrée", use_container_width=True, type="primary"):
                    product_id = product_options[selected_product]
                    dm.add_entry(product_id, quantite, fournisseur, notes)
                    st.success(f"✅ Entrée de {quantite} unités enregistrée!")
                    st.balloons()
                    st.rerun()
        else:
            st.warning("Ajoutez d'abord des produits avant d'enregistrer des entrées.")


def show_exits():
    """Gestion des sorties de stock."""
    st.markdown('<div class="main-header"><h1>📤 Sorties de Stock</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Historique", "➕ Nouvelle Sortie"])
    
    with tab1:
        exits = dm.get_exits()
        products = dm.get_products()
        
        if not exits.empty and not products.empty:
            # Joindre le nom du produit
            exits_display = exits.merge(
                products[["ID", "Nom"]], 
                left_on="Produit_ID", 
                right_on="ID", 
                suffixes=("", "_prod")
            )
            exits_display = exits_display.rename(columns={"Nom": "Produit"})
            exits_display = exits_display[["ID", "Date", "Produit", "Quantité", "Destination", "Notes"]]
            
            st.dataframe(exits_display, use_container_width=True, hide_index=True)
            
            # Graphique des sorties par destination
            fig = px.pie(exits_display, values="Quantité", names="Destination",
                        title="Répartition des Sorties par Destination")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune sortie enregistrée.")
    
    with tab2:
        products = dm.get_products()
        
        if not products.empty:
            with st.form("add_exit_form"):
                st.subheader("Enregistrer une sortie")
                
                product_options = {f"{p['Nom']} (Stock: {p['Stock_Actuel']} {p['Unité']})": p['ID'] 
                                  for _, p in products.iterrows()}
                
                col1, col2 = st.columns(2)
                with col1:
                    selected_product = st.selectbox("Produit *", list(product_options.keys()))
                    product_id = product_options[selected_product]
                    product = dm.get_product_by_id(product_id)
                    max_qty = int(product["Stock_Actuel"])
                    
                    quantite = st.number_input("Quantité *", min_value=1, max_value=max(1, max_qty), value=1)
                    
                    if max_qty < product["Stock_Sécurité"]:
                        st.warning(f"⚠️ Stock déjà critique: {max_qty} {product['Unité']}")
                
                with col2:
                    destination = st.text_input("Destination/Client", placeholder="Ex: Chantier ABC")
                    notes = st.text_area("Notes", placeholder="Commentaires optionnels")
                
                if st.form_submit_button("📤 Enregistrer la sortie", use_container_width=True, type="primary"):
                    result_id, error = dm.add_exit(product_id, quantite, destination, notes)
                    if error:
                        st.error(f"❌ Erreur: {error}")
                    else:
                        st.success(f"✅ Sortie de {quantite} unités enregistrée!")
                        st.rerun()
        else:
            st.warning("Ajoutez d'abord des produits avant d'enregistrer des sorties.")


def show_alerts():
    """Page des alertes."""
    st.markdown('<div class="main-header"><h1>🚨 Centre d\'Alertes</h1></div>', unsafe_allow_html=True)
    
    alerts = am.get_all_alerts()
    alerts_count = am.get_alerts_count()
    
    # Résumé des alertes
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔴 Critiques", alerts_count["critical"])
    with col2:
        st.metric("🟠 Réappro", alerts_count["warning"])
    with col3:
        st.metric("🔵 Surstock", alerts_count["overstock"])
    with col4:
        st.metric("📊 Total", alerts_count["total"])
    
    st.divider()
    
    if alerts:
        # Filtres
        filter_type = st.radio(
            "Filtrer par type:",
            ["Toutes", "🔴 Critiques", "🟠 Réapprovisionnement", "🔵 Surstock"],
            horizontal=True
        )
        
        for alert in alerts:
            # Appliquer le filtre
            if filter_type == "🔴 Critiques" and alert["type"] != AlertType.CRITICAL:
                continue
            if filter_type == "🟠 Réapprovisionnement" and alert["type"] != AlertType.WARNING:
                continue
            if filter_type == "🔵 Surstock" and alert["type"] != AlertType.OVERSTOCK:
                continue
            
            # Affichage de l'alerte
            if alert["type"] == AlertType.CRITICAL:
                with st.container():
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); 
                                padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem;">
                        <h3 style="margin: 0;">{alert['icon']} {alert['product_name']}</h3>
                        <p style="margin: 0.5rem 0;">{alert['message']}</p>
                        <small>{alert['details']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            elif alert["type"] == AlertType.WARNING:
                with st.container():
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #F2994A 0%, #F2C94C 100%); 
                                padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem;">
                        <h3 style="margin: 0;">{alert['icon']} {alert['product_name']}</h3>
                        <p style="margin: 0.5rem 0;">{alert['message']}</p>
                        <small>{alert['details']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with st.container():
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%); 
                                padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem;">
                        <h3 style="margin: 0;">{alert['icon']} {alert['product_name']}</h3>
                        <p style="margin: 0.5rem 0;">{alert['message']}</p>
                        <small>{alert['details']}</small>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.success("✅ Aucune alerte active! Tous vos stocks sont dans les niveaux normaux.")
        st.balloons()


# Navigation
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/warehouse.png", width=100)
    st.title("📦 GestiStock")
    st.caption("Gestion de Stock Intelligente")
    
    st.divider()
    
    # Menu de navigation
    page = st.radio(
        "Navigation",
        ["🏠 Tableau de bord", "📦 Produits", "📥 Entrées", "📤 Sorties", "🚨 Alertes"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Indicateurs rapides
    alerts_count = am.get_alerts_count()
    if alerts_count["total"] > 0:
        st.error(f"⚠️ {alerts_count['total']} alerte(s) active(s)")
    else:
        st.success("✅ Tous les stocks OK")
    
    st.divider()
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Affichage de la page sélectionnée
if page == "🏠 Tableau de bord":
    show_dashboard()
elif page == "📦 Produits":
    show_products()
elif page == "📥 Entrées":
    show_entries()
elif page == "📤 Sorties":
    show_exits()
elif page == "🚨 Alertes":
    show_alerts()

st.image("assets/porte drapeau SEAHORSE.png", width=100)