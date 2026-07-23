from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards import main_menu

router = Router()

@router.message(F.text.casefold() == "отмена")
@router.message(F.text == "/cancel")
async def cancel_all(message: Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        await message.answer("Нет активных действий.", reply_markup=main_menu())
        return
    await state.clear()
    await message.answer("✅ Действие отменено.", reply_markup=main_menu())