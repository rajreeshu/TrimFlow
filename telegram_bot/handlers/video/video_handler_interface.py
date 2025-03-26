from abc import ABC, abstractmethod
from telegram.ext import CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from controllers.url_controller import UrlController
from models.video_models import VideoProcessInfo


def generate_question_keyboard(question_type):
    if question_type == "orientation":
        keyboard = [
            [InlineKeyboardButton("Landscape", callback_data="orientation_landscape"),
             InlineKeyboardButton("Portrait", callback_data="orientation_portrait")]
        ]
    elif question_type == "video_length":
        keyboard = [
            [InlineKeyboardButton("30 seconds", callback_data="length_30"),
             InlineKeyboardButton("1 minute", callback_data="length_60"),
             InlineKeyboardButton("Custom", callback_data="length_custom")]
        ]
    elif question_type == "start_time":
        keyboard = [
            [InlineKeyboardButton("0 seconds", callback_data="start_0"),
             InlineKeyboardButton("Custom", callback_data="start_custom")]
        ]
    elif question_type == "end_time":
        keyboard = [
            [InlineKeyboardButton("End of video", callback_data="end_video"),
             InlineKeyboardButton("Custom", callback_data="end_custom")]
        ]
    else:
        keyboard = []

    return InlineKeyboardMarkup(keyboard)


async def handle_callback_query(update: Update, context: CallbackContext) -> None:
    """Handle the callback query and send a reply."""
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    question_type = data[0]
    response = data[1]

    next_question = None
    if question_type == "orientation":
        next_question = "video_length"
        text = "Select the Output Video Length:"
    elif question_type == "length":
        next_question = "start_time"
        text = "Select the Start Time:"
    elif question_type == "start":
        next_question = "end_time"
        text = "Select the End Time:"
    elif question_type == "end":
        text = "Thank you! Your responses have been recorded."

    if next_question:
        reply_markup = generate_question_keyboard(next_question)
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            text=text
        )
        link = context.user_data.get('pending_link')
        await UrlController(update).upload_from_url(VideoProcessInfo(), link)


class MessageHandlerInterface(ABC):
    @abstractmethod
    async def handle(self, update: Update, context: CallbackContext):
        pass

