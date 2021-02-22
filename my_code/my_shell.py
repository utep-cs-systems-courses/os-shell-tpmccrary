import os, sys, re
from my_read import myReadLine
from my_shell_commands import changeDirectory

#  fd #0 is "standard input" (by default, attached to kbd)
#  fd #1 is "standard ouput" (by default, attached to display)
#  fd #2 is "standard error" (by default, attached to display for error output)

def main():
    # Check if PS1 exist, if it does, flag that is exists.
    ps1Exist = False
    if (os.environ.get("PS1") != None):
        ps1Exist = True

    while True:
        # If the PS1 exist in the environ, use it, else, set my own.
        if (ps1Exist):
            PS1 = os.environ.get("PS1")
        else:
            os.environ["PS1"] = str(os.environ.get("USER") + ":" + str(os.getcwd()) + "$ ")
            PS1 = os.environ.get("PS1")

        # Prints a prompt.
        os.write(1, PS1.encode())

        # Wait for user to input, and then tockenize that input.
        rawInput = myReadLine()
        inputArgs = tokenizeArgs(rawInput)

        # Check if they want to exit.
        # if inputArgs[0] == "exit":
        #     exit()
        # Check for shell command. Return false if it was not a shell command.
        usedShellCom = checkForShellCommand(inputArgs)

        if (usedShellCom == False):
            # Fork process and attempt to run commmand using the user input arguments.
            forkProcess(inputArgs)
        

# Given the user input, checks to see if it is a shell command.
def checkForShellCommand(inputArgs):

    if (inputArgs[0] == "exit"):
        exit()
    elif (inputArgs[0] == "cd"):
        changeDirectory(inputArgs)
        return True

    return False


# Returns the list of arguments from the user input.
def tokenizeArgs(input):
    # If user inputs nothing, return empty arguments.
    if input == '\n' or input == '':
        return ['']
    
    inputArgs = []
    arg = ''
    inQuote = False

    i = 0
    while(i < len(input)):
        # Here we go through every character in the user input to make up an argument.
        # A space is what decides the speration of arguments, however, if we are in a quote, spaces are part of the argument.

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
def forkProcess(inputArgs):
    # If there is no argument, no need to try and execute anything.
    if inputArgs[0] == '':
        return

    

    pid = os.getpid()
    rc = os.fork()
    redirect = False

    # Fork failed.
    if rc < 0:
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0: #child

        # Check for piping. If we do a pipe, split up the arguments between the pipes.
        if ('|' in inputArgs):
            tempArgs = inputArgs
            inputArgs = []
            splitArgs = []
            for arg in tempArgs:
                if (arg == '|'):
                    inputArgs.append(splitArgs)
                    splitArgs = []
                    continue
                splitArgs.append(arg)
            if (splitArgs != []):
                inputArgs.append(splitArgs)
            pipeProcess(inputArgs, 0)

        # Checks for guzinta (goes into).
        # TODO: Put this in its own function.
        if ('>' in inputArgs):
            tempInputArgs = inputArgs
            inputArgs = []
            i = 0
            while(i < len(tempInputArgs)):
                if (tempInputArgs[i] == '>'):
                    if (i + 1 < len(tempInputArgs)):
                        fileName = tempInputArgs[i + 1]
                        redirect = True
                    break
                inputArgs.append(tempInputArgs[i])
                i += 1
            if (redirect == True):
                os.close(1)
                os.open(fileName, os.O_CREAT | os.O_WRONLY)
                os.set_inheritable(1, True)

        # Checks for file input.
        # TODO: Put his in its own function.
        if ('<' in inputArgs):
            tempInputArgs = inputArgs
            inputArgs = []
            i = 0
            while(i < len(tempInputArgs)):
                if (tempInputArgs[i] == '<'):
                    if (i + 1 < len(tempInputArgs)):
                        fileName = tempInputArgs[i + 1]
                        redirect = True
                    break
                inputArgs.append(tempInputArgs[i])
                i += 1
            if (redirect == True):
                os.close(0)
                os.open(fileName, os.O_RDONLY)
                os.set_inheritable(1, True)
                rawInput = myReadLine()
                tokenInput = tokenizeArgs(rawInput)
                for arg in tokenInput:
                    inputArgs.append(arg)

        # Execute command with arguments.
        execCommand(inputArgs)  
    else: # parent
        # os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
        #          (pid, rc)).encode())
        childPidCode = os.wait()

# Recursive function that pipes given commands.
def pipeProcess(inputArgs, index):

    pid = os.getpid()  # get and remember pid

    # Start pipe, get read and write.
    pr,pw = os.pipe() 

    for f in (pr, pw):
        os.set_inheritable(f, True)
    # print("pipe fds: pr=%d, pw=%d" % (pr, pw))

    # print("About to fork (pid=%d)" % pid)

    rc = os.fork()

    if rc < 0:
        print("fork failed, returning %d\n" % rc, file=sys.stderr)
        sys.exit(1)

    elif rc == 0:                   #  child - will write to pipe
        # print("Child: My pid==%d.  Parent's pid=%d" % (os.getpid(), pid), file=sys.stderr)

        # Checks for guzinta (goes into).
        # TODO: Put this in its own function.
        if ('>' in inputArgs[index]):
            tempInputArgs = inputArgs[index]
            inputArgs[index] = []
            i = 0
            while(i < len(tempInputArgs)):
                if (tempInputArgs[i] == '>'):
                    if (i + 1 < len(tempInputArgs)):
                        fileName = tempInputArgs[i + 1]
                        redirect = True
                    break
                inputArgs[index].append(tempInputArgs[i])
                i += 1
            if (redirect == True):
                os.close(1)
                os.open(fileName, os.O_CREAT | os.O_WRONLY)
                os.set_inheritable(1, True)

        # Checks for file input.
        # TODO: Put his in its own function.
        if ('<' in inputArgs[index]):
            tempInputArgs = inputArgs[index]
            inputArgs[index] = []
            i = 0
            while(i < len(tempInputArgs)):
                if (tempInputArgs[i] == '<'):
                    if (i + 1 < len(tempInputArgs)):
                        fileName = tempInputArgs[i + 1]
                        redirect = True
                    break
                inputArgs[index].append(tempInputArgs[i])
                i += 1
            if (redirect == True):
                os.close(0)
                os.open(fileName, os.O_RDONLY)
                os.set_inheritable(1, True)
                rawInput = myReadLine()
                tokenInput = tokenizeArgs(rawInput)
                for arg in tokenInput:
                    inputArgs[index].append(arg)

        os.close(1) # redirect child's stdout. Close it.
        os.dup(pw) # redirect to pipe write.
        os.set_inheritable(1, True)
        for fd in (pr, pw): #Close initial read and write
            os.close(fd)
        execCommand(inputArgs[index])
                
    else:  # parent (forked ok)
        # print("Parent: My pid==%d.  Child's pid=%d" % (os.getpid(), rc), file=sys.stderr)
        os.close(0) # Close standard in.
        os.dup(pr) # Redirect to pipe read.
        os.set_inheritable(0, True)
        for fd in (pw, pr): #Close initial read and write.
            os.close(fd)
        # Checks if we are at end of arguments. If we are not, call pipe recursively to do the next arguments.
        if (index + 1 != len(inputArgs)):
            pipeProcess(inputArgs, index + 1)
            execCommand(inputArgs[index + 1])
        return
        
            
        
            

    

# Given arguments, tries to execute command from the PATH.
def execCommand(inputArgs):
    # Go through every directory in the PATH and try to find command.
    for dir in re.split(":", os.environ['PATH']):
        # Concatinate string with the path and the command.
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
        # os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
        #          childPidCode).encode())
            

if __name__ == '__main__':
    main()

