import telebot
from telebot import types

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = '6806153412:AAEM_j0hQ8v3eAYpK1E_r0f9Q5x-GaQ03yM'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(func=lambda message: True, content_types=['text', 'document'])

def handle_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Hello")
    print("nice")

    if message.text:
        # If the message is a text (link)
        bot.send_message(chat_id, f"Received link: {message.text}")
    elif message.document:
        print("hi")
        # If the message is a document (file)
        file_info = bot.get_file(message.document.file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        bot.send_message(chat_id, f"Received file: {file_url}")
        bot.send_document(chat_id, file_info.file_id)

    print("he")

@bot.inline_handler(lambda query: True)
def inline_query(inline_query):
    try:
        link = inline_query.query

        # Create a link button
        link_button = types.InlineKeyboardButton(text="Send Link", url=link)
        markup = types.InlineKeyboardMarkup().add(link_button)

        # Create an InlineQueryResultArticle
        result = types.InlineQueryResultArticle(
            id=1,
            title="Send Link",
            input_message_content=types.InputTextMessageContent(
                message_text=f"Received link: {link}"
            ),
            reply_markup=markup
        )

        # Answer the inline query
        bot.answer_inline_query(inline_query.id, [result])
    except Exception as e:
        print(e)

if __name__ == "__main__":
    bot.polling(none_stop=True)