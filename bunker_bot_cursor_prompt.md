# CURSOR AI — BUNKER TELEGRAM BOT — TO'LIQ LOYIHA

## LOYIHA HAQIDA

Sen menga "Bunker" nomli Telegram group o'yinini to'liq ishlaydigan bot sifatida yozib berishing kerak.
Bunker — bu rus party o'yini bo'lib, apokalipsis ssenariyida o'yinchilar bunkerdagi o'rinlar uchun kurashadi.
O'yin group chatda bo'ladi, lekin har bir o'yinchi o'z kartasini bot bilan shaxsiy (private) suhbatda ko'radi.

---

## TEXNOLOGIYALAR

- **Til**: Python 3.11+
- **Bot framework**: `python-telegram-bot==20.7` (async, webhook ready)
- **Database**: SQLite (lokal) + SQLAlchemy ORM, Railway uchun PostgreSQL ga koʻchirish mumkin
- **Scheduler**: `APScheduler` (timer va countdown uchun)
- **Deploy**: Railway.app (webhook rejimi)
- **Env management**: `python-dotenv`

---

## LOYIHA TUZILMASI

Quyidagi fayl strukturasini to'liq yaratib ber:

```
bunker-bot/
├── bot.py                    # Asosiy kirish nuqtasi, webhook/polling
├── config.py                 # Sozlamalar, env o'zgaruvchilari
├── requirements.txt          # Barcha dependencylar
├── railway.toml              # Railway deploy konfiguratsiyasi
├── Procfile                  # Process fayli
├── .env.example              # Misol env fayli
├── README.md                 # O'rnatish va ishlatish yo'riqnomasi
│
├── game/
│   ├── __init__.py
│   ├── manager.py            # O'yin holati boshqaruvi (GameManager class)
│   ├── models.py             # Ma'lumotlar modellari (dataclass yoki pydantic)
│   ├── cards.py              # Karta generatsiya va kartalar ma'lumot bazasi
│   ├── scenarios.py          # Apokalipsis ssenariylari va bunker tavsifi
│   ├── voting.py             # Ovoz berish logikasi
│   └── actions.py            # Maxsus harakatlar logikasi
│
├── database/
│   ├── __init__.py
│   ├── db.py                 # Database ulanish va sessiya
│   ├── models.py             # SQLAlchemy ORM modellari
│   └── crud.py               # CRUD operatsiyalar
│
├── handlers/
│   ├── __init__.py
│   ├── commands.py           # /start, /help, /newgame, /join, /rules
│   ├── game_handlers.py      # O'yin davomidagi handlerlar
│   ├── voting_handlers.py    # Ovoz berish callback handlerlar
│   └── admin_handlers.py     # Admin buyruqlar
│
└── utils/
    ├── __init__.py
    ├── keyboards.py          # InlineKeyboard va ReplyKeyboard generatorlar
    ├── messages.py           # Barcha bot xabar shablonlari
    └── helpers.py            # Yordamchi funksiyalar
```

---

## O'YIN QOIDALARI (buni to'liq implement qil)

### O'yin boshlanishi
1. Kimdir group chatda `/newgame` yozadi — u HOST bo'ladi
2. Bot group chatga xabar yuboradi: "Yangi Bunker o'yini! Qo'shilish uchun /join yozing"
3. Boshqa o'yinchilar `/join` yozib qo'shiladi (minimum 4, maksimum 10 kishi)
4. Host `/begin` yozganda o'yin boshlanadi (minimum 4 kishi bo'lsa)
5. Qo'shilish vaqti: 3 daqiqa (configdan o'zgartirilsin)

### Karta tarqatish
- O'yin boshlanishi bilan har bir o'yinchiga bot SHAXSIY xabar yuboradi
- Agar o'yinchi botga /start yozmagan bo'lsa, bot group chatga "Iltimos, avval @BotName ga /start yuboring" deb aytadi
- Karta formati shaxsiy xabarda chiroyli emoji bilan ko'rinadi

### O'yinchi kartasi tarkibi (random generatsiya)
Har bir o'yinchi quyidagi atributlarni oladi:
- **Kasb** (50+ variant): Shifokor, Muhandis, Fermer, Psixolog, Harbiy, Oshpaz, IT mutaxassisi, Biolog va h.k.
- **Yosh**: 18-65 orasida random
- **Jins**: Erkak / Ayol
- **Salomatlik**: (masalan) "Mutlaqo sog'lom", "Diabet 2-darajali", "Ko'r", "Allergiya — changga", "Homilador 3 oy" va h.k. (30+ variant)
- **Sevimli mashg'ulot**: "Bog'dorchilik", "Qurol-yaroq ta'mirlash", "Tibbiy yordam", "Ovchilik" va h.k.
- **Yuk / Buyum**: "Birinchi yordam to'plami", "Generator", "Urug'lar to'plami", "Qurol va o'q-dorilar" va h.k.
- **Qo'shimcha xususiyat**: "Kuchli lider", "Paranoid", "Ishonchli", "Janjalkash" va h.k.
- **Fobiya**: "Tor joylardan qo'rqadi", "Qorong'ulikdan qo'rqadi", "Qondan qo'rqadi" va h.k.
- **Maxsus harakat** (x1, faqat bir marta ishlatiladi):
  - `🔄 Karta almashtirish` — kartangizni to'liq yangisiga almashtirish
  - `🔍 Razvedka` — bir o'yinchining to'liq kartasini ko'rish
  - `🛡️ Immunitet` — bu raundda chiqarib bo'lmaydi
  - `🗣️ Extra vaqt` — taqdimot vaqtingizni 30 soniyaga uzaytirish
  - `📢 Fosh qilish` — birovning bir atributini ochiq aytish
  - `🔄 Ovoz bekor` — siz berilgan ovozni bekor qilish (bir marta)

### Apokalipsis ssenariylari (minimum 15 ta turli ssenairy yoz)
Har bir ssenaریda:
- **Nima bo'ldi** (tavsif)
- **Bunker sig'imi** (o'yinchilar sonining yarmi, yaxlitlangan)
- **Bunker resurslari** (suv X oy, oziq-ovqat X oy, elektr bor/yo'q, tibbiy buyumlar)
- **Maxsus shart** (masalan: "Elektr yo'q — IT mutaxassis keraksiz" yoki "Oziq-ovqat kam — fermer muhim")

Ssenariy misollari:
- Yadroviy urush (50 yil yer osti)
- Pandemiya (mutant virus)
- Meteor zarba
- Iqlim faloqati
- Zombi apokalipsisi
- Sun'iy intellekt isyoni
- Vulqon otilishi
- Dengiz sathi ko'tarilishi
- va h.k.

### O'yin bosqichlari (RAUNDLAR)

**Raund 1 — Taqdimot:**
- Har bir o'yinchi o'zini tanishtiradi (botga yozadi, bot group chatga forward qiladi)
- Birinchi raundda faqat KASB va YOSH ochilishi shart (qolganlarni yashirish mumkin)
- Ixtiyoriy: boshqa atributlarni oshkor qilish

**Raund 2+ — Muhokama va ovoz berish:**
- Group chatda erkin muhokama (2-3 daqiqa timer)
- Keyin inline keyboard bilan ovoz berish boshlanadi
- Har bir o'yinchi boshqa o'yinchiga ovoz bera oladi (o'ziga ovoz berish mumkin emas)
- Ovoz anonim (natijalar faqat raund oxirida ko'rinadi)
- Ko'p ovoz olgan kishi chiqariladi (teng bo'lsa, qayta ovoz berish)
- Chiqarilgan o'yinchining TO'LIQ kartasi group chatga ochiladi

**O'yin tugash sharti:**
- Bunkerdagi o'rinlar soni qolgan o'yinchilar soniga teng bo'lganda — qolganlar G'OLIB
- Masalan: 8 o'yinchi, bunker sig'imi 4 → 4 kishi chiqarilganda o'yin tugaydi

### Maxsus harakatlar qoidalari
- Har o'yinchi maxsus harakatni FAQAT BIR MARTA ishlatishi mumkin
- Faqat ovoz berish bosqichida (muhokama vaqtida) ishlatiladi
- `/action` buyrug'i bilan shaxsiy botda ishlatiladi

---

## DATABASE MODELLARI

SQLAlchemy bilan quyidagi modellarni yaratib ber:

```python
# Game — o'yin xonasi
class Game:
    id: int (PK)
    chat_id: int (Telegram group chat ID)
    game_code: str (unikal kod, masalan "BNK-X7K2")
    status: enum ("waiting", "active", "voting", "finished")
    host_user_id: int
    scenario_id: int (FK)
    bunker_capacity: int
    current_round: int
    created_at: datetime
    started_at: datetime
    finished_at: datetime

# Player — o'yinchi
class Player:
    id: int (PK)
    game_id: int (FK)
    user_id: int (Telegram user ID)
    username: str
    full_name: str
    is_alive: bool
    is_host: bool
    card_id: int (FK)
    special_action_used: bool
    elimination_round: int (qaysi raundda chiqarilgan)
    joined_at: datetime

# PlayerCard — o'yinchi kartasi
class PlayerCard:
    id: int (PK)
    player_id: int (FK, unique)
    profession: str
    age: int
    gender: str
    health: str
    hobby: str
    luggage: str
    trait: str
    phobia: str
    special_action: str
    # Qaysi atributlar ochiq
    profession_revealed: bool (default False)
    health_revealed: bool (default False)
    hobby_revealed: bool (default False)
    luggage_revealed: bool (default False)
    trait_revealed: bool (default False)
    phobia_revealed: bool (default False)

# Vote — ovoz
class Vote:
    id: int (PK)
    game_id: int (FK)
    round_number: int
    voter_id: int (FK Player)
    target_id: int (FK Player)
    created_at: datetime

# GameScenario — ssenaری
class GameScenario:
    id: int (PK)
    name: str
    description: str
    water_months: int
    food_months: int
    has_electricity: bool
    has_medical: bool
    special_condition: str
    capacity_formula: str ("half" yoki boshqa)

# PlayerStats — umumiy statistika
class PlayerStats:
    id: int (PK)
    user_id: int (unique)
    total_games: int (default 0)
    wins: int (default 0)
    eliminations: int (default 0)
    special_actions_used: int (default 0)
```

---

## BOT BUYRUQLARI

Quyidagi barcha buyruqlarni implement qil:

### Umumiy buyruqlar (istalgan joyda)
- `/start` — Botni boshlash, ro'yxatdan o'tish (shaxsiy chatda)
- `/help` — Yordam va qoidalar
- `/rules` — O'yin qoidalari (to'liq)
- `/stats` — Shaxsiy statistika (necha marta o'ynagan, g'oliblar soni)

### Guruh buyruqlari
- `/newgame` — Yangi o'yin xonasi yaratish
- `/join` — Mavjud o'yinga qo'shilish
- `/players` — Hozirgi o'yindagi o'yinchilar ro'yxati
- `/begin` — O'yinni boshlash (faqat host, minimum 4 kishi)
- `/endgame` — O'yinni bekor qilish (faqat host yoki admin)
- `/status` — O'yin holati (qaysi raund, necha kishi tirik)

### O'yin davomida (shaxsiy chatda)
- `/card` — O'z kartangni ko'rish
- `/reveal <atribut>` — Atributni ochish (masalan: `/reveal health`)
- `/action` — Maxsus harakatni ishlatish (inline menu ochiladi)

### Admin buyruqlari
- `/admin_games` — Barcha aktiv o'yinlar
- `/admin_end <game_id>` — O'yinni majburiy tugatish
- `/broadcast <xabar>` — Barcha foydalanuvchilarga xabar

---

## KEYBOARD DIZAYNI

### O'yinga qo'shilish:
```
[✅ O'yinga qo'shilish]   [❌ Qo'shilmaslik]
```

### Ovoz berish (inline, har bir tirik o'yinchi ko'rsatiladi):
```
Ovoz berish — kimni chiqaramiz?
[👤 Ali (Shifokor)]
[👤 Vali (Muhandis)]
[👤 Shodmon (Fermer)]
...
```

### Maxsus harakat tanlash:
```
Maxsus harakatingiz: 🛡️ Immunitet
[✅ Ishlatish]   [❌ Bekor qilish]
```

### Atribut ochish (reveal):
```
Qaysi atributni ochmoqchisiz?
[💼 Kasb]  [❤️ Salomatlik]
[🎯 Mashg'ulot]  [🎒 Yuk]
[✨ Xususiyat]  [😱 Fobiya]
```

### O'yin natijasi:
```
[🔄 Qayta o'ynash]   [📊 Statistika]
[🏆 Reyting]
```

---

## XABAR SHABLONLARI

Barcha bot xabarlarini `utils/messages.py` da SAQLASH KERAK.
Xabarlar O'ZBEK TILIDA bo'lsin. Emoji bilan chiroyli formatlab ber.

### Muhim xabarlar (namuna):

**O'yin boshlanishi:**
```
🚨 APOKALIPSIS BOSHLANDI! 🚨

📖 Ssenaریy: {scenario_name}
━━━━━━━━━━━━━━━━━━━━━
{scenario_description}
━━━━━━━━━━━━━━━━━━━━━
🏠 Bunker ma'lumotlari:
💧 Suv: {water_months} oy
🍞 Oziq-ovqat: {food_months} oy
⚡ Elektr: {electricity}
💊 Tibbiy: {medical}

🔑 Maxsus shart:
{special_condition}
━━━━━━━━━━━━━━━━━━━━━
👥 O'yinchilar: {player_count} kishi
🏠 Bunker sig'imi: {capacity} o'rin

Barcha o'yinchilarga karta yuborildi!
Shaxsiy chatingizni tekshiring 👇
```

**Shaxsiy kartа (DM):**
```
🎴 SIZNING KARTANGIZ
━━━━━━━━━━━━━━━━━━━━━
👤 {age} yoshli {gender}
💼 Kasb: {profession}
❤️ Salomatlik: {health}
🎯 Mashg'ulot: {hobby}
🎒 Yuk: {luggage}
✨ Xususiyat: {trait}
😱 Fobiya: {phobia}
━━━━━━━━━━━━━━━━━━━━━
⚡ Maxsus harakat (x1): {special_action}
━━━━━━━━━━━━━━━━━━━━━
💡 Qaysi ma'lumotlarni ochishni o'zingiz hal qiling!
/reveal buyrug'i bilan atributlarni ochasiz.
```

**Ovoz berish natijasi:**
```
📊 {round_number}-RAUND OVOZ BERISH NATIJALARI:
━━━━━━━━━━━━━━━━━━━━━
{results_table}
━━━━━━━━━━━━━━━━━━━━━
😔 {eliminated_name} bunkerdan chiqarildi!

🃏 Uning to'liq kartasi:
{full_card}
```

---

## TIMER LOGIKASI

- O'yinga qo'shilish: **3 daqiqa** (configda o'zgartirilsin)
- Taqdimot vaqti: **2 daqiqa** (har bir raund)
- Muhokama vaqti: **3 daqiqa**
- Ovoz berish vaqti: **1 daqiqa**
- Timer countdown: har 30 soniyada guruhga eslatma yuborilsin
- Vaqt tugaganda avtomatik keyingi bosqichga o'tish

---

## XATOLIKLAR VA EDGE CASE'LAR

Quyidagi holatlarni to'liq handle qil:

1. O'yinchi botga /start yozmagan — karta yuborib bo'lmaydi, guruhga ogohlantirish
2. O'yinchi o'yin davomida guruhdan chiqib ketsa — o'yindan chiqarilgan hisoblansin
3. Host o'yindan chiqib ketsa — random o'yinchi yangi host bo'lsin
4. Teng ovoz bo'lsa — qayta ovoz berish bosqichi
5. Bir o'yinchi ikki marta ovoz berishga urinsa — xatolik xabari
6. O'yin allaqachon boshlanganidan keyin /join — rad etish
7. Guruhda bir vaqtda bir nechta o'yin — har xona alohida chat_id ga bog'liq
8. Maxsus harakatni allaqachon ishlatgan o'yinchi qayta ishlatishga urinsa — rad etish
9. Database ulanish xatosi — graceful error handling

---

## RAILWAY DEPLOY KONFIGURATSIYASI

**railway.toml:**
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python bot.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

**Procfile:**
```
web: python bot.py
```

**requirements.txt (to'liq):**
```
python-telegram-bot==20.7
sqlalchemy==2.0.23
aiosqlite==0.19.0
psycopg2-binary==2.9.9
apscheduler==3.10.4
python-dotenv==1.0.0
aiohttp==3.9.1
```

**.env.example:**
```env
BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite+aiosqlite:///bunker.db
WEBHOOK_URL=https://your-railway-url.railway.app
WEBHOOK_SECRET=your_secret_here
PORT=8080
ADMIN_USER_IDS=123456789,987654321
JOIN_TIMEOUT=180
DISCUSSION_TIMEOUT=180
VOTING_TIMEOUT=60
```

**bot.py da webhook va polling ikkalasi ham ishlashi kerak:**
```python
# Lokal: polling rejimi (WEBHOOK_URL yo'q bo'lsa)
# Railway: webhook rejimi (WEBHOOK_URL bo'lsa)
```

---

## QOLGAN MUHIM TALABLAR

1. **Async/await** — barcha database operatsiyalar va telegram API chaqiruvlari async bo'lsin
2. **Logging** — barcha muhim hodisalar loglansin (o'yin boshlandi, kishi chiqarildi va h.k.)
3. **Config** — barcha sozlamalar (timeout, min/max players) config.py da bo'lsin, hardcode qilinmasin
4. **Error handling** — try/except barcha handlerlarda
5. **Conversation states** — `ConversationHandler` ishlatilmasin, state database da saqlansin
6. **Thread safety** — bir vaqtda bir nechta o'yin bo'lishi mumkin, concurrent access handle qilinsin
7. **Health endpoint** — Railway uchun `/health` HTTP endpoint (aiohttp bilan)
8. **Graceful shutdown** — SIGTERM handle qilsin, o'yinlar to'g'ri to'xtatilsin
9. **README.md** — o'rnatish, lokal ishlatish va Railway deploy qilish yo'riqnomasi

---

## KARTA MA'LUMOTLAR BAZASI (minimum miqdorlar)

`game/cards.py` da quyidagi listlarni to'ldirgin:

- **Kasblar**: minimum 60 ta (turli soha: tibbiyot, muhandislik, qishloq xo'jaligi, harbiy, ijtimoiy, san'at, ilm-fan)
- **Salomatlik holatlari**: minimum 40 ta (sog'lom va kasalliklar, nogironliklar)
- **Mashg'ulotlar**: minimum 40 ta
- **Yuklar/buyumlar**: minimum 40 ta (foydali va foydalisiz ham bo'lsin — muvozanat uchun)
- **Xususiyatlar**: minimum 30 ta (ijobiy va salbiy)
- **Fobiyalar**: minimum 25 ta
- **Maxsus harakatlar**: 6 ta (yuqorida ko'rsatilgan)
- **Ssenariylar**: minimum 15 ta

---

## BONUS FUNKSIYALAR (agar vaqt bo'lsa)

1. **Leaderboard**: `/top10` buyrug'i — haftalik eng ko'p g'alaba qozonganlar
2. **Takroriy o'yin**: O'yin tugagach "Qayta o'ynash" tugmasi
3. **Kuzatuvchi rejimi**: Chiqarilgan o'yinchilar kuzatuvchi sifatida qoladi va boshqalarning kartasini ko'rishi mumkin (lekin ovoz bera olmaydi)
4. **O'yin tarixi**: `/history` — oxirgi 5 ta o'yin natijasi
5. **Inline mode**: `@BotName bunker` yozib istalgan guruhga o'yin havolasini yuborish

---

## ISHNI BOSHLASH

Iltimos, quyidagi tartibda yoz:

1. Avval `requirements.txt` va `config.py`
2. `database/` papkasini to'liq
3. `game/cards.py` va `game/scenarios.py` (ma'lumotlar)
4. `game/models.py` va `game/manager.py` (o'yin logikasi)
5. `game/voting.py` va `game/actions.py`
6. `utils/keyboards.py` va `utils/messages.py`
7. `handlers/` papkasini to'liq
8. `bot.py` (asosiy fayl)
9. Deploy fayllar (`railway.toml`, `Procfile`, `.env.example`)
10. `README.md`

Har bir faylni to'liq yoz, hech narsa qoldirma. Kod ichida izohlar (comments) o'zbek yoki ingliz tilida bo'lsin.
