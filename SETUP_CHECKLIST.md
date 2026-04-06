# IG Trading Bot - Setup Checklista

## ✅ Vad är klart:
- [x] All kod skriven (10 filer)
- [x] Tester skapade
- [x] Dokumentation färdig
- [x] Cron-jobb konfigurerat

## ❌ Vad behövs göra:

### 1. Telegram Bot Setup
- [ ] Skapa NY bot via @BotFather ( separat från Binance boten)
- [ ] Få token
- [ ] Få chat ID
- [ ] Uppdatera .env filen

### 2. IG Konto
- [ ] Skapa IG-konto på ig.com
- [ ] Aktivera API-access (IG Labs)
- [ ] Få API-nyckel
- [ ] Få account ID
- [ ] Uppdatera .env filen

### 3. Testa Backtesting
```bash
cd /home/johan/.openclaw/workspace/ig-trading-bot
python3 scripts/longterm_backtest.py
```

### 4. GitHub
- [ ] Skapa nytt repo på GitHub
- [ ] Pusha all kod
- [ ] Lägg till README

---

## 🔧 Detaljerade instruktioner:

### 1. Telegram Bot för IG

**VIKTIGT:** Använd INTE samma bot som för Binance!

1. Gå till @BotFather på Telegram
2. Skriv `/newbot`
3. Följ instruktionerna
4. Spara token (t.ex. `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Få chat ID via @userinfobot
6. Uppdatera `.env`:
   ```
   TG_BOT_TOKEN=din_nya_token
   TG_CHAT_ID=ditt_chat_id
   ```

### 2. IG Konto Setup

1. Gå till https://www.ig.com
2. Skapa konto (välj "CFD Trading" för att få API-access)
3. Logga in på IG Labs: https://labs.ig.com/
4. Skapa API-nyckel
5. Hitta ditt Account ID (i kontoinställningar)
6. Uppdatera `.env`:
   ```
   IG_API_KEY=din_api_nyckel
   IG_IDENTIFIER=ditt_användarnamn
   IG_PASSWORD=ditt_lösenord
   IG_ACCOUNT_ID=ditt_konto_id
   ```

### 3. Kör Backtest

```bash
# Gå till mappen
cd /home/johan/.openclaw/workspace/ig-trading-bot

# Installera beroenden
pip install -r requirements.txt

# Kör backtest
python3 scripts/longterm_backtest.py

# Resultat sparas i reports/backtest_results.json
```

### 4. Pusha till GitHub

```bash
cd /home/johan/.openclaw/workspace/ig-trading-bot

# Initiera git
git init

# Lägg till alla filer
git add .

# Commit
git commit -m "Initial IG Trading Bot setup"

# Lägg till remote (byt ut med ditt repo)
git remote add origin https://github.com/ditt-användarnamn/ig-trading-bot.git

# Pusha
git push -u origin master
```

---

## 🚨 VIKTIGT:

**Innan du kör live:**
1. ✅ Använd alltid `USE_DEMO=true` först!
2. ✅ Testa i minst 1 vecka i demo
3. ✅ Verifiera att Telegram-notiser fungerar
4. ✅ Kontrollera att backtesting ger rimliga resultat

**Säkerhet:**
- `.env` filen ska INTE pushas till GitHub (ligger i .gitignore)
- API-nycklar är hemliga - dela aldrig!

---

Vill du att jag ska hjälpa dig med något av stegen ovan? 🎯
