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

        print(inputCom)
        print(inputArgs)

        # Check if they want to exit.
        if inputCom == "exit":
            exit()

        # Fork process and attempt to run commmand.
        forkProcess(inputCom, inputArgs)


# Returns the user commmand from input.
def tokenizeCommand(input):
    # Splits the string at the dollar sign.
    input = input.split("$")[0]
    # Removes new line from string.
    input = input[:-1]
    # Splits the string at every spaces and just keeps the command.
    input = input.split()[0]
    return input

# Returns the list of arguments from the input.
def tokenizeArgs(input):
    input = input.split()
    input = input[1:]
    if input == []:
        input = [' ']
    return input

# Forks and attempts to run process given a command and arguments.
def forkProcess(inputCom, inputArgs):
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
            program = "%s/%s" % (dir, inputCom)
            # os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
            try:
                 os.execve(program, inputArgs, os.environ)
            # Expected as we are going through the whole PATH.
            except FileNotFoundError:
                pass
        # Finally, if we reach the end of the PATH and cannot find the command, tell the user, exit fork with error.
        os.write(2, (inputCom + ": Command not found.\n").encode())
        sys.exit(1)  # terminate with error
    else: # parent
        # os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
        #          (pid, rc)).encode())
        childPidCode = os.wait()
        # os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
        #          childPidCode).encode())
            

if __name__ == '__main__':
    main()