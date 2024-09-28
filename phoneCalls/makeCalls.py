# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
import random
import json
import datetime
import time
from os import path
# Download the helper library from https://www.twilio.com/docs/python/install
from dotenv import load_dotenv

# load variables from .env file: 
load_dotenv()

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilPhone = os.getenv('TWILIO_PHONE')
client = Client(account_sid, auth_token)

# where phone nums are stored
filename = 'numbers.json'


# filename = 'numbers.json'
# with open(filename) as fp:
#     users = json.load(fp)

# def fishPhoneCall(thisUser, hour, minute, second):
#     # pygame.init()

#     # creating display
#     # display = pygame.display.set_mode((300, 300))

#     print("waiting until", hour, ":", minute, ":", second, "to call\n")
    
#     while True:

#         currTime = datetime.datetime.now()

#         with open(filename) as fp:
#             users = json.load(fp)

#         # for event in pygame.event.get():
#         #     if event.type == pygame.KEYDOWN:
#         #         if event.key == pygame.K_NUMLOCK:    
#         #                 number = 'END'
#         #                 return number
#         #         elif event.key == pygame.K_BACKQUOTE:    
#         #                 number = 'END'
#         #                 return number

#         # Waits until the designated time to make the call
#         if currTime.hour == hour and currTime.minute == minute and currTime.second == second:

#             #get the phone number of specified user
#             phoneNum = users[thisUser]['phoneNum']

#             # list of fish tracks
#             fish_audio = [
#             'mixdown-2track.mp3',
#             'newplaytest3.mp3',
#             'fish01.mp3',
#             'fish02.mp3',
#             'foghorn.mp3',
#             'whoop.mp3'
#             ]
            

#             # Pick and locate a random track
#             this_audio = fish_audio[random.randint(0, len(fish_audio)-1)]
#             audio_url = 'https://roberttwomey.com/downloads/' + this_audio
#             #print(audio_url)

#             try:
#                 # Replace 'phone_number' with the number you want to validate
#                 number_validation = client.lookups \
#                                         .phone_numbers(phoneNum) \
#                                         .fetch(type=['carrier'])

#                 # If the number is valid, 'carrier' information will be available
#                 if number_validation.carrier:
#                     print("The number is valid and the carrier is:", number_validation.carrier['name'])
#                     call = client.calls.create(
#                                         url=audio_url,
#                                         to=phoneNum,
#                                         from_=twilPhone
#                                     )
#                     printTime = currTime.strftime("%c")
#                     print("Called user", thisUser, "with", this_audio,"at", phoneNum, "on", printTime, "\n")
#                 else:
#                     print("The number is not valid.")
#                     return 'INVALID'
#             except Exception as e:
#                 print("An error occurred:", e)
#                 print("calling random number instead")
#                 randomFishCall()
#                 # print("calling Reid Instead")
#                 # call = client.calls.create(
#                 #                         url=audio_url,
#                 #                         to='+13088800470',
#                 #                         from_=twilPhone
#                 #                     )
#             return 'CALLED'  
        

def updateFishPhoneCall(thisUser, hour, minute, second):
    # non-blocking fish phone call function
    currTime = datetime.datetime.now()

    # Waits until the designated time to make the call
    if currTime.hour == hour and currTime.minute == minute and currTime.second == second:
        # TOOD: THIS SHOULD BE >= AS OPPOSED TO ==
        with open(filename) as fp:
            users = json.load(fp)
        
        thisUser = random.randint(0, len(users)-1)

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

        try:
            # Replace 'phone_number' with the number you want to validate
            number_validation = client.lookups \
                                    .phone_numbers(phoneNum) \
                                    .fetch(type=['carrier'])

            # If the number is valid, 'carrier' information will be available
            if number_validation.carrier:
                print("The number is valid and the carrier is:", number_validation.carrier['name'])
                call = client.calls.create(
                                    url=audio_url,
                                    to=phoneNum,
                                    from_=twilPhone
                                )
                printTime = currTime.strftime("%c")
                print("Called user", thisUser, "with", this_audio,"at", phoneNum, "on", printTime, "\n")

            else:
                print("The number is not valid.")
                return 'INVALID'
        except Exception as e:
            print("An error occurred:", e)
            print("calling random number instead")
            randomFishCall()              
        return 'CALLED' 
    else:
        return 'WAITING'
    

def randomFishCall():

    #print("waiting until", hour, ":", minute, "to call\n")
    
    # while True:

        #currTime = datetime.datetime.now()

    with open(filename) as fp:
        users = json.load(fp)
    
    thisUser = random.randint(0, len(users)-1)
    #thisUser = 0

    # Waits until the designated time to make the call
    # if currTime.hour == hour and currTime.minute == minute:

        #get the phone number of specified user
    phoneNum = users[thisUser]['phoneNum']
    #phoneNum = "+10000000000"

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

    try:
        # Replace 'phone_number' with the number you want to validate
        number_validation = client.lookups \
                                .phone_numbers(phoneNum) \
                                .fetch(type=['carrier'])

        # If the number is valid, 'carrier' information will be available
        if number_validation.carrier:
            print("The number is valid and the carrier is:", number_validation.carrier['name'])
            call = client.calls.create(
                                url=audio_url,
                                to=phoneNum,
                                from_=twilPhone
                            )
            printTime = currTime.strftime("%c")
            print("Called user", thisUser, "with", this_audio,"at", phoneNum, "on", printTime, "\n")
        else:
            print("The number is not valid.")
            return 'INVALID'
    except Exception as e:
        print("An error occurred:", e)
        print("calling skipped")
        #randomFishCall()

    return "CALLED"


# print("Number of stored users:", len(users), "\n")
# currTime = datetime.datetime.now()
# print("The current time is", currTime.hour, ":", currTime.minute, "\n")

# userNum = int(input("Enter the user you would like to call: \n"))

#hour = int(input("Enter the hour you would like to call: \n"))
#minute = int(input("Enter the minute you would like to call: \n"))
# fishPhoneCall(userNum, hour, minute)

# multiple calls at certain times (make sure to be in time order.)

#randomFishCall()

#fishPhoneCall(1, currTime.hour, currTime.minute, '59')
# fishPhoneCall(random.rand, 11, 9)
# fishPhoneCall(0, 11, 10)
# fishPhoneCall(0, 11, 11)
