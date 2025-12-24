from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from keyboards.admin_keyboards import admin_menu_kb, ticket_action_kb
from database.queries import get_all_users, get_all_tickets, get_ticket_by_id, update_ticket_status
from states.ticket import AdminAnswerState

router = Router()

# Проверка на админа
def is_admin(user_id):
    return user_id in ADMIN_IDS

# --- Вход в админку ---
@router.message(Command("admin"))
async def admin_start(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("👮‍♂️ Админ-панель:", reply_markup=admin_menu_kb())

# --- Список пользователей ---
@router.callback_query(F.data == "admin_users")
async def admin_users_list(callback: types.CallbackQuery):
    users = await get_all_users()
    text = "👥 **Пользователи:**\n"
    for u in users[-10:]: 
        text += f"{u.id}. {u.name} ({u.group_name})\n"
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_menu_kb())

# --- Только НОВЫЕ заявки ---
@router.callback_query(F.data == "admin_tickets_new")
async def admin_tickets_new(callback: types.CallbackQuery):
    tickets = await get_all_tickets(status_filter="Новая")
    if not tickets:
        await callback.answer("Новых заявок нет", show_alert=True)
        return
    
    for row in tickets:
        ticket, user = row
        txt = f"🆕 **Заявка #{ticket.id}**\n👤 {user.name} ({user.group_name})\n📄 {ticket.text}"
        
        # Для новых всегда показываем кнопки
        keyboard = ticket_action_kb(ticket.id)

        if ticket.photo:
            await callback.message.answer_photo(ticket.photo, caption=txt, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await callback.message.answer(txt, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

# --- ВСЕ заявки (исправленная версия) ---
@router.callback_query(F.data == "admin_tickets_all")
async def admin_tickets_all_handler(callback: types.CallbackQuery):
    # Запрашиваем вообще все заявки
    tickets = await get_all_tickets(status_filter=None)
    
    if not tickets:
        await callback.answer("Заявок вообще нет.", show_alert=True)
        return
    
    # Берем последние 10, чтобы не спамить
    latest_tickets = tickets[:10] 

    for row in latest_tickets:
        ticket, user = row
        
        # Выбираем иконку в зависимости от статуса
        if ticket.status == "Новая":
            status_icon = "🆕"
        elif ticket.status == "Отвечено":
            status_icon = "✅"
        else:
            status_icon = "❌"
        
        txt = (
            f"{status_icon} **Заявка #{ticket.id}**\n"
            f"👤 {user.name} ({user.group_name})\n"
            f"📊 Статус: {ticket.status}\n"
            f"📄 Текст: {ticket.text}"
        )
        
        # --- ЛОГИКА КНОПОК ---
        # Показываем кнопки ТОЛЬКО если заявка "Новая". 
        # Если уже ответили или отклонили — кнопок не будет.
        keyboard = None
        if ticket.status == "Новая":
            keyboard = ticket_action_kb(ticket.id)
        # ---------------------
        
        if ticket.photo:
            await callback.message.answer_photo(
                ticket.photo, 
                caption=txt, 
                reply_markup=keyboard, 
                parse_mode="Markdown"
            )
        else:
            await callback.message.answer(
                txt, 
                reply_markup=keyboard, 
                parse_mode="Markdown"
            )
            
    await callback.answer()

# --- Нажатие кнопки "Ответить" ---
@router.callback_query(F.data.startswith("answer_"))
async def start_answer(callback: types.CallbackQuery, state: FSMContext):
    ticket_id = int(callback.data.split("_")[1])
    await state.update_data(ticket_id=ticket_id)
    await callback.message.answer("✍ Введите ответ пользователю:")
    await state.set_state(AdminAnswerState.message)
    await callback.answer()

# --- Отправка ответа ---
@router.message(AdminAnswerState.message)
async def send_answer(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    ticket_id = data['ticket_id']
    answer_text = message.text
    
    row = await get_ticket_by_id(ticket_id)
    if row:
        ticket, user = row
        await update_ticket_status(ticket_id, "Отвечено")
        try:
            await bot.send_message(user.telegram_id, f"🔔 **Ответ на заявку #{ticket_id}:**\n\n{answer_text}", parse_mode="Markdown")
            await message.answer("✅ Ответ отправлен!")
        except:
            await message.answer("⚠ Ответ не доставлен (бот заблокирован?)")
    
    await state.clear()

# --- Нажатие кнопки "Отклонить" ---
@router.callback_query(F.data.startswith("reject_"))
async def reject_ticket(callback: types.CallbackQuery):
    ticket_id = int(callback.data.split("_")[1])
    await update_ticket_status(ticket_id, "Отклонено")
    await callback.message.edit_text(f"❌ Заявка #{ticket_id} отклонена.")