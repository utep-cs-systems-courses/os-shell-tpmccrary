from os import read, write

# Global buffer to remember what character we are on.
buff = None

# Gets the buffer.
def myGetChar():
    global buff

    buff = read(0, 100)

    return buff

# Reads a line.
def myReadLine():
    global buff

    # If buff is none, that means we havent read anything yet.
    if buff == None:
        buff = myGetChar()

    # print("buff is: " + str(buff))


    line = ""
    index = 0
    # While there are character in the buffer.
    while len(buff):
        # Fill a string with the characters.
        line += chr(buff[index])

        # If we find a new line character, change the buffer to start from there and return the line.
        if buff[index] == 10:
            buff = buff[index + 1:len(buff)]
            return line
        
        index += 1

        # If we reached the end of the buffer, with no new line character, get the next buffer.
        if index == len(buff):
            index = 0
            buff = read(0, 100)
            # print(buff)
    
    # Will reach here if the buffer is empty.
    return ""




