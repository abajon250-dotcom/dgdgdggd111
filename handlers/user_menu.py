from aiogram import Router, F
from aiogram.types import Message

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
    await message.answer(
        "📂 <b>Ваши последние заявки:</b>\n\n"
        "Активных заявок пока не найдено.",
        parse_mode="HTML"
    )