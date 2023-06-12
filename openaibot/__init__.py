import logging
from os import getenv
from telegram.ext import Application, ConversationHandler
from . import start, settings, new_image, var_image, edit_image


logging.basicConfig(level=logging.INFO)


def init():
    app = Application.builder() \
        .token(getenv('TELEGRAM_TOKEN')) \
        .build()

    conversation = ConversationHandler([], {}, [])
    start.configure(conversation)
    settings.configure(conversation)
    new_image.configure(conversation)
    var_image.configure(conversation)
    edit_image.configure(conversation)
    app.add_handler(conversation)

    return app
