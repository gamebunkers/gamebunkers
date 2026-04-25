from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def join_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ O'yinga qo'shilish", callback_data="join_yes"), InlineKeyboardButton("❌ Qo'shilmaslik", callback_data="join_no")]])


def voting_keyboard(players: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"👤 {name}", callback_data=f"vote:{pid}")] for pid, name in players])


def action_keyboard(action_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ Ishlatish", callback_data=f"action_confirm:{action_name}"), InlineKeyboardButton("❌ Bekor qilish", callback_data="action_cancel")]])


def reveal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💼 Kasb", callback_data="reveal:profession"), InlineKeyboardButton("❤️ Salomatlik", callback_data="reveal:health")],
        [InlineKeyboardButton("🎯 Mashg'ulot", callback_data="reveal:hobby"), InlineKeyboardButton("🎒 Yuk", callback_data="reveal:luggage")],
        [InlineKeyboardButton("✨ Xususiyat", callback_data="reveal:trait"), InlineKeyboardButton("😱 Fobiya", callback_data="reveal:phobia")],
    ])
