import serial

# import time 
# arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1) 

# def write_read(x): 
# 	arduino.write(bytes(x, 'utf-8')) 
# 	time.sleep(0.05) 
# 	data = arduino.readline() 
# 	return data 

# while True: 
# 	num = input("Enter a number: ") # Taking input from user 
# 	value = write_read(num) 
# 	print(value) # printing the value 

def readserial(comport, baudrate):

    ser = serial.Serial(comport, baudrate, timeout=0.1)         # 1/timeout is the frequency at which the port is read

    while True:
        data = ser.readline().decode().strip()
        if data:
            print(data)


if __name__ == '__main__':

    readserial('COM3', 9600)