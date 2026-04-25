def game_created(host: str) -> str:
    return f"🎮 Yangi Bunker o'yini!\nHost: {host}\nQo'shilish uchun /join"


def join_success(name: str) -> str:
    return f"✅ {name} o'yinga qo'shildi"


def game_start_announcement(scenario, player_count: int, capacity: int) -> str:
    electricity = "Bor" if scenario.has_electricity else "Yo'q"
    medical = "Bor" if scenario.has_medical else "Yo'q"
    return (
        "🚨 APOKALIPSIS BOSHLANDI! 🚨\n"
        f"📖 Ssenariy: {scenario.name}\n"
        f"{scenario.description}\n\n"
        f"💧 Suv: {scenario.water_months} oy\n🍞 Oziq-ovqat: {scenario.food_months} oy\n"
        f"⚡ Elektr: {electricity}\n💊 Tibbiy: {medical}\n\n"
        f"🔑 Shart: {scenario.special_condition}\n"
        f"👥 O'yinchilar: {player_count}\n🏠 Sig'im: {capacity}"
    )


def card_message(card) -> str:
    return (
        "🎴 SIZNING KARTANGIZ\n"
        f"👤 {card.age} yoshli {card.gender}\n"
        f"💼 Kasb: {card.profession}\n❤️ Salomatlik: {card.health}\n"
        f"🎯 Mashg'ulot: {card.hobby}\n🎒 Yuk: {card.luggage}\n"
        f"✨ Xususiyat: {card.trait}\n😱 Fobiya: {card.phobia}\n"
        f"⚡ Maxsus: {card.special_action}"
    )


def not_private_started(bot_username: str) -> str:
    return f"⚠️ Avval @{bot_username} ga private chatda /start yozing"


def help_text() -> str:
    return """📚 Buyruqlar:
/start /help /rules /stats
/newgame /join /players /begin /status /endgame
/card /reveal <attribute> /action
"""


def rules_text() -> str:
    return "Bunker qoidasi: eng foydali o'yinchilar bunkerda qoladi, qolganlar ovoz bilan chiqariladi."
