#Data
Folder = ""
ScriptFile = Folder + "AI_Script.ais"
OutputDataFile = Folder + "AI Script Output.txt"
OutputDataFile2 = Folder + "AI Script Output Offsets.txt"
ErrorFile = Folder + "AI Build Errors.txt"
Commands = Folder + "commands.aisp"

def AI_Compiler():
    output = open(ErrorFile, 'w')
    actualoutput = open(OutputDataFile, 'w')
    offsetsoutput = open(OutputDataFile2, 'w')
    with open (ScriptFile, 'r') as script:
        linenum = 0
        offset = 0x0
        defines = []
        dynamicoffsets = {}
        bytelist = []
        broken = False
        commandlist = CommandListMaker(output)
        if commandlist[1] == False:
            print('Compilation Cancelled.')
            return
        commandlist = commandlist[0]
        ClassicScriptError = 'Error in script file: "' + ScriptFile + '" on line ' + str(linenum) + '.\n'
        for line in script:
            linenum += 1
            errortitle = 'Error in script file: "' + ScriptFile + '" on line ' + str(linenum) + ': '
            currentcommand = ''
            
#Check For Comment Line
            if line[:2] == '//' or line == '\n':
                pass
        
#Check if #dynamic line
            elif '#dynamic' in line:
                try:
                    try:
                        offset = int(line.rstrip().split('#dynamic ')[1])
                        if offset >= 0x1000000:
                            offset - 0x1000000 + 0x9000000
                        else:
                            offset += 0x8000000
                    except ValueError:
                        try:
                            offset = int(line.rstrip().split('#dynamic ')[1], 16)
                            if offset >= 0x1000000:
                                offset - 0x1000000 + 0x9000000
                            else:
                                offset += 0x8000000
                        except ValueError:
                            error = errortitle + line.rstrip().split('#dynamic ')[1] + '" is not a valid integer.\n'
                            print(error)
                            output.write(error)
                            broken = True
                except:
                    print(ClassicScriptError)
                    output.write(ClassicScriptError)
                                     
#Check if #include line
            elif '#include' in line:
                try:
                    definepath = line.rstrip().split('#include ')[1]
                    defines.append(DefinesDictMaker(Folder + definepath, output))
                except:
                    print(ClassicScriptError)
                    output.write(ClassicScriptError)
                    
#Check if #org line
            elif '#ORG' in allUppercase(line):
                try:
                    linelist = []
                    orgcombos = ['#org ', '#Org ', '#oRg ', '#orG ', '#ORg ', '#oRG ', '#OrG ', '#ORG ']
                    for a in orgcombos:
                        linelist = line.rstrip().split(a)
                        if len(linelist) > 1:
                            key = linelist[1]
                    try:
                        int(key)
                        error = errortitle + 'This compiler is not currently capable of compiling to specific offsets. Please change this to a @dynamic offset.\n'
                        print(error)
                        output.write(error)
                        broken = True
                    except ValueError:
                        try:
                            int(key, 16)
                            error = errortitle + 'This compiler is not currently capable of compiling to specific offsets. Please change this to a @dynamic offset.\n'
                            print(error)
                            output.write(error)
                            broken = True
                        except ValueError:
                            if key[0] != '@':
                                error =  errortitle + 'Dynamic offsets must start with the "@" symbol.\n'
                                print(error)
                                output.write(error)
                                broken = True
                            else:
                                if key in dynamicoffsets:
                                    error = errortitle + 'Warning! "' + key + '" is defined more than once.\n'
                                    print(error)
                                    output.write(error)
                                    broken = True
                                dynamicoffsets[key] = offset
                except:
                    print(ClassicScriptError)
                    output.write(ClassicScriptError)

#check if blank line
            elif line == '\n' or line == '':
                pass
            
#convert commands
            else:
                linelist = line.rstrip().split(' ')
                for command in commandlist:
                    if command.name == allUppercase(linelist[0]):
                        currentcommand = command
                        break
                if currentcommand == '':
                    error =  errortitle + 'Error with command "' + linelist[0] + '".\n'
                    print(error)
                    output.write(error)
                    broken = True
                else:
                #increase offset
                    offset += 1
                    for a in currentcommand.arglengths:
                        offset += a
                        
                    bytelist.append(dec2hex(currentcommand.num))
                
                    if currentcommand.argnum != 0:
                        try:
                            for a in range(1, currentcommand.argnum+1):
                                num = ''
                                value = linelist[a]
                                if value[0] == '@':
                                    bytelist.append(value)
                                else:
                                    try:
                                        num = int(value)

                                    except ValueError:
                                        try:
                                            num = int(value, 16)

                                        except ValueError:
                                                for dicty in defines:
                                                    if allUppercase(value) in dicty:
                                                        num = dicty[allUppercase(value)]
                                                if type(num) == str:
                                                    error = errortitle + 'Error with define "' + value + '".\n'
                                                    print(error)
                                                    output.write(error)
                                                    broken = True
                                                    num = 0

                                    if num > 2**(8*currentcommand.arglengths[a-1]):
                                        error = errortitle + 'Error with argument "' + str(num) + '". Value is too large.\n'
                                        print(error)
                                        output.write(error)
                                        broken = True
                                        num == 0

                                    bytelist.append(dec2hex_alt(num, currentcommand.arglengths[a-1]))
                        except IndexError:
                            error = errortitle + 'Incorrect number of arguments.\n'
                            print(error)
                            output.write(error)
                            broken = True
                            
#Fix Up the Data  
        newbytelist = []
        for a in bytelist:
            if a[0] != '@':
                newbytelist.append(reversebytes(a))
            else:
                try:
                    num = dec2hex_alt(dynamicoffsets[a], 4)
                except:
                    error = 'Error in script file: "' + ScriptFile + '": Dynamic offset "' + a + '" does not point to anything.\n'
                    print(error)
                    output.write(error)
                    num = '00000000'
                    broken = True
                newbytelist.append(reversebytes(num))
                        
#Write the data
        if broken == False:
            for a in newbytelist:
                actualoutput.write(a)

            for a in dynamicoffsets:
                offsetsoutput.write(a + ': ' + hex(dynamicoffsets[a]) + '\n')

    output.close()
    actualoutput.close()
    offsetsoutput.close()
    print ('Compilation Complete!')

def DefinesDictMaker(path, errorfile):
    try:
        output = errorfile
        with open(path, 'r') as file:
            OutputDict = {}
            linenum = 0
            for line in file:
                linenum += 1
                errortitle = 'Error in defines file: "' + path + '" on line ' + str(linenum) + ': '
                if line.rstrip() != '':
                    try:
                        key = line.strip().split(' ')[0]
                        if key[0:3] == 'ï»¿':
                            key = key.split('﻿ï»¿')[1]
                        if checkLetters(key) == False:
                            error = errortitle + '"' + key + '" begins with non-alphabetical characters.\n'
                            print(error)
                            output.write(error)
                        else:
                            try:
                                value = line.rstrip().split(' ')[1]
                                if key in OutputDict:
                                    error = errortitle + 'Warning! "' + key + '" is defined more than once.\n'
                                    print(error)
                                    output.write(error)
                                OutputDict[allUppercase(key)] = int((value))
                            except IndexError:
                                error = errortitle + 'No value detected.\n'
                                print(error)
                                output.write(error)
                            except ValueError:
                                OutputDict[allUppercase(key)] = int((value), 16)
                    except ValueError:
                        if value == '':
                            error = errortitle + 'There are extra spaces.\n'
                            print(error)
                            output.write(error)
                        else:
                            error = errortitle + '"' + value + '"is not a valid integer.\n'
                            print(error)
                            output.write(error)
                    except:
                        error = 'Error in defines file: "' + path + '" on line ' + str(linenum) + '.\n'
                        print(error)
                        output.write(error)
        return OutputDict
    except FileNotFoundError:
        error = 'Defines Loading Error: No file named "' + path + '" was found.\n'
        print(error)
        output.write(error)
        return {}
    
def CommandListMaker(errorfile):
    commandlist = []
    output = errorfile
    with open(Commands, 'r') as file:
        linenum = 0
        SkipAdd = False
        for line in file:
            linenum += 1
            errortitle = 'Error in commands file: "' + Commands + '" on line ' + str(linenum) + ': '
            if line != '\n':
                linelist = (line.rstrip()).split(' ')
                commandnum, argnum, arglengths, argnames = 0, 0, [], []
                for a in range(len(linelist)):
                    if a >= 3:
                        if a % 2 == 0:
                            try:
                                arglengths.append(int(linelist[a]))
                            except ValueError:
                                try:
                                    arglengths.append(int(linelist[a], 16))
                                except ValueError:
                                    error = errortitle + 'There was a problem with parsing the argument lengths. Make sure the only space characters are between arguments, and not within argument names.\n'
                                    print(error)
                                    output.write(error)
                                    SkipAdd = True
                        else:
                            try:
                                int(linelist[a])
                                error = errortitle + 'There was a problem with parsing the argument names. Make sure the only space characters are between arguments, and not within argument names.\n'
                                print(error)
                                output.write(error)
                                SkipAdd = True
                            except ValueError:
                                try:
                                    int(linelist[a], 16)
                                    error = errortitle + 'There was a problem with parsing the argument names. Make sure the only space characters are between arguments, and not within argument names.\n'
                                    print(error)
                                    output.write(error)
                                    SkipAdd = True
                                except ValueError:
                                    argnames.append(linelist[a])
                                    
                if checkLetters(linelist[0]) == False:
                    error = errortitle + '"' + linelist[0] + '" begins with non-alphabetical characters.\n'
                    print(error)
                    output.write(error)
                    SkipAdd = True
                    
                try:
                    commandnum = int(linelist[1])
                except ValueError:
                    try:
                        commandnum = int(linelist[1], 16)
                    except ValueError:
                        error = errortitle + '"' + linelist[1] + '" is not a valid command number.\n'
                        print(error)
                        output.write(error)
                        SkipAdd = True
                        
                try:
                    argnum = int(linelist[2])
                except ValueError:
                    try:
                        argnum = int(linelist[2], 16)
                    except ValueError:
                        error = errortitle + '"' + linelist[2] + '" is not a valid number for argument amount.\n'
                        print(error)
                        output.write(error)
                        SkipAdd = True
                except IndexError:
                    pass
                
                if SkipAdd == False:
                    try:
                        commandlist.append(AICommands(allUppercase(linelist[0]), commandnum, argnum, arglengths, argnames))
                    except IndexError:
                        commandlist.append(AICommands(allUppercase(linelist[0]), commandnum, 0, [], []))
                        
    if SkipAdd == False:    
        return [commandlist, True]
    else:
        return [[], False]

lowercaseletters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'] 
uppercaseletters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
def checkLetters(string):
    for a in string:
        if a not in lowercaseletters and a not in uppercaseletters:
            return False
        return True
    
def allUppercase(string):
    ns = ''
    for a in string:
        if a in uppercaseletters:
            ns += a
        else:
            try:
                ns += uppercaseletters[lowercaseletters.index(a)]
            except ValueError:
                ns += a
    return ns

class AICommands:
    def __init__(self, name, num, argnum, arglengths, argnames):
        self.name = name
        self.num = num
        self.argnum = argnum
        self.arglengths = arglengths
        self.argnames = argnames
        
DecHexDict = {10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F'}
def dec2hex(num):
    b = ''
    if num == 0:
        b = '00'
    else:
        while num > 0:
            remainder = num % 16
            if remainder in DecHexDict:
                remainder = DecHexDict[remainder]
            num //= 16
            b = str(remainder) + b
    if len(b) == 1:
        b = '0' + b
    return b

def dec2hex_alt(num, length):
    b = ''
    if num == 0:
        b = '00'
    else:
        while num > 0:
            remainder = num % 16
            if remainder in DecHexDict:
                remainder = DecHexDict[remainder]
            num //= 16
            b = str(remainder) + b
    while len(b) < length*2:
        b = '0' + b
    return b

def reversebytes(string):
    ns = ''
    inter = ''
    counter = 0
    for a in string:
        if counter == 1:
            inter += a
            ns = inter + ns
            inter = ''
            counter = 0
        else:
            inter += a
            counter += 1
    return ns

AI_Compiler()