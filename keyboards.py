from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Создать заявку"), KeyboardButton(text="📂 Мои заявки")],
            [KeyboardButton(text="📞 Поддержка")]
        ],
        resize_keyboard=True
    )

def sub_check_keyboard(channel_username: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{channel_username.lstrip('@')}")],
            [InlineKeyboardButton(text="🔄 Я подписался(-ась)", callback_data="check_sub")]
        ]
    )

def main_service_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 СБП (Аденьги / Манимен)", callback_data="category_sbp")],
            [InlineKeyboardButton(text="📱 Сдать номер (Аденьги / Манимен)", callback_data="category_numbers")]
        ]
    )

def sbp_type_inline():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔹 Аденьги (СБП)", callback_data="service_sbp_adengi")],
            [InlineKeyboardButton(text="🔹 Манимен (СБП)", callback_data="service_sbp_manimen")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main_menu")]
        ]
    )

def numbers_type_inline():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔹 Аденьги (Номер)", callback_data="service_num_adengi")],
            [InlineKeyboardButton(text="🔹 Манимен (Номер)", callback_data="service_num_manimen")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main_menu")]
        ]
    )

def admin_sbp_buttons(app_id: int, user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Запросить реквизиты", callback_data=f"admin_req_sbp:{app_id}:{user_id}")],
            [InlineKeyboardButton(text="✅ Завершить", callback_data=f"admin_done:{app_id}:{user_id}")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data=f"admin_cancel:{app_id}:{user_id}")]
        ]
    )

def admin_sdat_buttons(app_id: int, user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📲 Запросить код", callback_data=f"admin_req_code:{app_id}:{user_id}")],
            [InlineKeyboardButton(text="✅ Завершить", callback_data=f"admin_done:{app_id}:{user_id}")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data=f"admin_cancel:{app_id}:{user_id}")]
        ]
    )

def admin_buttons(app_id: int, user_id: int, is_sbp: bool = False):
    if is_sbp:
        return admin_sbp_buttons(app_id, user_id)
    return admin_sdat_buttons(app_id, user_id)