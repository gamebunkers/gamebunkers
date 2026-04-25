# Bunker Telegram Bot

Uzbek tilida Telegram group uchun Bunker o'yini boti.

## O'rnatish

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` faylda `BOT_TOKEN` kiriting.

## Ishga tushirish

```bash
python bot.py
```

- `WEBHOOK_URL` bo'sh bo'lsa polling.
- `WEBHOOK_URL` bo'lsa webhook.

## Buyruqlar

- Umumiy: `/start`, `/help`, `/rules`, `/stats`
- Guruh: `/newgame`, `/join`, `/players`, `/begin`, `/status`, `/endgame`
- Private: `/card`, `/reveal <attribute>`
- Admin: `/admin_games`, `/admin_end <game_id>`, `/broadcast <xabar>`

## Railway

`railway.toml` va `Procfile` tayyor.
