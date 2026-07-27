from aiogram import Router, F
from aiogram.types import Message
from database import get_user_applications

router = Router()


@router.message(F.text == "📞 Поддержка")
async def cmd_support(message: Message):
    await message.answer(
        "📞 <b>Служба поддержки:</b>\n\n"
        "Если у вас возникли вопросы или проблемы с заявкой, обратитесь к администратору: @admin",
        parse_mode="HTML"
    )


@router.message(F.text == "📂 Мои заявки")
async def cmd_my_apps(message: Message):
    apps = get_user_applications(message.from_user.id)

    if not apps:
        await message.answer(
            "📂 <b>Ваши последние заявки:</b>\n\nУ вас пока нет созданных заявок.",
            parse_mode="HTML"
        )
        return

    text = "📂 <b>Ваши последние заявки:</b>\n\n"
    for app_id, service_type, status in apps:
        text += f"🔹 <b>Заявка #{app_id}</b>\nСервис: {service_type}\nСтатус: {status}\n\n"

    await message.answer(text, parse_mode="HTML")