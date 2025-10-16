import telebot
from telebot import types

# Замени на свой токен
bot = telebot.TeleBot("8287607784:AAFToqSTAGtH989wEmI5tdT0bBDMFeM0RHE")

# Словари для хранения данных
user_requests = {}
user_applications = {}  # Храним заявки пользователей
admin_reply_mode = {}   # Режим ответа админа

# ЗАМЕНИ НА СВОЙ ID
ADMIN_ID = 5049406522  # ← ТВОЙ ID ЗДЕСЬ

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Если это админ в режиме ответа - сбрасываем режим
    if message.chat.id == ADMIN_ID and ADMIN_ID in admin_reply_mode:
        del admin_reply_mode[ADMIN_ID]
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_problem = types.KeyboardButton('🚨 Проблема')
    btn_suggestion = types.KeyboardButton('💡 Предложение')
    markup.add(btn_problem, btn_suggestion)
    
    welcome_text = """👋 Привет! Добро пожаловать в *БотТехПоддержки DogClient*! 
    
📝 Опиши проблему/предложение для чита, награды не пожалеем! 🎁💰

*Выбери тип обращения:*"""
    
    bot.send_message(message.chat.id, welcome_text, 
                     reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text in ['🚨 Проблема', '💡 Предложение'])
def handle_request_type(message):
    chat_id = message.chat.id
    
    # Если админ в режиме ответа - игнорируем
    if chat_id == ADMIN_ID and ADMIN_ID in admin_reply_mode:
        return
    
    request_type = "проблему" if message.text == '🚨 Проблема' else "предложение"
    
    # Сохраняем тип заявки
    user_requests[chat_id] = {'type': request_type}
    
    sample_text = f"""
📋 *Образец оформления {request_type}:*

1️⃣ *Кратко опишите {request_type}*
2️⃣ *К чему она относится* (читы, функционал, баги и т.д.)
3️⃣ *Опишите предложение* по решению/улучшению

✨ *Пример:*
1. Не работает автопотеря
2. Относится к модулю PvP
3. Предлагаю добавить проверку координат перед использованием

⚠️ *Пожалуйста, пришлите сообщение в одном сообщении по образцу выше*"""
    
    # Убираем клавиатуру для чистого ввода
    markup = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, sample_text, 
                     reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.chat.id in user_requests)
def handle_user_request(message):
    chat_id = message.chat.id
    
    # Если админ в режиме ответа - игнорируем
    if chat_id == ADMIN_ID and ADMIN_ID in admin_reply_mode:
        return
    
    user_request = user_requests[chat_id]
    
    # Проверяем, содержит ли сообщение все три пункта
    lines = message.text.split('\n')
    numbered_lines = [line for line in lines if any(line.strip().startswith(str(i)) for i in range(1, 4))]
    
    if len(numbered_lines) >= 3:
        # Формируем заявку
        request_text = f"""🎯 *Новая заявка в техподдержку*

👤 *От пользователя:* @{message.from_user.username or 'Нет username'}
🆔 *ID:* {message.from_user.id}
📊 *Тип:* {user_request['type']}

📝 *Содержание:*
{message.text}

⏰ *Время:* {message.date}"""
        
        # Сохраняем заявку для ответа
        application_id = f"{chat_id}_{message.message_id}"
        user_applications[application_id] = {
            'user_id': chat_id,
            'username': message.from_user.username or 'Без username',
            'text': message.text
        }
        
        # Отправляем подтверждение пользователю
        bot.send_message(chat_id, "✅ *Спасибо! Ваша заявка принята!*\n\n🎁 Награда уже на пути к вам! 🚀", 
                         parse_mode='Markdown')
        
        # Отправляем заявку админу с кнопкой "Ответить"
        markup = types.InlineKeyboardMarkup()
        btn_reply = types.InlineKeyboardButton('💌 Ответить пользователю', callback_data=f'reply_{application_id}')
        markup.add(btn_reply)
        
        try:
            bot.send_message(ADMIN_ID, request_text, reply_markup=markup, parse_mode='Markdown')
            print(f"✅ Заявка отправлена админу (ID: {ADMIN_ID})")
        except Exception as e:
            print(f"❌ Ошибка отправки админу: {e}")
        
        # Удаляем временные данные
        del user_requests[chat_id]
        
    else:
        bot.send_message(chat_id, "❌ *Сообщение не соответствует формату!*\n\n⚠️ Пожалуйста, используйте образец с тремя пунктами:\n\n1. Краткое описание\n2. К чему относится\n3. Ваше предложение", 
                         parse_mode='Markdown')

# Обработчик кнопки "Ответить"
@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def handle_reply_callback(call):
    application_id = call.data.replace('reply_', '')
    
    if application_id in user_applications:
        application = user_applications[application_id]
        
        # Включаем режим ответа для админа
        admin_reply_mode[ADMIN_ID] = {
            'target_user_id': application['user_id'],
            'application_id': application_id,
            'username': application['username']
        }
        
        # Просим админа написать ответ
        bot.send_message(ADMIN_ID, 
                        f"💌 *Режим ответа включен*\n\n"
                        f"👤 *Пользователь:* @{application['username']}\n"
                        f"🆔 *ID:* {application['user_id']}\n\n"
                        f"📝 *Напиши ответ сообщением ниже:*\n"
                        f"(Для отмены отправь /start)",
                        parse_mode='Markdown')
        
        # Подтверждаем нажатие кнопки
        bot.answer_callback_query(call.id, "Режим ответа активирован! Напиши сообщение")

# Обработчик сообщений админа (когда он в режиме ответа)
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.chat.id in admin_reply_mode)
def handle_admin_reply(message):
    # Игнорируем команды
    if message.text.startswith('/'):
        return
    
    admin_data = admin_reply_mode[ADMIN_ID]
    target_user_id = admin_data['target_user_id']
    
    try:
        # Отправляем ответ пользователю
        reply_text = f"""💌 *Ответ от техподдержки DogClient:*

{message.text}

🎁 *Спасибо за вашу заявку!*"""
        
        bot.send_message(target_user_id, reply_text, parse_mode='Markdown')
        bot.send_message(ADMIN_ID, "✅ *Ответ успешно отправлен пользователю!*", parse_mode='Markdown')
        
        # Удаляем заявку из памяти
        application_id = admin_data['application_id']
        if application_id in user_applications:
            del user_applications[application_id]
            
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ *Ошибка отправки:* {e}", parse_mode='Markdown')
    
    # Выключаем режим ответа
    del admin_reply_mode[ADMIN_ID]

# Обработчик для любой другой команды
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    # Если пользователь не в процессе заявки - предлагаем начать
    if message.chat.id not in user_requests and message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "🤖 Используй /start чтобы начать!")
    elif message.chat.id == ADMIN_ID and ADMIN_ID in admin_reply_mode:
        # Админ в режиме ответа - игнорируем другие команды
        pass

# Запускаем бота
print("🤖 Бот техподдержки запущен!")
print("💌 Режим ответов на заявки активирован!")
bot.polling(none_stop=True)
