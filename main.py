from pyrogram import Client, filters, types
import keyboard  as kb
import datetime
import asyncio

api_id ="API_ID"
api_hash ="API_HASH"
bot_token ="BOT_TOKEN"

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

poll_data = {}
voters = {} 
@app.on_message(filters.command("start"))
async def start(client, message):
    keyboard =kb.one_keyboard()
    await message.reply("Нажмите кнопку, чтобы создать опрос:",reply_markup=keyboard)
@app.on_message(filters.command("create_poll"))
async def ask_question(client, message):
    user_id = message.from_user.id
    poll_data[user_id] = {"chat_id":"CHAT_ID"}
    await message.reply("Введите вопрос для опроса:")

@app.on_message(filters.text & filters.private)
async def ask_options(client, message):
    user_id = message.from_user.id
    if user_id in poll_data and "question" not in poll_data[user_id]:
        poll_data[user_id]["question"] = message.text
        await message.reply("Теперь введите варианты ответов через точку с запятой:")
    elif user_id in poll_data and "options" not in poll_data[user_id]:
        options = message.text.split(";")
        options = [option.strip() for option in options]
        if len(options) < 2:
            await message.reply("Пожалуйста, введите минимум 2 варианта ответа.")
            return
        poll_data[user_id]["options"] = options
        await message.reply("Введите время в формате ЧЧ:ММ, когда нужно проверить, кто не проголосовал (например, 14:30):")
    elif user_id in poll_data and "check_time" not in poll_data[user_id]:
        try:
            check_time = datetime.datetime.strptime(message.text, "%H:%M").time()
            poll_data[user_id]["check_time"] = check_time
        except ValueError:
            await message.reply("Пожалуйста, введите время в формате ЧЧ:ММ.")
            return
        
        await send_poll(client, message, poll_data[user_id],user_id)
async def send_poll(client, message, poll_info,user_id):
    try:
        poll_message = await client.send_poll(
            chat_id=poll_info["chat_id"],
            question=poll_info["question"],
            options=poll_info["options"],
            is_anonymous=False
        )
        
       
        if poll_message:  
            poll_data[user_id]["poll_id"] = poll_message.poll.id
            poll_data[user_id]["poll_message_id"] = poll_message.id
            poll_data[user_id]["voters"] = set() 
            await message.reply("Опрос создан!")
            await schedule_non_voters_check(client, user_id)
    
    except Exception as e:
        await message.reply(f"Ошибка при создании опроса: {e}")
async def schedule_non_voters_check(client, user_id: int):
    check_time = poll_data[user_id]["check_time"]
    now = datetime.datetime.now()
    check_datetime = datetime.datetime.combine(now.date(), check_time)

   
    if check_datetime < now:
        check_datetime += datetime.timedelta(days=1)
    
    
    wait_seconds = (check_datetime - now).total_seconds()
    await asyncio.sleep(wait_seconds)

    chat_id = poll_data[user_id]["chat_id"]

   
    members = [member.user.id async for member in client.get_chat_members(chat_id)]
    non_voters = [member for member in members if member not in poll_data[user_id]["voters"] and  member != (await app.get_me()).id]

    if non_voters:
       
        non_voters_mentions = []
        for user_id in non_voters:
            user = await client.get_users(user_id)
            mention = f"@{user.username}"
            non_voters_mentions.append(mention)
    
    
        await client.send_message(
            chat_id,
            f"Эти участники не проголосовали: {', '.join(non_voters_mentions)}",  
            reply_to_message_id=poll_data[user_id]["poll_message_id"] 
        )
    else:
        await client.send_message(chat_id, "Все участники проголосовали!")
    del poll_data[user_id]


# Запуск бота
app.run()
