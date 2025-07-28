English Readme is under French :

# 🚀 KuCoin EMA Scanner & Auto Trader

Un programme Python avancé pour scanner automatiquement les cryptomonnaies sur KuCoin et exécuter des trades basés sur les signaux EMA20 avec gestion automatique des Stop Loss et Take Profits via les niveaux de Fibonacci.

## ✨ Fonctionnalités

### 🔍 Scanner Intelligent
- **Scan temps réel** de tous les coins sur KuCoin
- **Détection EMA20** : Identifie les coins qui franchissent leur EMA20 en timeframe 4h
- **Filtre volume** : Détecte les augmentations de volume >50% par rapport à la bougie précédente
- **Filtre futures** : Ne sélectionne que les coins avec contrats perpétuels disponibles
- **Nouveaux listings** : Surveillance continue des nouveaux coins listés

### 💰 Trading Automatisé
- **Ordres intelligents** : Placement automatique d'ordres d'achat avec SL/TP
- **Fibonacci intégré** : Calcul automatique des niveaux TP basés sur les retracements/extensions Fibonacci (timeframe 15min)
- **Gestion des risques** : Stop Loss configurables et Take Profits multiples (TP1, TP2, TP3)
- **Taille de position adaptative** : Calcul automatique basé sur le risque défini

### 🖥️ Interface Utilisateur
- **Interface Streamlit** moderne et intuitive
- **Dashboard en temps réel** avec métriques de performance
- **Configuration flexible** : Paramétrage complet des stratégies
- **Logs détaillés** : Suivi de toutes les transactions et signaux
- **Graphiques de performance** : Visualisation des résultats

## 📦 Installation

### Prérequis
- Python 3.8 ou supérieur
- Compte KuCoin avec API activée
- TA-Lib installé sur votre système

### Installation des dépendances

```bash
# Cloner le projet
git clone <repository-url>
cd kucoin-ema-scanner

# Installer les dépendances Python
pip install -r requirements.txt

# Installation de TA-Lib (requis pour l'analyse technique)
# Sur Windows : télécharger le wheel depuis https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
# Sur macOS : brew install ta-lib
# Sur Ubuntu/Debian : sudo apt-get install libta-lib-dev
```

## ⚙️ Configuration

### 1. Configuration API KuCoin

Créez un fichier `.env` à la racine du projet :

```env
# Configuration KuCoin API
KUCOIN_API_KEY=your_api_key_here
KUCOIN_API_SECRET=your_api_secret_here
KUCOIN_PASSPHRASE=your_passphrase_here
KUCOIN_SANDBOX=true  # false pour le trading réel

# Configuration optionnelle
LOG_LEVEL=INFO
```

### 2. Obtenir les clés API KuCoin

1. Connectez-vous à votre compte [KuCoin](https://www.kucoin.com)
2. Allez dans **API Management** dans les paramètres
3. Créez une nouvelle API avec les permissions :
   - **General** (lecture du compte)
   - **Trade** (placement d'ordres)
   - **Futures** (accès aux contrats à terme)
4. Notez bien votre **Passphrase** lors de la création
5. Configurez les restrictions IP si nécessaire

### 3. Configuration des paramètres

Le fichier `config.py` contient tous les paramètres configurables :

```python
# Scanner
SCAN_INTERVAL = 60  # Intervalle de scan en secondes
VOLUME_THRESHOLD = 50  # Seuil d'augmentation du volume en %
EMA_PERIOD = 20  # Période EMA

# Trading
DEFAULT_POSITION_SIZE = 100  # Taille de position en USDT
DEFAULT_SL_PERCENT = 2.0  # Stop Loss en %
TP1_PERCENT = 1.5  # Take Profit 1 en %
TP2_PERCENT = 3.0  # Take Profit 2 en %
TP3_PERCENT = 5.0  # Take Profit 3 en %
```

## 🚀 Utilisation

### Lancement du programme

```bash
# Lancer l'interface graphique
streamlit run main.py

# Ou directement
python main.py
```

### Tests préliminaires

```bash
# Vérifier l'installation et la configuration
python main.py --test

# Afficher l'aide
python main.py --help
```

### Utilisation de l'interface

1. **Configuration** : Ajustez les paramètres dans la barre latérale
2. **Démarrage** : Cliquez sur "▶️ Démarrer" pour lancer le scanner automatique
3. **Surveillance** : Consultez l'onglet "🎯 Signaux" pour voir les détections
4. **Trading** : Exécutez les trades manuellement ou configurez l'automatisation
5. **Suivi** : Surveillez vos positions dans "💼 Trades Actifs"

## 📊 Structure du Projet

```
/kucoin-ema-scanner/
├── main.py              # Point d'entrée principal
├── scanner.py           # Logic de scan et détection des signaux
├── trading.py           # Gestion des ordres et du trading
├── gui.py              # Interface utilisateur Streamlit
├── config.py           # Configuration globale
├── requirements.txt    # Dépendances Python
├── README.md          # Documentation
├── .env               # Variables d'environnement (à créer)
└── trading.log        # Fichier de logs (généré automatiquement)
```

## 🛡️ Stratégie de Trading

### Critères de Détection
1. **EMA20 Crossover** : Le prix franchit l'EMA20 à la hausse sur timeframe 4h
2. **Volume Spike** : Augmentation du volume >50% par rapport à la bougie précédente
3. **Contrat Future** : Le coin doit avoir un contrat perpétuel disponible sur KuCoin

### Gestion des Positions
- **Entrée** : Ordre au marché lors de la détection du signal
- **Stop Loss** : Calculé automatiquement (défaut : 2% sous le prix d'entrée)
- **Take Profits** : 3 niveaux basés sur les extensions de Fibonacci
  - TP1 : 1/3 de la position (niveau 1.272 ou 1.5% par défaut)
  - TP2 : 1/3 de la position (niveau 1.414 ou 3% par défaut)  
  - TP3 : 1/3 de la position (niveau 1.618 ou 5% par défaut)

### Calcul Fibonacci
- **Timeframe** : 15 minutes pour plus de précision
- **Swing Points** : Détection automatique des hauts/bas récents
- **Niveaux utilisés** :
  - Extensions : 1.272, 1.414, 1.618, 2.0, 2.618
  - Retracements : 0.236, 0.382, 0.5, 0.618, 0.786

## 📈 Fonctionnalités Avancées

### Scanner en Temps Réel
- Surveillance continue de tous les marchés KuCoin
- Détection automatique des nouveaux listings
- Filtrage intelligent des signaux de qualité

### Interface Dashboard
- **Métriques en temps réel** : Solde, positions, performance
- **Graphiques interactifs** : Évolution des P&L, historique des trades
- **Logs détaillés** : Traçabilité complète des opérations
- **Configuration dynamique** : Modification des paramètres sans redémarrage

### Gestion des Risques
- **Position Sizing** : Calcul automatique basé sur le risque défini
- **Stop Loss adaptatif** : Ajustement selon la volatilité du marché
- **Take Profits échelonnés** : Réduction progressive du risque
- **Limite de drawdown** : Protection contre les pertes importantes

## ⚠️ Avertissements et Risques

### Risques du Trading Automatisé
- **Pertes financières** : Le trading comportes des risques de perte en capital
- **Volatilité** : Les cryptomonnaies sont extrêmement volatiles
- **Bugs logiciels** : Aucun programme n'est exempt d'erreurs
- **Conditions de marché** : Les stratégies peuvent ne pas fonctionner dans tous les environnements

### Bonnes Pratiques
1. **Testez d'abord en sandbox** avant le trading réel
2. **Commencez avec de petits montants** pour valider la stratégie
3. **Surveillez régulièrement** les positions ouvertes
4. **Sauvegardez vos clés API** en sécurité
5. **Gardez le logiciel à jour** pour les correctifs de sécurité

### Recommandations de Sécurité
- Utilisez des clés API avec permissions limitées
- Configurez des restrictions IP sur vos clés API
- Ne partagez jamais vos clés API ou passphrase
- Utilisez un VPN si vous tradez depuis des réseaux publics
- Gardez des sauvegardes de votre configuration

## 🔧 Dépannage

### Problèmes Courants

**Erreur "Exchange non initialisé"**
- Vérifiez vos clés API dans le fichier `.env`
- Assurez-vous que les permissions API sont correctes
- Testez la connexion avec `python main.py --test`

**Erreur "TA-Lib non trouvé"**
- Installez TA-Lib pour votre système d'exploitation
- Redémarrez votre environnement Python après installation

**Aucun signal détecté**
- Vérifiez que le seuil de volume n'est pas trop élevé
- Assurez-vous que les marchés sont actifs (heures de trading)
- Consultez les logs pour identifier d'éventuelles erreurs

**Interface Streamlit ne se charge pas**
- Vérifiez que le port 8501 n'est pas utilisé
- Essayez `streamlit run main.py --server.port 8502`
- Videz le cache avec `streamlit cache clear`

## 📚 API et Documentation

### KuCoin API
- [Documentation officielle](https://docs.kucoin.com/)
- [Limites de taux](https://docs.kucoin.com/#request-rate-limit)
- [Code d'erreur](https://docs.kucoin.com/#errors)

### Bibliothèques Utilisées
- **CCXT** : Connexion aux exchanges de cryptomonnaies
- **TA-Lib** : Analyse technique et calculs d'indicateurs
- **Pandas** : Manipulation et analyse de données
- **Streamlit** : Interface utilisateur web
- **Plotly** : Graphiques interactifs

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet  
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

### Idées d'Améliorations
- Support d'autres exchanges (Binance, OKX, etc.)
- Stratégies de trading additionnelles
- Backtesting intégré
- Notifications (Discord, Telegram, email)
- Mode paper trading
- API REST pour intégrations externes

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour obtenir de l'aide :

1. **Issues GitHub** : Signalez les bugs et demandez des fonctionnalités
2. **Discussions** : Posez vos questions dans les discussions GitHub
3. **Documentation** : Consultez ce README et les commentaires du code

## 🏆 Remerciements

- **KuCoin** pour leur API robuste et bien documentée
- **CCXT** pour l'excellente bibliothèque d'accès aux exchanges
- **Streamlit** pour l'outil de création d'interfaces web en Python
- **La communauté open source** pour les nombreuses bibliothèques utilisées

---

**⚠️ Avertissement Final :** Ce logiciel est fourni "tel quel" sans aucune garantie. L'utilisation de ce programme pour le trading de cryptomonnaies comporte des risques financiers importants. Les utilisateurs sont entièrement responsables de leurs décisions de trading et de toute perte financière qui pourrait en résulter. Tradez uniquement avec des fonds que vous pouvez vous permettre de perdre.

---

# 🚀 KuCoin EMA Scanner & Auto Trader

An advanced Python program to automatically scan cryptocurrencies on KuCoin and execute trades based on EMA20 signals, with automatic Stop Loss and Take Profit management using Fibonacci levels.

## ✨ Features

### 🔍 Smart Scanner

* **Real-time scanning** of all coins on KuCoin
* **EMA20 Detection**: Identifies coins crossing their 4h EMA20
* **Volume filter**: Detects volume increases >50% compared to the previous candle
* **Futures filter**: Only selects coins with available perpetual contracts
* **New listings**: Continuous monitoring of newly listed coins

### 💰 Automated Trading

* **Smart orders**: Automatic placement of buy orders with SL/TP
* **Built-in Fibonacci**: Automatic calculation of TP levels based on Fibonacci retracements/extensions (15min timeframe)
* **Risk management**: Configurable Stop Loss and multiple Take Profits (TP1, TP2, TP3)
* **Adaptive position sizing**: Automatically calculated based on defined risk

### 🖥️ User Interface

* **Modern, intuitive Streamlit interface**
* **Real-time dashboard** with performance metrics
* **Flexible configuration**: Fully customizable strategies
* **Detailed logs**: Tracks all trades and signals
* **Performance charts**: Visualization of results

## 📦 Installation

### Prerequisites

* Python 3.8 or higher
* KuCoin account with API enabled
* TA-Lib installed on your system

### Installing Dependencies

```bash
# Clone the project
git clone <repository-url>
cd kucoin-ema-scanner

# Install Python dependencies
pip install -r requirements.txt

# TA-Lib installation (required for technical analysis)
# On Windows: download the wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
# On macOS: brew install ta-lib
# On Ubuntu/Debian: sudo apt-get install libta-lib-dev
```

## ⚙️ Configuration

### 1. KuCoin API Configuration

Create a `.env` file in the root of the project:

```env
# KuCoin API configuration
KUCOIN_API_KEY=your_api_key_here
KUCOIN_API_SECRET=your_api_secret_here
KUCOIN_PASSPHRASE=your_passphrase_here
KUCOIN_SANDBOX=true  # false for live trading

# Optional configuration
LOG_LEVEL=INFO
```

### 2. Get KuCoin API Keys

1. Log into your [KuCoin](https://www.kucoin.com) account
2. Go to **API Management** in settings
3. Create a new API with permissions:

   * **General** (account read access)
   * **Trade** (order placement)
   * **Futures** (access to futures contracts)
4. Note your **Passphrase** during creation
5. Configure IP restrictions if necessary

### 3. Strategy Configuration

The `config.py` file contains all configurable parameters:

```python
# Scanner
SCAN_INTERVAL = 60  # Scan interval in seconds
VOLUME_THRESHOLD = 50  # Volume increase threshold in %
EMA_PERIOD = 20  # EMA period

# Trading
DEFAULT_POSITION_SIZE = 100  # Position size in USDT
DEFAULT_SL_PERCENT = 2.0  # Stop Loss in %
TP1_PERCENT = 1.5  # Take Profit 1 in %
TP2_PERCENT = 3.0  # Take Profit 2 in %
TP3_PERCENT = 5.0  # Take Profit 3 in %
```

## 🚀 Usage

### Launch the Program

```bash
# Launch the graphical interface
streamlit run main.py

# Or directly
python main.py
```

### Preliminary Tests

```bash
# Check installation and configuration
python main.py --test

# Display help
python main.py --help
```

### Using the Interface

1. **Configuration**: Adjust settings in the sidebar
2. **Start**: Click "▶️ Start" to launch the auto-scanner
3. **Monitoring**: View the "🎯 Signals" tab for detections
4. **Trading**: Execute trades manually or enable automation
5. **Tracking**: Monitor your positions in "💼 Active Trades"

## 📊 Project Structure

```
/kucoin-ema-scanner/
├── main.py              # Main entry point
├── scanner.py           # Scan logic and signal detection
├── trading.py           # Order and trading management
├── gui.py               # Streamlit user interface
├── config.py            # Global configuration
├── requirements.txt     # Python dependencies
├── README.md            # Documentation
├── .env                 # Environment variables (to create)
└── trading.log          # Log file (auto-generated)
```

## 🛡️ Trading Strategy

### Detection Criteria

1. **EMA20 Crossover**: Price crosses above EMA20 on 4h timeframe
2. **Volume Spike**: Volume increases >50% compared to the previous candle
3. **Futures Contract**: The coin must have a perpetual contract available on KuCoin

### Position Management

* **Entry**: Market order upon signal detection
* **Stop Loss**: Automatically calculated (default: 2% below entry price)
* **Take Profits**: 3 levels based on Fibonacci extensions

  * TP1: 1/3 of position (level 1.272 or 1.5% default)
  * TP2: 1/3 of position (level 1.414 or 3% default)
  * TP3: 1/3 of position (level 1.618 or 5% default)

### Fibonacci Calculation

* **Timeframe**: 15 minutes for precision
* **Swing Points**: Automatic detection of recent highs/lows
* **Used Levels**:

  * Extensions: 1.272, 1.414, 1.618, 2.0, 2.618
  * Retracements: 0.236, 0.382, 0.5, 0.618, 0.786

## 📈 Advanced Features

### Real-Time Scanner

* Continuous monitoring of all KuCoin markets
* Automatic detection of new listings
* Smart filtering of high-quality signals

### Dashboard Interface

* **Real-time metrics**: Balance, positions, performance
* **Interactive charts**: P\&L evolution, trade history
* **Detailed logs**: Full traceability of operations
* **Dynamic configuration**: Modify parameters without restarting

### Risk Management

* **Position sizing**: Automatically calculated based on defined risk
* **Adaptive Stop Loss**: Adjusted according to market volatility
* **Staggered Take Profits**: Gradual risk reduction
* **Drawdown limit**: Protection from significant losses

## ⚠️ Warnings and Risks

### Risks of Automated Trading

* **Financial loss**: Trading carries the risk of capital loss
* **Volatility**: Cryptocurrencies are extremely volatile
* **Software bugs**: No software is bug-free
* **Market conditions**: Strategies may not work in all environments

### Best Practices

1. **Test in sandbox first** before going live
2. **Start with small amounts** to validate the strategy
3. **Monitor open positions regularly**
4. **Keep your API keys secure**
5. **Keep the software updated** for security patches

### Security Recommendations

* Use API keys with limited permissions
* Configure IP restrictions for your API keys
* Never share your API keys or passphrase
* Use a VPN when trading from public networks
* Keep backups of your configuration

## 🔧 Troubleshooting

### Common Issues

**"Exchange not initialized" error**

* Check your API keys in the `.env` file
* Ensure correct API permissions
* Test the connection with `python main.py --test`

**"TA-Lib not found" error**

* Install TA-Lib for your OS
* Restart your Python environment after installation

**No signals detected**

* Check if volume threshold is too high
* Make sure markets are active (during trading hours)
* Consult logs to identify potential errors

**Streamlit interface not loading**

* Check if port 8501 is occupied
* Try `streamlit run main.py --server.port 8502`
* Clear cache with `streamlit cache clear`

## 📚 API and Documentation

### KuCoin API

* [Official documentation](https://docs.kucoin.com/)
* [Rate limits](https://docs.kucoin.com/#request-rate-limit)
* [Error codes](https://docs.kucoin.com/#errors)

### Libraries Used

* **CCXT**: Connection to cryptocurrency exchanges
* **TA-Lib**: Technical analysis and indicator calculations
* **Pandas**: Data manipulation and analysis
* **Streamlit**: Web-based user interface
* **Plotly**: Interactive charts

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

### Improvement Ideas

* Support for other exchanges (Binance, OKX, etc.)
* Additional trading strategies
* Built-in backtesting
* Notifications (Discord, Telegram, email)
* Paper trading mode
* REST API for external integrations

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## 🆘 Support

For help:

1. **GitHub Issues**: Report bugs and request features
2. **Discussions**: Ask questions in GitHub Discussions
3. **Documentation**: Refer to this README and code comments

## 🏆 Acknowledgments

* **KuCoin** for their robust and well-documented API
* **CCXT** for the excellent exchange library
* **Streamlit** for making Python web UIs easy
* **The open-source community** for countless libraries used

---

**⚠️ Final Disclaimer:** This software is provided "as is" with no warranty. Using this tool for cryptocurrency trading carries significant financial risk. Users are fully responsible for their trading decisions and any financial loss incurred. Only trade with funds you can afford to lose.

---
