import sqlite3
import telebot
from telebot import types
from config import DATABASE

DB_NAME = "quiz.db"
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(BOT_TOKEN)


def serialize_options(options):
    return "|".join(options)


def parse_options(options_text):
    return options_text.split("|") if options_text else []


def build_options_keyboard(options):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(text=opt) for opt in options]
    keyboard.add(*buttons)
    return keyboard

def create_quiz_database():
    # 1. Подключаемся к файлу БД (если его нет, он создастся автоматически)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Инициализация базы данных...")

    # 2. Создаем таблицу для пользователей и их прогресса
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            score INTEGER DEFAULT 0,
            current_question INTEGER DEFAULT 0
        )
    ''')
    print("-> Таблица 'users' проверена/создана.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            options TEXT,
            correct_idx INTEGER
        )
    ''')

    print("-> Таблица 'questions' проверена/создана.")
    
    # 4. Проверяем, пустая ли таблица с вопросами
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        # Подготавливаем список вопросов
        # Варианты ответов упаковываем как разделённую строку для использования в TeleBot
        initial_questions = [
            ("Сколько спутников у Марса?", serialize_options(["1", "2", "3", "0"]), 1),
            ("Какая планета самая близкая к Солнцу?", serialize_options(["Венера", "Земля", "Меркурий", "Марс"]), 2),
            ("Какой океан самый большой?", serialize_options(["Атлантический", "Тихий", "Индийский"]), 1),
            ("В каком году Юрий Гагарин полетел в космос?", serialize_options(["1957", "1961", "1965", "1969"]), 1),
            ("Какой химический элемент обозначается как Au?", serialize_options(["Серебро", "Медь", "Золото", "Железо"]), 2)
        ]
        
        # Массово записываем вопросы в БД
        cursor.executemany(
            "INSERT INTO questions (text, options, correct_idx) VALUES (?, ?, ?)", 
            initial_questions
        )
        # Сохраняем изменения в файле
        conn.commit()
        print(f"-> Добавлено {len(initial_questions)} стартовых вопросов.")
    else:
        print("-> Вопросы уже существуют в базе, добавление пропущено.")
    
    # 5. Закрываем соединение
    conn.close()
    print("База данных успешно настроена и готова к работе!")

if __name__ == "__main__":
    create_quiz_database()
