import asyncio
import datetime
import os
from datetime import date
import discord
import emojis
import requests
from bs4 import BeautifulSoup
from google.cloud import vision
import random
import json
import io
import base64




intents = discord.Intents.all()
client = discord.Client(intents=intents)
threadRunning = False
url = os.getenv("URL")
dungeonList = ["dos","mots","hoa","pf","sd","soa","nw","top"]
fileTypes = [".jpeg", ".png", ".jpg"]
negativeLabels = ["dog","cat","bird"]

file = open("./Shared/quotes.txt","r")
quotes = []
for line in file:
    quotes.append(line)

def webToSoup(webpage):
    result = requests.get(webpage)
    assert(result.status_code == 200)
    src = result.content
    soup = BeautifulSoup(src, 'html5lib')
    return soup

wagos = {}
def updateLinks():
    soup = webToSoup(url)
    count = 0
    for iframe in soup.find_all("iframe")[:8]:
        src = iframe.get("src")
        wago = src.split("/e")[0]
        wagos[dungeonList[count]] = wago
        count += 1

def quote():
    number = random.randint(0,len(quotes)-1)
    return quotes[number]

async def detect_labels_uri(uri):
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.label_detection(image=image)
    labels = response.label_annotations
    labelList = [d.description.lower() for d in labels]
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return labelList

currencies = [":dollar:", ":euro:", ":money_with_wings:", ":yen:",":pound:"]
async def countCurrency(*dates):
    chan = await client.fetch_channel(os.getenv("CHANNEL1"))
    if dates:
        messages = await chan.history(limit=500, before=dates[0], after=dates[1]).flatten()
    elif not dates:
        messages = await chan.history(limit=500).flatten()
    authors = []
    pairs = {}
    for msg in messages: 
        decoded = emojis.decode(msg.content)
        for currency in currencies:  
            if(currency in decoded):
                currCount =  decoded.count(currency) 
                author = msg.author.name
                if(author not in authors):
                    authors.append(author)
                    pairs[author] = currCount
                else:
                    pairs[author] = int(pairs.get(author)) +currCount
    sortedPairs = {}
    sortedKeys = sorted(pairs, key=pairs.get, reverse=True)
    for key in sortedKeys:
        sortedPairs[key] = pairs[key]
    return sortedPairs

async def gotmCurrent():
    currentDate = datetime.datetime.now()
    startDate = datetime.datetime(currentDate.year,currentDate.month,1)
    count = await countCurrency(currentDate,startDate)
    gotm = next(iter(count.keys()))
    pairsString = str(count).replace(",", "\n").replace("{","").replace("}","").replace("'","")     
    msg = ("Currently **"+ str(gotm) + "** is Gamer of The Month!\n" + "Here's the leaderboard: \n"+ pairsString)
    return msg

monthlyFlag = False
async def monthlyGotmCheck():
    global monthlyFlag
    currentDate = datetime.datetime.now()
    if(currentDate.day == 1):
        if(monthlyFlag is False):
            monthlyFlag = True
            chan = await client.fetch_channel(os.getenv("CHANNEL1"))
            endDate = datetime.datetime(currentDate.year,currentDate.month,currentDate.day)
            startDate = datetime.datetime(currentDate.year,currentDate.month-1 ,1)
            count = await countCurrency(endDate,startDate)
            try:
                gotm = next(iter(count.keys()))
            except:
                await chan.send("No users founds")
            
                return
            pairsString = str(count).replace(",", "\n").replace("{","").replace("}","").replace("'","")     
            msg = ("Congrats **"+ str(gotm) + "**, you are Gamer of The Month!\n" + "Here's the leaderboard: \n"+ pairsString)
            await chan.send(msg)
    else:
        monthlyFlag = False

fridayFlag = False
async def fridayCheck():
    global fridayFlag
    chan = await client.fetch_channel(os.getenv("MAINCHANNEL"))
    currentDay = date.today().weekday()
    if(currentDay == 4):
        if fridayFlag is False:
            fridayFlag = True
            await chan.send("Check out Daft Punk's new single \"Get Lucky\" if you get the chance. Sound of the summer.")
    else:
        fridayFlag = False   

async def gotmThread():
    while True:
        print("Checking...")
        await fridayCheck()
        await monthlyGotmCheck()
        await asyncio.sleep(12*3600)


async def generateImage(prompt):
    print(prompt)
    payload = {
    "prompt": prompt,
    "steps": 20,
    "sampler_index":'DDIM'
    }
    try:
        response = requests.post(url=f'http://{os.getenv("SDServer_API")}/sdapi/v1/txt2img', json=payload)
        if response.status_code == 200:
            for i in response.json()['images']:
                return '',io.BytesIO(base64.b64decode(i.split(",",1)[0]))
        else:
            return response.json()['detail'][0].get('msg'),None
    except requests.exceptions.RequestException as e:
        print(e)
        return None,None
    

@client.event
async def on_ready():   
    updateLinks()
    asyncio.get_event_loop().create_task(gotmThread()) if threadRunning == False else print("Thread Already Running")
    print('Bot logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.attachments:
        for i in message.attachments:
            for type in fileTypes:
                if(i.filename.endswith(type)):
                    foundLabel = []
                    labels = await detect_labels_uri(i.url)
                    print(labels)   
                    for l in negativeLabels:
                        if l in labels:
                            foundLabel.append(l)
                    if len(foundLabel) == 1:
                            await message.reply("Haha, what a funny " +foundLabel[0] + " :rofl:")
                    elif len(foundLabel) > 1:
                            await message.reply("Wow, this " + " and ".join(foundLabel) + " are really funny! :smiling_face_with_3_hearts: ")
 
    if message.content.startswith('%'):
        msg = message.content.split("%")[1].lower()
        if(msg == "update"):
            updateLinks()
            
            await message.channel.send("Updated routes")
        elif(msg in wagos):
            await message.channel.send(wagos[msg])
        elif(msg == "yep"):
            await message.channel.send("COCK")
        elif (msg == "count"):
            count = await countCurrency()
            pairsString = str(count).replace(",", "\n").replace("{","").replace("}","").replace("'","")     
            await message.channel.send(pairsString)
        elif (msg == "gotm"):
            count = await gotmCurrent()
            await message.channel.send(count)
        elif (msg == "wake"):
            await message.channel.send(str(os.getenv("LIMMY")))
        elif (msg == "quote"):
            await message.channel.send(quote())
        elif ("gen" in msg):
            prompt = msg.split("gen")[1]
            await message.channel.send("Processing your prompt...")
            response = await generateImage(prompt)
            if response[1]:
                await message.channel.send(file=discord.File(response[1],filename='output.png'))
            elif response[0]:
                await message.channel.send(response[0])
            else:
                await message.channel.send("SD server not online")
        else:
            await message.channel.send("Command not found")


client.run(os.getenv("TEST_TOKEN"))




