import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor

from config import Config, load_config
from database import Database
from filters import AdminFilter, IsGroupFilter, IsPrivateFilter
from handlers.admin import register_admin_handlers
from handlers.channel import register_channel_handlers
from handlers.common import register_common_handlers
from handlers.group import register_group_handlers
from handlers.pm import register_pm_handlers
from keyboards import set_default_commands

logger = logging.getLogger(__name__)

class QuoteBot:
    def __init__(self, config: Config):
        self.config = config
        self.bot = Bot(token=config.tg_bot.token, parse_mode=types.ParseMode.HTML)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)
        self.db = Database(config.db)
        
        # Регистрация фильтров
        self.dp.filters_factory.bind(AdminFilter)
        self.dp.filters_factory.bind(IsGroupFilter)
        self.dp.filters_factory.bind(IsPrivateFilter)
        
        # Регистрация обработчиков
        register_common_handlers(self.dp)
        register_admin_handlers(self.dp, self.config.tg_bot.admin_ids)
        register_group_handlers(self.dp)
        register_pm_handlers(self.dp, self.db)
        register_channel_handlers(self.dp, self.db)
        
        # Обработка ошибок
        self.dp.register_errors_handler(self.errors_handler)
    
    async def errors_handler(self, update: types.Update, exception: Exception):
        """Обработка ошибок"""
        logger.exception(f'Update: {update}\nException: {exception}')
        return True
    
    async def on_startup(self, dp: Dispatcher):
        """Действия при запуске бота"""
        await set_default_commands(dp)
        await self.db.create_tables()
        logger.info("Бот запущен")
    
    async def on_shutdown(self, dp: Dispatcher):
        """Действия при остановке бота"""
        await dp.storage.close()
        await dp.storage.wait_closed()
        logger.info("Бот остановлен")
    
    def run(self):
        """Запуск бота"""
        executor.start_polling(
            self.dp,
            on_startup=self.on_startup,
            on_shutdown=self.on_shutdown,
            skip_updates=True
        )

def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    # Загрузка конфигурации
    config = load_config()
    
    # Создание и запуск бота
    bot = QuoteBot(config)
    bot.run()

if __name__ == '__main__':
    main()