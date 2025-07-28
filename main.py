#!/usr/bin/env python3
"""
KuCoin EMA Scanner & Auto Trader
================================

Programme principal pour scanner les cryptomonnaies sur KuCoin
et exécuter des trades automatiques basés sur les signaux EMA20.

Auteur: Assistant IA
Version: 1.0.0
"""

import sys
import os
import logging
from pathlib import Path

# Ajouter le répertoire courant au path Python
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Imports locaux
from config import Config
from scanner import KuCoinScanner
from trading import KuCoinTrader
from gui import TradingGUI

def setup_logging():
    """Configure le système de logging global"""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Réduire le niveau de logging pour les librairies externes
    logging.getLogger('ccxt').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    required_packages = [
        'ccxt', 'pandas', 'numpy', 'talib', 'streamlit', 
        'plotly', 'dotenv', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dépendances manquantes:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Installez-les avec: pip install -r requirements.txt")
        return False
    
    return True

def check_api_configuration():
    """Vérifie la configuration des clés API"""
    if not Config.KUCOIN_API_KEY or not Config.KUCOIN_API_SECRET or not Config.KUCOIN_PASSPHRASE:
        print("⚠️  Configuration API incomplète!")
        print("Veuillez configurer vos clés API KuCoin dans l'interface ou via un fichier .env")
        print("\nVariables d'environnement requises:")
        print("- KUCOIN_API_KEY")
        print("- KUCOIN_API_SECRET") 
        print("- KUCOIN_PASSPHRASE")
        return False
    
    return True

def create_env_template():
    """Crée un fichier .env template s'il n'existe pas"""
    env_file = Path('.env')
    
    if not env_file.exists():
        template = """# Configuration KuCoin API
KUCOIN_API_KEY=your_api_key_here
KUCOIN_API_SECRET=your_api_secret_here
KUCOIN_PASSPHRASE=your_passphrase_here
KUCOIN_SANDBOX=true

# Configuration optionnelle
LOG_LEVEL=INFO
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"📝 Fichier .env template créé: {env_file.absolute()}")
        print("Veuillez le remplir avec vos clés API KuCoin.")

def run_tests():
    """Execute des tests de base pour vérifier le fonctionnement"""
    print("🧪 Exécution des tests de base...")
    
    try:
        # Test 1: Initialisation du scanner
        print("   Test 1: Initialisation scanner... ", end="")
        scanner = KuCoinScanner()
        if scanner.exchange is None and Config.KUCOIN_API_KEY:
            print("❌ Échec - Vérifiez vos clés API")
            return False
        print("✅ OK")
        
        # Test 2: Initialisation du trader
        print("   Test 2: Initialisation trader... ", end="")
        trader = KuCoinTrader()
        print("✅ OK")
        
        # Test 3: Chargement des marchés (si API configurée)
        if Config.KUCOIN_API_KEY and scanner.exchange:
            print("   Test 3: Chargement marchés... ", end="")
            try:
                scanner.load_markets()
                print(f"✅ OK ({len(scanner.markets_info)} marchés)")
            except Exception as e:
                print(f"❌ Échec - {e}")
                return False
        
        print("✅ Tous les tests sont passés!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

def print_banner():
    """Affiche la bannière du programme"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🚀 KuCoin EMA Scanner & Auto Trader v1.0             ║
    ║                                                              ║
    ║        Détection automatique des signaux EMA20              ║
    ║        Trading automatisé avec SL/TP Fibonacci              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_usage():
    """Affiche les instructions d'utilisation"""
    print("""
📋 Instructions d'utilisation:

1. 🔧 Configuration:
   - Remplissez le fichier .env avec vos clés API KuCoin
   - Ou configurez-les directement dans l'interface Streamlit

2. 🚀 Lancement:
   - Interface graphique: streamlit run main.py
   - Tests: python main.py --test
   - Aide: python main.py --help

3. 📊 Utilisation:
   - Configurez vos paramètres dans la barre latérale
   - Démarrez le scanner automatique
   - Surveillez les signaux détectés
   - Exécutez les trades manuellement ou automatiquement

⚠️  AVERTISSEMENT:
Ce programme peut exécuter des trades réels avec votre argent.
Testez d'abord en mode sandbox et utilisez des montants raisonnables.
    """)

def main():
    """Fonction principale"""
    # Analyser les arguments de ligne de commande
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h']:
            print_banner()
            print_usage()
            return
        
        elif arg in ['--test', '-t']:
            print_banner()
            setup_logging()
            create_env_template()
            
            if not check_dependencies():
                sys.exit(1)
            
            if not run_tests():
                sys.exit(1)
            
            print("\n✅ Tous les tests sont passés! Vous pouvez maintenant lancer l'interface:")
            print("   streamlit run main.py")
            return
        
        elif arg in ['--version', '-v']:
            print("KuCoin EMA Scanner & Auto Trader v1.0.0")
            return
    
    # Lancement normal de l'application
    print_banner()
    
    # Configuration initiale
    setup_logging()
    create_env_template()
    
    # Vérifications
    if not check_dependencies():
        sys.exit(1)
    
    # Logger le démarrage
    logging.info("=" * 60)
    logging.info("Démarrage de KuCoin EMA Scanner & Auto Trader")
    logging.info("=" * 60)
    
    try:
        # Lancer l'interface Streamlit
        print("🚀 Lancement de l'interface Streamlit...")
        print("📊 Ouvrez votre navigateur à l'adresse: http://localhost:8501")
        print("⏹️  Appuyez sur Ctrl+C pour arrêter")
        
        # Importer et lancer l'interface
        gui = TradingGUI()
        gui.run()
        
    except KeyboardInterrupt:
        print("\n👋 Arrêt du programme par l'utilisateur")
        logging.info("Programme arrêté par l'utilisateur")
    
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        logging.error(f"Erreur critique: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        logging.info("Arrêt du programme")

if __name__ == "__main__":
    main()