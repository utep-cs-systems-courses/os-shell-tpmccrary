import os, sys, re
from my_read import myReadLine

#  fd #0 is "standard input" (by default, attached to kbd)
#  fd #1 is "standard ouput" (by default, attached to display)
#  fd #2 is "standard error" (by default, attached to display for error output)

def main():
    while True:
        # Prints a prompt.
        os.write(1, ("tpmccrary-shell@os-shell:$ ").encode())

        # Wait for user to input here.
        rawInput = myReadLine()
        inputCom = tokenizeCommand(rawInput)
        inputArgs = tokenizeArgs(rawInput)

        print(inputArgs)

        # Check if they want to exit.
        if inputCom == "exit":
            exit()

        # Fork process and attempt to run commmand.
        forkProcess(inputCom, inputArgs)


# Returns the user commmand from input.
def tokenizeCommand(input):
    if input == "\n":
        return "\n"
    # Splits the string at the dollar sign.
    # input = input.split("$")[0]
    # Removes new line from string.
    # input = input[:-1]
    # Splits the string at every spaces and just keeps the command.
    input = input.split()[0]
    return input

# Returns the list of arguments from the input.
def tokenizeArgs(input):
    inputArgs = []
    arg = ''
    inQuote = False

    i = 0
    while(i < len(input)):

        # If we find our first quote, flag that we are in a quote, and move on to the next character.
        if input[i] == '"' and inQuote == False:
            inQuote = True
            i += 1
        # If we reach a second quote, flag that we are out of the quote, and move on to the next character.
        elif input[i] == '"' and inQuote == True:
            inQuote = False
            i += 1

        # If the character is not a space, or if we are in a 
        # quote (therefore we do not care about spaces), add the character to the argument.
        if (input[i] != ' ' and input[i] != '\n') or inQuote == True:
            arg += input[i]
        # If the character is a space, we are not in a quote, and the argument is not empty, 
        # add the argument to the list of arguments.
        elif (input[i] == ' ' or input[i] == '\n') and inQuote == False and arg != '':
            inputArgs.append(arg)
            arg = ''

        i += 1

    return inputArgs

    # OLD: Keeping for now.
    input = input.split()
    input[0] = ' ' 
    # Check for no commands.
    if input == []:
        input = [' ']
    return input

# Forks and attempts to run process given a command and arguments.
def forkProcess(inputCom, inputArgs):
    if inputArgs[0] == '':
        return

    pid = os.getpid()
    rc = os.fork()

    # Fork failed.
    if rc < 0:
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0: #child
        # Go through every directory in the PATH and try to find command.
        for dir in re.split(":", os.environ['PATH']):
            # Concatinate string where the path and the command.
            program = "%s/%s" % (dir, inputArgs[0])
            # os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
            try:
                 os.execve(program, inputArgs, os.environ)
            # Expected as we are going through the whole PATH.
            except FileNotFoundError:
                pass
        # Finally, if we reach the end of the PATH and cannot find the command, tell the user, exit fork with error.
        os.write(2, (inputArgs[0] + ": command not found\n").encode())
        sys.exit(1)  # terminate with error
    else: # parent
        # os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
        #          (pid, rc)).encode())
        childPidCode = os.wait()
        # os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
        #          childPidCode).encode())
            

if __name__ == '__main__':
    main()