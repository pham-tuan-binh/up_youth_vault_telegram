import os
import json
import telebot
import requests
from upyouth_vault_assist.upyouth_vault_interface import *

# UpYouth Bot
# BOT_TOKEN = '6792208041:AAHaeLis5jciaTTAj_s50GQ7jnyDqu9zj48'

# Test Bot
BOT_TOKEN = '6806153412:AAEM_j0hQ8v3eAYpK1E_r0f9Q5x-GaQ03yM'

API_ENDPOINT = 'https://script.google.com/macros/s/AKfycbwvy35Xvp7oAzoEzpvYgCCQ4HdcID-PrfPaXWoDMfg-I6evdN64cgzCYtL1CWPnxQ0wjA/exec'

# Create a bot instancecn
bot = telebot.TeleBot(BOT_TOKEN)

# Set up UpYouth Vault
vault = UpYouthVault("https://script.google.com/macros/s/AKfycbwvy35Xvp7oAzoEzpvYgCCQ4HdcID-PrfPaXWoDMfg-I6evdN64cgzCYtL1CWPnxQ0wjA/exec")

commands = {  # command description used in the "help" command
    'start'       : 'Get used to the bot.',
    'help'        : 'Gives you information about the available commands.',
    'authorize': "Prove you're an UpYouthian by saying the magic word.",
    'subscribe'    : "Subscribe to new resources' updates.",
    'new_resource': "Upload new resource.",
    'send_resource_directly': "Upload new resource in 1-step.",
    'chat': "Chat with Bob",
    'search': "Search sematically for resources on Vault",
    'give_food': "Give food to Bob."
}

# File paths for persistent data
AUTHORIZED_USERS_FILE = './TelegramUsersStorage/authorized_users.json'
SUBSCRIBERS_FILE = './TelegramUsersStorage/subscribers.json'

# Load authorized users from file
def load_authorized_users():
    if os.path.exists(AUTHORIZED_USERS_FILE):
        with open(AUTHORIZED_USERS_FILE, 'r') as file:
            return json.load(file)
    return []

# Save authorized users to file
def save_authorized_users(authorized_users):
    with open(AUTHORIZED_USERS_FILE, 'w') as file:
        json.dump(authorized_users, file)

# Load subscribers from file
def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, 'r') as file:
            return json.load(file)
    return []

# Save subscribers to file
def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, 'w') as file:
        json.dump(subscribers, file)

# Initialize persistent data
authorized_users = load_authorized_users()
subscribers = load_subscribers()

# food counter
food = 0

@bot.message_handler(commands=['give_food'])
def give_food(message):
    global food
    food += 1
    bot.send_message(message.chat.id, f"Yummy! I've eaten this much: {food}") 

def createNotification(resource):
    line_seperate = "\n_____________\n"

    name = f"<b>{resource['name']}</b>"
    description = resource['description']
    tags = f"<b>Tags:</b> {resource['tags']}"
    link = f"<b>Link:</b> <a href='{resource['link']}'>Click me for the resource!</a>"
    author = f"<i>A new resource is uploaded by <b>{resource['uploadedBy']}</b></i>"
    cta = f"<b>Shortcut:</b> <a href='https://docs.google.com/spreadsheets/d/1-V_X7kJ6Oc9cr0vtW6VkpTpTh-myJ0hLN31ORF6gGag/edit?usp=sharing'>View all resources in UpYouth Vault!</a>"

    message = f"{author}{line_seperate}\n{name}\n{description}\n\n{tags}\n{link}\n{cta}"

    return message

def postNotification(resource):
    text = createNotification(resource)
    for id in subscribers:
        bot.send_message(id, text, parse_mode='HTML')
        if resource["type"] == "photo":
            bot.send_photo(id, resource["id"])
        elif resource["type"] == "doc":
            bot.send_document(id, resource["id"])
        
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "To talk to me, the following commands are available: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        # function which connects all strings
        "Hello, I'm <b>Bob</b>, proud guardian of the Vault of UpYouth.",
        parse_mode='HTML'
    )
    command_help(message)

@bot.message_handler(commands=['show'])
def show(message):
    print(authorized_users)
    print(subscribers)

@bot.message_handler(commands=['get_chat_id'])
def get_chat_id(message):
    bot.reply_to(
        message, f"Your chat id is: {message.chat.id}"
    )

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    chat_id = message.chat.id

    if chat_id not in authorized_users:
        bot.send_message(chat_id, "Hey! Present yourself using /authorize")
        return
    
    if chat_id in subscribers:
        bot.send_message(chat_id, "Don't you annoy me! You subscribed already.")
        return
    
    subscribers.append(chat_id)
    save_subscribers(subscribers);
    
    bot.send_message(chat_id, "You're subscribed to the vault.")

    

@bot.message_handler(commands=['authorize'])
def authorize(message):
    chat_id = message.chat.id

    if chat_id in authorized_users:
        bot.send_message(chat_id, "Arghh! You're already authorized.")
        return
    
    sent_message = bot.send_message(chat_id, "You're a stranger! Present yourself or be gone. Tell me the secret password!")
    bot.register_next_step_handler(sent_message, check_password)

def check_password(message):
    
    if message.text == "Meoww":
        authorized_users.append(message.chat.id)
        save_authorized_users(authorized_users);

        bot.send_message(message.chat.id, "Hehe! Come in, make yourself at home.")
    else:
        bot.send_message(message.chat.id, "You imposter! Don't come near.")

@bot.message_handler(commands=['send_resource_directly'])
def send_resource_directly(message):
    chat_id = message.chat.id

    if chat_id not in authorized_users:
        bot.send_message(chat_id, "Hey! Present yourself using /authorize")
        return

    resource_name = bot.send_message(chat_id, "Send me your resource.")
    
    resource = {}
    resource["name"] = "Directly sent resource"
    resource["description"] = "Directly sent resource"
    resource["tags"] = "direct"

    bot.register_next_step_handler(resource_name, after_link, resource)



@bot.message_handler(commands=['new_resource'])
def add_resource(message):
    chat_id = message.chat.id

    if chat_id not in authorized_users:
        bot.send_message(chat_id, "Hey! Present yourself using /authorize")
        return

    resource_name = bot.send_message(chat_id, "Tell me the name of your resource")
    
    resource = {}
    bot.register_next_step_handler(resource_name, after_name, resource)

def after_name(message, resource):
    chat_id = message.chat.id
    resource_name = message.text
    resource["name"] = resource_name

    bot.send_message(chat_id, "Yummy! \"" + resource_name + "\" sounds good." )
    

    description = bot.send_message(chat_id, "What is it though? Give me a brief description." )

    bot.register_next_step_handler(description, after_description,resource)

def after_description(message, resource):
    chat_id = message.chat.id
    description = message.text
    resource["description"] = description

    bot.send_message(chat_id, "Now I understand!")
    tags = bot.send_message(chat_id, "Give me some tags to describe the content you just give me! It should be the following format: tag1,tag2,tag3.")

    bot.register_next_step_handler(tags, after_tags, resource)

def after_tags(message, resource):
    chat_id = message.chat.id
    tags = message.text
    resource["tags"] = tags

    link = bot.send_message(chat_id, "Aight, give me the resource.")

    bot.register_next_step_handler(link, after_link, resource)

def after_link(message, resource):
    if message.text:
        # If the message is a text (link)
        resource["link"] = message.text
        resource["type"] = "txt"
    elif message.document:
        # If the message is a document (file)
        file_info = bot.get_file(message.document.file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        resource["id"] = message.document.file_id
        resource["link"] = file_url
        resource["type"] = "doc"
    elif message.photo:
        # If the message is a photo
        photo_info = message.photo[-1]  # Get the last photo (highest resolution)
        file_info = bot.get_file(photo_info.file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        resource["id"] = photo_info.file_id
        resource["link"] = file_url
        resource["type"] = "photo"

    confirmation(message, resource)

def confirmation(message, resource):
    chat_id = message.chat.id

    confirm = bot.send_message(chat_id, "Confirm you want to upload this resource by typing yes/no.")

    bot.register_next_step_handler(confirm, upload_resource, resource)


def upload_resource(message, resource):
    chat_id = message.chat.id

    if message.text != "yes":
        bot.send_message(chat_id, "Your secret is safe with me.")
        return
    
    if message.chat.first_name is None:
        first_name = ""
    else:
        first_name = message.chat.first_name

    if message.chat.last_name is None:
        last_name = ""
    else:
        last_name = message.chat.last_name

    resource["uploadedBy"] = f"{first_name} {last_name}"
    
    json_payload = json.dumps(resource, indent=2)

    # Post JSON payload to the API endpoint
    response = post_to_api(json_payload)

    chromaDocumentResource = {
        "link": resource["link"],
        "brief": resource["description"],
        "name": resource["name"]
    }

    vault.addResourceToChroma(chromaDocumentResource)

    if response is not None and response.status_code == 200:
        bot.reply_to(message, "Hehe! Your resource is saved!")
        postNotification(resource)
    else:
        bot.reply_to(message, "Your resource was lost in delivery! I'm looking into it with my troops. Please re-upload!")

def post_to_api(json_payload):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_ENDPOINT, data=json_payload, headers=headers)
        return response
    except Exception as e:
        print(f"Error posting request to API: {e}")
        return None

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

    if cid not in authorized_users:
        bot.send_message(cid, "Hey! Present yourself using /authorize")
        return

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

    if cid not in authorized_users:
        bot.send_message(cid, "Hey! Present yourself using /authorize")
        return

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

if __name__ == '__main__':
    bot.polling(non_stop=True)
