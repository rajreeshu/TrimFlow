from abc import ABC, abstractmethod
from typing import List, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import telegram_bot.handlers.video.questions as questions
from controllers.controller_factory import ControllerFactory
from models.file_type_model import FileData
from models.video_models import VideoProcessInfo, VideoScreenType
from telegram_bot.handlers.video.questions import QuestionType, QuestionConfig
from telegram_bot.messenger import TelegramMessenger


class VideoProcessingFlow:
    def __init__(self):
        self.question_configs = questions.create_default_questions()

        self.answers: Dict[QuestionType, Any] = {}
        self.current_question_index = 0

    def get_current_question(self) -> QuestionConfig:
        """Get the current question configuration."""
        return self.question_configs[self.current_question_index]

    def get_keyboard_options(self) -> List[Dict[str, Any]]:
        """Generate keyboard options for the current question."""
        return self.get_current_question().options

    def handle_answer(self, answer: str) -> Dict[str, Any]:
        """
        Process the user's answer for the current question.

        Returns:
        - A dictionary with processing status and next steps
        """
        current_config = self.get_current_question()

        # Handle custom input
        if answer == "custom":
            return {
                "status": "needs_custom_input",
                "question_type": current_config.type
            }

        # Find matching option
        matching_option = next(
            (opt for opt in current_config.options if str(opt['value']) == str(answer)),
            None
        )

        if not matching_option:
            return {
                "status": "invalid_option",
                "message": "Invalid selection. Please try again."
            }

        # Validate and convert if needed
        value = matching_option['value']
        if current_config.validator and not current_config.validator(str(value)):
            return {
                "status": "invalid_input",
                "message": "Invalid input. Please try again."
            }

        if current_config.converter:
            value = current_config.converter(value)

        # Store answer
        self.answers[current_config.type] = value

        # Move to next question or complete flow
        self.current_question_index += 1

        if self.current_question_index >= len(self.question_configs):
            return {
                "status": "completed",
                "answers": self.answers
            }

        return {
            "status": "next_question",
            "question": self.get_current_question()
        }

    def handle_custom_input(self, input_value: str) -> Dict[str, Any]:
        """Handle custom input for the current question."""
        current_config = self.get_current_question()

        # Validate custom input
        if current_config.validator and not current_config.validator(input_value):
            return {
                "status": "invalid_input",
                "message": "Invalid input. Please enter a valid value."
            }

        # Convert input if needed
        value = current_config.converter(input_value) if current_config.converter else input_value

        # Store answer
        self.answers[current_config.type] = value

        # Move to next question or complete flow
        self.current_question_index += 1

        if self.current_question_index >= len(self.question_configs):
            return {
                "status": "completed",
                "answers": self.answers
            }

        return {
            "status": "next_question",
            "question": self.get_current_question()
        }


# Example usage in a Telegram bot context
async def start_video_processing_flow(update: Update, context: CallbackContext):
    """Start the video processing question flow."""
    flow = VideoProcessingFlow()
    context.user_data['processing_flow'] = flow

    current_question = flow.get_current_question()
    keyboard = [
        [InlineKeyboardButton(opt['label'], callback_data=str(opt['value']))
         for opt in current_question.options]
    ]

    await update.message.reply_text(
        current_question.message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_callback_query(update: Update, context: CallbackContext):
    """Handle callback queries during the video processing flow."""
    query = update.callback_query
    await query.answer()

    flow = context.user_data.get('processing_flow')
    if not flow:
        await query.edit_message_text("Flow not found. Please restart.")
        return

    result = flow.handle_answer(query.data)

    if result['status'] == 'needs_custom_input':
        await query.edit_message_text("Please enter the custom value:")
        context.user_data['awaiting_custom_input'] = True
        return

    if result['status'] == 'next_question':
        next_question = result['question']
        keyboard = [
            [InlineKeyboardButton(opt['label'], callback_data=str(opt['value']))
             for opt in next_question.options]
        ]

        await query.edit_message_text(
            next_question.message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    if result['status'] == 'completed':
        # Final processing when all questions are answered
        answers = result['answers']

        await send_video_update(answers, update, context)


async def handle_custom_input(update: Update, context: CallbackContext):
    """Handle custom input during the video processing flow."""
    if not context.user_data.get('awaiting_custom_input'):
        return

    flow = context.user_data.get('processing_flow')
    if not flow:
        await update.message.reply_text("Flow not found. Please restart.")
        return

    result = flow.handle_custom_input(update.message.text)

    context.user_data['awaiting_custom_input'] = False

    if result['status'] == 'next_question':
        next_question = result['question']
        keyboard = [
            [InlineKeyboardButton(opt['label'], callback_data=str(opt['value']))
             for opt in next_question.options]
        ]

        await update.message.reply_text(
            next_question.message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    if result['status'] == 'completed':

        # Final processing when all questions are answered
        answers = result['answers']



async def handle_text_input(update: Update, context: CallbackContext):
    """
    Handle text input during the video processing flow.

    This method checks if the bot is expecting a custom input
    and processes it accordingly.
    """
    flow = context.user_data.get('processing_flow')

    # Check if we're expecting custom input
    if not context.user_data.get('awaiting_custom_input'):
        return

    # Validate flow exists
    if not flow:
        await update.message.reply_text(
            "Processing flow was lost. Please restart the video upload process."
        )
        context.user_data['awaiting_custom_input'] = False
        return

    # Process the custom input
    result = flow.handle_custom_input(update.message.text)

    # Reset the awaiting flag
    context.user_data['awaiting_custom_input'] = False

    # Handle different result statuses
    if result['status'] == 'invalid_input':
        # If input is invalid, ask user to try again
        await update.message.reply_text(
            result.get('message', 'Invalid input. Please try again.')
        )
        context.user_data['awaiting_custom_input'] = True
        return

    if result['status'] == 'next_question':
        # Move to the next question
        next_question = result['question']
        keyboard = [
            [InlineKeyboardButton(opt['label'], callback_data=str(opt['value']))
             for opt in next_question.options]
        ]

        await update.message.reply_text(
            next_question.message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    if result['status'] == 'completed':
        # Final processing when all questions are answered
        answers = result['answers']
        await send_video_update(answers, update, context)

async def send_video_update(answers: Dict[QuestionType, Any], update: Update, context: CallbackContext):
    # Create VideoProcessInfo or call your upload handler
    video_process = VideoProcessInfo()
    video_process.screen_type = VideoScreenType(answers.get(QuestionType.ORIENTATION).lower())
    video_process.segment_time = answers.get(QuestionType.VIDEO_LENGTH)
    video_process.start_time = answers.get(QuestionType.START_TIME)
    video_process.end_time = answers.get(QuestionType.END_TIME)

    # Get the video file information
    file_data = FileData.generate(context.user_data.get('video_info'))
    readable_answers = "\n".join([f"{key.name}: {value}" for key, value in answers.items()])
    await TelegramMessenger(update, context).send_text_message(
        f"Processing Started !\nAnswers:\n{readable_answers}"
    )
    # Trigger the upload process
    await ControllerFactory(update, context).get_upload_controller(file_data).upload(
        video_process,
        file_data
    )

class MessageHandlerInterface(ABC):
    @abstractmethod
    async def handle(self, update: Update, context: CallbackContext):
        pass

