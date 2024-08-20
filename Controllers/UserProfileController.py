from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, ConversationHandler, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler

USERNAME, INFO, PHOTO, SELECT_USER = range(4)

# Estados de la conversación para agregar usuarios
ADD_USERNAME = range(5)

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
        if message.photo:  # Si el usuario envió una foto
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

        # Almacenar el perfil del usuario
        user_profiles.append(context.user_data.copy())
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
    async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_index = int(query.data.split('_')[1])
        selected_user = user_profiles[user_index]
        context.user_data.update(selected_user)
        await query.edit_message_text(f"Has seleccionado a {selected_user['username']}.")

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
            [InlineKeyboardButton(f"{profile['username']}", callback_data=f"select_{i}")]
            for i, profile in enumerate(user_profiles)
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Selecciona un usuario para eliminar:", reply_markup=keyboard)

    @staticmethod
    async def handle_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_index = int(query.data.split('_')[1])
        deleted_user = user_profiles.pop(user_index)
        await query.edit_message_text(f"El usuario {deleted_user['username']} ha sido eliminado.")

    @staticmethod
    async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Operación cancelada.")
        return ConversationHandler.END
    
    @staticmethod
    async def start_adding_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Introduce el nombre de usuario para agregar:")
        return ADD_USERNAME

    @staticmethod
    async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        username = update.message.text
        user_profiles.append({'username': username})
        await update.message.reply_text(f"Usuario {username} añadido.")
        return ConversationHandler.END

# Conversation handler para agregar usuarios
add_user_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("add_user", UserProfileController.start_adding_user)],
    states={
        ADD_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, UserProfileController.add_user)],
    },
    fallbacks=[MessageHandler(filters.COMMAND, UserProfileController.cancel_operation)]
)

# Conversation handler para la creación de perfiles de usuario
user_profile_controller_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("profile", UserProfileController.starting_get_info)],
    states={
        USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, UserProfileController.get_username)],
        INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, UserProfileController.get_info)],
        PHOTO: [MessageHandler(filters.ALL & ~filters.COMMAND, UserProfileController.get_photo)],
    },
    fallbacks=[MessageHandler(filters.COMMAND, UserProfileController.cancel_operation)]
)

# Conversation handler para agregar usuarios
add_user_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("add_user", UserProfileController.start_adding_user)],
    states={
        ADD_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, UserProfileController.add_user)],
    },
    fallbacks=[MessageHandler(filters.COMMAND, UserProfileController.cancel_operation)]
)

# Callback handler para manejar la selección de usuario

# Callback handler para manejar la selección de usuario
callback_handler = CallbackQueryHandler(UserProfileController.handle_selection, pattern="select_")

# Callback handler para manejar la eliminación de usuario
delete_callback_handler = CallbackQueryHandler(UserProfileController.handle_delete, pattern="delete_")