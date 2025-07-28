import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    # Configuration KuCoin API
    KUCOIN_API_KEY = os.getenv('KUCOIN_API_KEY', '')
    KUCOIN_API_SECRET = os.getenv('KUCOIN_API_SECRET', '')
    KUCOIN_PASSPHRASE = os.getenv('KUCOIN_PASSPHRASE', '')
    KUCOIN_SANDBOX = os.getenv('KUCOIN_SANDBOX', 'False').lower() == 'False'
    
    # Configuration du scanner
    SCAN_INTERVAL = 60  # Intervalle de scan en secondes
    VOLUME_THRESHOLD = 150  # Seuil d'augmentation du volume en %
    EMA_PERIOD = 20  # Période EMA
    TIMEFRAME_MAIN = '4h'  # Timeframe principal pour EMA
    TIMEFRAME_FIBONACCI = '15m'  # Timeframe pour Fibonacci
    
    # Configuration des ordres
    DEFAULT_POSITION_SIZE = 100  # Taille de position par défaut en USDT
    RISK_REWARD_RATIO = 2.0  # Ratio risque/rendement
    
    # Niveaux Fibonacci
    FIBONACCI_LEVELS = {
        'retracement': [0.236, 0.382, 0.5, 0.618, 0.786],
        'extension': [1.272, 1.414, 1.618, 2.0, 2.618]
    }
    
    # Configuration Stop Loss / Take Profit
    DEFAULT_SL_PERCENT = 2.0  # Stop Loss en %
    DEFAULT_LEVERAGE = 1.0 #Effet de Levier
    TP1_PERCENT = 1.5  # Take Profit 1 en %
    TP2_PERCENT = 3.0  # Take Profit 2 en %
    TP3_PERCENT = 5.0  # Take Profit 3 en %
    
    # Configuration logging
    LOG_LEVEL = 'NOTSET'
    LOG_FILE = 'trading.log'