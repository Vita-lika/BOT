import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest

async def fetch_quote_from_api():
    """Получение цитаты с внешнего API"""
    async with aiohttp.ClientSession() as session:
        async with session.get(config.quotes_api.url, headers={"X-API-KEY": config.quotes_api.key}) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data['quote'], data['author']
            return None, None

def register_channel_handlers(dp, db):
    @dp.channel_post_handler(content_types=types.ContentType.TEXT)
    async def handle_channel_post(message: types.Message):
        """Обработка постов в канале"""
        pass
    
    @dp.message_handler(Command("publish_quote"))
    async def publish_quote(message: types.Message):
        """Публикация цитаты в канал"""
        # Можно получить цитату из БД или с внешнего API
        quote = await db.get_random_quote()
        if not quote:
            quote_text, quote_author = await fetch_quote_from_api()
            if quote_text:
                quote = Quote(text=quote_text, author=quote_author, published=True)
                await db.add_quote(quote)
        
        if quote:
            try:
                await dp.bot.send_message(
                    chat_id=config.tg_bot.channel_id,
                    text=f"{quote.text}\n\n— {quote.author}"
                )
                await db.mark_quote_as_published(quote.id)
                await message.answer("Цитата опубликована!")
            except BadRequest as e:
                await message.answer(f"Ошибка публикации: {e}")
        else:
            await message.answer("Не удалось получить цитату")