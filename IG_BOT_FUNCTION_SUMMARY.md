# IG Trading Bot - Funktionsöversikt
## Sammanfattning för icke-teknisk användare

---

## 📋 Översikt
Denna trading bot är designad för **långsiktig tillväxt** med IG.com. Den handlar med riktiga aktier och ETF:er (inte CFD:er eller hävstål).

**Strategi:** Dollar-Cost Averaging (DCA) + Trendföljning

---

## 🔧 Fil 1: config.py (Konfiguration)

### Vad den gör:
Denna fil innehåller alla inställningar för boten. Den läser från en `.env` fil där du sparar dina lösenord och API-nycklar.

### Viktiga inställningar:

| Inställning | Standardvärde | Vad det betyder |
|-------------|---------------|-----------------|
| **DCA_AMOUNT** | €500 | Hur mycket pengar boten investerar varje månad |
| **DCA_DAY** | 1 | Vilken dag i månaden (1-31) som köpet görs |
| **MAX_POSITION_PCT** | 20% | Maximal del av portföljen i en enda aktie/ETF |
| **MAX_POSITIONS** | 5 | Max antal olika aktier/ETF:er att äga samtidigt |
| **STOP_LOSS** | -10% | Om en aktie faller 10%, säljs den automatiskt (skydd) |
| **TAKE_PROFIT** | +25% | Om en aktie stiger 25%, säljs den (ta vinst) |
| **MIN_CASH_BUFFER** | €1000 | Minsta kontantbehållning, inte investeras |

### Vilka tillgångar som handlas:
- **SPY** - S&P 500 ETF (bred marknad)
- **QQQ** - Nasdaq 100 ETF (teknologi)
- **VTI** - Total Stock Market ETF (hela marknaden)
- **VXUS** - Internationella aktier
- **BND** - Obligationsfond
- **AAPL, MSFT, GOOGL** - Blåsippor (Apple, Microsoft, Alphabet)

---

## 🔧 Fil 2: ig_client.py (IG API Anslutning)

### Vad den gör:
Denna fil hanterar kommunikationen med IG.com's server. Den loggar in, hämtar information och skickar köp/sälj-order.

### Viktiga funktioner:

#### 🔐 authenticate()
- **Vad:** Loggar in på IG med dina uppgifter
- **Varför:** Nödvändigt för att kunna handla
- **Säkerhet:** Skapar en "token" som är giltig en begränsad tid

#### 📊 get_account_info()
- **Vad:** Hämtar information om ditt konto
- **Visar:** Kontosaldo, tillgängliga medel, realiserad/inte realiserad vinst

#### 📋 get_positions()
- **Vad:** Visar alla dina öppna positioner (vad du äger just nu)
- **Visar:** Aktie, antal, inköpspris, nuvarande värde, vinst/förlust

#### 🛒 place_order()
- **Vad:** Skickar köp- eller sälj-order till marknaden
- **Parametrar:**
  - Vilken aktie (market_id)
  - Köp eller sälj (direction)
  - Hur många (size)
  - Stop-loss nivå (stop_distance)
  - Take-profit nivå (limit_distance)

#### 🔍 search_market()
- **Vad:** Letar upp en akties "epic" kod från dess namn
- **Exempel:** "AAPL" → hittar rätt marknad-ID hos IG

#### ⏱️ rate_limit()
- **Vad:** Väntar 1 sekund mellan API-anrop
- **Varför:** IG begränsar hur ofta man kan anropa deras API

---

## 🔧 Fil 3: strategy.py (Strategi och Beslut)

### Vad den gör:
Denna fil innehåller "hjärnan" i boten. Den beslutar NÄR och VAD som ska köpas/säljas.

### Viktiga funktioner:

#### 💰 dca_logic()
- **Vad:** Kollar om det är dags för månatligt DCA-köp
- **Hur:** Jämför dagens datum med DCA_DAY-inställningen
- **Exempel:** Om DCA_DAY=1 och idag är den 1:a, då är det dags att köpa

#### 📈 trend_analyzer()
- **Vad:** Analyserar om marknaden är i uppåt- eller nedåttrend
- **Hur:** Använder EMA (Exponential Moving Average)
  - EMA 50 = snitt över 50 dagar
  - EMA 200 = snitt över 200 dagar
- **Signal:** Om EMA50 > EMA200 = uppåttrend (bra att köpa)

#### ⚖️ rebalancing()
- **Vad:** Kollar om portföljen behöver rebalanseras
- **Hur:** Jämför nuvarande fördelning med målfördelning
- **Exempel:** Om en aktie växt från 20% till 30%, säljs en del

#### 📊 get_historical_data()
- **Vad:** Hämtar historiska priser för beräkningar
- **Hur:** Anropar IG's API för prishistorik

---

## 🔧 Fil 4: position_manager.py (Portföljhantering)

### Vad den gör:
Denna fil håller koll på vad du äger, beräknar hur mycket du kan köpa, och övervakar stop-loss/take-profit.

### Viktiga funktioner:

#### 💾 load_positions() & save_positions()
- **Vad:** Läser och sparar din portfölj till en JSON-fil
- **Varför:** Så boten kommer ihåg vad du äger mellan körningar
- **Fil:** `data/positions.json`

#### 📏 calculate_position_size()
- **Vad:** Räknar ut hur många aktier du kan köpa
- **Hur:** 
  1. Tar totala portföljvärdet
  2. Räknar ut max 20% (MAX_POSITION_PCT)
  3. Delar med aktiepriset
  4. Avrundar neråt till hela aktier

#### 🚨 check_stop_losses_and_take_profits()
- **Vad:** Kollar om någon aktie nått stop-loss eller take-profit
- **Hur:** Jämför nuvarande pris med inköpspris
- **Åtgärd:** Skickar sälj-order om gräns nådd

#### 🔄 update_trailing_stops()
- **Vad:** Uppdaterar "trailing stop-loss"
- **Hur:** Om aktien stiger, flyttas stop-loss uppåt
- **Exempel:** Köpte för €100, stop-loss vid €90. Aktien stiger till €120 → stop-loss flyttas till €110 (skyddar vinst)

---

## 🔧 Fil 5: notifier.py (Telegram Notiser)

### Vad den gör:
Skickar meddelanden till din Telegram när saker händer.

### Viktiga funktioner:

#### 📱 send_dca_purchase_notification()
- **När:** Varje månad när DCA-köp görs
- **Meddelande:** "Monthly DCA purchase: SPY - €500"

#### 🚨 send_stop_loss_take_profit_alert()
- **När:** När stop-loss eller take-profit triggas
- **Meddelande:** "Stoploss triggered for AAPL" eller "Takeprofit triggered for MSFT"

#### 📊 send_weekly_portfolio_summary()
- **När:** En gång per vecka
- **Visar:** Total portföljvärde, innehav, veckans förändring

#### ⚖️ send_rebalancing_alert()
- **När:** När rebalansering behövs
- **Meddelande:** "Rebalancing needed: AAPL overweight by 8%"

#### 💬 send_telegram_message()
- **Vad:** Grundfunktion som skickar alla meddelanden
- **Hur:** Anropar Telegram's API med din bot-token

---

## 🔧 Fil 6: main.py (Huvudprogrammet)

### Vad den gör:
Detta är "startknappen". Den sätter igång allt och koordinerar de andra filerna.

### Viktiga funktioner:

#### 📝 initialize_logging()
- **Vad:** Sätter upp loggning
- **Varför:** Alla händelser sparas i `logs/ig_bot.log`
- **Användning:** Felsökning och historik

#### 📅 daily_checks()
- **Vad:** Körs varje dag
- **Gör:**
  1. Kollar om DCA-dag (köper om ja)
  2. Kollar alla positioner för stop-loss/take-profit
  3. Uppdaterar trailing stops

#### 📆 monthly_tasks()
- **Vad:** Körs varje månad
- **Gör:**
  1. Rebalansering av portföljen
  2. Uppdaterar månadsstatistik

#### 🚀 Main execution
- **Vad:** Startar hela boten
- **Flöde:**
  1. Initierar loggning
  2. Skapar position manager
  3. Skapar strategi
  4. Skapar notifier
  5. Kör dagliga kontroller
  6. Kör månatliga uppgifter
  7. Sparar allt
  8. Hanterar fel

---

## 🔄 Arbetsflöde (Hur boten jobbar)

```
1. START (varje dag)
   ↓
2. Logga in på IG
   ↓
3. Kolla om det är DCA-dag?
   → JA: Köp för €500 av varje tillgång i listan
   → NEJ: Gå vidare
   ↓
4. Kolla alla öppna positioner
   → Om stop-loss nådd (-10%): Sälj
   → Om take-profit nådd (+25%): Sälj
   → Uppdatera trailing stops
   ↓
5. En gång per månad:
   → Rebalansera portföljen
   ↓
6. Skicka notifieringar till Telegram
   ↓
7. Spara allt och avsluta
```

---

## 🛡️ Säkerhetsfunktioner

1. **Demo-läge som standard** - Börja med testkonto
2. **Max 20% per tillgång** - Riskspridning
3. **Max 5 positioner** - Koncentration
4. **€1000 kontantbuffert** - Reserv
5. **Stop-loss på -10%** - Skydd mot stora förluster
6. **Ingen hävstål** - Endast cash-aktier
7. **Loggning av allt** - Full transparens

---

## ⚠️ Viktigt att komma ihåg

- Boten handlar **aktier/ETF:er**, inte CFD:er
- **Ingen hävstål** - du äger verkliga tillgångar
- **Långsiktigt fokus** - veckor, månader, år
- **DCA-strategi** - köp regelbundet oavsett pris
- **Rebalansering** - håll portföljen balanserad

---

## 📝 Nästa steg för att komma igång

1. Skapa IG-konto (demo först)
2. Skaffa API-nyckel från IG
3. Fyll i `.env` filen med dina uppgifter
4. Testa i demo-läge
5. När allt fungerar: byt till live-läge

---

*Genererad: 2026-04-06*
*Av: Qwen2.5:14b och Claude*
