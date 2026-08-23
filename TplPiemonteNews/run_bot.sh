#!/usr/bin/env bash

# Script di esecuzione del Bot TPL Piemonte (Telegram + WhatsApp)
PROJECT_DIR="/home/antonio/TplPiemonteNews"

export TELEGRAM_BOT_TOKEN="8836154487:AAFfg-uQuqUlB7sb4VradYzzljyFGKnLzVU"
export TELEGRAM_CHAT_ID="@TplPiemonteNews"

# Configurazioni WhatsApp (opzionali - compila quando hai l'API WhatsApp)
# export WHATSAPP_API_URL="https://gate.whapi.cloud/messages/text" # Esempio provider API WhatsApp
# export WHATSAPP_TOKEN="IL_TUO_TOKEN_WHATSAPP"
# export WHATSAPP_CHANNEL_ID="120363xxxxxx@newsletter" # ID canale o gruppo WhatsApp

cd "$PROJECT_DIR" || exit 1
"$PROJECT_DIR/venv/bin/python3" "$PROJECT_DIR/bot.py" >> "$PROJECT_DIR/bot.log" 2>&1
