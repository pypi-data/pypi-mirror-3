def fileReader(filePath):
    try:
        openedFile = open(filePath)
        delimiterChar = ':'
        for eachLine in openedFile:
            try:
               (role, script) = eachLine.split(delimiterChar)
	       print '%s said: %s' %(role, script)
            except ValueError:
               pass
        openedFile.close()
    except IOError:
        print 'The file doesn\'t exist'
