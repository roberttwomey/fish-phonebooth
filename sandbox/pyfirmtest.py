import pyfirmata
import time

board = pyfirmata.Arduino('/dev/cu.usbmodem143301')

it = pyfirmata.util.Iterator(board)
it.start()

board.digital[6].mode = pyfirmata.INPUT

while True:
    sw = board.digital[6].read()
    print(sw)
    # if sw == 1:
    #     board.digital[10].write(1)
    # else:
    #     board.digital[10].write(0)
    time.sleep(1)