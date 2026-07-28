"""
Клавиатуры для работы с проверкой подписки и меню бота
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def main_menu() -> ReplyKeyboardMarkup:
    """Главное Reply-меню пользователя внизу экрана"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Создать заявку"), KeyboardButton(text="📂 Мои заявки")],
            [KeyboardButton(text="📞 Поддержка")]
        ],
        resize_keyboard=True
    )


def sub_check_keyboard(channel_username: str) -> InlineKeyboardMarkup:
    """Клавиатура для проверки подписки на канал."""
    clean_username = channel_username[1:] if channel_username.startswith("@") else channel_username

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Подписаться на канал",
                    url=f"https://t.me/{clean_username}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Я подписался(-ась)",
                    callback_data="check_sub"
                )
            ]
        ]
    )


def main_service_menu() -> InlineKeyboardMarkup:
    """Меню выбора категорий заявок"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 СБП (Аденьги / Манимен)", callback_data="category_sbp")],
            [InlineKeyboardButton(text="📱 Сдать номер (Аденьги / Манимен)", callback_data="category_numbers")]
        ]
    )


def sbp_type_inline() -> InlineKeyboardMarkup:
    """Выбор сервиса для СБП"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔹 Аденьги (СБП)", callback_data="service_sbp_adengi")],
            [InlineKeyboardButton(text="🔹 Манимен (СБП)", callback_data="service_sbp_manimen")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main_menu")]
        ]
    )


def numbers_type_inline() -> InlineKeyboardMarkup:
    """Выбор сервиса для номера"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔹 Аденьги (Номер)", callback_data="service_num_adengi")],
            [InlineKeyboardButton(text="🔹 Манимен (Номер)", callback_data="service_num_manimen")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main_menu")]
        ]
    )


def admin_buttons(app_id: int, user_id: int, is_sbp: bool = False) -> InlineKeyboardMarkup:
    """Интерактивные кнопки администратора в приватном канале уведомлений"""
    if is_sbp:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💳 Запросить реквизиты", callback_data=f"admin_req_sbp:{app_id}:{user_id}")],
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


def admin_main_menu() -> InlineKeyboardMarkup:
    """Главное меню администратора"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Инструкция", callback_data="admin_help")],
            [InlineKeyboardButton(text="👥 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings")]
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


def close_keyboard() -> InlineKeyboardMarkup:
    """Кнопка для закрытия сообщения"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✖️ Закрыть", callback_data="close")]
        ]
    )