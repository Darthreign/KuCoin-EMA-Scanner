import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import threading
from scanner import KuCoinScanner
from trading import KuCoinTrader
from config import Config
import logging

class TradingGUI:
    def __init__(self):
        self.scanner = KuCoinScanner()
        self.trader = KuCoinTrader()
        self.is_scanning = False
        self.scan_thread = None
        
    def setup_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(
            page_title="KuCoin EMA Scanner & Auto Trader",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🚀 KuCoin EMA Scanner & Auto Trader")
        st.markdown("---")
    
    def sidebar_config(self):
        """Configuration de la barre latérale"""
        st.sidebar.header("⚙️ Configuration")
        
        # Configuration API
        with st.sidebar.expander("🔑 Configuration API", expanded=False):
            api_key = st.text_input("API Key", value=Config.KUCOIN_API_KEY, type="password")
            api_secret = st.text_input("API Secret", value=Config.KUCOIN_API_SECRET, type="password")
            passphrase = st.text_input("Passphrase", value=Config.KUCOIN_PASSPHRASE, type="password")
            sandbox = st.checkbox("Mode Sandbox", value=Config.KUCOIN_SANDBOX)
            
            if st.button("💾 Sauvegarder API"):
                Config.KUCOIN_API_KEY = api_key
                Config.KUCOIN_API_SECRET = api_secret
                Config.KUCOIN_PASSPHRASE = passphrase
                Config.KUCOIN_SANDBOX = sandbox
                st.success("Configuration API sauvegardée!")
        
        # Configuration du scanner
        with st.sidebar.expander("🔍 Configuration Scanner", expanded=True):
            Config.SCAN_INTERVAL = st.slider("Intervalle de scan (secondes)", 30, 300, Config.SCAN_INTERVAL)
            Config.VOLUME_THRESHOLD = st.slider("Seuil volume (%)", 50, 2000, Config.VOLUME_THRESHOLD, 50)
            Config.EMA_PERIOD = st.slider("Période EMA", 10, 50, Config.EMA_PERIOD)
        
        # Configuration trading
        with st.sidebar.expander("💰 Configuration Trading", expanded=True):
            Config.DEFAULT_POSITION_SIZE = st.number_input("Taille position (USDT)", 1, 10000, Config.DEFAULT_POSITION_SIZE)
            Config.DEFAULT_LEVERAGE = st.slider("Effet de levier", 1.0, 20.0, Config.DEFAULT_LEVERAGE)
            Config.DEFAULT_SL_PERCENT = st.slider("Stop Loss (%)", 0.5, 10.0, Config.DEFAULT_SL_PERCENT)
            Config.TP1_PERCENT = st.slider("Take Profit 1 (%)", 0.5, 5.0, Config.TP1_PERCENT)
            Config.TP2_PERCENT = st.slider("Take Profit 2 (%)", 1.0, 10.0, Config.TP2_PERCENT)
            Config.TP3_PERCENT = st.slider("Take Profit 3 (%)", 2.0, 15.0, Config.TP3_PERCENT)
        
        st.sidebar.markdown("---")
        
        # Contrôles du scanner
        st.sidebar.header("🎮 Contrôles")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("▶️ Démarrer", disabled=self.is_scanning):
                self.start_scanning()
        
        with col2:
            if st.button("⏹️ Arrêter", disabled=not self.is_scanning):
                self.stop_scanning()
        
        if st.sidebar.button("🔄 Scan Manuel"):
            self.manual_scan()
        
        # Statut
        status = "🟢 En cours" if self.is_scanning else "🔴 Arrêté"
        st.sidebar.markdown(f"**Statut Scanner:** {status}")
    
    def display_account_info(self):
        """Affiche les informations du compte"""
        col1, col2, col3, col4 = st.columns(4)
        
        try:
            balance = self.trader.get_account_balance()
            usdt_balance = balance.get('USDT', {})
            
            with col1:
                st.metric("💰 Solde USDT", f"{usdt_balance.get('free', 0):.2f}")
            
            with col2:
                st.metric("🔒 USDT Utilisé", f"{usdt_balance.get('used', 0):.2f}")
            
            with col3:
                positions = self.trader.get_open_positions()
                st.metric("📊 Positions Ouvertes", len(positions))
            
            with col4:
                st.metric("📈 Trades Historique", len(self.trader.orders_history))
                
        except Exception as e:
            st.error(f"Erreur récupération compte: {e}")
    
    def display_signals_table(self):
        """Affiche le tableau des signaux détectés"""
        st.header("📊 Signaux Détectés")
        
        if not hasattr(self.scanner, 'detected_signals') or not self.scanner.detected_signals:
            st.info("Aucun signal détecté. Lancez un scan pour commencer.")
            return
        
        # Convertir en DataFrame
        signals_data = []
        for signal in self.scanner.detected_signals:
            signals_data.append({
                'Timestamp': signal['timestamp'].strftime("%H:%M:%S"),
                'Symbol': signal['symbol'],
                'Prix': f"{signal['price']:.6f}",
                'Volume +%': f"{signal['volume_increase']:.1f}%",
                'EMA20': f"{signal['ema_value']:.6f}",
                'Force': signal['signal_strength'],
                'Action': 'pending'
            })
        
        df = pd.DataFrame(signals_data)
        
        # Afficher le tableau avec possibilité de sélection
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                'Force': st.column_config.SelectboxColumn(
                    'Force Signal',
                    options=['FAIBLE', 'MOYENNE', 'FORTE'],
                ),
            }
        )
        
        # Boutons d'action pour chaque signal
        if st.button("🚀 Trader les Signaux Sélectionnés"):
            self.execute_selected_signals()
    
    def display_active_trades(self):
        """Affiche les trades actifs"""
        st.header("📈 Trades Actifs")

        # Vérifier que l'historique contient bien des ordres
        if not self.trader.orders_history:
            st.info("Aucun trade actif.")
            return

        # Filtrer les trades actifs (en fonction de ta structure réelle : ajuste si nécessaire)
        active_trades = [
            trade for trade in self.trader.orders_history
            if trade.get('status', '').lower() in ['active', 'open', 'opened']  # ajuster selon ta structure
            ]

        if not active_trades:
            st.info("Aucun trade actif.")
            return

        for i, trade in enumerate(active_trades):
            with st.expander(f"Trade {i+1}: {trade.get('symbol', 'N/A')}", expanded=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Informations Trade :**")
                    st.write(f"**Symbole**: {trade.get('symbol', 'N/A')}")
                    st.write(f"**Entrée**: {trade['levels'].get('entry_price', 0):.6f}")
                    st.write(f"**Taille**: {trade['position_info'].get('size', 0):.6f}")
                    st.write(f"**Valeur**: {trade['position_info'].get('value_usdt', 0):.2f} USDT")

                with col2:
                    st.markdown("**Niveaux :**")
                    st.write(f"Stop Loss: {trade['levels'].get('stop_loss', 0):.6f}")
                    for j, tp in enumerate(trade['levels'].get('take_profits', []), 1):
                        st.write(f"TP{j}: {tp:.6f}")

                with col3:
                    pnl = self.trader.calculate_pnl(trade)
                    st.markdown("**P&L Actuel :**")
                    if pnl:
                        pnl_color = "green" if pnl['pnl_usdt'] >= 0 else "red"
                        st.write(f"Prix actuel : {pnl['current_price']:.6f}")
                        st.markdown(
                            f"<span style='color:{pnl_color}'>"
                            f"P&L : {pnl['pnl_usdt']:.2f} USDT ({pnl['pnl_percent']:.2f}%)"
                            f"</span>",
                            unsafe_allow_html=True
                            )
                    else:
                        st.warning("Impossible de calculer le P&L.")

                # Bouton de fermeture du trade
                if st.button(f"❌ Fermer Trade {i+1}", key=f"close_trade_{i}"):
                    self.close_trade_manually(trade)
                    st.success(f"Trade {trade.get('symbol')} fermé.")
                    
    def display_performance_chart(self):
        """Affiche le graphique de performance"""
        st.header("📊 Performance")
        
        if not self.trader.orders_history:
            st.info("Aucune donnée de performance disponible.")
            return
        
        # Calculer les performances
        performance_data = []
        cumulative_pnl = 0
        
        for trade in self.trader.orders_history:
            pnl = self.trader.calculate_pnl(trade)
            if pnl:
                cumulative_pnl += pnl['pnl_usdt']
                performance_data.append({
                    'timestamp': trade['timestamp'],
                    'symbol': trade['symbol'],
                    'pnl': pnl['pnl_usdt'],
                    'cumulative_pnl': cumulative_pnl
                })
        
        if performance_data:
            df_perf = pd.DataFrame(performance_data)
            
            # Graphique de performance cumulative
            fig = px.line(df_perf, x='timestamp', y='cumulative_pnl', 
                         title='Performance Cumulative (USDT)',
                         labels={'cumulative_pnl': 'P&L Cumulé (USDT)', 'timestamp': 'Temps'})
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Métriques de performance
            col1, col2, col3, col4 = st.columns(4)
            
            total_trades = len(performance_data)
            winning_trades = len([p for p in performance_data if p['pnl'] > 0])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            with col1:
                st.metric("Total P&L", f"{cumulative_pnl:.2f} USDT")
            with col2:
                st.metric("Total Trades", total_trades)
            with col3:
                st.metric("Trades Gagnants", winning_trades)
            with col4:
                st.metric("Taux de Réussite", f"{win_rate:.1f}%")
    
    def display_logs(self):
        """Affiche les logs récents"""
        st.header("📋 Logs Récents")
        
        try:
            with open(Config.LOG_FILE, 'r') as f:
                logs = f.readlines()
            
            # Afficher les 20 dernières lignes
            recent_logs = logs[-20:]
            
            log_text = "".join(recent_logs)
            st.text_area("Logs", log_text, height=200)
            
        except FileNotFoundError:
            st.info("Aucun fichier de log trouvé.")
        except Exception as e:
            st.error(f"Erreur lecture logs: {e}")
    
    def start_scanning(self):
        """Démarre le scanner en arrière-plan"""
        if not self.is_scanning:
            self.is_scanning = True
            self.scan_thread = threading.Thread(target=self.scanning_loop, daemon=True)
            self.scan_thread.start()
            st.success("Scanner démarré!")
    
    def stop_scanning(self):
        """Arrête le scanner"""
        self.is_scanning = False
        st.success("Scanner arrêté!")
    
    def scanning_loop(self):
        """Boucle principale du scanner"""
        while self.is_scanning:
            try:
                # Vérifier les nouveaux listings
                new_listings = self.scanner.get_new_listings()
                if new_listings:
                    logging.info(f"Nouveaux listings: {new_listings}")
                
                # Scanner tous les symbols
                signals = self.scanner.scan_all_symbols()
                
                # Attendre avant le prochain scan
                time.sleep(Config.SCAN_INTERVAL)
                
            except Exception as e:
                logging.error(f"Erreur dans la boucle de scan: {e}")
                time.sleep(30)  # Pause en cas d'erreur
    
    def manual_scan(self):
        """Lance un scan manuel"""
        with st.spinner("Scan en cours..."):
            try:
                signals = self.scanner.scan_all_symbols()
                st.success(f"Scan terminé! {len(signals)} signaux détectés.")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur lors du scan: {e}")
    
    def execute_selected_signals(self):
        """Exécute les signaux sélectionnés"""
        if not self.scanner.detected_signals:
            st.warning("Aucun signal à exécuter.")
            return
        
        success_count = 0
        
        for signal in self.scanner.detected_signals:
            try:
                result = self.trader.execute_signal(signal, Config.DEFAULT_POSITION_SIZE)
                if result['success']:
                    success_count += 1
                    st.success(f"Trade exécuté pour {signal['symbol']}")
                else:
                    st.error(f"Erreur trade {signal['symbol']}: {result['error']}")
            except Exception as e:
                st.error(f"Erreur exécution {signal['symbol']}: {e}")
        
        st.info(f"{success_count} trades exécutés avec succès sur {len(self.scanner.detected_signals)} signaux.")
    
    def close_trade_manually(self, trade):
        """Ferme un trade manuellement"""
        try:
            symbol = trade['symbol']
            position_size = trade['position_info']['size']
            
            # Placer un ordre de vente au marché
            order = self.trader.place_market_order(symbol, 'sell', position_size)
            
            if order:
                # Annuler les ordres SL/TP en attente
                if trade.get('stop_loss_order'):
                    self.trader.cancel_order(trade['stop_loss_order']['id'], symbol)
                
                for tp_order in trade.get('take_profit_orders', []):
                    self.trader.cancel_order(tp_order['id'], symbol)
                
                # Marquer le trade comme fermé
                trade['status'] = 'closed_manually'
                trade['close_order'] = order
                
                st.success(f"Trade fermé manuellement pour {symbol}")
            else:
                st.error(f"Erreur lors de la fermeture du trade {symbol}")
                
        except Exception as e:
            st.error(f"Erreur fermeture manuelle: {e}")
    
    def run(self):
        """Lance l'interface graphique"""
        self.setup_page()
        self.sidebar_config()
        
        # Onglets principaux
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dashboard", 
            "🎯 Signaux", 
            "💼 Trades Actifs", 
            "📈 Performance", 
            "📋 Logs"
        ])
        
        with tab1:
            st.header("📊 Dashboard")
            self.display_account_info()
            
            # Statistiques rapides
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Marchés Surveillés")
                if hasattr(self.scanner, 'futures_symbols'):
                    st.metric("Symbols avec Futures", len(self.scanner.futures_symbols))
                else:
                    st.metric("Symbols avec Futures", "Chargement...")
            
            with col2:
                st.subheader("🔍 Dernière Activité")
                if hasattr(self.scanner, 'detected_signals'):
                    last_scan = max([s['timestamp'] for s in self.scanner.detected_signals]) if self.scanner.detected_signals else None
                    if last_scan:
                        st.write(f"Dernier signal: {last_scan.strftime('%H:%M:%S')}")
                    else:
                        st.write("Aucun signal récent")
        
        with tab2:
            self.display_signals_table()
        
        with tab3:
            self.display_active_trades()
        
        with tab4:
            self.display_performance_chart()
        
        with tab5:
            self.display_logs()
        
        # Auto-refresh toutes les 30 secondes si le scanner est actif
        if self.is_scanning:
            time.sleep(30)
            st.rerun()

def main():
    """Fonction principale"""
    gui = TradingGUI()
    gui.run()

if __name__ == "__main__":
    main()