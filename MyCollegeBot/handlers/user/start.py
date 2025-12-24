from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from database.queries import get_user, add_user
from states.register import RegisterState
from keyboards.user_keyboards import main_menu, phone_kb, confirm_kb, cancel_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user:
        await message.answer(f"С возвращением, {user.name}!", reply_markup=main_menu())
    else:
        await message.answer("Добро пожаловать! Давайте зарегистрируемся.\nВведите ваше Имя и Фамилию:", reply_markup=cancel_kb())
        await state.set_state(RegisterState.name)

@router.message(RegisterState.name)
async def process_name(message: types.Message, state: FSMContext):
    if len(message.text) < 3:
        await message.answer("Слишком короткое имя. Попробуйте еще раз.")
        return
    await state.update_data(name=message.text)
    await message.answer("Отлично! Теперь введите вашу учебную группу:", reply_markup=cancel_kb())
    await state.set_state(RegisterState.group)

@router.message(RegisterState.group)
async def process_group(message: types.Message, state: FSMContext):
    await state.update_data(group=message.text)
    await message.answer("Отправьте ваш номер телефона (кнопкой или текстом) или нажмите 'Пропустить':", reply_markup=phone_kb())
    await state.set_state(RegisterState.phone)

@router.message(RegisterState.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    if phone.lower() == "пропустить":
        phone = None
    
    await state.update_data(phone=phone)
    data = await state.get_data()
    
    info = f"Имя: {data['name']}\nГруппа: {data['group']}\nТелефон: {phone or 'Не указан'}"
    await message.answer(f"Проверьте данные:\n\n{info}\n\nВсе верно?", reply_markup=confirm_kb())
    await state.set_state(RegisterState.confirm)

@router.message(RegisterState.confirm, F.text.casefold() == "да")
async def process_confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_user(message.from_user.id, data['name'], data['group'], data['phone'])
    await message.answer("Регистрация успешно завершена!", reply_markup=main_menu())
    await state.clear()

@router.message(RegisterState.confirm)
async def process_retry(message: types.Message, state: FSMContext):
    await message.answer("Давайте начнем заново. Введите имя:", reply_markup=cancel_kb())
    await state.set_state(RegisterState.name)

@router.message(F.text.casefold() == "отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_menu())