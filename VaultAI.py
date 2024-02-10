import telebot

from upyouth_vault_assist.upyouth_vault_interface import *

BOT_TOKEN="6806153412:AAEM_j0hQ8v3eAYpK1E_r0f9Q5x-GaQ03yM"

# Set up UpYouth Vault
vault = UpYouthVault("https://script.google.com/macros/s/AKfycbwvy35Xvp7oAzoEzpvYgCCQ4HdcID-PrfPaXWoDMfg-I6evdN64cgzCYtL1CWPnxQ0wjA/exec")

# data = vault.retrieveResources()

# for document in data:
#     vault.addResourceToChroma(document)

# Initialize the bot and OpenAI
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hi! I'm a bot powered by GPT-3.5. Send me a message, and I'll respond!")


def createDocumentText(document):
    line_seperate = "\n_____________\n"

    name = f"<b>{document.metadata['name']}</b>"
    description = document.metadata['brief']
    link = f"<b>Link:</b> <a href='{document.metadata['url']}'>Click me for the resource!</a>"

    message = f"{name}\n{description}\n\n{link}"

    return message

def createReference(document):
    link = f"<b>Resource:</b> <a href='{document.metadata['url']}'>{document.metadata['name']}</a>"
    message = f"{link}"

    return message

@bot.message_handler(commands=['search'])
def search(message):
    cid = message.chat.id

    try:
        query = message.text.split(" ", maxsplit = 1)[1]
        
        results = vault.semanticSearch(query)

        for document in results[0:1]:
            bot.send_message(cid, createDocumentText(document), parse_mode='HTML')

    except Exception as e:
        print(e)
        bot.reply_to(message, f"Error: {str(e)}")


@bot.message_handler(commands=['chat'])
def echo_all(message):
    cid = message.chat.id

    try:
        query = message.text.split(" ", maxsplit = 1)[1]

        result = vault.chat(query)
        answer = result["answer"].content
        docs = result["docs"]

        bot.reply_to(message, answer)

        for document in docs[0:1]:
            bot.send_message(cid, createReference(document), parse_mode='HTML')

        

    except Exception as e:

        bot.reply_to(message, f"Error: {str(e)}")

# Start the bot
bot.polling()