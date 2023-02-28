import json, time, requests, random, openai
import openai, os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
AI_API_KEY = os.getenv('AI_API_KEY')


def askAI(text):
    openai.api_key = AI_API_KEY
    try:
        response = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = text,
        temperature = 0.6,
        max_tokens = 150)
        return response.choices[0].text
    except Exception as e:
        data = f'QUERY : {text}\n{e}\nTRACEBACK\n\n{e.with_traceback}\n\n---------------------\n\n'
        with open('msgErrorLog.txt', 'a', encoding='utf-8') as f:
            f.write(data)
            print("ERROR HAS BEEN LOGGED")
def resetFile():
    with open('users.json', 'r') as file:
        json_data = json.load(file)
        for i in json_data:
            i['images_generated'] = 0
    with open('users.json', 'w') as file:
        json.dump(json_data, file, indent=4)
        return "200"
    

    
def isValid(link):
    if link.startswith('https://youtu.be/') or link.startswith('https://youtube.com/watch') or link.startswith('https://www.youtube.com/watch') or link.startswith('https://m.youtube.com/watch') or link.startswith('https://youtube.com/shorts' or link.startswith('https://www.youtube.com/shorts') or link.startswith('https://m.youtube.com/shorts')):
        return True
    else:
        return False
    



def sourcecode(url):
    try:
        start = time.time()
        r = requests.get(url)
        end = time.time()
        time_taken = round(end) - round(start)
        if time_taken > 4:
            return 'timeout'
        else :
            return r.text
    except requests.exceptions.ConnectionError:
        return 'err'
    



def randomNumber():
    num = random.randint(1000, 9999)
    return num
def isSubscriber(userID):
    with open('subscribers.json', 'r') as filetoread:
        json_data = json.load(filetoread)
        status = 0
        for i in json_data:
            if i['id'] == str(userID):
                status = 1 # TRUE = 1 AND FALSE = 0
            else:
                status = 0
        return status
    





        



