from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    sdat_type = State()
    sdat_phone = State()
    sdat_waiting_admin = State()
    sdat_code_prompt = State()
    sdat_waiting_code = State()

    sbp_type = State()
    sbp_waiting_admin = State()
    sbp_waiting_amount = State()

class AdminStates(StatesGroup):
    waiting_cancel_reason = State()
    waiting_sbp_requisites = State()
    waiting_sbp_confirm = State()
    waiting_broadcast = State()