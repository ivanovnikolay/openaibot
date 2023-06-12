from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
)


SETTINGS_SIZE = None
SETTINGS_COUNT = None
SETTINGS_BACK = '_back'


def configure(conversation: ConversationHandler):
    conversation.entry_points.extend([
        CommandHandler('settings', settings),
        CallbackQueryHandler(settings_size, pattern='settings_size'),
        CallbackQueryHandler(settings_count, pattern='settings_count'),
    ])

    global SETTINGS_SIZE
    SETTINGS_SIZE = len(conversation.states)
    conversation.states[SETTINGS_SIZE] = [CallbackQueryHandler(settings_size_change)]

    global SETTINGS_COUNT
    SETTINGS_COUNT = len(conversation.states)
    conversation.states[SETTINGS_COUNT] = [CallbackQueryHandler(settings_count_change)]


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    image_size, image_count = get_user_settings(context)

    text='Выберите настройку'
    reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text=f'Размер изображения (выбрано: {image_size})', callback_data='settings_size')],
        [InlineKeyboardButton(text=f'Количество изображений (выбрано: {image_count})', callback_data='settings_count')],
    ])
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)
    return ConversationHandler.END


async def settings_size(update: Update, _):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text='Выберите размер генерируемого изображения',
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text='256x256', callback_data='256x256'),
                InlineKeyboardButton(text='512x512', callback_data='512x512'),
                InlineKeyboardButton(text='1024x1024', callback_data='1024x1024'),
            ],
            [InlineKeyboardButton(text='⇦ Назад', callback_data=SETTINGS_BACK)],
        ]))
    return SETTINGS_SIZE


async def settings_count(update: Update, _):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text='Выберите количество генерируемых изображений',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text=n, callback_data=n) for n in range(1, 6)],
            [InlineKeyboardButton(text=n, callback_data=n) for n in range(6, 11)],
            [InlineKeyboardButton(text='⇦ Назад', callback_data=SETTINGS_BACK)],
        ]))
    return SETTINGS_COUNT


async def settings_size_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data != SETTINGS_BACK:
        context.user_data['image_size'] = update.callback_query.data
    return await settings(update, context)


async def settings_count_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data != SETTINGS_BACK:
        context.user_data['image_count'] = int(update.callback_query.data)
    return await settings(update, context)


def get_user_settings(context: ContextTypes.DEFAULT_TYPE):
    return \
        context.user_data.get('image_size', '1024x1024'), \
        context.user_data.get('image_count', 1)
