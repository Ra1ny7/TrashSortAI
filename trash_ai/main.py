import os
from dotenv import load_dotenv
import telebot
from gtm_service import predict_image_class, recycling_tips

load_dotenv()
TG_TOKEN = os.getenv('TG_TOKEN')

bot = telebot.TeleBot(TG_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    text = (
        f'Привет, {message.from_user.first_name}! 👋\n\n'
        'Я бот, который помогает определить тип мусора по фото ♻️🗑️\n\n'
        '📸 Просто отправь мне изображение — и я подскажу, что это за отход и как его правильно утилизировать 🌍\n\n'
        '🔍 *Важно:* я лучше распознаю, если на фото изображён только один вид мусора. Например, только одна батарейка, одна бутылка или одна пара обуви.\n'
        'Если на фото сразу много всего — я могу запутаться 🙈\n\n'
        'Давайте сортировать мусор вместе — это просто и полезно! 💚'
        )
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    temp_message = bot.reply_to(message, 'Обработка фото...')
    file_info = bot.get_file(message.photo[-1].file_id)
    file_name = file_info.file_path.split('/')[-1]
    image_path= f'images/{file_name}'
    
    downloaded_file = bot.download_file(file_info.file_path)
    with open(image_path, 'wb') as file:
        file.write(downloaded_file)
        
    image_class, percentage_probability = predict_image_class(image_path)    
    
    bot.delete_message(message.chat.id, temp_message.message_id)
    bot.reply_to(message, f'С вероятностью {percentage_probability}% на фото {image_class.lower()}')
    
    if image_class is None:
        bot.reply_to(message, "🤔 Извините, я не уверен, что изображено на фото.")
    else:
        tip = recycling_tips.get(image_class, "ℹ️ Увы, у меня нет совета по этому виду мусора.")
        response = f"✅ На фото: *{image_class.lower()}* (уверенность {percentage_probability}%).\n\n{tip}"
        bot.reply_to(message, response, parse_mode='Markdown')
    
    os.remove(image_path)
    
bot.infinity_polling()