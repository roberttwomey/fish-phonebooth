# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
import random
import json
import datetime
import time
from os import path

filename = 'numbers.json'
with open(filename) as fp:
    users = json.load(fp)

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = ''
auth_token = ''
client = Client(account_sid, auth_token)
twilPhone = ''





def fishPhoneCall(thisUser, hour, minute):

    print("waiting until", hour, ":", minute, "to call\n")
    
    while True:

        currTime = datetime.datetime.now()

        # Waits until the designated time to make the call
        if currTime.hour == hour and currTime.minute == minute:

            #get the phone number of specified user
            phoneNum = users[thisUser]['phoneNum']

            # list of fish tracks
            fish_audio = [
            'mixdown-2track.mp3',
            'newplaytest3.mp3',
            'fish01.mp3',
            'fish02.mp3',
            'foghorn.mp3',
            'whoop.mp3'
            ]
            

            # Pick and locate a random track
            this_audio = fish_audio[random.randint(0, len(fish_audio)-1)]
            audio_url = 'https://roberttwomey.com/downloads/' + this_audio
            #print(audio_url)

            call = client.calls.create(
                                    url=audio_url,
                                    to=phoneNum,
                                    from_=twilPhone
                                )

            printTime = currTime.strftime("%c")
            print("Called user", thisUser, "with", this_audio,"at", phoneNum, "on", printTime, "\n")
            return


print("Number of stored users:", len(users), "\n")
currTime = datetime.datetime.now()
print("The current time is", currTime.hour, ":", currTime.minute, "\n")

# userNum = int(input("Enter the user you would like to call: \n"))

#hour = int(input("Enter the hour you would like to call: \n"))
#minute = int(input("Enter the minute you would like to call: \n"))
# fishPhoneCall(userNum, hour, minute)

# multiple calls at certain times (make sure to be in time order.)
fishPhoneCall(0, 18, 7)
fishPhoneCall(0, 18, 8)
fishPhoneCall(0, 18, 9)
fishPhoneCall(0, 18, 10)
fishPhoneCall(0, 18, 11)
