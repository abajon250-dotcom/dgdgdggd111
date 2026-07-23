from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Сдать номер")],
            [KeyboardButton(text="💳 Запросить СБП")]
        ],
        resize_keyboard=True
    )

def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

def type_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 АДЕНЬГИ", callback_data="type_adengi")],
        [InlineKeyboardButton(text="🔵 МАНИМЕН", callback_data="type_manimen")]
    ])

def admin_sdat_buttons(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Запросить код", callback_data=f"sdat_code_{app_id}_{user_id}")],
        [InlineKeyboardButton(text="❌ Отменить заявку", callback_data=f"sdat_cancel_{app_id}_{user_id}")]
    ])

def admin_sbp_buttons(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Ввести реквизиты СБП", callback_data=f"sbp_req_{app_id}_{user_id}")],
        [InlineKeyboardButton(text="❌ Отменить заявку", callback_data=f"sbp_cancel_{app_id}_{user_id}")]
    ])

def user_code_prompt() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 Ввести код", callback_data="user_enter_code")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="user_cancel")]
    ])

def user_sbp_amount_prompt(app_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я перевел(а) сумму", callback_data=f"sbp_amount_{app_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="user_cancel")]
    ])

def admin_sbp_confirm_buttons(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✔️ Подтвердить выплату", callback_data=f"sbp_confirm_{app_id}_{user_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"sbp_cancel_confirm_{app_id}_{user_id}")]
    ])

def subscribe_check_keyboard(channel_id: str | int) -> InlineKeyboardMarkup:
    kb = []
    channel_str = str(channel_id)
    if channel_str.startswith('@'):
        kb.append([InlineKeyboardButton(text="🔗 Перейти в канал", url=f"https://t.me/{channel_str[1:]}")])
    kb.append([InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subscription")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📋 Список заявок", callback_data="admin_list")],
        [InlineKeyboardButton(text="📨 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🔒 Закрыть", callback_data="admin_close")]
    ])