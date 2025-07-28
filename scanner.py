import ccxt
import pandas as pd
import numpy as np
import talib
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
from config import Config

class KuCoinScanner:
    def __init__(self):
        self.exchange = self._init_exchange()
        self.markets_info = {}
        self.futures_symbols = set()
        self.detected_signals = []
        self.setup_logging()
        
    def _init_exchange(self):
        """Initialise la connexion à KuCoin"""
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
            logging.error(f"Erreur lors de l'initialisation de l'exchange: {e}")
            return None
    
    def setup_logging(self):
        """Configure le système de logging"""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def load_markets(self):
        """Charge les informations des marchés"""
        try:
            self.exchange.load_markets()
            self.markets_info = self.exchange.markets
            logging.info(f"Chargé {len(self.markets_info)} marchés")
            self._identify_futures_symbols()
        except Exception as e:
            logging.error(f"Erreur lors du chargement des marchés: {e}")
    
    def _identify_futures_symbols(self):
        """Identifie les symbols disposant de contrats futures perpétuels"""
        try:
            futures_markets = {
                k: v for k, v in self.markets_info.items()
                if v.get('type') == 'swap' and v.get('active', False)
            }
            for symbol in futures_markets:
                self.futures_symbols.add(symbol)  # Utilise le nom exact du marché
            logging.info(f"Trouvé {len(self.futures_symbols)} symbols avec futures")
        except Exception as e:
            logging.error(f"Erreur lors de l'identification des futures: {e}")
    
    def get_ohlcv_data(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Récupère les données OHLCV pour un symbol"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv:
                return None
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logging.warning(f"Erreur lors de la récupération des données pour {symbol}: {e}")
            return None
    
    def calculate_ema(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calcule l'EMA"""
        return talib.EMA(data['close'].values, timeperiod=period)
    
    def check_ema_crossover(self, data: pd.DataFrame) -> bool:
        """Vérifie si le prix vient de franchir l'EMA20 à la hausse"""
        if len(data) < Config.EMA_PERIOD + 2:
            return False
        ema = self.calculate_ema(data, Config.EMA_PERIOD)
        current_price = data['close'].iloc[-1]
        previous_price = data['close'].iloc[-2]
        current_ema = ema[-1]
        previous_ema = ema[-2]
        return previous_price <= previous_ema and current_price > current_ema
    
    def check_volume_increase(self, data: pd.DataFrame) -> tuple:
        """Vérifie l'augmentation du volume"""
        if len(data) < 2:
            return False, 0
        current_volume = data['volume'].iloc[-1]
        previous_volume = data['volume'].iloc[-2]
        if previous_volume == 0:
            return False, 0
        volume_increase = ((current_volume - previous_volume) / previous_volume) * 100
        return volume_increase >= Config.VOLUME_THRESHOLD, volume_increase
    
    def calculate_fibonacci_levels(self, symbol: str) -> Dict:
        """Calcule les niveaux de Fibonacci sur la timeframe 15min"""
        try:
            data_15m = self.get_ohlcv_data(symbol, Config.TIMEFRAME_FIBONACCI, 50)
            if data_15m is None or len(data_15m) < 20:
                return {}
            high_idx = data_15m['high'].rolling(10).max().idxmax()
            low_idx = data_15m['low'].rolling(10).min().idxmin()
            swing_high = data_15m.loc[high_idx, 'high']
            swing_low = data_15m.loc[low_idx, 'low']
            diff = swing_high - swing_low
            levels = {
                'swing_high': swing_high,
                'swing_low': swing_low,
                'direction': 'bullish' if high_idx > low_idx else 'bearish',
                'retracements': {},
                'extensions': {}
            }
            for level in Config.FIBONACCI_LEVELS['retracement']:
                levels['retracements'][level] = (
                    swing_high - diff * level if high_idx > low_idx else swing_low + diff * level
                )
            for level in Config.FIBONACCI_LEVELS['extension']:
                levels['extensions'][level] = (
                    swing_high + diff * (level - 1) if high_idx > low_idx else swing_low - diff * (level - 1)
                )
            return levels
        except Exception as e:
            logging.error(f"Erreur calcul Fibonacci pour {symbol}: {e}")
            return {}
    
    def scan_symbol(self, symbol: str) -> Optional[Dict]:
        """Scanne un symbol spécifique"""
        try:
            if symbol not in self.futures_symbols:
                return None
            data_4h = self.get_ohlcv_data(symbol, Config.TIMEFRAME_MAIN, 50)
            if data_4h is None or len(data_4h) < Config.EMA_PERIOD + 2:
                return None
            if not self.check_ema_crossover(data_4h):
                return None
            volume_ok, volume_increase = self.check_volume_increase(data_4h)
            if not volume_ok:
                return None
            fibonacci_levels = self.calculate_fibonacci_levels(symbol)
            signal = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'price': float(data_4h['close'].iloc[-1]),
                'volume_increase': round(volume_increase, 2),
                'ema_value': float(self.calculate_ema(data_4h)[-1]),
                'fibonacci_levels': fibonacci_levels,
                'market_info': self.markets_info.get(symbol, {}),
                'signal_strength': self._calculate_signal_strength(data_4h, volume_increase)
            }
            logging.info(f"Signal détecté pour {symbol}: Prix={signal['price']}, Volume+{volume_increase:.1f}%")
            logging.info(f"Force du signal pour {symbol}: {signal['signal_strength']}")
            return signal
        except Exception as e:
            logging.error(f"Erreur lors du scan de {symbol}: {e}")
            return None
    
    def _calculate_signal_strength(self, data: pd.DataFrame, volume_increase: float) -> str:
        """Calcule la force du signal"""
        score = 0
        if volume_increase > 100:
            score += 3
        elif volume_increase > 75:
            score += 2
        else:
            score += 1
        if len(data) >= 5:
            recent_closes = data['close'].tail(5)
            if recent_closes.is_monotonic_increasing:
                score += 2
            elif recent_closes.tail(3).is_monotonic_increasing:
                score += 1
        ema = self.calculate_ema(data)
        current_price = data['close'].iloc[-1]
        if current_price > ema[-1] * 1.02:
            score += 1
        return "FORTE" if score >= 5 else "MOYENNE" if score >= 3 else "FAIBLE"
    
    def scan_all_symbols(self) -> List[Dict]:
        """Scanne tous les symbols avec futures actifs"""
        signals = []
        if not self.exchange:
            logging.error("Exchange non initialisé")
            return signals
        if not self.markets_info:
            self.load_markets()
        futures_active_symbols = [
            symbol for symbol in self.futures_symbols
            if symbol in self.markets_info and self.markets_info[symbol].get('active', False)
        ]
        logging.info(f"Scan de {len(futures_active_symbols)} symbols...")
        for i, symbol in enumerate(futures_active_symbols):
            try:
                signal = self.scan_symbol(symbol)
                if signal:
                    signals.append(signal)
                if i % 10 == 0:
                    time.sleep(1)
            except Exception as e:
                logging.error(f"Erreur lors du scan de {symbol}: {e}")
                continue
        self.detected_signals = signals
        logging.info(f"Scan terminé. {len(signals)} signaux détectés.")
        return signals
    
    def get_new_listings(self) -> List[str]:
        """Détecte les nouveaux coins listés"""
        try:
            current_symbols = set(self.markets_info.keys())
            self.exchange.load_markets()
            new_markets = self.exchange.markets
            new_symbols = set(new_markets.keys())
            truly_new = new_symbols - current_symbols
            if truly_new:
                logging.info(f"Nouveaux listings détectés: {list(truly_new)}")
                self.markets_info = new_markets
                self._identify_futures_symbols()
            return list(truly_new)
        except Exception as e:
            logging.error(f"Erreur lors de la détection des nouveaux listings: {e}")
            return []
