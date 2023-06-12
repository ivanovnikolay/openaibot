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

VAR_IMAGE = None


def configure(conversation: ConversationHandler):
    conversation.entry_points.append(CommandHandler('var', var_image))

    global VAR_IMAGE
    VAR_IMAGE = len(conversation.states)
    conversation.states[VAR_IMAGE] = [MessageHandler(filters.ALL & ~filters.COMMAND, var_image)]


async def var_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.effective_message.document
    if not document and update.effective_message.reply_to_message:
        document = update.effective_message.reply_to_message.document

    if not document:
        await update.message.reply_text('Загрузите изображение с опцией Отправка без сжатия, для которого будут сгенерированы вариации\n'
                                        'Изображение должно быть квадратным в формате PNG и менее 4Мб')
        return VAR_IMAGE

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
    try:
        file = await context.bot.get_file(document.file_id)
        image = await file.download_as_bytearray()
        size, count = settings.get_user_settings(context)

        images = await dalle.var_images(image, size, count)
        for i, (body, thumb) in enumerate(images, start=1):
            name = str(update.effective_message.id) + f'_({i}).png'
            await update.message.reply_document(body, filename=name, thumb=thumb)
    except Exception as err:
        log.exception('/var command failed')
        await update.message.reply_text(f'Ошибка: {err}')
    return ConversationHandler.END
