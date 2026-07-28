from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from config import NOTIFY_CHANNEL_ID, ADMIN_ID
from keyboards import sbp_type_inline, admin_buttons, main_menu
from database import create_application, update_app

router = Router()


@router.callback_query(F.data == "category_sbp")
async def sbp_cat(callback: CallbackQuery):
    await callback.message.edit_text("💳 Выберите сервис СБП:", reply_markup=sbp_type_inline())


@router.callback_query(F.data.in_(["service_sbp_adengi", "service_sbp_manimen"]))
async def sbp_create(callback: CallbackQuery, bot: Bot):
    service = "Аденьги (СБП)" if "adengi" in callback.data else "Манимен (СБП)"
    uid, uname = callback.from_user.id, callback.from_user.username or "нет"

    app_id = create_application(uid, uname, "СБП", service, "Ожидание")
    msg = await bot.send_message(
        NOTIFY_CHANNEL_ID,
        f"📥 <b>Заявка СБП #{app_id}</b>\nСервис: {service}\nОт: @{uname} (<code>{uid}</code>)\nСтатус: ⏳ Ожидание",
        reply_markup=admin_buttons(app_id, uid, True),
        parse_mode="HTML"
    )
    update_app(app_id, channel_message_id=msg.message_id)

    is_admin = (uid == ADMIN_ID)
    await callback.message.delete()
    await callback.message.answer(f"✅ Заявка #{app_id} успешно создана! Ожидайте реквизиты от администратора.",
                                  reply_markup=main_menu(is_admin))