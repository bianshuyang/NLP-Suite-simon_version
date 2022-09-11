# Written by Roberto Franzosi

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "NLP_parsers_annotators_main", ['tkinter', 'subprocess']) == False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_files_util
import config_util
import reminders_util
import Stanford_CoreNLP_util
import Stanford_CoreNLP_coreference_util
import Stanza_util
import spaCy_util

# RUN section ______________________________________________________________________________________________________________________________________________________

# https://stackoverflow.com/questions/45886128/unable-to-set-up-my-own-stanford-corenlp-server-with-error-could-not-delete-shu
# for the Error [Thread-0] INFO CoreNLP - CoreNLP Server is shutting down
# sometimes the error appears but processing actually continues; but rebooting should do the trick if processing does not continue

# dateInclude indicates whether there is date embedded in the file name.
# 1: included 0: not included

def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,
        memory_var,
        document_length_var,
        limit_sentence_length_var,
        manual_Coref, open_GUI,
        dateInclude, sep, date_field_position, dateFormat,
        parser_var,
        parser_menu_var,
        single_quote,
        CoNLL_table_analyzer_var, annotators_var, annotators_menu_var):

    filesToOpen = []
    outputCoNLLfilePath = ''

    # display_available_options()
    #changed_NLP_package_set_parsers()

    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return

    if parser_var == 0 and CoNLL_table_analyzer_var == 1:
        mb.showinfo("Warning", "You have selected to open the CoNLL table analyser GUI. This option expects to run the parser first.\n\nPlease, tick the CoreNLP parser checkbox and try again.")
        return

    if annotators_var and annotators_menu_var == '':
        mb.showinfo("Warning", "You have selected to run a CoreNLP annotator but no annotator has been selected.\n\nPlease, select an annotator and try try again.")
        return

# Stanford CoreNLP ---------------------------------------------------------------------------
    if package=='Stanford CoreNLP':
        if parser_var or (annotators_var and annotators_menu_var != ''):
            annotator = []
            if IO_libraries_util.check_inputPythonJavaProgramFile('Stanford_CoreNLP_util.py') == False:
                return

            if parser_var:
                if 'PCFG' in parser_menu_var:
                    annotator='parser (pcfg)'
                elif parser_menu_var == 'Neural Network':
                    annotator='parser (nn)'
            else:
                if annotators_var and annotators_menu_var != '':
                    if 'NER (GUI)' in annotators_menu_var: # NER annotator
                        if IO_libraries_util.check_inputPythonJavaProgramFile('Stanford_CoreNLP_NER_main.py') == False:
                            return
                        call("python Stanford_CoreNLP_NER_main.py", shell=True)
                    elif 'Sentence splitter (with sentence length)' in annotators_menu_var:
                        annotator = 'Sentence'
                    elif 'Lemma annotator' in annotators_menu_var:
                        annotator = 'Lemma'
                    elif 'POS annotator' in annotators_menu_var:
                        annotator = 'All POS'
                    elif 'Gender' in annotators_menu_var:
                        annotator = 'gender'
                    elif 'Quote' in annotators_menu_var:
                        annotator = 'quote'
                    elif 'Normalized' in annotators_menu_var:
                        annotator = 'normalized-date'
                    elif '*' in annotators_menu_var:
                        annotator = ['gender','normalized-date','quote']
                    elif 'Sentiment analysis' in annotators_menu_var:
                        annotator = ['sentiment']
                    elif 'SVO' in annotators_menu_var:
                        annotator = ['SVO']
                    elif 'OpenIE' in annotators_menu_var:
                        annotator = ['OpenIE']
                    elif 'Coreference PRONOMINAL resolution' in annotators_menu_var:
                        annotator = []
                        if IO_libraries_util.check_inputPythonJavaProgramFile(
                                "Stanford_CoreNLP_coReference_util.py") == False:
                            return
                        file_open, error_indicator = Stanford_CoreNLP_coreference_util.run(config_filename, inputFilename,
                                                                                           inputDir,
                                                                                           outputDir, openOutputFiles,
                                                                                           createCharts, chartPackage,
                                                                                           language, memory_var,
                                                                                           manual_Coref)

                        if error_indicator != 0:
                            mb.showinfo("Coreference Resolution Error",
                                        "Since Stanford CoreNLP Co-Reference Resolution throws error, " +
                                        "and you either didn't choose manual Co-Reference Resolution or manual Co-Referenece Resolution fails as well, the process ends now.")
                        filesToOpen.append(file_open)
                    else:
                        return

            if len(annotator)>0:
                tempOutputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                               outputDir,
                                                                               openOutputFiles, createCharts, chartPackage,
                                                                               annotator, False, #'All POS',
                                                                               language, memory_var, document_length_var, limit_sentence_length_var,
                                                                               extract_date_from_filename_var=dateInclude,
                                                                               date_format=dateFormat,
                                                                               date_separator_var=sep,
                                                                               date_position_var=date_field_position,
                                                                               single_quote_var = single_quote)

                if len(tempOutputFiles)>0:
                    filesToOpen.append(tempOutputFiles)
                    if 'parser' in annotator:
                        reminders_util.checkReminder(config_filename,
                                                     reminders_util.title_options_CoreNLP_NER_tags,
                                                     reminders_util.message_CoreNLP_NER_tags,
                                                     True)

# spaCy ---------------------------------------------------------------------------
    if package == 'spaCy':
        if parser_var or (annotators_var and annotators_menu_var != ''):
            if IO_libraries_util.check_inputPythonJavaProgramFile(
                    'spaCy_util.py') == False:
                return
        if annotators_var:
            if annotators_menu_var == '':
                mb.showwarning('Warning',
                               'The option of running a spaCy annotator has been selected but no annotaor has been selected.\n\nPlease, select an annotator option and try again.')
                return
            if 'Sentence splitter (with sentence length)' in annotators_menu_var:
                annotator = 'Sentence'
            elif 'Lemma annotator' in annotators_menu_var:
                annotator = 'Lemma'
            elif 'POS annotator' in annotators_menu_var:
                annotator = 'All POS'
            elif 'NER annotator' in annotators_menu_var:  # NER annotator
                annotator = 'NER'
            elif 'Sentiment analysis' in annotators_menu_var:
                annotator = 'sentiment'
            elif 'SVO extraction' in annotators_menu_var:
                annotator = 'SVO'
            elif 'Gender' in annotators_menu_var or 'Quote' in annotators_menu_var or 'Normalized NER' in annotators_menu_var or 'Gender' in annotators_menu_var or 'OpenIE' in annotators_menu_var:
                mb.showwarning(title='Option not available in spaCy',
                               message='The ' + annotators_menu_var + ' is not available in spaCy.\n\nThe annotator is available in Stanford CoreNLP. If you wish to run the annotator, please, using the Setup dropdown menu at the bottom of this GUI, select the Setup NLP package and corpus language option and select Stanford CoreNLP as your default package and try again.')
                return
            else:
                mb.showwarning('Warning',
                               'The selected option ' + annotators_menu_var + ' is not available in spaCy (yet).\n\nPlease, select another annotator and try again.')
                return

        document_length_var = 1
        limit_sentence_length_var = 1000
        tempOutputFiles = spaCy_util.spaCy_annotate(config_filename, inputFilename, inputDir,
                                                    outputDir,
                                                    openOutputFiles,
                                                    createCharts, chartPackage,
                                                    annotator, False,
                                                    language,
                                                    memory_var, document_length_var, limit_sentence_length_var,
                                                    extract_date_from_filename_var=dateInclude,
                                                    date_format=dateFormat,
                                                    date_separator_var=sep,
                                                    date_position_var=date_field_position)

        if tempOutputFiles == None:
            return

        if len(tempOutputFiles) > 0:
            filesToOpen.append(tempOutputFiles)
            if 'parser' in annotator:
                reminders_util.checkReminder(config_filename,
                                             reminders_util.title_options_CoreNLP_NER_tags,
                                             reminders_util.message_CoreNLP_NER_tags,
                                             True)

# Stanza ---------------------------------------------------------------------------

    if package == 'Stanza':
        if parser_var or (annotators_var and annotators_menu_var != ''):

            if IO_libraries_util.check_inputPythonJavaProgramFile(
                    'Stanza_util.py') == False:
                return
        if parser_var:
            if parser_menu_var == 'Constituency parser':
                mb.showwarning('Warning',
                               'The selected option is not available yet. Sorry!\n\nPlease, select a different option and try again.')
                return
            annotator = 'depparse'

        if annotators_var:
            if annotators_menu_var == '':
                mb.showwarning('Warning',
                               'The option of running a Stanza annotator has been selected but no annotaor has been selected.\n\nPlease, select an annotator option and try again.')
                return
            if 'Sentence splitter (with sentence length)' in annotators_menu_var:
                annotator = 'Sentence'
            elif 'Lemma annotator' in annotators_menu_var:
                annotator = 'Lemma'
            elif 'POS annotator' in annotators_menu_var:
                annotator = 'All POS'
            elif 'NER annotator' in annotators_menu_var:  # NER annotator
                annotator = 'NER'
            elif 'Sentiment analysis' in annotators_menu_var:
                annotator = 'sentiment'
            elif 'SVO extraction' in annotators_menu_var:
                annotator = 'SVO'
            elif 'Gender' in annotators_menu_var or 'Quote' in annotators_menu_var or 'Normalized NER' in annotators_menu_var or 'Gender' in annotators_menu_var or 'OpenIE' in annotators_menu_var:
                mb.showwarning(title='Option not available in Stanza',
                               message='The ' + annotators_menu_var + ' is not available in Stanza.\n\nThe annotator is available in Stanford CoreNLP. If you wish to run the annotator, please, using the Setup dropdown menu at the bottom of this GUI, select the Setup NLP package and corpus language option and select Stanford CoreNLP as your default package and try again.')
                return
            else:
                mb.showwarning('Warning',
                               'The selected option ' + annotators_menu_var + ' is not available in Stanza (yet).\n\nPlease, select another annotator and try again.')
                return

        document_length_var = 1
        limit_sentence_length_var = 1000
        tempOutputFiles = Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir,
                                                      outputDir,
                                                      openOutputFiles,
                                                      createCharts, chartPackage,
                                                      annotator, False,
                                                      language_list,
                                                      memory_var, document_length_var, limit_sentence_length_var,
                                                      extract_date_from_filename_var=dateInclude,
                                                      date_format=dateFormat,
                                                      date_separator_var=sep,
                                                      date_position_var=date_field_position)

        if tempOutputFiles == None:
            return

        if len(tempOutputFiles) > 0:
            filesToOpen.append(tempOutputFiles)
            if 'parser' in annotator:
                reminders_util.checkReminder(config_filename,
                                             reminders_util.title_options_CoreNLP_NER_tags,
                                             reminders_util.message_CoreNLP_NER_tags,
                                             True)

    # CoNLL table analyzer
    if CoNLL_table_analyzer_var:
        if IO_libraries_util.check_inputPythonJavaProgramFile('CoNLL_table_analyzer_main.py') == False:
            return
        # open the analyzer having saved the new parser output in config so that it opens the right input file
        config_filename_temp = 'conll_table_analyzer_config.csv'
        config_input_output_numeric_options = [1, 0, 0, 1]
        config_input_output_alphabetic_options = [str(tempOutputFiles[0]), '','',outputDir]
        config_util.write_config_file(GUI_util.window, config_filename_temp, config_input_output_numeric_options, config_input_output_alphabetic_options, True)

        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_CoNLL_analyzer,
                                     reminders_util.message_CoNLL_analyzer,
                                     True)

        call("python CoNLL_table_analyzer_main.py", shell=True)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated

run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_chart_output_checkbox.get(),
                                 GUI_util.charts_dropdown_field.get(),
                                 memory_var.get(),
                                 document_length_var.get(),
                                 limit_sentence_length_var.get(),
                                 manual_Coref_var.get(),
                                 open_GUI_var.get(),
                                 fileName_embeds_date.get(),
                                 date_separator_var.get(),
                                 date_position_var.get(),
                                 date_format.get(),
                                 parser_var.get(),
                                 parser_menu_var.get(),
                                 quote_var.get(),
                                 CoNLL_table_analyzer_var.get(),
                                 annotators_var.get(),
                                 annotators_menu_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=480, # height at brief display
                             GUI_height_full=560, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for NLP parsers & annotators'
# The 4 values of config_option refer to:
#   input file
        # 1 for CoNLL file
        # 2 for TXT file
        # 3 for csv file
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#   input dir
#   input secondary dir
#   output dir
config_input_output_numeric_options=[2,1,0,1]
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('main.py', 'config.csv')

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path

def clear(e):
    # package.set('Stanford CoreNLP')
    # language.set("English")
    parser_var.set(1)
    parser_menu_var.set("Probabilistic Context Free Grammar (PCFG)")
    annotators_var.set(0)
    annotators_menu_var.set('')
    manual_Coref_checkbox.place_forget()  # invisible
    open_GUI_checkbox.place_forget()  # invisible
    quote_checkbox.place_forget()  # invisible
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

package = tk.StringVar()
language = tk.StringVar()
language_list = []
memory_var = tk.IntVar()
date_extractor_var = tk.IntVar()
CoreNLP_gender_annotator_var = tk.IntVar()
split_files_var = tk.IntVar()
quote_extractor_var = tk.IntVar()
manual_Coref_var = tk.IntVar()
open_GUI_var = tk.IntVar()
parser_var = tk.IntVar()
parser_menu_var = tk.StringVar()
fileName_embeds_date = tk.IntVar()

date_format = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

CoNLL_table_analyzer_var = tk.IntVar()

annotators_var = tk.IntVar()
annotators_menu_var = tk.StringVar()

quote_var = tk.IntVar()
y_multiplier_integer_SV=0 # used to set the quote_var widget on the proper GUI line

pre_processing_button = tk.Button(window, width=50, text='Pre-processing tools (Open file checking & cleaning GUI)',command=lambda: call('python file_checker_converter_cleaner_main.py'))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               pre_processing_button)

# memory options

memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               memory_var_lb, True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(4)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+100, y_multiplier_integer,
                                               memory_var,True)

document_length_var_lb = tk.Label(window, text='Document length')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               document_length_var_lb, True)

document_length_var = tk.Scale(window, from_=40000, to=90000, orient=tk.HORIZONTAL)
document_length_var.pack()
document_length_var.set(90000)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+150, y_multiplier_integer,
                                               document_length_var,True)

limit_sentence_length_var_lb = tk.Label(window, text='Limit sentence length')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 370, y_multiplier_integer,
                                               limit_sentence_length_var_lb,True)

limit_sentence_length_var = tk.Scale(window, from_=70, to=400, orient=tk.HORIZONTAL)
limit_sentence_length_var.pack()
limit_sentence_length_var.set(100)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 550, y_multiplier_integer,
                                               limit_sentence_length_var)

date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy-dd-mm', 'yyyy-mm',
                                 'yyyy')

fileName_embeds_date_msg = tk.Label()
date_position_menu_lb = tk.Label()
date_position_menu = tk.OptionMenu(window, date_position_var, 1, 2, 3, 4, 5)
date_format_lb = tk.Label()
date_separator = tk.Entry(window, textvariable=date_separator_var)
date_separator_lb = tk.Label()

fileName_embeds_date_checkbox = tk.Checkbutton(window, text='Filename embeds date', variable=fileName_embeds_date,
                                               onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               fileName_embeds_date_checkbox, True)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               fileName_embeds_date_msg, True)

date_format.set('mm-dd-yyyy')
date_format_lb = tk.Label(window, text='Date format ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               date_format_lb, True)
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy-dd-mm', 'yyyy-mm',
                                 'yyyy')
date_format_menu.configure()
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 90, y_multiplier_integer,
                                               date_format_menu, True)

date_separator_lb = tk.Label(window, text='Date character separator ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 230, y_multiplier_integer,
                                               date_separator_lb, True)

date_separator_var.set('_')
date_separator = tk.Entry(window, textvariable=date_separator_var)
date_separator.configure(width=2)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 390, y_multiplier_integer,
                                               date_separator, True)

date_position_var.set(2)
date_position_menu_lb = tk.Label(window, text='Date position ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 440, y_multiplier_integer,
                                               date_position_menu_lb, True)
date_position_menu = tk.OptionMenu(window, date_position_var, 1, 2, 3, 4, 5)
date_position_menu.configure(width=2)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 530, y_multiplier_integer,
                                               date_position_menu)


def check_CoreNLP_dateFields(*args):
    if fileName_embeds_date.get() == 1:
        # fileName_embeds_date_msg.config(text="Date option ON")
        date_format_menu.config(state="normal")
        date_separator.config(state='normal')
        date_position_menu.config(state='normal')
    else:
        # fileName_embeds_date_msg.config(text="Date option OFF")
        date_format_menu.config(state="disabled")
        date_separator.config(state='disabled')
        date_position_menu.config(state="disabled")
fileName_embeds_date.trace('w', check_CoreNLP_dateFields)

y_multiplier_integer_SV1=y_multiplier_integer

# if package != '':
#     available_parsers = 'Parsers for ' + package + '                          '
# else:
#     available_parsers = 'Parsers'
#
parser_checkbox = tk.Checkbutton(window, variable=parser_var, onvalue=1, offvalue=0)

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer_SV1,
                                               parser_checkbox, True, False, False, False, 90,
                                               GUI_IO_util.get_labels_x_coordinate(),
                                               "If you wish to change the NLP package used (spaCy, Stanford CoreNLP, Stanza) and their available parsers, use the Setup dropdown menu at the bottom of this GUI")

available_parsers=''
parser_lb = tk.Label(window, text=available_parsers)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+40, y_multiplier_integer,
                                               parser_lb, True)
parser_var.set(1)

parsers=[]

if len(parsers) == 0:
    parser_menu = tk.OptionMenu(window, parser_menu_var, parsers)
else:
    parser_menu = tk.OptionMenu(window, parser_menu_var, *parsers)
#     # place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.get_open_file_directory_coordinate(),
                                               y_multiplier_integer,
                                               parser_menu, False, False, False, False, 90,
                                               GUI_IO_util.get_labels_x_coordinate(),
                                               "If you wish to change the NLP package used (spaCy, Stanford CoreNLP, Stanza) and their available parsers, use the Setup dropdown menu at the bottom of this GUI")
if len(parsers) > 0:
    parser_menu_var.set(parsers[0])


# def display_available_options(*args):
#     global y_multiplier_integer, y_multiplier_integer_SV1, error, package, parsers, language, package_display_area_value, language_list
#     error, package, parsers, package_basics, language, package_display_area_value = config_util.read_NLP_package_language_config()
#     language_list=[language]
#     parser_var.set(1)
#     if package!='':
#         available_parsers = 'Parsers for ' + package +'                          '
#     else:
#         available_parsers='Parsers'
#     if len(parsers)>0:
#         parser_menu_var.set(parsers[0])
#
#     parser_checkbox = tk.Checkbutton(window, text=available_parsers, variable=parser_var, onvalue=1, offvalue=0)
#     # place widget with hover-over info
#     y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer_SV1,
#                                                    parser_checkbox, True, False, False, False, 90,
#                                                    GUI_IO_util.get_labels_x_coordinate(),
#                                                    "If you wish to change the NLP package used (spaCy, Stanford CoreNLP, Stanza) and their available parsers, use the Setup dropdown menu at the bottom of this GUI")
#     if len(parsers) == 0:
#         parser_menu = tk.OptionMenu(window, parser_menu_var, parsers)
#     else:
#         parser_menu = tk.OptionMenu(window, parser_menu_var, *parsers)
#     y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.get_open_file_directory_coordinate(),
#                                                    y_multiplier_integer,
#                                                    parser_menu)
#     return y_multiplier_integer
# parser_menu_var.trace('w',display_available_options())
# display_available_options()

def activate_SentenceTable(*args):
    global parser_menu
    if parser_var.get() == 0:
        parser_menu_var.set('')
        parser_menu.configure(state='disabled')
        # compute_sentence_var.set(0)
        CoNLL_table_analyzer_var.set(0)
    else:
        parser_menu_var.set('Probabilistic Context Free Grammar (PCFG)')
        parser_menu.configure(state='normal')
        # compute_sentence_var.set(1)
        CoNLL_table_analyzer_var.set(1)

CoNLL_table_analyzer_var.set(0)
CoNLL_table_analyzer_checkbox = tk.Checkbutton(window, text='CoNLL table analyzer', variable=CoNLL_table_analyzer_var,
                                               onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               CoNLL_table_analyzer_checkbox, True)
CoNLL_table_analyzer_checkbox_msg = tk.Label()
CoNLL_table_analyzer_checkbox_msg.config(text="Open the CoNLL table analyzer GUI")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               CoNLL_table_analyzer_checkbox_msg)

def check_CoNLL_table(*args):
    if CoNLL_table_analyzer_var.get() == 1:
        CoNLL_table_analyzer_checkbox_msg.config(text="Open CoNLL table analyzer GUI")
    else:
        CoNLL_table_analyzer_checkbox_msg.config(text="Do NOT open CoNLL table analyzer GUI")
CoNLL_table_analyzer_var.trace('w', check_CoNLL_table)

check_CoNLL_table()

Annotators_checkbox = tk.Checkbutton(window, text='Annotators', variable=annotators_var,
                                             onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               Annotators_checkbox, True)

annotators_menu_var.set("")
annotators_menu_var.set("")
annotators_menu = tk.OptionMenu(window, annotators_menu_var,
        'Sentence splitter (with sentence length)',
        'Lemma annotator',
        'POS annotator',
        'NER (GUI)',
        'Coreference PRONOMINAL resolution (Neural Network)',
        'Sentiment analysis (Neural Network)',
        'OpenIE - Relation triples extractor (Neural Network)',
        'SVO extraction (Enhanced++ Dependencies; Neural Network)',
        '*',
        'Gender annotator (Neural Network)',
        'Normalized NER date annotator',
        'Quote/dialogue annotator (Neural Network)')

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               annotators_menu)

manual_Coref_checkbox = tk.Checkbutton(window, text='Manual edit',
                                       variable=manual_Coref_var,
                                       onvalue=1, offvalue=0)

open_GUI_checkbox = tk.Checkbutton(window, text='Open coreference GUI',
                                       variable=open_GUI_var,
                                       onvalue=1, offvalue=0)

quote_checkbox = tk.Checkbutton(window, text='Include single quotes',
                                       variable=quote_var,
                                       onvalue=1, offvalue=0)

def activate_annotators_menu(*args):
    global y_multiplier_integer, y_multiplier_integer_SV
    if annotators_var.get() == True:
        if parser_var.get():
            if 'POS' in annotators_menu_var.get():
                mb.showinfo("Warning", "You have selected to run the CoreNLP parser AND the lemma/POS annotator. The parser already computes lemmas and POS tags.\n\nPlease, tick either the parser or the annotator checkbox.")
                annotators_var.set(0)
                annotators_menu_var.set('')
                return
        annotators_menu.configure(state='normal')
        if y_multiplier_integer_SV == 0:
            y_multiplier_integer_SV = y_multiplier_integer
        if '*' in annotators_menu_var.get() or 'dialogue' in annotators_menu_var.get():
            y_multiplier_integer=y_multiplier_integer_SV-1
            quote_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 400,
                                                           y_multiplier_integer,
                                                           quote_checkbox,True)
            quote_checkbox.configure(state='normal')
        else:
            quote_checkbox.place_forget()  # invisible

        if 'Coreference' in annotators_menu_var.get():
            y_multiplier_integer=y_multiplier_integer-1
            manual_Coref_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 400,
                                                           y_multiplier_integer,
                                                           manual_Coref_checkbox,True)

            open_GUI_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 550,
                                                           y_multiplier_integer,
                                                           open_GUI_checkbox)
            open_GUI_checkbox.configure(state='normal')
            if input_main_dir_path.get()!='':
                manual_Coref_checkbox.configure(state='disabled')
            else:
                manual_Coref_checkbox.configure(state='normal')
        else:
            manual_Coref_checkbox.place_forget()  # invisible
            open_GUI_checkbox.place_forget()  # invisible
    else:
        manual_Coref_checkbox.place_forget()  # invisible
        open_GUI_checkbox.place_forget()  # invisible
        annotators_menu_var.set('')
        annotators_menu.configure(state='disabled')

annotators_var.trace('w', activate_annotators_menu)
annotators_menu_var.trace('w', activate_annotators_menu)

activate_annotators_menu()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Stanford CoreNLP download': 'TIPS_NLP_Stanford CoreNLP download install run.pdf',
               'Stanford CoreNLP performance & accuracy':'TIPS_NLP_Stanford CoreNLP performance and accuracy.pdf',
               'Stanford CoreNLP parser': 'TIPS_NLP_Stanford CoreNLP parser.pdf',
               'Stanford CoreNLP memory issues': 'TIPS_NLP_Stanford CoreNLP memory issues.pdf',
               'NER (Named Entity Recognition)': 'TIPS_NLP_NER (Named Entity Recognition).pdf',
               'Stanford CoreNLP date extractor (NER normalized date)': 'TIPS_NLP_Stanford CoreNLP date extractor.pdf',
               'Stanford CoreNLP OpenIE': 'TIPS_NLP_Stanford CoreNLP OpenIE.pdf',
               'Stanford CoreNLP coreference resolution': 'TIPS_NLP_Stanford CoreNLP coreference resolution.pdf',
               'Excel - Enabling Macros': 'TIPS_NLP_Excel Enabling macros.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'utf-8 encoding': 'TIPS_NLP_Text encoding.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf',
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf',
               'Stanford CoreNLP supported languages':'TIPS_NLP_Stanford CoreNLP supported languages.pdf',
               'CoNLL Table': 'TIPS_NLP_Stanford CoreNLP CoNLL table.pdf',
               'POSTAG (Part of Speech Tags)': "TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf",
               'Gender annotator':'TIPS_NLP_Gender annotator.pdf',
               'Quote annotator':'',
               'Normalized NER date annotator':'TIPS_NLP_Stanford CoreNLP date extractor.pdf',
               'Sentiment analysis':'TIPS_NLP_Sentiment analysis.pdf',
               'Noun Analysis': "IPS_NLP_Noun Analysis.pdf",
               'Verb Analysis': "TIPS_NLP_Verb Analysis.pdf",
               'Function Words Analysis': 'TIPS_NLP_Function Words Analysis.pdf',
               'Clause Analysis': 'TIPS_NLP_Clause analysis.pdf'}
               # 'Java download install run': 'TIPS_NLP_Java download install run.pdf',
TIPS_options = 'utf-8 encoding', 'Excel - Enabling Macros', 'Excel smoothing data series', 'csv files - Problems & solutions', 'Statistical measures', 'Stanford CoreNLP supported languages', 'Stanford CoreNLP performance & accuracy', 'Stanford CoreNLP download', 'Stanford CoreNLP parser', 'Stanford CoreNLP memory issues', 'Stanford CoreNLP date extractor (NER normalized date)', 'Stanford CoreNLP coreference resolution', 'Stanford CoreNLP OpenIE', 'CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)', 'NER (Named Entity Recognition)','Gender annotator','Quote annotator','Normalized NER date annotator','Sentiment analysis','Things to do with words: Overall view' #, 'Java download install run'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.

def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, click on the 'Pre-processing tools' button to open the GUI where you will be able to perform a variety of\n   file checking options (e.g., utf-8 encoding compliance of your corpus or sentence length);\n   file cleaning options (e.g., convert non-ASCII apostrophes & quotes and % to percent).\n\nNon utf-8 compliant texts are likely to lead to code breakdown in various algorithms.\n\nASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n\n% signs will lead to code breakdon of Stanford CoreNLP.\n\nSentences without an end-of-sentence marker (. ! ?) in Stanford CoreNLP will be processed together with the next sentence, potentially leading to very long sentences.\n\nSentences longer than 70 or 100 words may pose problems to Stanford CoreNLP (the average sentence length of modern English is 20 words). Please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.")
    # y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
    #                               "Please, click on the 'Setup' button to open the GUI that will allow you to select the NLP package to be used (e.g., spaCy, Stanford CoreNLP, Stanza).\n\nDifferent NLP packages support a different range of languages. The Setup GUI will also allow you to select the language of your input txt file(s).\n\nTHE CURRENT NLP PACKAGE AND LANGUAGE SELECTION IS DISPLAYED IN THE TEXT WIDGET."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "The Stanford CoreNLP performance is affected by various issues: memory size of your computer, document size, sentence length\n\nPlease, select the memory size Stanford CoreNLP will use. Default = 4. Lower this value if CoreNLP runs out of resources.\n   For CoreNLP co-reference resolution you may wish to increase the value when processing larger files (compatibly with the memory size of your machine).\n\nLonger documents affect performace. Stanford CoreNLP has a limit of 100,000 characters processed (the NLP Suite limits this to 90,000 as default). If you run into performance issues you may wish to further reduce the document size.\n\nSentence length also affect performance. The Stanford CoreNLP recommendation is to limit sentence length to 70 or 100 words.\n   You may wish to compute the sentence length of your document(s) so that perhaps you can edit the longer sentences.\n\nOn these issues, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if your filenames embed a date (e.g., The New York Times_12-23-1992).\n\nWhen the date option is ticked, the script will add a date field to the CoNLL table. The date field will be used by other NLP scripts (e.g., Ngrams).\n\nOnce you have ticked the 'Filename embeds date' option, you will need to provide the follwing information:\n   1. the date format of the date embedded in the filename (default mm-dd-yyyy); please, select.\n   2. the character used to separate the date field embedded in the filenames from the other fields (e.g., _ in the filename The New York Times_12-23-1992) (default _); please, enter.\n   3. the position of the date field in the filename (e.g., 2 in the filename The New York Times_12-23-1992; 4 in the filename The New York Times_1_3_12-23-1992 where perhaps fields 2 and 3 refer respectively to the page and column numbers); please, select.\n\nIF THE FILENAME EMBEDS A DATE AND THE DATE IS THE ONLY FIELD AVAILABLE IN THE FILENAME (e.g., 2000.txt), enter . in the 'Date character separator' field and enter 1 in the 'Date position' field.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to use the CoreNLP parser to obtain a CoNLL table (CoNLL U format).\n\nThe CoNLL table is the basis of many of the NLP analyses: noun & verb analysis, function words, clause analysis, query CoNLL.\n\nYou have a choice between two types of papers:\n   1. the recommended default Probabilistic Context Free Grammar (PCFG) parser;\n   2. a Neural-network dependency parser.\n\nThe neural network approach is more accurate but much slower.\n\nIn output the scripts produce a CoNLL table with the following 9 fields: ID, FORM, LEMMA, POSTAG, NER (23 classes), HEAD, DEPREL, DEPS, CLAUSAL TAGS (the neural-network parser does not produce clausal tags).\n\nThe following fields will be automatically added to the standard 9 fields of a CoNLL table (CoNLL U format): RECORD NUMBER, DOCUMENT ID, SENTENCE ID, DOCUMENT (INPUT filename), DATE (if the filename embeds a date).\n\nIf you suspect that CoreNLP may have given faulty results for some sentences, you can test those sentences directly on the Stanford CoreNLP website at https://corenlp.run")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick/untick the checkbox if you want to open (or not) the CoNLL table analyzer GUI to analyze the CoreNLP parser results contained in the CoNLL table.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select one of the many other annotators available through Stanford CoreNLP: Coreference pronominal resolution, DepRel, POS, NER (Named Entity Recognition), NER normalized date. gender, quote, and sentiment analysis.\n\nANNOTATORS MARKED AS NEURAL NETWORK ARE MORE ACCURATE, BUT SLOW AND REQUIRE A GREAT DEAL OF MEMORY.\n\n1.  PRONOMINAL co-reference resolution refers to such cases as 'John said that he would...'; 'he' would be substituted by 'John'. CoreNLP can resolve other cases but the algorithm here is restricted to pronominal resolution.\n\nThe co-reference resolution checkbox is disabled when selected an entire directory in input. The co-reference resolution algorithm is a memory hog. You may not have enough memory on your machine.\n\nTick the checkbox Manually edit coreferenced document if you wish to resolve manually cases of unresolved or wrongly resolved coreferences. MANUAL EDITING REQUIRES A LOT OF MEMORY SINCE BOTH ORIGINAL AND CO-REFERENCED FILE ARE BROUGHT IN MEMORY. DEPENDING UPON FILE SIZES, YOU MAY NOT HAVE ENOUGH MEMORY FOR THIS STEP.\n\nTick the Open GUI checkbox to open the specialized GUI for pronominal coreference resolution.\n\n2.  The CoreNLP NER annotator recognizes the following NER values:\n  named (PERSON, LOCATION, ORGANIZATION, MISC);\n  numerical (MONEY, NUMBER, ORDINAL, PERCENT);\n  temporal (DATE, TIME, DURATION, SET).\n  In addition, via regexner, the following entity classes are tagged: EMAIL, URL, CITY, STATE_OR_PROVINCE, COUNTRY, NATIONALITY, RELIGION, (job) TITLE, IDEOLOGY, CRIMINAL_CHARGE, CAUSE_OF_DEATH.\n\n3.  The NER NORMALIZED DATE annotator extracts standard dates from text in the yyyy-mm-dd format (e.g., 'the day before Christmas' extracted as 'xxxx-12-24').\n\n4.  The CoreNLP coref GENDER annotator extracts the gender of both first names and personal pronouns (he, him, his, she, her, hers) using a neural network approach. This annotator requires a great deal of memory. So, please, adjust the memory allowing as much memory as you can afford.\n\n5.  The CoreNLP QUOTE annotator extracts quotes from text and attributes the quote to the speaker. The default CoreNLP parameter is DOUBLE quotes. If you want to process both DOUBLE and SINGLE quotes, plase tick the checkbox 'Include single quotes.'\n\n6.  The SENTIMENT ANALYSIS annotator computes the sentiment values (negative, neutral, positive) of each sentence in a text.\n\n6.  The OpenIE (Open Information Extraction) annotator extracts  open-domain relation triples, representing a subject, a relation, and the object of the relation.\n\n\n\nIn INPUT the algorithms expect a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithms will produce a number of csv files  and Excel charts. The Gender annotator will also produce an html file with male tags displayed in blue and female tags displayed in red. The Coreference annotator will produce txt-format copies of the same input txt files but co-referenced.\n\Select * to run Gender annotator (Neural Network), Normalized NER date, and Quote/dialogue annotator (Neural Network).")
    # y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
    #                               "Please, tick the checkbox if you want to open the GUI to run other parsers and annotatators available in the NLP Suite: spaCy & Stanza. Use the dropdown menu to select the GUI you wish to open.\n\nBoth spaCy and Stanza use neural networks for all their parsers and annotators. spcaCy is also lighting fast.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), 0)

# change the value of the readMe_message
readMe_message = "This Python 3 script will perform different types of textual operations using a selected NLP package (e.g., spaCy, Stanford CoreNLP, Stanza). The main operation is text parsing to produce the CoNLL table (CoNLL U format).\n\nYOU MUST BE CONNETED TO THE INTERNET TO RUN THE SCRIPTS.\n\nIn INPUT the algorithms expect a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithms will produce different file types: txt-format copies of the same input txt files for co-reference, csv for annotators (HTML for gender annotator)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName, False)

def activate_NLP_options(*args):
    global error, parsers, available_parsers, parser_lb, package, package_display_area_value, language, language_list
    error, package, parsers, package_basics, language, package_display_area_value, package_display_area_value_new = GUI_util.handle_setup_options(y_multiplier_integer, scriptName)
    if package != '':
        available_parsers = 'Parsers for ' + package + '                          '
    else:
        available_parsers = 'Parsers'
    if package_display_area_value_new != package_display_area_value:
        language_list = [language]
        parser_menu_var.set(parsers[0])
        m = parser_menu["menu"]
        m.delete(0, "end")
        for s in parsers:
            s=s.lstrip() # remove leading blanks since parsers are separated by ,blank
            m.add_command(label=s, command=lambda value=s: parser_menu_var.set(value))
        parser_lb.config(text=available_parsers)
GUI_util.setup_menu.trace('w', activate_NLP_options)
activate_NLP_options()

if error:
    mb.showwarning(title='Warning',
               message="The config file 'NLP_default_package_language_config.csv' could not be found in the sub-directory 'config' of your main NLP Suite folder.\n\nPlease, setup the default NLP package and language options using the Setup widget at the bottom of this GUI.")

GUI_util.window.mainloop()