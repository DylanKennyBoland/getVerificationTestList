#!/usr/bin/python

# Author: Dylan Boland

# Modules that will be useful
import argparse
import os
import sys
import re

# ==== Some General-info Strings ====
# Tags - define these here so they can be quickly and easily changed
errorTag   = """\t***Error: """
successTag = """\t***Success: """
infoTag    = """\t***Info: """

# ==== Help, Information and Error Messages ====
descriptionMsg = """This script can be used to extract the names of all the tests or sequences that are run
as part of a regression. The results are normally located in a separate directories. These directories could have
the following form:
    run<seed_number> or sim<seed_number> or test<seed_number> etc.

At the moment, this script assumes that the results of all the tests that were run during the regression are stored in
sim_<seed_number> directories. It is also assumed that these sim_<seed_number> directories are located in a directory that
ends in:
    .../designs/<design_name>/results

The script accepts the absolute path to the directory where all the result directories (sim_<seed_number>) are. An example of calling
the script might be:

    "get_test_list.py --path /home/dylanKB/projects/multiplier/results"

A list of all the tests is written to an output text file which has the following form:

    "<design_name>_test_list.txt"
    
An idea: You can add an alias to your ~/.aliases file that will point to the script - e.g.:

    "alias get_test_list '<path_to_directory_with_script>/get_test_list.py'"

Then, you can simply call 'get_test_list --path <absolute_path_to_directory_with_sim_dirs>' from *anywhere* in your
Linux environment (assumming you have sourced your .aliases file)"""
helpMsg    = infoTag + """Please provide the absolute path to the directory where all the sim_<seed_number> directories are stored."""
noArgsMsg  = errorTag + """No input arguments were specified."""
noDesignNameIdentifiedMsg  = errorTag + """No design name could be identified in the following path: {}"""
changingDirMsg = """==== Changing directory to {} ====\n"""
noSimDirsFoundMsg = errorTag + """==== No sim_<seed_number> directories were found ====\n"""
simDirsFoundMsg = """==== {} sim_<seed_number> directories were found! ====\n"""
readErrorMsg = errorTag + """==== Error reading {} file in {} ====\n"""
noSeqNameFoundMsg  = errorTag + """No test sequence name could be identified in {} - Skipping this directory...\n"""
testSeqsFoundMsg = """====""" + successTag + """ {} test sequences were found in total! Number of unique tests: {} ====\n"""
outputFileHeaderMsg = """=================================================================================

            Total number of tests run: {}
            Total number of unique tests run: {}
            Total number of sim_<seed_number> directories skipped: {}
            Total number of test sequence names that could not be identified: {}

================================================================================="""
goodbyeMsg = """==== The list of test sequence can be found in {}! Goodbye! ===="""

# Function to handle the input arguments
def parsingArguments():
        parser = argparse.ArgumentParser(description = descriptionMsg)
        parser.add_argument('--path', type = str, help = helpMsg)
        return parser.parse_args()

if __name__ == "__main__":
    args = parsingArguments() # parse the input arguments (if there are any)
    if len(sys.argv) == 1:
        print(noArgsMsg)
        exit()
                                                    
    # ==== Step 1: Get the input arguments ====
    resultsDirectory = args.path # get the path to where all the sim_<seed_number> directories are
                                                                
    # ==== Step 2: Change directory ====
    print(changingDirMsg.format(resultsDirectory)) # let the user know that we are changing directory
    os.chdir(resultsDirectory) # change directory

    # ==== Step 3: Get a list of the sim_<seed_number> folders ====
    simDirs = [] # this will be used to store all the sim_<seed_number> directories
    simDirPattern = "sim_" # the pattern seen at the start of the sim directories
    # Walk (iterate) over the root, files, and subdirectories
    for root, directoryName, fileName in os.walk(resultsDirectory):
        # Check if any of the directories contain "sim_" in their names
        if simDirPattern in str(directoryName):
           simDirs.extend(directoryName) # append the sim_<seed_number> directory to the list
                                                                                                                                
    # Check if the list is empty
    if (len(simDirs) == 0):
        print(noSimDirsFoundMsg)
        exit()
    else:
        numSeeds = len(simDirs) # the number of sim directories found (equal to the number of seeds used in the regression)
        print(simDirsFoundMsg.format(numSeeds))

    # ==== Step 4: Go into each sim_<seed_number> directory and get the name of the test that was run ====
    testList = [] # the list of test sequence names - empty at the moment
    testSeqNamePattern = re.compile(r'TEST_NAME=([a-zA-Z\_0-9]+) ') # the pattern for extracting the name of the test sequence
    testSeqName = ""
    cmdFileName = "test_cmd.txt" # the name of the temporary text file to which we will 'cat' the contents of 'test_cmd'
    cmdLineContents = "" # a string to store the contents of the command-line string that was used to initiate the test
    numSimDirsSkipped = 0 # the number of sim directories skipped (due to an error in reading the test_cmd file)
    seqNameNotFoundCount = 0 # keep track of how many times we cannot identify the test sequence name in a sim_<seed_number> directory
    # ==== Iterating through the sim_<seed_number> directories ====
    for simDir in simDirs:
        simDirPath = resultsDirectory + "/" + simDir # form the path to the sim_<seed_number> directory
        print(changingDirMsg.format(simDir))
        os.chdir(simDirPath) # enter the sim directory
        os.system('cat test_cmd >> test_cmd.txt')
        with open(cmdFileName) as p:
            try:
                cmdLineContents = p.read()
            except:
                print(readErrorMsg.format(cmdFileName, simDir))
                numSimDirsSkipped = numSimDirsSkipped + 1 # increment the count value
                continue # skip this sim directory

        # ==== Get the name of the test sequence ====
        matches = re.findall(testSeqNamePattern, cmdLineContents)
        numMatches = len(matches) # the number of matches

        if (numMatches == 0):
            print(noSeqNameFoundMsg.format(simDir))
            seqNameNotFoundCount = seqNameNotFoundCount + 1 # increment the count value (this will be useful when providing information further down)
            continue
        testSeqName = matches[0] # extract the first match (if there is more than one match, they will all be the same anyway)
        testList.append(testSeqName) # add the test name to the list
    
    # ==== Return to the results directory as this is where we want to generate the output file ====
    print(changingDirMsg.format(resultsDirectory)) # let the user know that we are changing directory
    os.chdir(resultsDirectory)

    # ==== Step 5: Form a list of the unique test sequences (as some sequences may get called many times) ====
    uniqueTestList = set(testList) # convert the list to a set - in a set, any element only appears once
    
    # ==== Inform the User ====
    numTestsFound = len(testList) # get the number of test sequences that were found
    numUniqueTestsFound = len(uniqueTestList)
    print(testSeqsFoundMsg.format(numTestsFound, numUniqueTestsFound))

    # ==== Step 6: Form the string which we will write to the output file =====
    # Get the name of the design used based on the path to the results directory
    designNamePattern = re.compile(r'/designs/([a-zA-Z\_0-9.\-]+)/results') # the pattern for extracting the design name from the path argument
    designName = ""
    designNameFound = False
    matches = re.findall(designNamePattern, resultsDirectory) # try and find (extract) the design name from the path string
    numMatches = len(matches) # the number of matches
    if (numMatches == 0):
        print(noDesignNameIdentifiedMsg.format(resultsDirectory))
        designName = errorTag + "Could not be identified"
    else:
        designName = matches[0]
        designNameFound = True # indicate that we have extracted (found) the design name

    outputFileContents = outputFileHeaderMsg.format(designName, numTestsFound, numUniqueTestsFound, numSimDirsSkipped, seqNameNotFoundCount) + "\n\n"
    for test in uniqueTestList:
        testSeqRunCount = testList.count(test) # count how many times the test sequence was sim in the whole regression
        outputFileContents += "{}, total number of runs in the regression: {}\n".format(test, testSeqRunCount)

    # ==== Step 7: Write the string contents to the output file ====
    outputFileName = "test_sequence_list.txt" # the name of the file to which we will write the list of test sequences
    if (designNameFound): # if we know the design name...
        outputFileName = designName + "_" + outputFileName # prepend it to the name of the output file
    with open(outputFileName, "w") as p:
        p.write(outputFileContents) # write the contents into the file
        print(goodbyeMsg.format(outputFileName))





