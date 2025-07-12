from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import json
from datetime import datetime

DATA_FILE = 'data.json'
CONFIG_FILE = 'config.json'

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "receiver": {
                "user_id": "",
                "name": "",
                "score": 0,
                "actions": []
            },
            "history": []
        }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Добавление баллов
async def award(update: Update, context: ContextTypes.DEFAULT_TYPE, points: int, reason: str, extra: str = None):
    user_id = update.effective_user.id
    config = load_config()
    data = load_data()

    if user_id not in config["admins"]:
        await update.message.reply_text("⛔ У вас нет прав.")
        return

    data["score"] += points
    data["actions"].append({
        "from": user_id,
        "points": points,
        "reason": reason,
        "time": datetime.now().isoformat()
    })

    save_data(data)
    await update.message.reply_text(f"Ярослав получил {points:+} баллов за: {reason}")

    if extra:
        await update.message.reply_text(extra)

# Команды для конкретных действий
async def morn_routine(update, context): await award(update, context, +1, "утреннюю рутину", extra="так держать!")
async def self_room(update, context): await award(update, context, +2, "уборку комнаты")
async def kitchen(update, context): await award(update, context, +2, "уборку кухни")
async def sport(update, context): await award(update, context, +2, "выполнение спорт нормы дня")
async def chapter(update, context): await award(update, context, +1, "прочитанную главу книги")
async def self_initiated(update, context): await award(update, context, +3, "помощь семье без просьбы")
async def brain_trained(update, context): await award(update, context, +1, "развитие ума")
async def perfect_kid(update, context): await award(update, context, +1, "вел_себя_образцово")
async def poop(update, context): await award(update, context, +1, "уборку выбросов кота", extra = "Марсель благодарит вас, о блюститель лотковой чистоты! Мяу 😻")
async def orator1(update, context): await award(update, context, +1, "хорошее чтение вслух", extra = "не отчаивайтесь, сэр")
async def orator2(update, context): await award(update, context, +2, "отличное чтение вслух", extra = "мои поздравления, сэр")

async def rowdiness(update, context): await award(update, context, -2, "упрямство")
async def ignored(update, context): await award(update, context, -1, "игнор просьбы > 10мин")
async def conflict(update, context): await award(update, context, -3, "конфликт")
async def stroke(update, context): await award(update, context, -2, "не выполнил задание из списка дел на день")
async def brainroot(update, context): await award(update, context, -1, "сидел/лежал в телефоне не выполнив цель дня")

# Итог дня
async def itog_dnya(update, context):
    data = load_data()
    msg = "🏁 *Итог дня:*\n"
    for uid, info in data["users"].items():
        msg += f"{info['name']}: {info['score']} баллов\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# За что
async def za_chto(update, context):
    data = load_data()
    msg = "📋 *Детализация действий:*\n"
    for record in data["history"][-20:]:  # последние 20
        user = data["users"].get(record["user_id"], {"name": "Неизвестно"})
        msg += f"{user['name']}: {record['points']} за {record['reason']}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# Главная функция
def main():
    app = ApplicationBuilder().token("8058566086:AAGPqbG5ulEw2DIrBWW5CQCHcQPJ6AflxRo").build()

    app.add_handler(CommandHandler("results", itog_dnya))
    app.add_handler(CommandHandler("why", za_chto))

    app.add_handler(CommandHandler("morning_routine", morn_routine))
    app.add_handler(CommandHandler("room_is_clean", self_room))
    app.add_handler(CommandHandler("kitchen_is_clean", kitchen))
    app.add_handler(CommandHandler("sport", sport))
    app.add_handler(CommandHandler("chapter", chapter))
    app.add_handler(CommandHandler("self_initiated", self_initiated))
    app.add_handler(CommandHandler("brain_trained", brain_trained))
    app.add_handler(CommandHandler("perfect_kid", perfect_kid))
    app.add_handler(CommandHandler("cat_poop", poop))
    app.add_handler(CommandHandler("speaker_1", orator1))
    app.add_handler(CommandHandler("speaker_2", orator2))

    app.add_handler(CommandHandler("rowdiness", rowdiness)) #упрямство
    app.add_handler(CommandHandler("ignored", ignored)) #игнор просьбы > 10мин
    app.add_handler(CommandHandler("conflict", conflict)) #грубость/капри/спор
    app.add_handler(CommandHandler("stroke", stroke)) #не выполнил задание из списка дел на день
    app.add_handler(CommandHandler("brain_root", brainroot)) #сидел/лежал в телефоне не выполнив цель дня

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()