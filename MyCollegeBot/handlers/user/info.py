from aiogram import Router, F, types

router = Router()

@router.message(F.text == "ℹ Информация")
async def cmd_info(message: types.Message):
    await message.answer(
        "🏫 **Учебный бот колледжа**\n\n"
        "Этот бот создан для упрощения подачи заявок и получения информации.\n"
        "Версия: 1.0\n"
        "Разработчик: Студент 3 курса",
        parse_mode="Markdown"
    )

@router.message(F.text == "❓ Помощь")
async def cmd_help(message: types.Message):
    await message.answer("Используйте меню для навигации. Если что-то сломалось, введите /start заново.")