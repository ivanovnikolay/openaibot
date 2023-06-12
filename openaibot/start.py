from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ConversationHandler


def configure(conversation: ConversationHandler):
    start_command = CommandHandler(('start', 'help', 'cancel'), start)
    conversation.entry_points.append(start_command)
    conversation.fallbacks.append(start_command)


async def start(update: Update, _):
    text = \
        'Генерация изображений с использованием нейросети [DALL·E 2](https://openai.com/dall-e-2)\n' \
        'По умолчанию создается 1 изображение размером 1024x1024, ' \
        'командой /settings можно изменить параметры по умолчанию\n' \
        '\n' \
        '/new - создание новых изображений\n' \
        '/edit - редактирование изображения\n' \
        '/var - создание вариаций изображения\n' \
        '/settings - настройка количества и размер генерируемых изображений\n'
    await update.message.reply_text(text, ParseMode.MARKDOWN, disable_web_page_preview=True)
    return ConversationHandler.END
