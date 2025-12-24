from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Все пользователи", callback_data="admin_users")],
        [InlineKeyboardButton(text="📝 Новые заявки", callback_data="admin_tickets_new")],
        [InlineKeyboardButton(text="📝 Все заявки", callback_data="admin_tickets_all")]
    ])

def ticket_action_kb(ticket_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉ Ответить", callback_data=f"answer_{ticket_id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{ticket_id}")]
    ])