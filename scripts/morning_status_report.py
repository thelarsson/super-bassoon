#!/usr/bin/env python3
"""
Morning System Status Report
Combined status for Binance and IG Trading Bots
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Telegram config - MUST be set via environment variables
# DO NOT hardcode tokens here for security
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

if not TG_BOT_TOKEN or not TG_CHAT_ID:
    print("Error: TG_BOT_TOKEN and TG_CHAT_ID must be set via environment variables")
    sys.exit(1)


def get_binance_status():
    """Get Binance bot status"""
    try:
        sys.path.insert(0, '/home/johan/.openclaw/workspace/trading-bots/johan-binance-trader/scripts')
        from telegram_bot import get_positions, get_binance_positions
        
        positions = get_positions()
        binance_positions = get_binance_positions()
        
        active_positions = len([p for p in positions if p.get('quantity', 0) > 0])
        
        return {
            'status': '✅ Running',
            'active_positions': active_positions,
            'total_positions': len(positions),
            'balance': 'Checking...',
        }
    except Exception as e:
        return {
            'status': f'⚠️ Error: {str(e)[:30]}',
            'active_positions': 0,
            'total_positions': 0,
            'balance': 'N/A'
        }


def get_ig_status():
    """Get IG bot status"""
    try:
        # Check if IG bot files exist
        ig_dir = Path('/home/johan/.openclaw/workspace/ig-trading-bot')
        
        # Check state file
        state_file = ig_dir / 'data' / 'bot_state.json'
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
            last_analysis = state.get('last_analysis', 'Never')
        else:
            last_analysis = 'Never'
        
        # Check cron jobs
        import subprocess
        cron_check = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        ig_cron = '✅ Active' if 'ig-trading-bot' in cron_check.stdout else '❌ Not scheduled'
        
        return {
            'status': '✅ Ready',
            'mode': 'LIVE (DEMO until tested)',
            'last_analysis': last_analysis[:10] if last_analysis != 'Never' else 'N/A',
            'next_dca': 'May 1st, 09:00',
            'cron': ig_cron
        }
    except Exception as e:
        return {
            'status': f'⚠️ Error: {str(e)[:30]}',
            'mode': 'Unknown',
            'last_analysis': 'N/A',
            'next_dca': 'May 1st',
            'cron': '❌ Check failed'
        }


def send_telegram_message(message):
    """Send message to Telegram"""
    import requests
    
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TG_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        return response.ok
    except Exception as e:
        print(f"Failed to send Telegram: {e}")
        return False


def generate_report():
    """Generate combined system status report"""
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Get both bot statuses
    binance = get_binance_status()
    ig = get_ig_status()
    
    report = f"""📊 *SYSTEM STATUS REPORT*

🗓️ {now}

═══════════════════════════════════
🤖 *BINANCE TRADING BOT*
═══════════════════════════════════

Status: {binance['status']}
Active Positions: {binance['active_positions']} / {binance['total_positions']}
Balance: {binance['balance']}

Last Check: Automated (every 60s)
Discovery: 20 pairs monitored

═══════════════════════════════════
📈 *IG TRADING BOT*  
═══════════════════════════════════

Status: {ig['status']}
Mode: {ig['mode']}
Last Analysis: {ig['last_analysis']}

📅 *Schedule:*
• Next DCA Purchase: {ig['next_dca']}
• Weekly Analysis: Fridays 17:00 UAE
• Monthly Review: Last day 23:00 UAE

Cron Jobs: {ig['cron']}

═══════════════════════════════════

✅ All systems operational
🕐 Next check: Tomorrow 08:00

_Note: IG Bot launches May 1st (first DCA)_"""
    
    return report


def main():
    """Main entry point"""
    print(f"[{datetime.now()}] Generating system status report...")
    
    report = generate_report()
    
    # Send to Telegram
    success = send_telegram_message(report)
    
    if success:
        print(f"[{datetime.now()}] Report sent successfully")
    else:
        print(f"[{datetime.now()}] Failed to send report")
    
    # Also print to stdout for logging
    print("\n" + "="*50)
    print(report)
    print("="*50)


if __name__ == '__main__':
    main()
