from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
import urllib.parse
import discord
import os
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
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")
        wago = src.split("/e")[0]
        wagos[dungeonList[count]] = wago
        count += 1
      

@client.event
async def on_ready():
    updateLinks()
    print('We have logged in as {0.user}'.format(client))

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
        else:
           await message.channel.send("Command not found") 

client.run(os.getenv("TOKEN"))


