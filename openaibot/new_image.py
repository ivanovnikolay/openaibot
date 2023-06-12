from logging import getLogger
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from . import dalle, settings


log = getLogger(__name__)

NEW_IMAGE = None


def configure(conversation: ConversationHandler):
    conversation.entry_points.append(CommandHandler('new', new_image))

    global NEW_IMAGE
    NEW_IMAGE = len(conversation.states)
    conversation.states[NEW_IMAGE] = [MessageHandler(filters.ALL & ~filters.COMMAND, new_image)]


async def new_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not (prompt := _parse_command(update.effective_message.text)):
        await update.message.reply_text('Введите описание, по которому будет сгенерировано изображение (max 1000 символов)')
        return NEW_IMAGE

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
    try:
        size, count = settings.get_user_settings(context)
        images = await dalle.new_images(prompt, size, count)
        for i, (body, thumb) in enumerate(images, start=1):
            name = str(update.effective_message.id) + f'_({i}).png'
            await update.message.reply_document(body, filename=name, thumb=thumb)
    except Exception as err:
        log.exception('/new command failed')
        await update.message.reply_text(f'Ошибка: {err}')
    return ConversationHandler.END


def _parse_command(command: str):
    return command[5:] if command and command.strip().startswith('/new') else command
