from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, ConversationHandler, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler

USERNAME, INFO, PHOTO = range(3)

user_profiles = []

class UserProfileController:

    @staticmethod
    async def starting_get_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Creación de perfil, escribe tu nombre de usuario:")
        return USERNAME

    @staticmethod
    async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["username"] = update.message.text
        await update.message.reply_text("Perfecto, escribe tu info:")
        return INFO
    
    @staticmethod
    async def get_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["user_info"] = update.message.text
        await update.message.reply_text("Muchas gracias, podrías proporcionarnos una foto de perfil?")
        return PHOTO
    
    @staticmethod
    async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.effective_message
        if message.photo:
            context.user_data["user_photo"] = message.photo[-1].file_id
            await update.message.reply_photo(
                photo=context.user_data["user_photo"],
                caption=f"Nombre de usuario: {context.user_data['username']}\nInfo: {context.user_data['user_info']}"
            )
        else:
            await update.message.reply_text("No se proporcionó una foto.")
            await update.message.reply_text(
                f"Nombre de usuario: {context.user_data['username']}\nInfo: {context.user_data['user_info']}"
            )

        user_profiles.append(context.user_data)
        return ConversationHandler.END
    
    @staticmethod
    async def select_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not user_profiles:
            await update.message.reply_text("No hay perfiles disponibles para seleccionar.")
            return

        buttons = [
            [InlineKeyboardButton(f"{profile['username']}", callback_data=f"select_{i}")]
            for i, profile in enumerate(user_profiles)
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Selecciona un usuario:", reply_markup=keyboard)
    
    @staticmethod
    async def view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not user_profiles:
            await update.message.reply_text("No hay perfiles registrados.")
            return
        
        users_list = "\n".join([f"{i + 1}. {profile['username']}" for i, profile in enumerate(user_profiles)])
        await update.message.reply_text(f"Usuarios registrados:\n{users_list}")
    
    @staticmethod
    async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not user_profiles:
            await update.message.reply_text("No hay perfiles disponibles para eliminar.")
            return

        buttons = [
            [InlineKeyboardButton(f"{profile['username']}", callback_data=f"delete_{i}")]
            for i, profile in enumerate(user_profiles)
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Selecciona un usuario para eliminar:", reply_markup=keyboard)

    @staticmethod
    async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Operación cancelada.")
        return ConversationHandler.END

    @staticmethod
    async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Escribe el nombre de usuario que deseas añadir:")
        return USERNAME

    @staticmethod
    async def handle_add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        username = update.message.text
        if any(profile['username'] == username for profile in user_profiles):
            await update.message.reply_text(f"El usuario '{username}' ya existe.")
        else:
            new_profile = {"username": username, "user_info": "", "user_photo": None}
            user_profiles.append(new_profile)
            await update.message.reply_text(f"Usuario '{username}' añadido con éxito.")
        return ConversationHandler.END

user_profile_controller_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("profile", UserProfileController.starting_get_info)],
    states={
        USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, UserProfileController.get_username)],
        INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, UserProfileController.get_info)],
        PHOTO: [MessageHandler(filters.ALL & ~filters.COMMAND, UserProfileController.get_photo)],
    },
    fallbacks=[MessageHandler(filters.COMMAND, UserProfileController.cancel_operation)]
)

add_user_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("add_user", UserProfileController.add_user)],
    states={
        USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, UserProfileController.handle_add_user)]
    },
    fallbacks=[MessageHandler(filters.COMMAND, UserProfileController.cancel_operation)]
)