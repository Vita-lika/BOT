from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

def register_group_handlers(dp):
    @dp.message_handler(IsGroupFilter(), Command("quote"))
    async def cmd_quote(message: types.Message):
        """Отправка случайной цитаты в группу"""
        quote = await db.get_random_quote()
        if quote:
            await message.answer(f"{quote.text}\n\n— {quote.author}")
        else:
            await message.answer("Цитаты не найдены")
    
    @dp.message_handler(IsGroupFilter(), content_types=types.ContentType.TEXT)
    async def filter_bad_words(message: types.Message):
        """Фильтрация мата в группе"""
        banned_words = await db.get_banned_words()
        text = message.text.lower()
        
        for word in banned_words:
            if word in text:
                await message.delete()
                warn_msg = await message.answer(
                    f"{message.from_user.get_mention()}, пожалуйста, избегайте нецензурной лексики!"
                )
                await asyncio.sleep(10)
                await warn_msg.delete()
                break