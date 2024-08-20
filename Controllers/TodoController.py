from telegram import Update
from telegram.ext import ContextTypes
from Models.Todo import Todo
from Models.TodoList import user_task_lists

todos = []

class TodoController:
    @staticmethod
    async def create_task_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.args:
            list_name = " ".join(context.args)
            user = context.user_data.get("current_user", "desconocido")
            
            if user not in user_task_lists:
                user_task_lists[user] = {}

            if list_name not in user_task_lists[user]:
                user_task_lists[user][list_name] = []
                await update.message.reply_text(f"Lista de tareas '{list_name}' creada.")
            else:
                await update.message.reply_text(f"La lista de tareas '{list_name}' ya existe.")
        else:
            await update.message.reply_text("Por favor, proporciona el nombre de la lista de tareas.")

    @staticmethod
    async def select_task_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.args:
            list_name = " ".join(context.args)
            user = context.user_data.get("current_user", "desconocido")
            
            if user in user_task_lists and list_name in user_task_lists[user]:
                context.user_data["current_task_list"] = list_name
                await update.message.reply_text(f"Lista de tareas actual seleccionada: '{list_name}'.")
            else:
                await update.message.reply_text(f"La lista de tareas '{list_name}' no existe.")
        else:
            await update.message.reply_text("Por favor, proporciona el nombre de la lista de tareas.")

    @staticmethod
    async def add_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.args:
            task_title = " ".join(context.args)
            user = context.user_data.get("current_user", "desconocido")
            task_list_name = context.user_data.get("current_task_list", "default")

            if user in user_task_lists and task_list_name in user_task_lists[user]:
                user_task_lists[user][task_list_name].append(Todo(task_title, user))
                await update.message.reply_text(f"Tarea '{task_title}' añadida a la lista '{task_list_name}'.")
            else:
                await update.message.reply_text("Primero selecciona una lista de tareas válida.")
        else:
            await update.message.reply_text("Por favor, proporciona el título de la tarea.")

    @staticmethod
    async def list_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = context.user_data.get("current_user", "desconocido")
        task_list_name = context.user_data.get("current_task_list", "default")

        if user in user_task_lists and task_list_name in user_task_lists[user]:
            user_todos = user_task_lists[user][task_list_name]
            if user_todos:
                task_list = "\n".join([f"{i + 1}. {str(todo)}" for i, todo in enumerate(user_todos)])
                await update.message.reply_text(f"Tareas en '{task_list_name}':\n{task_list}")
            else:
                await update.message.reply_text(f"No hay tareas en la lista '{task_list_name}'.")
        else:
            await update.message.reply_text("Primero selecciona una lista de tareas válida.")

    @staticmethod
    async def check_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.args:
            try:
                index = int(context.args[0]) - 1
                user = context.user_data.get("current_user", "desconocido")
                task_list_name = context.user_data.get("current_task_list", "default")
                if user in user_task_lists and task_list_name in user_task_lists[user]:
                    user_todos = user_task_lists[user][task_list_name]
                    if 0 <= index < len(user_todos):
                        task = user_todos[index]
                        if not task.is_completed:
                            task.set_completed()
                            await update.message.reply_text(f"Tarea '{task.title}' marcada como completada.")
                        else:
                            await update.message.reply_text(f"La tarea '{task.title}' ya está completada.")
                        
                        # Mostrar la lista actualizada
                        await TodoController.list_todos(update, context)
                    else:
                        await update.message.reply_text("Índice de tarea no válido.")
                else:
                    await update.message.reply_text("Primero selecciona una lista de tareas válida.")
            except ValueError:
                await update.message.reply_text("Por favor, proporciona un número válido.")
        else:
            await update.message.reply_text("Por favor, proporciona el número de la tarea a marcar como completada.")
    
    @staticmethod
    async def clear_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if todos:
            todos.clear()
            await update.message.reply_text("Todas las tareas han sido eliminadas.")
        else:
            await update.message.reply_text("No hay tareas para eliminar.")