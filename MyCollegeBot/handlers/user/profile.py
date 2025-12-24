from aiogram import Router, F, types
from database.queries import get_user

router = Router()

@router.message(F.text == "📄 Мой профиль")
async def show_profile(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Вы не зарегистрированы. Введите /start")
        return
    
    text = (
        f"👤 **Профиль студента**\n"
        f"📛 Имя: {user.name}\n"
        f"🎓 Группа: {user.group_name}\n"
        f"📱 Телефон: {user.phone or 'Не указан'}\n"
        f"📅 Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}"
    )
    await message.answer(text, parse_mode="Markdown")