from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from bot.keyboards import get_main_menu_keyboard, get_cancel_keyboard
from bot.states import AddQuoteStates
from models import Quote

def register_pm_handlers(dp, db):
    @dp.message_handler(IsPrivateFilter(), Command("start"))
    async def cmd_start(message: types.Message):
        """Обработка команды /start в личных сообщениях"""
        await db.add_user(User.from_telegram(message.from_user))
        await message.answer(
            "Привет! Я бот с цитатами. Вот что я умею:",
            reply_markup=get_main_menu_keyboard()
        )
    
    @dp.message_handler(IsPrivateFilter(), text="Добавить цитату")
    async def add_quote_start(message: types.Message):
        """Начало процесса добавления цитаты"""
        await AddQuoteStates.text.set()
        await message.answer(
            "Пришлите текст цитаты:",
            reply_markup=get_cancel_keyboard()
        )
    
    @dp.message_handler(state=AddQuoteStates.text)
    async def process_quote_text(message: types.Message, state: FSMContext):
        """Обработка текста цитаты"""
        async with state.proxy() as data:
            data['text'] = message.text
        
        await AddQuoteStates.next()
        await message.answer("Теперь укажите автора цитаты:")
    
    @dp.message_handler(state=AddQuoteStates.author)
    async def process_quote_author(message: types.Message, state: FSMContext):
        """Обработка автора цитаты"""
        async with state.proxy() as data:
            data['author'] = message.text
        
        quote = Quote(
            text=data['text'],
            author=data['author'],
            added_by=message.from_user.id
        )
        
        quote_id = await db.add_quote(quote)
        await state.finish()
        await message.answer(
            f"Цитата сохранена (ID: {quote_id})!",
            reply_markup=get_main_menu_keyboard()
        )