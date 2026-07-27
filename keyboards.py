from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu() -> ReplyKeyboardMarkup:
    """Главная клавиатура бота для обычных пользователей"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои заявки"), KeyboardButton(text="➕ Создать заявку")],
            [KeyboardButton(text="ℹ️ Информация"), KeyboardButton(text="📞 Поддержка")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню..."
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены действия"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )


def main_service_menu() -> InlineKeyboardMarkup:
    """Главный выбор категории: СБП или Номера"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 СБП", callback_data="category_sbp")],
        [InlineKeyboardButton(text="📱 Номера (Сдать номер)", callback_data="category_numbers")]
    ])


def sbp_type_inline() -> InlineKeyboardMarkup:
    """Выбор сервиса для СБП: АДЕНЬГИ или МАНИМЕН"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 АДЕНЬГИ (СБП)", callback_data="service_sbp_adengi")],
        [InlineKeyboardButton(text="🔥 МАНИМЕН (СБП)", callback_data="service_sbp_manimen")]
    ])


def numbers_type_inline() -> InlineKeyboardMarkup:
    """Выбор сервиса для Номеров: АДЕНЬГИ или МАНИМЕН"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 АДЕНЬГИ (Номер)", callback_data="service_num_adengi")],
        [InlineKeyboardButton(text="🔥 МАНИМЕН (Номер)", callback_data="service_num_manimen")]
    ])


def subscribe_check_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    """Клавиатура проверки подписки на канал"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url=channel_url)],
        [InlineKeyboardButton(text="✅ Я подписался(-ась)", callback_data="check_subscribe")]
    ])


def admin_sdat_buttons(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Кнопки управления заявкой для админа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔑 Запросить код", callback_data=f"sdat_code_{app_id}_{user_id}"),
            InlineKeyboardButton(text="✅ Завершить", callback_data=f"sdat_complete_{app_id}_{user_id}")
        ],
        [
            InlineKeyboardButton(text="❌ Отменить заявку", callback_data=f"sdat_cancel_{app_id}_{user_id}")
        ]
    ])


def admin_sbp_buttons(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Кнопки управления заявкой «СБП» для админа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Отправить реквизиты", callback_data=f"sbp_req_{app_id}_{user_id}"),
            InlineKeyboardButton(text="💰 Запросить сумму", callback_data=f"sbp_sum_{app_id}_{user_id}")
        ],
        [
            InlineKeyboardButton(text="✅ Завершить", callback_data=f"sbp_complete_{app_id}_{user_id}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"sbp_cancel_{app_id}_{user_id}")
        ]
    ])


def admin_sbp_confirm_buttons(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Кнопки подтверждения перевода СБП"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить перевод", callback_data=f"sbp_confirm_{app_id}_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"sbp_cancel_confirm_{app_id}_{user_id}")
        ]
    ])


def user_code_prompt() -> InlineKeyboardMarkup:
    """Кнопка для ввода кода пользователем"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ввести код", callback_data="user_enter_code")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="user_cancel")]
    ])


def user_sbp_amount_prompt(app_id: int) -> InlineKeyboardMarkup:
    """Кнопки отправки суммы СБП пользователем"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я перевел(а) сумму", callback_data=f"sbp_amount_{app_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="user_cancel")]
    ])