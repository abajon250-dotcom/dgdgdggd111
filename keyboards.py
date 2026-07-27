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


def subscribe_check_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    """Клавиатура проверки подписки на канал"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url=channel_url)],
        [InlineKeyboardButton(text="✅ Я подписался(-ась)", callback_data="check_subscribe")]
    ])


def admin_sdat_buttons(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Интерактивные кнопки управления заявкой «Сдать номер» для админа"""
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
    """Интерактивные кнопки управления заявкой «СБП» для админа"""
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