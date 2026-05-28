import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

from src.services.protocol import AgentControllerProtocol
from src.core.i18n import get_text

logger = logging.getLogger(__name__)


def register_handlers(router: Router, controller: AgentControllerProtocol) -> None:
    """
    Register all Telegram handlers on the given router.
    This is a thin Inbound Adapter: it translates aiogram Updates into
    AgentController calls. No business logic lives here.

    Args:
        router: The aiogram Router to register handlers on.
        controller: The AgentController that processes all commands and interactions.
    """

    @router.message(CommandStart())
    async def on_start(message: Message) -> None:
        """Handle /start — show language selection keyboard."""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇻🇳 Tiếng Việt", callback_data="lang:vi"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ]
        ])
        # Use a bilingual prompt since user hasn't chosen language yet
        await message.answer(
            get_text("onboarding_choose_language", "vi"),
            reply_markup=keyboard,
        )

    @router.callback_query(F.data.startswith("lang:"))
    async def on_language_selected(callback: CallbackQuery) -> None:
        """Handle language selection callback during onboarding."""
        await callback.answer()
        if not callback.data or not callback.message:
            return
        language = callback.data.split(":", 1)[1]
        recipient_id = str(callback.message.chat.id)
        await controller.handle_interaction(
            recipient_id, "select_language", {"language": language}
        )

    @router.message(Command("follow"))
    async def on_follow(message: Message) -> None:
        """Handle /follow command — delegate to AgentController."""
        if not message.text:
            return
        recipient_id = str(message.chat.id)
        await controller.handle_user_command(recipient_id, message.text)

    @router.message(Command("block"))
    async def on_block(message: Message) -> None:
        """Handle /block command — delegate to AgentController."""
        if not message.text:
            return
        recipient_id = str(message.chat.id)
        await controller.handle_user_command(recipient_id, message.text)

    @router.message(Command("list"))
    async def on_list(message: Message) -> None:
        """Handle /list command — delegate to AgentController."""
        recipient_id = str(message.chat.id)
        await controller.handle_user_command(recipient_id, "/list")

    @router.message(F.text)
    async def on_text_message(message: Message) -> None:
        """Handle any other text message — delegate to AgentController."""
        if not message.text:
            return
        recipient_id = str(message.chat.id)
        await controller.handle_user_command(recipient_id, message.text)

    @router.callback_query(F.data.startswith("deep_dive:"))
    async def on_deep_dive_callback(callback: CallbackQuery) -> None:
        """Handle deep_dive callback — enter Focus Mode for a specific article."""
        await callback.answer()
        if not callback.data or not callback.message:
            return
        article_id = callback.data.split(":", 1)[1]
        recipient_id = str(callback.message.chat.id)
        await controller.handle_interaction(
            recipient_id, "deep_dive", {"article_id": article_id}
        )

    @router.callback_query(F.data == "exit_focus")
    async def on_exit_focus_callback(callback: CallbackQuery) -> None:
        """Handle exit_focus callback — leave Focus Mode."""
        await callback.answer()
        if not callback.message:
            return
        recipient_id = str(callback.message.chat.id)
        await controller.handle_interaction(recipient_id, "exit_focus", {})

    @router.callback_query(F.data == "settings")
    async def on_settings_callback(callback: CallbackQuery) -> None:
        """Handle settings callback — placeholder for settings UI."""
        await callback.answer()
        if not callback.message:
            return
        recipient_id = str(callback.message.chat.id)
        await controller.handle_interaction(recipient_id, "settings", {})
