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

EDIT_IMAGE = None


def configure(conversation: ConversationHandler):
    conversation.entry_points.append(CommandHandler('edit', edit_image))

    global EDIT_IMAGE
    EDIT_IMAGE = len(conversation.states)
    conversation.states[EDIT_IMAGE] = [MessageHandler(filters.ALL & ~filters.COMMAND, edit_image), CommandHandler('skip', edit_image)]


async def edit_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'image' not in context.user_data:
        if document := update.effective_message.document:
            file = await context.bot.get_file(document.file_id)
            context.user_data['image'] = await file.download_as_bytearray()
        else:
            await update.message.reply_text('Загрузите изображение с опцией Отправка без сжатия, для которого будут сгенерированы отредактированные версии этого изображения\n' \
                                            'Изображение должно быть квадратным в формате PNG и менее 4Мб')
            return EDIT_IMAGE

    if 'prompt' not in context.user_data:
        if prompt := update.effective_message.text:
            context.user_data['prompt'] = prompt
        else:
            await update.message.reply_text('Введите описание, по которому будет отредактировано загруженное изображение (max 1000 символов)')
            return EDIT_IMAGE

    if 'mask' not in context.user_data:
        if document := update.effective_message.document:
            file = await context.bot.get_file(document.file_id)
            context.user_data['mask'] = await file.download_as_bytearray()
        elif update.effective_message.text == '/skip':
            context.user_data['mask'] = None
        else:
            await update.message.reply_text('Загрузите изображение с опцией Отправка без сжатия, которое будет использовано в качестве маски для редактирования или пропустите этот шаг командой /skip\n' \
                                            'В прозрачной области маски (где альфа канал нулевой) будет редактироваться изображение\n' \
                                            'Маска должна быть того же размера, что и загруженное ранее изображение, в формате PNG и менее 4Мб')
            return EDIT_IMAGE

    image = context.user_data.pop('image')
    prompt = context.user_data.pop('prompt')
    mask = context.user_data.pop('mask')
    size, count = settings.get_user_settings(context)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)

    try:
        images = await dalle.edit_images(image, mask, prompt, size, count)
        for i, (body, thumb) in enumerate(images, start=1):
            name = str(update.effective_message.id) + f'_({i}).png'
            await update.message.reply_document(body, filename=name, thumb=thumb)
    except Exception as err:
        log.exception('/edit command failed')
        await update.message.reply_text(f'Ошибка: {err}')
    return ConversationHandler.END
