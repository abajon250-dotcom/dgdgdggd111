from aiogram import Router, F, Bot
from aiogram.types import Message
from config import NOTIFY_CHANNEL_ID
from database import get_user_applications

router = Router()


@router.message(F.text == "📞 Поддержка")
async def support(message: Message):
    await message.answer("📞 По всем вопросам обращайтесь в поддержку: @admin")


@router.message(F.text == "📂 Мои заявки")
async def my_apps(message: Message):
    apps = get_user_applications(message.from_user.id)
    if not apps:
        return await message.answer("📂 У вас пока нет активных заявок.")
    text = "📂 **Ваши последние заявки:**\n\n" + "".join(
        [f"🔹 #{i} | {s} | Статус: <code>{st}</code>\n" for i, s, st in apps])
    await message.answer(text, parse_mode="HTML")


@router.message(F.text & ~F.text.startswith("/"))
async def forward_data(message: Message, bot: Bot):
    if message.text in ["➕ Создать заявку", "📂 Мои заявки", "📞 Поддержка", "👑 Админ-панель"]:
        return
    uid, uname, text = message.from_user.id, message.from_user.username or "нет", message.text.strip()
    apps = get_user_applications(uid)
    app_info = f"#{apps[0][0]} ({apps[0][1]})" if apps else "Нет активных"

    await bot.send_message(
        NOTIFY_CHANNEL_ID,
        f"📩 <b>Данные от @{uname}</b> (ID: <code>{uid}</code>)\nЗаявка: {app_info}\n\n<code>{text}</code>",
        parse_mode="HTML"
    )
    await message.answer("✅ Данные переданы администратору!")