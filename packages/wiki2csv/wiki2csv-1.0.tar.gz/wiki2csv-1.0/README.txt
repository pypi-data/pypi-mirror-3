README wiki2csv
===============

Copyright © 2012 Jan Kanis

This program is licenced under terms of the GNU General Public Licence as published by the Free Software Foundataion,  either version 3 of the licence or (at your option) any later version. This program is distributed without any warranty whatsoever. 


Purpose
-------

This program was designed to help edit large tables on wikipedia in the wikitable format. It works by converting the wikitable syntax to comma separated value syntax, that can be edited with Excel or LibreOffice. The result can then be transformed back to wikitable syntax. The program tries to preserve the wikitable formatting and metadata as good as is practically possible. 

The wikitable format is documented at http://en.wikipedia.org/wiki/Help:Wikitable. 


Requirements
------------

wiki2csv requires Python 2.7, available at http://www.python.org. The core conversion routines will probably also work on older Python versions, but wiki2csv uses the argparse library to parse command line arguments, that is only available since Python 2.7. 


Usage
-----

wiki2csv was designed to be used as follows:

1) Be sure wiki2csv is installed somewhere where you can find it, and als make sure that the right version of Python is available on your system. Running "python wiki2csv.py -h" should produce the program's help output. 
2) Copy the wikitable from the edit view on wikipedia into a new file on your computer. The wikitable is everything starting from '{|' up to and including the '|}'. Be sure to save this into a text file: on Windows use Notepad, or if you use Word be sure to save the file as 'plain text' and not as a .doc file. On Linux you could use for example Gedit. For these instructions I will assume you named your file "table.wiki". 
3) Open a command window and move to the directory where you saved your file. 
4) Run "python wiki2csv.py table.wiki table.csv". (Or change table.wiki to the location of your file, and table.csv to the location of your file with the extension changed to .csv)
5) Start Excel or LibreOffice Calc and open the newly created file table.csv. 
6) Excel/LibreOffice will come up with a dialogue asking how it should read the file. Choose 'separated by' and check 'comma', and make sure all other possible separators are unchecked. Also make sure that 'merge delimiters' is unckecked and 'text delimiter' is set to the double quote (") character. Any other options should probably be disabled. 
7) You should now be able to edit the table in Excel/LibreOffice. As you can see, all formatting directives are preserved as text rather than by formatting the content of the cells in the editor. 
8) When you are done editing, save the file under the same name. 
9) In the command window, run "python wiki2csv.py --towiki table.csv table.wiki". This will overwrite 'table.wiki' with the changes you've made. 
10) Reload or reopen table.wiki in the text editor, and copy the changed wikitable to the edit box on the wikipedia website. 


Invocation
----------

wiki2csv will by default convert SOURCE from wikitable format to CSV format. However, if it is invoked as csv2wiki (possibly with an extension) it will default to working in the other direction. The --towiki or --tocsv flags take precedence when supplied. See the output of "wiki2csv.py --help" for further documentation. 


Limitations
-----------

- wiki2csv does not preserve the wiki '||' sytax to place multiple table cells on one source line. When converted back from csv, the cells will appear each on a separate line. This limitation does not hold for header cells. 
- The optional |- before the first table row is not preserved, and neither are multiple |-'s without any data inbetween. A final |- before the end of the table is however produced. 
- wiki2csv does not deal very well with nested tables. 
- Correct wikitable syntax should be handled correctly, but if wiki2csv encounters bad wikitable syntax it can generate garbage output or crash. 


Todo
----

The program is doing what I need it to do, so I have no significant improvements planned (though I do intend to fix bugs if they are found). However, the user interface is not yet very great. It would be very nice if someone was interested in either creating a GUI interface, or implementing this as a web service. (Using Google Appengine that shouldn't be too difficult.) Even better would be a plug-in for LibreOffice to allow it to directly edit wikitables, but that is probably a lot more work. 


Contact & Bugs
--------------

This program is maintained on bitbucket at https://bitbucket.org/JanKanis/wiki2csv. That page also contains a bugtracker. 