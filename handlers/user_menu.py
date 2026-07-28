from aiogram import Router, F, Bot
from aiogram.types import Message
from config import NOTIFY_CHANNEL_ID, CHANNEL_USERNAME
from keyboards import sub_check_keyboard
from database import get_user_applications
from handlers.start import check_sub

router = Router()


@router.message(F.text == "📞 Поддержка")
async def support(message: Message, bot: Bot):
    if not await check_sub(bot, message.from_user.id):
        return await message.answer("❌ Нужна подписка на канал!", reply_markup=sub_check_keyboard(CHANNEL_USERNAME))
    await message.answer("📞 Поддержка: @admin")


@router.message(F.text == "📂 Мои заявки")
async def my_apps(message: Message, bot: Bot):
    if not await check_sub(bot, message.from_user.id):
        return await message.answer("❌ Нужна подписка на канал!", reply_markup=sub_check_keyboard(CHANNEL_USERNAME))

    apps = get_user_applications(message.from_user.id)
    if not apps: return await message.answer("📂 У вас нет заявок.")
    text = "📂 Ваши заявки:\n\n" + "".join([f"🔹 #{i} | {s} | {st}\n" for i, s, st in apps])
    await message.answer(text)


@router.message(F.text & ~F.text.startswith("/"))
async def forward_data(message: Message, bot: Bot):
    if message.text in ["➕ Создать заявку", "📂 Мои заявки", "📞 Поддержка"]: return
    if not await check_sub(bot, message.from_user.id):
        return await message.answer("❌ Нужна подписка на канал!", reply_markup=sub_check_keyboard(CHANNEL_USERNAME))

    uid, uname, text = message.from_user.id, message.from_user.username or "нет", message.text.strip()
    apps = get_user_applications(uid)
    app_info = f"#{apps[0][0]} ({apps[0][1]})" if apps else "Нет активных"

    await bot.send_message(NOTIFY_CHANNEL_ID,
                           f"📩 <b>Данные от @{uname}</b> (ID: <code>{uid}</code>)\nЗаявка: {app_info}\n\n<code>{text}</code>",
                           parse_mode="HTML")
    await message.answer("✅ Данные переданы администратору!")