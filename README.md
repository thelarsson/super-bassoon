# IG Trading Bot

## Översikt
En professionell trading bot för **långsiktig tillväxt** med IG.com. Fokuserar på Dollar-Cost Averaging (DCA) och trendföljning med ETF:er och blue-chip aktier.

**Viktigt:** Denna bot handlar med **cash equities** (riktiga aktier/ETF:er), INTE CFD:er eller hävstålade produkter.

---

## 🎯 Strategi

- **Dollar-Cost Averaging (DCA):** Investerar fast belopp varje månad oavsett pris
- **Trendanalys:** Använder EMA 50/200 för att identifiera marknadstrender
- **Riskhantering:** Hård stop-loss (-10%), take-profit (+25%)
- **Sektordiversifiering:** Upp till 5 olika tillgångar, max 20% per position

---

## 📁 Filstruktur

```
ig-trading-bot/
├── scripts/
│   ├── config.py              # Konfiguration och inställningar
│   ├── ig_client.py           # IG API wrapper
│   ├── main.py                # Huvudprogram (entry point)
│   ├── strategy.py            # DCA och trend strategi
│   ├── position_manager.py    # Portföljhantering
│   ├── notifier.py            # Telegram notifikationer
│   ├── weekly_analyzer.py     # Veckoanalys (fre 17:00)
│   ├── market_research.py     # Marknadsanalys och research
│   ├── longterm_backtest.py   # Historisk backtesting
│   └── pdf_generator.py       # PDF rapport-generering
├── .env.template              # Mall för miljövariabler
├── .env                       # Dina API-nycklar (skapa denna)
├── reports/                   # Genererade rapporter
├── data/                      # Sparad data och state
└── logs/                      # Loggfiler
```

---

## 🚀 Installation

### 1. Förkrav

```bash
# Python 3.8+
python3 --version

# Installera beroenden
pip install -r requirements.txt
```

### 2. Krav på Python-paket

Skapa `requirements.txt`:

```
requests>=2.28.0
pandas>=1.5.0
numpy>=1.23.0
python-dotenv>=0.20.0
yfinance>=0.2.0
fpdf2>=2.7.0
matplotlib>=3.6.0
```

Installera:
```bash
pip install -r requirements.txt
```

### 3. Konfiguration

1. Kopiera mallen:
```bash
cp .env.template .env
```

2. Fyll i dina uppgifter i `.env`:
```bash
# IG API (från IG Labs)
IG_API_KEY=din_api_nyckel
IG_IDENTIFIER=ditt_användarnamn
IG_PASSWORD=ditt_lösenord
IG_ACCOUNT_ID=ditt_konto_id

# Telegram (från @BotFather)
TG_BOT_TOKEN=din_bot_token
TG_CHAT_ID=ditt_chat_id

# Trading inställningar
DCA_AMOUNT=2500              # AED per månad
DCA_DAY=1                    # Dag i månaden
MAX_POSITION_PCT=20          # Max % per tillgång
STOP_LOSS_PERCENTAGE=-10     # Stop-loss nivå
TAKE_PROFIT_PERCENTAGE=25    # Take-profit nivå
```

### 4. IG Konto

1. Skapa IG-konto på [ig.com](https://www.ig.com)
2. Aktivera API-access (IG Labs)
3. Börja med **DEMO-läge** (`USE_DEMO=true`)

---

## 🎮 Användning

### Manuell körning

```bash
cd scripts

# Kör huvudprogrammet
python3 main.py

# Kör veckoanalys
python3 weekly_analyzer.py

# Kör backtest
python3 longterm_backtest.py
```

### Schemalagd körning (Cron)

Lägg till i crontab:

```bash
# Öppna crontab
 crontab -e

# Daglig check (08:00 UAE)
0 8 * * * cd /path/to/ig-trading-bot && python3 scripts/main.py >> logs/cron.log 2>&1

# Veckoanalys (fredag 17:00 UAE)
0 13 * * 5 cd /path/to/ig-trading-bot && python3 scripts/weekly_analyzer.py >> logs/weekly.log 2>&1
```

---

## 📊 Funktioner

### 1. DCA (Dollar-Cost Averaging)
- Köper för konstant belopp varje månad
- Tar bort emotionella beslut
- Fungerar bra över lång tid (år)

### 2. Trendanalys
- EMA 50/200 crossover
- BULLISH/BEARISH/NEUTRAL signaler
- Används för att justera DCA-timing

### 3. Riskhantering
- **Stop-loss:** -10% (skyddar mot stora förluster)
- **Take-profit:** +25% (låser in vinster)
- **Max position:** 20% per tillgång (diversifiering)
- **Trailing stops:** Skyddar vinster när priset stiger

### 4. Veckoanalys
- Körs varje fredag 17:00 UAE
- Analyserar alla ETF:er
- Skickar Telegram-sammanfattning
- Sparar tillstånd i JSON

### 5. Backtesting
- Testar strategier på historisk data (5-10 år)
- Jämför DCA vs Lump Sum
- Visar avkastning, volatilitet, max drawdown

### 6. PDF Rapporter
- Professionella veckorapporter
- Backtest-resultat
- Portföljsammanfattningar

---

## 🛡️ Säkerhet

### Viktiga säkerhetsfunktioner:

1. **Ingen mock data** - Om API nere, stoppas bot (ingen handel på fejkdata)
2. **Demo-läge default** - Börja alltid med testkonto
3. **Validering** - Alla order valideras innan de skickas
4. **Max-gränser** - Hårda gränser för positioner och förluster
5. **Logging** - Alla händelser loggas för audit

### Risker att vara medveten om:

- **Marknadsrisk:** Aktier kan gå ner i värde
- **Likviditetsrisk:** Vissa ETF:er kan ha låg omsättning
- **API-risk:** IG eller Yahoo Finance kan vara otillgängliga
- **Teknisk risk:** Buggar i kod (testa noga i demo!)

---

## 📈 Tillgångar

### Standard ETF:er:
- **SPY** - S&P 500 (bred USA-marknad)
- **QQQ** - Nasdaq 100 (tech-tung)
- **VTI** - Total Stock Market (hela USA)
- **VXUS** - Internationella aktier
- **BND** - Obligationsfond

### Blue-chip aktier:
- **AAPL** - Apple
- **MSFT** - Microsoft
- **GOOGL** - Alphabet (Google)

---

## 🔧 Konfigurationsalternativ

### I `.env` filen:

| Variabel | Standard | Beskrivning |
|----------|----------|-------------|
| `DCA_AMOUNT` | 2500 | Månadsinvestering (AED) |
| `DCA_DAY` | 1 | Vilken dag i månaden |
| `MAX_POSITION_PCT` | 20 | Max % per tillgång |
| `MAX_POSITIONS` | 5 | Max antal tillgångar |
| `STOP_LOSS` | -10 | Stop-loss % |
| `TAKE_PROFIT` | 25 | Take-profit % |
| `TRAILING_STOP` | true | Aktivera trailing stop |
| `REBALANCE_FREQUENCY` | monthly | Rebalansering: monthly/quarterly |

---

## 📝 Exempel på Telegram-notiser

### DCA Köp:
```
📈 Monthly DCA Purchase

AAPL: $500 @ $175.50
Units: 2.85
Portfolio: 18% → 20%
```

### Stop-loss:
```
🚨 Stop-loss Triggered

MSFT sold @ $320.50
Entry: $340.00
Loss: -5.7%

Action: Funds returned to cash
```

### Veckosammanfattning:
```
📊 Weekly Analysis - 2024-01-15

SPY: 🟢 BULLISH - HOLD
QQQ: 🟢 BULLISH - REDUCE (High RSI)
VTI: 🟡 NEUTRAL - HOLD

Market Outlook: Cautiously Optimistic
Action: Maintain positions
```

---

## 🧪 Testning

### Innan live-trading:

1. **Demo-konto** - Kör minst 1 månad i demo
2. **Backtest** - Testa på 5-10 års historik
3. **Unit tests** - Kör testerna:
```bash
python3 -m pytest tests/
```

### Manuella tester:

```bash
# Testa veckoanalys
python3 scripts/weekly_analyzer.py --force

# Testa backtest
python3 scripts/longterm_backtest.py

# Testa PDF
python3 scripts/pdf_generator.py
```

---

## 📚 Resurser

- [IG API Documentation](https://labs.ig.com/)
- [Yahoo Finance Python](https://pypi.org/project/yfinance/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

## ⚠️ Disclaimer

**Viktigt:** Detta är en experimentell trading bot. Använd på egen risk. 

- **Inga garantier** för avkastning
- **Förluster kan överstiga** insatsen (teoretiskt, med stop-loss minimal)
- **Testa alltid** i demo-läge först
- **Övervaka** boten regelbundet
- **Ha en plan** för när saker går fel

---

## 🔧 Felsökning

### Vanliga problem:

**"IG API authentication failed"**
- Kontrollera credentials i `.env`
- Verifiera att API-access är aktiverat på IG

**"No data returned for ETF"**
- Kontrollera ticker-symbol
- Yahoo Finance kan ha avbrott

**"Telegram message failed"**
- Kontrollera bot token
- Verifiera chat ID

**"ImportError: No module named yfinance"**
- Kör: `pip install yfinance`

---

## 🤝 Bidrag

Detta är ett personligt projekt, men förbättringar är välkomna!

---

## 📄 Licens

MIT License - Se LICENSE fil

---

## Kontakt

För frågor eller support, kontakta via Telegram bot.

---

**Senast uppdaterad:** 2026-04-06
**Version:** 1.0.0
**Skapare:** Qwen2.5:14b, GLM-5:cloud & Claude
