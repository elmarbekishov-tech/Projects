from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from database.queries import create_ticket, get_user_tickets
from states.ticket import TicketState
from keyboards.user_keyboards import main_menu, cancel_kb
from config import ADMIN_IDS

router = Router()

@router.message(F.text == "📚 Мои заявки")
async def my_tickets(message: types.Message):
    tickets = await get_user_tickets(message.from_user.id)
    if not tickets:
        await message.answer("У вас пока нет заявок.")
        return
    
    response = "📋 **Ваши последние заявки:**\n\n"
    for t in tickets[:5]: 
        response += f"🆔 #{t.id} | Статус: {t.status}\n📝 {t.text[:50]}...\n\n"
    await message.answer(response, parse_mode="Markdown")

@router.message(F.text == "📝 Оставить заявку")
async def start_ticket(message: types.Message, state: FSMContext):
    await message.answer("Опишите вашу проблему или вопрос:", reply_markup=cancel_kb())
    await state.set_state(TicketState.text)

@router.message(TicketState.text)
async def ticket_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Прикрепите фото (или напишите 'нет'):")
    await state.set_state(TicketState.photo)

@router.message(TicketState.photo)
async def ticket_finish(message: types.Message, state: FSMContext, bot: Bot):
    photo_id = message.photo[-1].file_id if message.photo else None
    data = await state.get_data()
    
    ticket_id = await create_ticket(message.from_user.id, data['text'], photo_id)
    
    await message.answer(f"✅ Заявка #{ticket_id} создана!", reply_markup=main_menu())
    await state.clear()
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f"🆕 **Новая заявка #{ticket_id}**\nОт: {message.from_user.full_name}", parse_mode="Markdown")
        except:
            pass