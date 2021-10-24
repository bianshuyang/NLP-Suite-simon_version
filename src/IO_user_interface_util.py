import time
import tkinter as tk
import tkinter.messagebox as mb
import os
import json
import logging

import IO_csv_util

logger = logging.getLogger()

#The argument GUI is the title of the GUI displayed (e.g., Narrative Analysis)
def GUI_under_construction(GUI):
    mb.showwarning(title='GUI under construction', message='The "' + GUI + '" GUI is under construction. Sorry!\n\nPlease, revisit this option soon.')

def script_under_construction(script):
    mb.showwarning(title='Script under construction', message='The "' + script + '" script is still under development. Please, revisit this option soon.')

def script_under_development(script):
    mb.showwarning(title='Script under development', message='The "' + script + '" script is still under development. Take the results with a grain of salt and revisit this option soon.')

def convert_time(time):
    hours = int(time / 3600)
    minutes = int((time - hours * 3600) / 60)
    seconds = int(time - hours * 3600 - minutes * 60)
    message=''
    if seconds == 0:
        second_label = ''
    if seconds == 1:
        second_label = ' second'
    else:
        second_label = ' seconds'
    if minutes == 0:
        minute_label = ''
    elif minutes == 1:
        minute_label = ' minute '
    else:
        minute_label = ' minutes '
    if hours == 0:
        hour_label = ''
    elif hours == 1:
        hour_label = ' hours '
    else:
        hour_label = ' hours '

    if hours>0:
        message=str(hours) + hour_label + ', '
    if minutes>0:
        if hours == 0:
            message=message+str(minutes) + minute_label + ' and '
        else:
            message = message + str(minutes) + minute_label + ', and '
    if seconds>0:
        message=message+str(seconds) + second_label

    return hours, minutes, seconds, message

def timed_alert(window, timeout, message_title, message_text, time_needed=False, extraLine='', printInCommandLine=True, startTime=''):
    if time_needed == True:
        # time has year [0], month [1], dat [2], hour [3], minute [4], second [5] & more
        time_report = time.localtime()
        message_text = message_text + ' ' + str(time_report[3]) + ':' + str(time_report[4])
        if startTime != '':
            endTime = time.time()
            totalTime = endTime - startTime # in number of seconds
            hours, minutes, seconds, time_message = convert_time(totalTime)
            # totalTime= ((endTime - startTime)/60)/60 # convert to hours and minutes
            # needs to convert to a message: 32 hours (if there are hours), 12 minutes and 45 seconds.
            message_text = message_text + ' taking ' + time_message # + str(hours) + ' hours, ' + str(minutes) + ' minutes, and ' + str(seconds) + ' seconds'
        message_text = message_text + '.'
    if len(extraLine) > 0:
        message_text = message_text + '\n\n' + extraLine
    top_message = tk.Toplevel(window)
    top_message.title(message_title)
    # windowHeight=len(message_text)
    # print("windowHeight",windowHeight)
    windowHeight = 200
    windowSize = '400x200'  # +str(windowHeight)
    top_message.geometry(windowSize)

    mbox = tk.Message(top_message, text=message_text, padx=20, pady=20, width=260)
    top_message.attributes('-topmost', 'true')
    mbox.after(timeout, top_message.destroy)
    mbox.pack()
    button = tk.Button(top_message, text="OK", command=top_message.destroy)
    button.pack()
    top_message.wait_window()
    # if ('Started running' in message_text) or ('Finished running' in message_text):
    if printInCommandLine:
        print('\n' + message_text + '\n')
    window.focus_force()
    return time.time()

def input_output_save(script):
    result = mb.askyesno(script,
                         script + " will save changes directly in the input file. Make sure you have backup of the input.\n\nAre you sure you want to continue?")
    if result == False:  # yes no False
        return False
    else:
        return True


def single_file_output_save(inputDir, script):
    if len(inputDir) != 0:
        mb.showwarning(title='Warning',
                       message='The output filename generated by ' + script + ' is the name of the directory processed in input, rather than any individual file in the directory.\n\nThe output csv file includes all the files in the input directory processed by the script.')


def subdirectory_file_output_save(inputDir, inputSubdir, IO, script):
    if len(inputDir) != 0:
        mb.showwarning(title='Warning',
                       message='The ' + script + ' script has saved output in \n\n  ' + inputSubdir + '\n\na subdirectory of the ' + IO + ' directory\n\n  ' + inputDir)


# inputFilename has complete path
# filesError is []
def process_CoreNLP_error(window, CoreNLP_output, inputFilename, nDocs, filesError, text, silent=True):
    errorFound = False
    duration = 1000
    head, tail = os.path.split(inputFilename)
    error = None
    if isinstance(CoreNLP_output, str):
        logger.warning("[Warning] Stanford CoreNLP is not JSON. Trying to convert output to JSON... ")

        if text and not CoreNLP_output:
            error = 'Bad Response from Stanford Core NLP Server. This might be due to various reasons. The server might' \
                    'be busy, and please try later. If you are running it with a proxy, please try turning it off ' \
                    'before running it again.'
            logger.error('[Error] ' + error)
            errorFound = True
        else:
            try:
                CoreNLP_output = json.loads(CoreNLP_output)
                logger.warning("[Info] Successfully converted CoreNLP output to JSON. Proceeding as normal.")
                # logger.warning(CoreNLP_output)
            except Exception as e:
                logger.error("[Error] Could not convert output to JSON! Error: " + str(e))
                errorFound = True
                error = str(e)
    # OutOfMemoryError Java heap space
    # this error may occur with Java JDK version > 8. Java heap memoryy size is set to 32 bits by default instead of 64, leading to this error.
    # for memory errors and solutions https://stackoverflow.com/questions/40832022/outofmemoryerror-when-running-the-corenlp-tool
    # You can use Java8. They use metaspace for heap. So, no heap space error will occur.
    # see also
    # https://stackoverflow.com/questions/909018/avoiding-initial-memory-heap-size-error

    # need to add -d64 to the Java call (e.g., ['java', '-mx' + str(memory_var) + "g", '-d64', '-cp', os.path.join(CoreNLPdir, '*'),
    #          'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-timeout', '999999'])
    # TODO % will break the code
    # The reasons are explained here: https://docs.oracle.com/javase/8/docs/api/java/net/URLDecoder.html
    #   The character "%" is allowed but is interpreted as the start of a special escaped sequence.
    # Needs special handling https://stackoverflow.com/questions/6067673/urldecoder-illegal-hex-characters-in-escape-pattern-for-input-string
    if errorFound:
        if len(filesError) > 2:
            silent = True
        elif len(filesError) == 2:
            duration = 1000
        elif len(filesError) == 1:
            duration = 2000
        elif len(filesError) == 0:
            filesError.append(['Document ID', 'Document', 'Error'])
            duration = 3000
        msg = 'Stanford CoreNLP failed to process your document\n\n' + tail + '\n\nexiting with the following error:\n\n   ' + (
            str(
                CoreNLP_output) if CoreNLP_output else error) + '\n\nPlease, CHECK CAREFULLY THE REASONS FOR FAILURE REPORTED BY STANFORD CORENLP. If necessary, then edit the file leading to errors if necessary.'
        msgPrint = "Stanford CoreNLP failed to process your document " + tail
        # + '\nexiting with the following error:\n\n' + CoreNLP_output + '\n\nTHE ERROR MAY HAPPEN WHEN CoreNLP HANGS. REBOOT YOUR MACHINE AND TRY AGAIN.\n\nTHE ERROR IS ALSO LIKELY TO HAPPEN WHEN THE STANFORD CORENLP HAS BEEN STORED TO A CLOUD SERVICE (e.g., OneDrive) OR INSIDE THE /NLP/src DIRECTORY. TRY TO MOVE THE STANFORD CORENLP FOLDER TO A DIFFERENT LOCATION.
        if nDocs > 1:
            msg = msg + " Processing will continue with the next file."
            msgPrint += " Processing will continue with the next file."
        # mb.showwarning("Stanford CoreNLP Error", msg)
        if not silent:
            timed_alert(window, duration, 'Stanford CoreNLP error', msg)
        print("\n\n" + msgPrint)
        filesError.append([len(filesError), IO_csv_util.dressFilenameForCSVHyperlink(inputFilename), str(CoreNLP_output) + " " + str(error)])
    return errorFound, filesError, CoreNLP_output
