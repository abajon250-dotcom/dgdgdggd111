import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from config import NOTIFY_CHANNEL_ID
from keyboards import sbp_type_inline, admin_sbp_buttons, main_menu
from database import create_application, update_app
from handlers.start import check_sub

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "category_sbp")
async def process_sbp_category(callback: CallbackQuery, bot: Bot):
    if not await check_sub(bot, callback.from_user.id):
        await callback.answer("❌ Нужна подписка!", show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(
        "💳 Выберите сервис для СБП:",
        reply_markup=sbp_type_inline()
    )


@router.callback_query(F.data.in_(["service_sbp_adengi", "service_sbp_manimen"]))
async def process_sbp_creation(callback: CallbackQuery, bot: Bot):
    if not await check_sub(bot, callback.from_user.id):
        await callback.answer("❌ Нужна подписка!", show_alert=True)
        return

    await callback.answer()
    service_name = "АДЕНЬГИ" if "adengi" in callback.data else "МАНИМЕН"
    service_type = f"{service_name} (СБП)"

    user_id = callback.from_user.id
    username = callback.from_user.username or "отсутствует"

    app_id = create_application(
        user_id=user_id,
        username=username,
        type_choice="СБП",
        service_type=service_type,
        phone="Ожидание реквизитов"
    )

    text_for_group = (
        f"📥 <b>Новая заявка СБП (ID: {app_id}):</b>\n"
        f"Сервис: {service_type}\n"
        f"Пользователь: @{username} (ID: {user_id})\n"
        f"Статус: ⏳ Запрос реквизитов"
    )

    kb = admin_sbp_buttons(app_id, user_id)

    try:
        sent_msg = await bot.send_message(
            chat_id=NOTIFY_CHANNEL_ID,
            text=text_for_group,
            reply_markup=kb,
            parse_mode="HTML"
        )
        update_app(app_id, channel_message_id=sent_msg.message_id)
    except Exception as e:
        logger.error(f"Не удалось отправить заявку СБП в группу: {e}")

    await callback.message.edit_text(
        f"✅ <b>Заявка #{app_id} успешно создана!</b>\nАдминистратор скоро запросит ваши реквизиты.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )