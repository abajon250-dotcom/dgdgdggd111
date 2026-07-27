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
        [InlineKeyboardButton(text="💎 АДЕНЬГИ", callback_data="type_adengi")],
        [InlineKeyboardButton(text="🔥 МАНИМЕН", callback_data="type_manimen")]
    ])

def admin_sdat_buttons(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Кнопки управления сдачей номера с ID и эмодзи."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔑 [ID: {app_id}] Запросить код", callback_data=f"sdat_code_{app_id}_{user_id}")],
        [InlineKeyboardButton(text=f"🚫 [ID: {app_id}] Отмена", callback_data=f"sdat_cancel_{app_id}_{user_id}")]
    ])

def admin_sbp_buttons(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Кнопки управления СБП с ID и эмодзи."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 [ID: {app_id}] Ввести реквизиты", callback_data=f"sbp_req_{app_id}_{user_id}")],
        [InlineKeyboardButton(text=f"🚫 [ID: {app_id}] Отмена", callback_data=f"sbp_cancel_{app_id}_{user_id}")]
    ])

def user_code_prompt() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ввести код", callback_data="user_enter_code")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="user_cancel")]
    ])

def user_sbp_amount_prompt(app_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я перевел(а) сумму", callback_data=f"sbp_amount_{app_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="user_cancel")]
    ])

def admin_sbp_confirm_buttons(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ [ID: {app_id}] Подтвердить выплату", callback_data=f"sbp_confirm_{app_id}_{user_id}")],
        [InlineKeyboardButton(text=f"🚫 [ID: {app_id}] Отмена", callback_data=f"sbp_cancel_confirm_{app_id}_{user_id}")]
    ])

def admin_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📋 Список заявок", callback_data="admin_list")],
        [InlineKeyboardButton(text="📨 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="admin_close")]
    ])