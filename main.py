from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from Controllers.TodoController import TodoController
from Controllers.UserProfileController import (user_profile_controller_conversation_handler, add_user_conversation_handler, UserProfileController, callback_handler, delete_callback_handler)


# Token de acceso al bot
TOKEN = "7325840280:AAEQZOue7G0OiPBByeuSiClORaiwLK5bsUk"

# Función de inicio
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "¿Qué puede hacer el bot?\n\n"
        "Bot para gestionar listas de tareas de usuario.\n"
        "Escribe /help para ver la lista de comandos disponibles.\n\n"
        "Por ejemplo:\n"
        "- /create_list [nombre de la lista] - Crea una nueva lista de tareas\n"
        "- /select_list [nombre de la lista] - Selecciona la lista actual\n"
        "- /add [tarea] - Añade una nueva tarea\n"
        "- /list - Muestra la lista de tareas\n"
        "- /check [número de tarea] - Marca una tarea como completada\n"
        "- /clear - Borra todas las tareas en la lista actual\n"
    )
    await update.message.reply_text(welcome_message)

# Función de ayuda
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "👋 ¡Hola! Soy Yulex Bot. Puedo ayudarte a crear y gestionar listas de tareas."
    buttons = [
        [InlineKeyboardButton("Crear perfil", callback_data='/profile')],
        [InlineKeyboardButton("Añadir usuario", callback_data='/add_user')],
        [InlineKeyboardButton("Seleccionar usuario", callback_data='/select_user')],
        [InlineKeyboardButton("Ver usuarios", callback_data='/view_users')],
        [InlineKeyboardButton("Crear lista de tareas", callback_data='/create_list')],
        [InlineKeyboardButton("Seleccionar lista de tareas", callback_data='/select_list')],
        [InlineKeyboardButton("Añadir tarea", callback_data='/add')],
        [InlineKeyboardButton("Ver tareas", callback_data='/list')],
        [InlineKeyboardButton("Marcar tarea como completada", callback_data='/check')],
        [InlineKeyboardButton("Borrar todas las tareas", callback_data='/clear')],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

# Respuesta a "hola"
async def greet_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data.get("username", "¡papu!")
    await update.message.reply_text(f"¡Hola, {username}! 😊")

# Respuesta a "gracias"
async def thank_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡De nada! 😇")

# Construcción de la aplicación del bot
application = ApplicationBuilder().token(TOKEN).build()

# Agrega manejadores para los callback queries (botones)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    command = query.data

    command_map = {
        '/profile': UserProfileController.starting_get_info,
        '/add_user': UserProfileController.start_adding_user,
        '/select_user': UserProfileController.select_user,
        '/view_users': UserProfileController.view_users,
        '/create_list': TodoController.create_task_list,
        '/select_list': TodoController.select_task_list,
        '/add': TodoController.add_todo,
        '/list': TodoController.list_todos,
        '/check': TodoController.check_todo,
        '/clear': TodoController.clear_todos,
    }

    if command in command_map:
        await command_map[command](update, context)
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"Comando no encontrado: {command}")

# Registrando comandos en el bot
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help))
application.add_handler(CommandHandler("create_list", TodoController.create_task_list))
application.add_handler(CommandHandler("select_list", TodoController.select_task_list))
application.add_handler(CommandHandler("add", TodoController.add_todo))
application.add_handler(CommandHandler("list", TodoController.list_todos))
application.add_handler(CommandHandler("check", TodoController.check_todo))
application.add_handler(CommandHandler("clear", TodoController.clear_todos))

application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Hola$"), greet_user))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Gracias$"), thank_user))

# Añade los handlers
application.add_handler(user_profile_controller_conversation_handler)
application.add_handler(callback_handler)
application.add_handler(delete_callback_handler)
application.add_handler(add_user_conversation_handler)

# Añade más CommandHandlers si es necesario
application.add_handler(CommandHandler("view_users", UserProfileController.view_users))
application.add_handler(CommandHandler("select_user", UserProfileController.select_user))
application.add_handler(CommandHandler("delete_user", UserProfileController.delete_user))

# Añade el handler al bot
application.add_handler(add_user_conversation_handler)

# Corre el bot
application.run_polling(allowed_updates=Update.ALL_TYPES)