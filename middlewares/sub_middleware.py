import logging
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery, ChatMember
from typing import Callable, Dict, Any, Awaitable
from config import CHANNEL_USERNAME, CHANNEL_ID
from keyboards import sub_check_keyboard

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    """
    Middleware для проверки подписки пользователя на канал.

    Пропускает:
    - Команду /start
    - Callback-кнопку "check_sub"
    - Администратора (по необходимости раскомментировать)
    """

    # Команды и callback-данные, которые не требуют проверки подписки
    SKIP_COMMANDS = {"/start", "/help"}
    SKIP_CALLBACKS = {"check_sub"}

    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:

        user = event.from_user
        if not user:
            return await handler(event, data)

        # ===== ПРОПУСКАЕМ КОМАНДУ /start =====
        if isinstance(event, Message):
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)

        # ===== ПРОПУСКАЕМ КНОПКУ ПРОВЕРКИ ПОДПИСКИ =====
        if isinstance(event, CallbackQuery):
            if event.data == "check_sub":
                return await handler(event, data)

        # ===== ПРОВЕРЯЕМ ПОДПИСКУ =====
        bot: Bot = data["bot"]
        is_subscribed = await self._check_subscription(bot, user.id)

        if not is_subscribed:
            await self._send_subscription_warning(event, bot)
            return  # Прерываем обработку события

        # Если подписан - продолжаем обработку
        return await handler(event, data)

    async def _check_subscription(self, bot: Bot, user_id: int) -> bool:
        """
        Проверяет подписку пользователя на канал.

        Args:
            bot: экземпляр бота
            user_id: ID пользователя

        Returns:
            True если подписан, False если нет
        """
        try:
            # Пытаемся проверить по username
            member = await bot.get_chat_member(
                chat_id=CHANNEL_USERNAME,
                user_id=user_id
            )

            # Статусы подписчика
            if member.status in ["creator", "administrator", "member"]:
                logger.info(f"✅ Пользователь {user_id} подписан (статус: {member.status})")
                return True

            # Ограниченный доступ (может быть и подписан и не подписан)
            if member.status == "restricted":
                logger.warning(f"⚠️ Пользователь {user_id} имеет ограниченный доступ")
                return True  # Пропускаем ограниченных пользователей

            # Отписан или заблокирован
            logger.info(f"❌ Пользователь {user_id} не подписан (статус: {member.status})")
            return False

        except Exception as e:
            logger.error(f"❌ Ошибка при проверке подписки для {user_id}: {e}")
            # В случае ошибки - не пропускаем пользователя (перестраховка)
            return False

    async def _send_subscription_warning(
            self,
            event: Message | CallbackQuery,
            bot: Bot
    ) -> None:
        """Отправляет предупреждение о необходимости подписки"""

        text = (
            f"❌ <b>Требуется подписка!</b>\n\n"
            f"Чтобы пользоваться ботом, "
            f"подпишитесь на наш канал: {CHANNEL_USERNAME}\n\n"
            f"После подписки нажмите кнопку ниже 👇"
        )

        keyboard = sub_check_keyboard(CHANNEL_USERNAME)

        if isinstance(event, Message):
            try:
                await event.answer(text, reply_markup=keyboard)
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения: {e}")

        elif isinstance(event, CallbackQuery):
            try:
                await event.answer(
                    "❌ Сначала подпишитесь на канал!",
                    show_alert=True
                )
            except Exception as e:
                logger.error(f"Ошибка ответа на callback: {e}")


class OptionalSubscriptionMiddleware(BaseMiddleware):
    """
    Альтернативный middleware - работает, даже если канал недоступен.
    Не блокирует пользователя, но логирует попытки доступа.
    """

    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:

        user = event.from_user
        if not user:
            return await handler(event, data)

        # Пропускаем /start
        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            return await handler(event, data)

        bot: Bot = data["bot"]
        is_subscribed = await self._check_subscription_safe(bot, user.id)

        # Логируем попытку доступа
        event_type = "Message" if isinstance(event, Message) else "Callback"
        logger.info(
            f"{event_type} от {user.id} (@{user.username}) | "
            f"Подписан: {is_subscribed}"
        )

        return await handler(event, data)

    async def _check_subscription_safe(self, bot: Bot, user_id: int) -> bool:
        """Безопасная проверка подписки с полной обработкой ошибок"""
        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            return member.status in ["creator", "administrator", "member", "restricted"]
        except Exception as e:
            logger.warning(f"Не удалось проверить подписку: {e}")
            return None  # Неизвестный статус


# ===== ДОПОЛНИТЕЛЬНАЯ ФУНКЦИЯ ПРОВЕРКИ =====

async def manual_check_subscription(bot: Bot, user_id: int, channel_identifier: str) -> Dict[str, Any]:
    """
    Ручная проверка подписки с подробной информацией.
    Можно использовать в команде, например /check_status

    Args:
        bot: экземпляр бота
        user_id: ID пользователя
        channel_identifier: @username или ID канала

    Returns:
        Словарь с информацией о статусе
    """
    result = {
        "is_subscribed": False,
        "status": None,
        "error": None,
        "user_id": user_id
    }

    try:
        member: ChatMember = await bot.get_chat_member(
            chat_id=channel_identifier,
            user_id=user_id
        )

        result["status"] = member.status

        if member.status in ["creator", "administrator", "member"]:
            result["is_subscribed"] = True

        # Если ограничен - может быть баном или другим ограничением
        if member.status == "restricted":
            result["can_send_messages"] = member.can_send_messages
            result["is_member"] = member.is_member

        return result

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Ошибка проверки подписки для {user_id}: {e}")
        return result