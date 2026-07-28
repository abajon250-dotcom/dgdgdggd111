"""
Клавиатуры для работы с проверкой подписки и меню бота
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


def sub_check_keyboard(channel_username: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для проверки подписки на канал.

    Args:
        channel_username:Username канала (например, "@my_channel")

    Returns:
        InlineKeyboardMarkup с кнопками для подписки и проверки
    """

    # Убираем @ если присутствует
    if channel_username.startswith("@"):
        clean_username = channel_username[1:]
    else:
        clean_username = channel_username

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подписаться на канал",
                    url=f"https://t.me/{clean_username}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Я подписался, проверить ещё раз",
                    callback_data="check_sub"
                )
            ]
        ]
    )


def admin_main_menu() -> InlineKeyboardMarkup:
    """Главное меню администратора"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Инструкция",
                    callback_data="admin_help"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Статистика",
                    callback_data="admin_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ Настройки",
                    callback_data="admin_settings"
                )
            ]
        ]
    )


def user_start_menu() -> InlineKeyboardMarkup:
    """Стартовое меню для пользователя"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 СБП",
                    callback_data="choose_sbp"
                ),
                InlineKeyboardButton(
                    text="📱 Номер телефона",
                    callback_data="choose_phone"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Мои заявки",
                    callback_data="my_applications"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❓ Помощь",
                    callback_data="help"
                )
            ]
        ]
    )


def confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения (Да/Нет)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")
            ]
        ]
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    """Удаляет основную клавиатуру"""
    return ReplyKeyboardRemove()


def application_status_keyboard(app_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура со статусом заявки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Обновить статус",
                    callback_data=f"check_app_status:{app_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить заявку",
                    callback_data=f"cancel_app:{app_id}"
                )
            ]
        ]
    )


def close_keyboard() -> InlineKeyboardMarkup:
    """Кнопка для закрытия сообщения"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✖️ Закрыть",
                    callback_data="close"
                )
            ]
        ]
    )