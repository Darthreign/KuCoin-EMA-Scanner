import ccxt
import logging
from typing import Dict, List, Optional
from datetime import datetime
from config import Config

class KuCoinTrader:
    def __init__(self):
        self.exchange = self._init_exchange()
        self.positions = {}
        self.orders_history = []
        
    def _init_exchange(self):
        """Initialise la connexion à KuCoin pour le trading"""
        try:
            exchange = ccxt.kucoinfutures({
                'apiKey': Config.KUCOIN_API_KEY,
                'secret': Config.KUCOIN_API_SECRET,
                'password': Config.KUCOIN_PASSPHRASE,
                'sandbox': Config.KUCOIN_SANDBOX,
                'enableRateLimit': True,
            })
            return exchange
        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation du trader: {e}")
            return None
    
    def get_account_balance(self) -> Dict:
        """Récupère le solde du compte"""
        try:
            if not self.exchange:
                return {}
            
            balance = self.exchange.fetch_balance()
            return {
                'USDT': {
                    'free': balance.get('USDT', {}).get('free', 0),
                    'used': balance.get('USDT', {}).get('used', 0),
                    'total': balance.get('USDT', {}).get('total', 0)
                }
            }
        except Exception as e:
            logging.error(f"Erreur lors de la récupération du solde: {e}")
            return {}
    
    def calculate_position_size(self, symbol: str, price: float, risk_amount: float, leverage: float = 1.0) -> Dict:
        """Calcule la taille de position basée sur le risque avec effet de levier"""
        try:
            # Récupérer les informations du marché
            market = self.exchange.markets.get(symbol, {})
            min_amount = market.get('limits', {}).get('amount', {}).get('min', 0.001)
            max_leverage = market.get('limits', {}).get('leverage', {}).get('max', 1.0)
        
            # Limiter le levier au maximum autorisé par le marché
            leverage = min(leverage, max_leverage) if max_leverage else leverage
            leverage = max(leverage, 1.0)  # Minimum 1x
        
            # Calculer la taille de position
            sl_distance = price * (Config.DEFAULT_SL_PERCENT / 100)
        
            # Avec levier : on peut prendre une position plus grande
            # Le capital requis est divisé par le levier
            base_position_size = risk_amount / sl_distance
            leveraged_position_size = base_position_size * leverage
        
            # Le capital réellement utilisé (marge)
            margin_required = (leveraged_position_size * price) / leverage
        
            # Ajuster selon les limites du marché
            leveraged_position_size = max(leveraged_position_size, min_amount)
        
            return {
                'size': round(leveraged_position_size, 6),
                'value_usdt': round(leveraged_position_size * price, 2),
                'margin_required': round(margin_required, 2),
                'risk_usdt': round(risk_amount, 2),
                'sl_distance': round(sl_distance, 6),
                'leverage': leverage,
                'max_leverage': max_leverage
                }
        
        except Exception as e:
            logging.error(f"Erreur calcul taille position pour {symbol}: {e}")
            return {}
    
    def calculate_sl_tp_levels(self, symbol: str, entry_price: float, 
                              fibonacci_levels: Dict, direction: str = 'long') -> Dict:
        """Calcule les niveaux de SL et TP"""
        try:
            levels = {
                'entry_price': entry_price,
                'stop_loss': 0,
                'take_profits': []
            }
            
            if direction == 'long':
                # Stop Loss
                levels['stop_loss'] = entry_price * (1 - Config.DEFAULT_SL_PERCENT / 100)
                
                # Take Profits basés sur Fibonacci ou pourcentages par défaut
                if fibonacci_levels and 'extensions' in fibonacci_levels:
                    extensions = fibonacci_levels['extensions']
                    tp_levels = []
                    
                    # Prendre les 3 premiers niveaux d'extension au-dessus du prix
                    sorted_extensions = sorted([price for price in extensions.values() 
                                              if price > entry_price])[:3]
                    
                    if len(sorted_extensions) >= 3:
                        tp_levels = sorted_extensions
                    else:
                        # Fallback sur les pourcentages
                        tp_levels = [
                            entry_price * (1 + Config.TP1_PERCENT / 100),
                            entry_price * (1 + Config.TP2_PERCENT / 100),
                            entry_price * (1 + Config.TP3_PERCENT / 100)
                        ]
                else:
                    # Utiliser les pourcentages par défaut
                    tp_levels = [
                        entry_price * (1 + Config.TP1_PERCENT / 100),
                        entry_price * (1 + Config.TP2_PERCENT / 100),
                        entry_price * (1 + Config.TP3_PERCENT / 100)
                    ]
                
                levels['take_profits'] = [round(tp, 6) for tp in tp_levels[:3]]
            
            levels['stop_loss'] = round(levels['stop_loss'], 6)
            
            return levels
            
        except Exception as e:
            logging.error(f"Erreur calcul SL/TP pour {symbol}: {e}")
            return {}
    
    def place_market_order(self, symbol: str, side: str, amount: float) -> Optional[Dict]:
        """Place un ordre au marché"""
        try:
            if not self.exchange:
                logging.error("Exchange non initialisé")
                return None
            
            order = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=amount
            )
            
            logging.info(f"Ordre au marché placé: {side} {amount} {symbol}")
            return order
            
        except Exception as e:
            logging.error(f"Erreur placement ordre marché {symbol}: {e}")
            return None
    
    def place_limit_order(self, symbol: str, side: str, amount: float, price: float) -> Optional[Dict]:
        """Place un ordre limite"""
        try:
            if not self.exchange:
                logging.error("Exchange non initialisé")
                return None
            
            order = self.exchange.create_limit_order(
                symbol=symbol,
                side=side,
                amount=amount,
                price=price
            )
            
            logging.info(f"Ordre limite placé: {side} {amount} {symbol} @ {price}")
            return order
            
        except Exception as e:
            logging.error(f"Erreur placement ordre limite {symbol}: {e}")
            return None
    
    def place_stop_order(self, symbol: str, side: str, amount: float, stop_price: float) -> Optional[Dict]:
        """Place un ordre stop"""
        try:
            if not self.exchange:
                logging.error("Exchange non initialisé")
                return None
            
            # Note: La méthode exacte peut varier selon l'API KuCoin
            order = self.exchange.create_order(
                symbol=symbol,
                type='stop',
                side=side,
                amount=amount,
                params={'stopPrice': stop_price}
            )
            
            logging.info(f"Ordre stop placé: {side} {amount} {symbol} @ stop {stop_price}")
            return order
            
        except Exception as e:
            logging.error(f"Erreur placement ordre stop {symbol}: {e}")
            return None
    
    def execute_signal(self, signal: Dict, position_size_usdt: float) -> Dict:
        """Exécute un signal de trading complet"""
        try:
            symbol = signal['symbol']
            entry_price = signal['price']
            fibonacci_levels = signal.get('fibonacci_levels', {})
            
            # Calculer la taille de position
            position_info = self.calculate_position_size(
                symbol, entry_price, position_size_usdt * 0.02  # 2% de risque
            )
            
            if not position_info:
                return {'success': False, 'error': 'Impossible de calculer la taille de position'}
            
            # Calculer les niveaux SL/TP
            levels = self.calculate_sl_tp_levels(symbol, entry_price, fibonacci_levels)
            
            if not levels:
                return {'success': False, 'error': 'Impossible de calculer les niveaux SL/TP'}
            
            # Placer l'ordre d'achat principal
            main_order = self.place_market_order(symbol, 'buy', position_info['size'])
            
            if not main_order:
                return {'success': False, 'error': 'Échec placement ordre principal'}
            
            # Placer le Stop Loss
            sl_order = self.place_stop_order(
                symbol, 'sell', position_info['size'], levels['stop_loss']
            )
            
            # Placer les Take Profits (1/3 de la position chacun)
            tp_size = position_info['size'] / 3
            tp_orders = []
            
            for i, tp_price in enumerate(levels['take_profits']):
                tp_order = self.place_limit_order(
                    symbol, 'sell', tp_size, tp_price
                )
                if tp_order:
                    tp_orders.append(tp_order)
            
            # Enregistrer la transaction
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'signal': signal,
                'entry_order': main_order,
                'stop_loss_order': sl_order,
                'take_profit_orders': tp_orders,
                'position_info': position_info,
                'levels': levels,
                'status': 'active'
            }
            
            self.orders_history.append(trade_record)
            
            logging.info(f"Signal exécuté pour {symbol}: Entry={entry_price}, SL={levels['stop_loss']}, TPs={levels['take_profits']}")
            
            return {
                'success': True,
                'trade_record': trade_record,
                'message': f'Trade exécuté pour {symbol}'
            }
            
        except Exception as e:
            logging.error(f"Erreur lors de l'exécution du signal {signal.get('symbol', 'unknown')}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_open_positions(self) -> List[Dict]:
        """Récupère les positions ouvertes"""
        try:
            if not self.exchange:
                return []
            
            positions = self.exchange.fetch_positions()
            open_positions = [pos for pos in positions if pos.get('size', 0) > 0]
            
            return open_positions
            
        except Exception as e:
            logging.error(f"Erreur récupération positions ouvertes: {e}")
            return []
    
    def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict]:
        """Récupère le statut d'un ordre"""
        try:
            if not self.exchange:
                return None
            
            order = self.exchange.fetch_order(order_id, symbol)
            return order
            
        except Exception as e:
            logging.error(f"Erreur récupération statut ordre {order_id}: {e}")
            return None
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Annule un ordre"""
        try:
            if not self.exchange:
                return False
            
            result = self.exchange.cancel_order(order_id, symbol)
            logging.info(f"Ordre {order_id} annulé pour {symbol}")
            return True
            
        except Exception as e:
            logging.error(f"Erreur annulation ordre {order_id}: {e}")
            return False
    
    def get_trading_fees(self, symbol: str) -> Dict:
        """Récupère les frais de trading"""
        try:
            if not self.exchange:
                return {}
            
            market = self.exchange.markets.get(symbol, {})
            fees = market.get('fees', {})
            
            return {
                'maker': fees.get('maker', 0.001),
                'taker': fees.get('taker', 0.001)
            }
            
        except Exception as e:
            logging.error(f"Erreur récupération frais pour {symbol}: {e}")
            return {'maker': 0.001, 'taker': 0.001}
    
    def calculate_pnl(self, trade_record: Dict) -> Dict:
        """Calcule le P&L d'un trade"""
        try:
            symbol = trade_record['symbol']
            entry_price = trade_record['levels']['entry_price']
            position_size = trade_record['position_info']['size']
            
            # Récupérer le prix actuel
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Calculer P&L
            pnl_points = current_price - entry_price
            pnl_percent = (pnl_points / entry_price) * 100
            pnl_usdt = pnl_points * position_size
            
            return {
                'current_price': current_price,
                'entry_price': entry_price,
                'pnl_points': round(pnl_points, 6),
                'pnl_percent': round(pnl_percent, 2),
                'pnl_usdt': round(pnl_usdt, 2)
            }
            
        except Exception as e:
            logging.error(f"Erreur calcul P&L: {e}")
            return {}