from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from config import NOTIFY_CHANNEL_ID, CHANNEL_USERNAME
from keyboards import sbp_type_inline, admin_buttons, main_menu, sub_check_keyboard
from database import create_application, update_app
from handlers.start import check_sub

router = Router()


@router.callback_query(F.data == "category_sbp")
async def sbp_cat(callback: CallbackQuery, bot: Bot):
    if not await check_sub(bot, callback.from_user.id):
        return await callback.message.edit_text("❌ Нужна подписка на канал!",
                                                reply_markup=sub_check_keyboard(CHANNEL_USERNAME))
    await callback.message.edit_text("💳 Выберите сервис СБП:", reply_markup=sbp_type_inline())


@router.callback_query(F.data.in_(["service_sbp_adengi", "service_sbp_manimen"]))
async def sbp_create(callback: CallbackQuery, bot: Bot):
    if not await check_sub(bot, callback.from_user.id):
        return await callback.message.edit_text("❌ Нужна подписка на канал!",
                                                reply_markup=sub_check_keyboard(CHANNEL_USERNAME))

    service = "Аденьги (СБП)" if "adengi" in callback.data else "Манимен (СБП)"
    uid, uname = callback.from_user.id, callback.from_user.username or "нет"

    app_id = create_application(uid, uname, "СБП", service, "Ожидание")
    msg = await bot.send_message(NOTIFY_CHANNEL_ID,
                                 f"📥 <b>Заявка СБП #{app_id}</b>\nСервис: {service}\nОт: @{uname} (<code>{uid}</code>)\nСтатус: ⏳ Ожидание",
                                 reply_markup=admin_buttons(app_id, uid, True), parse_mode="HTML")
    update_app(app_id, channel_message_id=msg.message_id)

    await callback.message.delete()
    await callback.message.answer(f"✅ Заявка #{app_id} создана!", reply_markup=main_menu())