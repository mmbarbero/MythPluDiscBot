import asyncio
import datetime
import os
import urllib.parse
from datetime import date

import discord
import emojis
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()

url = os.getenv("URL")
dungeonList = ["dos","mots","hoa","pf","sd","soa","nw","top"]

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


async def monthlyGotmCheck():
    currentDate = datetime.datetime.now()
    if(currentDate.day == 1):
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


async def fridayCheck():
    chan = await client.fetch_channel(os.getenv("CHANNEL1"))
    currentDay = date.today().weekday()
    if(currentDay == 4):
        await chan.send("Check out Daft Punk's new single \"Get Lucky\" if you get the chance. Sound of the summer.")
        




async def gotmThread():
    while True:
        print("Checking...")
        await fridayCheck()
        await monthlyGotmCheck()
        await asyncio.sleep(24*3600)


@client.event
async def on_ready():
    updateLinks()
    asyncio.get_event_loop().create_task(gotmThread())
    print('Bot logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
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
        else:
            await message.channel.send("Command not found")


client.run(os.getenv("TOKEN"))




