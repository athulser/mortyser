import openai, telebot, urllib.request, re, datetime, os, time
from pytube import YouTube
from telebot import types
from functions import askAI, resetFile, sourcecode, isValid, randomNumber, isSubscriber, json
from dotenv import load_dotenv, find_dotenv
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
load_dotenv(find_dotenv())
TELE_API_KEY = os.getenv('TELE_API_KEY')
AI_API_KEY = os.getenv('AI_API_KEY')
SUDO_ID = os.getenv('SUDO_ID')

# INITIALISING THE BOT WITH TELEGRAM API
bot = telebot.TeleBot(TELE_API_KEY, threaded=True)
openai.api_key = AI_API_KEY


# FUNCTION TO SEARCH VIDEO AND RETURN DICT OF TITLE AND CORRESPONDING URL
def searchVideo(title):
    data = {}
    html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={title}")
    params = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    base = 'https://www.youtube.com/watch?v='
    for param in params[:5]:
        url = base + param
        video = YouTube(url)
        title = video.title
        data[title] = url
    return data


def generate_image(prompt, message):
    num_image = 1
    output_format='url'
    size='1024x1024'
    invalid_words = ['sexy', 'fuck', 'dick', 'sex','asshole', 'vagina', 'penis', 'butt','breast']
    for i in invalid_words:
        if i in prompt:
            bot.send_message(message.chat.id, "Your query contains forbidden words")
            return 'err'
    try:
        images = []
        response = openai.Image.create(
            prompt=prompt,
            n=num_image,
            size=size,
            response_format=output_format
        )
        if output_format == 'url':
            for image in response['data']:
                images.append(image.url)
        elif output_format == 'b64_json':
            images.append(image.b64_json)
        return {'created':datetime.datetime.fromtimestamp(response['created']), 'images':images}
    except Exception as e:
        with open('imgErrorLog.txt', 'a') as file:
            data = f'QUERY : {prompt}\n\n{e}\nTRACEBACK\n\n{e.with_traceback}\n\n---------------------\n\n'
            file.write(data)
            print("ERROR HAS BEEN LOGGED TO FILE")
            bot.send_message(message.chat.id, e)
            return 'err'


# /START COMMAND
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Morty AI Bot is a chatbot that provides a range of AI-driven services to help people manage their day-to-day tasks. It can help you with tasks such as:\n\n🔰 *AI Image generation*\n🔰 *AI ChatBot*\n🔰 *Youtube video/audio downloading*\n🔰 *Web scraping*\n🔰 *and more.*\n\nIt is powered by *natural language processing (NLP)* and *machine learning technology* to provide a personalized experience. To get started, simply send a message to Morty AI and it will respond with the help you need.\n\n*⚠️ BASIC COMMANDS ⚠️*\n/play - To play any music\n/img - To generate images based on your query\n/msg - Chat with Morty AI\n/youtube - Download YouTube video/audio\n/subscribe - Subscribe to premium\n/scrape - Web scraping\n/developer - Developer Information", parse_mode='Markdown')
    userID = message.chat.id
    exists = 1  # 0 is TRUE, 1 is FALSE
    with open('users.json','r') as file:
        json_data = json.load(file)
        for i in json_data:
            if i['id'] == str(userID):
                exists = 0
            elif i['id'] != str(userID):
                continue
    if exists == 1:
        towrite = {"id":str(userID), "images_generated":0}
        json_data.append(towrite)
        with open('users.json', 'w') as writefile:
            json.dump(json_data, writefile, indent=4)




# /PLAY COMMAND
@bot.message_handler(commands=['play'])
def play_command(message):
    id = message.chat.id
    query = message.text.replace('/play','')
    if len(query) == 0:
        bot.send_message(id, "Use `/play songname` format", parse_mode="Markdown")
    else:
        _message = bot.send_message(id, "`Fetching . . .`", parse_mode='Markdown')
        chat_id, message_id = _message.chat.id, _message.message_id
        query = query.replace(' ', '+')
        data = searchVideo(query)
        first_markup = InlineKeyboardMarkup()
        for title, url in data.items():
            first_markup.add(
                InlineKeyboardButton(title, callback_data=url)
            )
        first_markup.add(
            InlineKeyboardButton("❌ Cancel ❌", callback_data="cancel")
        )
        global filename
        filename = f'{query.replace("+", "")}.mp3'
        global _hehe
        _hehe = bot.edit_message_text(message_id=message_id,chat_id=chat_id, text="🎧 Select a music 🎧\n\n👇", reply_markup=first_markup)






# CALLBACK QUERY HANDLERS FOR ALL COMMANDS WITH INLINEKEYBOARD CALLBACKS
@bot.callback_query_handler(func=lambda message: True)
def callback_query_handler(call):
    if call.data.startswith('https://'):
        url = call.data
        try:
            global realvideo
            realvideo = YouTube(url=url)
            caption = f'_🎧 Feel the beats V1.0 🎧_\n\n_Title : {realvideo.title}_\n_Author : {realvideo.author}_\n_Duration : {datetime.timedelta(seconds=realvideo.length)}s_\n\n`Click the top panel to open interactive media player`'
        except:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="`Exception occured`", parse_mode="Markdown")
        _message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="`Processing . . .`", parse_mode="Markdown")
        # PHASE 1
        try:
            realvideo.streams.get_lowest_resolution().download(filename=filename)
        except Exception as m:
            bot.send_message(call.message.chat.id, "❗️ ERROR WHILE DOWNLOADING")
            print(f"ERROR WHILE DOWNLOADING\n\n{m}")
        # PHASE 2
        try:
            with open(filename, 'rb') as audiofile:
                bot.send_audio(call.message.chat.id, audiofile, caption=caption, parse_mode='Markdown')
                bot.delete_message(chat_id=_message.chat.id, message_id=_message.message_id)
        except Exception as n:
            bot.send_message(call.message.chat.id, "❗️ ERROR WHILE SENTING")
            print(f"ERROR WHILE SENTING\n\n{n}")
        #PHASE 3
        try:
            os.remove(filename)
        except:
            print("ERROR WHILE DELETING")
        newmarkup = InlineKeyboardMarkup()
        newmarkup.add(
            InlineKeyboardButton("Yes ✅", callback_data="yes"),
            InlineKeyboardButton("No ❌", callback_data="no")
        )
        global _msg
        _msg = bot.send_message(call.message.chat.id, "_Do you want more info about this music?_", parse_mode="Markdown", reply_markup=newmarkup)
    else:
        if call.data == 'no':
            bot.delete_message(chat_id=_msg.chat.id, message_id=_msg.message_id)
        elif call.data == 'yes':
            mainmsg = realvideo.thumbnail_url
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("Channel link", url=realvideo.channel_url)
            )
            content = f'*Title* : _{realvideo.title}_\n*Author* : _{realvideo.author}_\n*Duration* : _{datetime.timedelta(seconds=realvideo.length)}s_\n*Published On* : _{str(realvideo.publish_date)[:10]}_\n*Is age restricted* : _{str(realvideo.age_restricted)}_\n*Views* : _{str(realvideo.views)} views_\n*Rating* : _{str(realvideo.rating)}_'
            bot.delete_message(chat_id=_msg.chat.id, message_id=_msg.message_id)
            bot.send_photo(call.message.chat.id, mainmsg, caption=content, parse_mode='Markdown', reply_markup=markup)
        elif call.data == 'cancel':
            bot.delete_message(chat_id=_hehe.chat.id, message_id=_hehe.message_id)


# /SUBSCRIBE COMMAND
@bot.message_handler(commands=['subscribe'])
def subscribe_command(message):
    notSubscribed = True
    accessCode = message.text.replace('/subscribe', '')
    accessCode = accessCode.strip()
    if len(accessCode) == 0:
        bot.send_message(message.chat.id, "Here is the [link](https://paytm.me/FYCO-4w) for payment\n\nPay just *INR 99/-* and send the proof [here](https://t.me/ieatkidsforlunch) to get the access code.\n\nUse this Access code as\n'`/subscribe Youraccesscode`'\nto get Premium subscription\n\nSend '`/subscribe status`' to see your subscription status.\n\nYou will get:\n✅ - *Unlimited images*\n✅ - *Ultra realistic 4K images*\n✅ - *Accurate image rendering*\n✅ - *And many more...*", parse_mode='Markdown', disable_web_page_preview=True)
    elif accessCode == 'status':
        res = isSubscriber(message.chat.id)
        if res == 1:
            bot.send_message(message.chat.id, "*STATUS : PREMIUM USER*\n\nYou have all the benefits granted!", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "*STATUS : FREE USER*\n\nSend `/subscribe` to see more details on how to become a *premium user*", parse_mode="Markdown")
    else:
        accessCode = accessCode.strip()
        userID = message.chat.id
        with open('subscribers.json', 'r') as file:
            json_data = json.load(file)
            for i in json_data:
                if i['id'] == str(userID):
                    bot.reply_to(message, "You are already a subscriber, enjoy the benefits")
                    notSubscribed = False
                else:
                    notSubscribed = True
        accepted = 1 # TRUE = 0 AND FALSE = 1
        if notSubscribed:
            with open('Accesscodes.json', 'r') as file:
                json_code_data = json.load(file)
                for i in json_code_data:
                    if i['code'] == accessCode:
                        accepted = 0
                        bot.send_message(int(SUDO_ID), f"✅ @{str(message.from_user.username)} has subscribed to Morty AI\n\nID : {str(message.chat.id)}")
                        bot.send_message(message.chat.id, "✅ Congrats!!\nYou are subscribed to get acccess to many features. Enjoy your benefits.")
                        break
                    else:
                        accepted = 1
        if accepted == 0:
            for i in json_code_data:
                if i['code'] == accessCode:
                    json_code_data.remove(i)
            with open('Accesscodes.json', 'w') as filetowrite:
                json.dump(json_code_data, filetowrite, indent=4)
            towrite = {"id": str(userID)}
            json_data.append(towrite)
            with open('subscribers.json', 'w') as file:
                json.dump(json_data, file, indent=4)
        if accepted == 1 and notSubscribed == True:
            bot.send_message(userID, "❗️ The Access code was incorrect.")

# /BC COMMAND (OWNER)
@bot.message_handler(commands=['bc'])
def bc_command(message):
    if str(message.chat.id) == SUDO_ID:
        query = message.text.replace('/bc', '')
        if len(query) == 0:
            bot.send_message(int(SUDO_ID), "Type something")
        else:
            with open('users.json', 'r') as users:
                json_data = json.loads(users.read())

            bot.send_message(int(SUDO_ID), "Started delivering . . .")
            for i in json_data:
                bot.send_message(int(i['id']), query, parse_mode='Markdown')
                time.sleep(3)

            bot.send_message(int(SUDO_ID), f"Message sent!\n\nMessage : {query}")



# /DATA
@bot.message_handler(commands=['data'])
def data_command(message):
    if str(message.chat.id) == SUDO_ID:
        with open('users.json','r') as users:
            bot.send_document(chat_id=message.chat.id, document=users)
        with open('subscribers.json','r') as subscribers:
            bot.send_document(chat_id=message.chat.id, document=subscribers)
        with open('Accesscodes.json','r') as codes:
            bot.send_document(chat_id=message.chat.id, document=codes)


# /RESET COMMAND
@bot.message_handler(commands=['reset'])
def reset_data(message):
    if str(message.chat.id) == SUDO_ID:
        res = resetFile()
        if res == "200":
            bot.send_message(message.chat.id, "users.json has been resetted!")




# /IMG COMMAND
@bot.message_handler(commands=['img'])
def img_command(message):
    query = message.text.replace('/img', '')
    if len(query) == 0:
        bot.send_message(message.chat.id, "Sent in '`/img query`' format\nExample :\n\n`/img An astronaut in the ocean`", parse_mode='Markdown')
    else:
        userID = message.chat.id
        images_generated = 0
        with open('users.json','r') as file:
            json_data = json.load(file)
            for i in json_data:
                if i['id'] == str(userID):
                    images_generated = i['images_generated']
                    if images_generated >= 3 and isSubscriber(userID) == 0:
                        bot.send_message(message.chat.id, "Your daily Limit has been reached!\nYou can get unlimited images after subscription.")
                        bot.send_message(message.chat.id, "Send `/subscribe` to see details on premium user", parse_mode='Markdown')
                    else:
                        response = generate_image(query, message)
                        if response == 'err':
                            bot.send_message(message.chat.id, "❗️ Some error occured")
                        else:
                            response['created']
                            images = response['images']
                            try:
                                for image in images:
                                    bot.send_photo(message.chat.id, image, caption="Generated by Morty AI.")
                                    images_generated = images_generated + 1
                                    i['images_generated'] = images_generated
                            except Exception as e:
                                print(e)
                                bot.send_message(message.chat.id, "❗️ Some error occured")
        with open('users.json', 'w') as writefile:
            json.dump(json_data, writefile, indent=4)




# /DEVELOPER COMMAND
@bot.message_handler(commands=['developer'])
def developer(message):
    keys = InlineKeyboardMarkup(row_width=2)
    ig = types.InlineKeyboardButton(text="Instagram", url="https://instagram.com/atul.d4")
    gh = types.InlineKeyboardButton(text="Github", url="https://github.com/47hxl-53r")
    wp = types.InlineKeyboardButton(text="WhatsApp", url="https://wa.me/+918606672509")
    tg = types.InlineKeyboardButton(text="Telegram", url="https://t.me/ieatkidsforlunch")
    keys.add(ig, gh, wp, tg)
    bot.send_message(message.chat.id, "This BOT is developed by 47hx1-53r (Athul).", reply_markup=keys)




# /COUNT COMMAND
@bot.message_handler(commands=['count'])
def count_command(message):
    userID = message.chat.id
    if str(userID) == SUDO_ID:
        with open('users.json', 'r') as usersfile:
            json_data = json.load(usersfile)
            users = []
            for i in json_data:
                users.append(i['id'])
        with open('subscribers.json', 'r') as subsfile:
            json_subs_data = json.load(subsfile)
            premium_users = []
            for j in json_subs_data:
                premium_users.append(j['id'])
        users_count = len(users)
        premium_count = len(premium_users)
        now = datetime.datetime.now()
        bot.send_message(int(SUDO_ID), f"Total Users : {str(users_count)}\n\nFree users : {str(users_count - premium_count)}\nPremium users : {str(premium_count)}\nTime : {str(now)}")




# /ERRORS COMMAND (SUDO)
@bot.message_handler(commands=['errors'])
def errors_command(message):
    if str(message.chat.id) == SUDO_ID:
        errors = []
        with open('imgErrorLog.txt', 'r') as imgerrorfile:
            imgdata = imgerrorfile.read()
            if len(imgdata) == 0:
                errors.append("Image error logs are Empty!")
            else:
                errors.append(imgdata)
        with open('msgErrorLog.txt', 'r') as msgerrorfile:
            msgdata = msgerrorfile.read()
            if len(msgdata) == 0:
                errors.append("Message error logs are Empty!")
            else:
                errors.append(msgdata)
        for i in errors:
            bot.send_message(int(SUDO_ID), i)
        bot.send_message(message.chat.id, "Send /clearerrors to clear error logs")

        
# /CLEARERRORS COMMAND
@bot.message_handler(commands=['clearerrors'])
def clearerrors_command(message):
    if str(message.chat.id) == SUDO_ID:
        with open('imgErrorLog.txt', 'w') as imgerrorfile:
            imgerrorfile.write("")
        with open('msgErrorLog.txt', 'w') as msgerrorfile:
            msgerrorfile.write("")
        bot.send_message(message.chat.id, "Error Logs cleared")


# /YOUTUBE COMMAND
@bot.message_handler(commands=['youtube'])
def youtube_command(message):
    res = bot.send_message(message.chat.id, "Send the URL to YouTube video")
    bot.register_next_step_handler(res, youtube_markup)
def youtube_markup(message):
    global url
    url = message.text
    custom = types.ReplyKeyboardMarkup()
    download_video = types.KeyboardButton("Download Video")
    download_audio = types.KeyboardButton("Download Audio")
    custom.row(download_video, download_audio)
    res = bot.send_message(message.chat.id, "What do you want me to do?", reply_markup=custom)
    bot.register_next_step_handler(res, youtube_download)
def youtube_download(message):
    if message.text == 'Download Video':
        global filename1
        filename1 = f'youtube-{randomNumber()}.mp4'
        custom = types.ReplyKeyboardRemove()
        global dldmsg
        dldmsg = bot.send_message(message.chat.id, "_Downloading . . ._", reply_markup=custom, parse_mode='Markdown')
        if isValid(url):
            video = YouTube(url)
            try:
                video = video.streams.get_highest_resolution().download(filename=filename1)
            except Exception as h:
                bot.delete_message(chat_id=dldmsg.chat.id, message_id=dldmsg.message_id)
                bot.send_message(message.chat.id, "❗️ ERROR WHILE DOWNLOADING")
                print(f"ERROR WHILE DOWNLOADING VIDEO\n\n{h}")
            try:
                with open(filename1, 'rb') as f: 
                    bot.send_video(message.chat.id, f, caption=video.title)
                    bot.delete_message(chat_id=dldmsg.chat.id, message_id=dldmsg.message_id)
            except TimeoutError:
                os.remove(filename1)
                print("Force deleted due to timeout error")
                bot.delete_message(chat_id=dldmsg.chat.id, message_id=dldmsg.message_id)
                bot.send_message(message.chat.id, "❗️ Timeout error occured. try again")
            except Exception as g:
                bot.delete_message(chat_id=dldmsg.chat.id, message_id=dldmsg.message_id)
                bot.send_message(message.chat.id, "❗️ ERROR WHILE SENTING")
                print(f"ERROR WHILE SENTING\n\n{g}")
            try:
                os.remove(filename1)
            except:
                print("ERROR WHILE DELETING")
        else:
            bot.send_message(message.chat.id, "❗️ Invalid YouTube link")
    elif message.text == 'Download Audio':
        custom = types.ReplyKeyboardRemove()
        filename2 = f'youtube-{randomNumber()}.mp3'
        ehhe = bot.send_message(message.chat.id, "_Downloading . . ._", reply_markup=custom, parse_mode='Markdown')
        if isValid(url):
            try:
                videofile = YouTube(url)
                videofile = videofile.streams.get_lowest_resolution().download(filename=filename2)
            except Exception as m:
                bot.send_message(message.chat.id, "❗️ ERROR WHILE DOWNLOADING")
                print(f"ERROR WHILE DOWNLOADING\n\n{m}")
            try:
                with open(filename2, 'rb') as audiofile:
                    bot.send_audio(message.chat.id, audiofile, caption="Downloaded by Morty AI")
                bot.delete_message(ehhe.chat.id, ehhe.message_id)
            except TimeoutError:
                os.remove(filename2)
                bot.send_message(message.chat.id, "❗️ Timeout error occured. try again")
                bot.delete_message(ehhe.chat.id, ehhe.message_id)
            except Exception as n:
                bot.send_message(message.chat.id, "❗️ ERROR WHILE SENTING")
                bot.delete_message(ehhe.chat.id, ehhe.message_id)
                print(f"ERROR WHILE SENTING\n\n{n}")
            try:
                os.remove(filename2)
            except:
                print("ERROR WHILE DELETING")
        else:
            bot.send_message(message.chat.id, "❗️ Invalid URL")
    else:
        hehe = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "❗️ Invalid option", reply_markup=hehe)




# /SCRAPE COMMAND
@bot.message_handler(commands=['scrape'])
def geturl(message):
    global rescrape
    rescrape = bot.send_message(message.chat.id, "Send the URL of the website to scrape (Including http:// or https://)")
    bot.register_next_step_handler(rescrape, createfile)
def createfile(message):
    url = message.text
    if url.startswith('http://') or url.startswith('https://'):
        source_code = sourcecode(url)
        if source_code == 'err':
            bot.send_message(message.chat.id, "❗️ The given URL does not respond")
        elif source_code == 'timeout':
            bot.send_message(message.chat.id, '❗️ Timeout occured! Site responding too slow!')
        else:
            end = randomNumber()
            filename = f'scraped-{end}.txt'
            try:
                with open(filename, 'w+', encoding="utf-8") as f:
                    f.writelines(source_code)
                file = open(filename, 'rb')
                bot.delete_message(chat_id=rescrape.chat.id, message_id = rescrape.message_id)
                bot.send_document(message.chat.id, file)
                file.close()
            except Exception as e7:
                # PHASE 2 (EXCEPTION)
                print(f"\n\n{e7.with_traceback}\n\n")
                bot.delete_message(chat_id=rescrape.chat.id, message_id=rescrape.message_id)
                bot.send_message(message.chat.id, "❗️ Some error occured!")
            try:
                # PHASE 3
                os.remove(filename)
            except FileNotFoundError as fnf:
                # PHASE 3 (EXCEPTION)
                print(f"\n{fnf}\n")
    else:
        bot.edit_message_text(chat_id=rescrape.chat.id, message_id=rescrape.message_id, text= "❗️ Invalid URL detected")




# AI CHAT HANDLER (AI IS USED HERE)
@bot.message_handler(commands=['msg'])
def aiChatHandlerFunction(message):
    query = message.text.replace('/msg', '')
    if len(query) == 0:
        bot.send_message(message.chat.id, "Sent in '`/msg query`' format\nExample :\n\n`/msg How to make a pizza?`", parse_mode='Markdown')
    else:
        query = query.strip()
        ai_response = askAI(query)
        if ai_response == None:
            bot.send_message(message.chat.id, "❗️ Some error occured")
        else:
            bot.send_message(message.chat.id, ai_response)









bot.infinity_polling()






