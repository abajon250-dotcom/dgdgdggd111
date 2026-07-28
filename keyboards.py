from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu(is_admin: bool = False):
    keyboard = [
        [KeyboardButton(text="➕ Создать заявку"), KeyboardButton(text="📂 Мои заявки")],
        [KeyboardButton(text="📞 Поддержка")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="👑 Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def sub_check_keyboard(channel_username: str):
    clean_username = channel_username[1:] if channel_username.startswith("@") else channel_username
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{clean_username}")],
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

def admin_buttons(app_id: int, user_id: int, is_sbp: bool = False):
    if is_sbp:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💳 Выдать реквизиты", callback_data=f"admin_req_sbp:{app_id}:{user_id}")],
                [InlineKeyboardButton(text="✅ Завершить", callback_data=f"admin_done:{app_id}:{user_id}")],
                [InlineKeyboardButton(text="❌ Отменить", callback_data=f"admin_cancel:{app_id}:{user_id}")]
            ]
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📲 Запросить код", callback_data=f"admin_req_code:{app_id}:{user_id}")],
            [InlineKeyboardButton(text="✅ Завершить", callback_data=f"admin_done:{app_id}:{user_id}")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data=f"admin_cancel:{app_id}:{user_id}")]
        ]
    )