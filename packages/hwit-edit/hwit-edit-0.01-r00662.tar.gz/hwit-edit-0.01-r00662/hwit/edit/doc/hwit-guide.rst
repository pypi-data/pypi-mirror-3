:Author:    D Haynes
:Date:      June 2009

..  Titling
    ##++::==~~--''``

HWIT User Guide
===============

Opening a form
~~~~~~~~~~~~~~

Follow these instructions if someone has given you a `.hwit` file,
and you want to edit it or fill it out.

Microsoft Windows
    Launch the `HWIT` program from *Start-All Programs-HWIT*. 

All platforms
    Launch the `HWIT` program by running `hwit-edit` from the command line.

Open the `HWIT` form via the *File-Open* command as shown below:

..  image:: _static/hwit_open-200x150.png

The HWIT editor will display the form you chose. In this example we
show the `scout_camp.hwit` form which is included in the `test/ref` folder
of the `hwit-core` distribution. This will allow us to point out certain
features of the program.

Filling out a form
~~~~~~~~~~~~~~~~~~

The graphical window is split from top to bottom. On the left is a
list of each section of the `HWIT` document. When you select one, it is
displayed on the right.

..  image:: _static/hwitpqt_editor-600x336.png

You should prioritise those sections which are highlighted in red.

After filling out the fields, you click the `Apply` button to store
your changes. Sections change to a more subdued colour when complete.

You can save the form at any time via the *File-Save* command. So, if
you haven't fully completed it, you can load it up again later on.

Making your own form
~~~~~~~~~~~~~~~~~~~~

When you've used HWIT a few times, you might think of an idea for a form
of your own. The HWIT program can help you make one.

The method for making your own form proceeds as follows:

1. Make a spreadsheet which describes your form
2. Export the spreadsheet to a tab-separated values (TSV) file
3. Feed the TSV file to HWIT.

Let's go through step by step...

Create the spreadsheet
----------------------

You keep the definitions of your forms as sheets in a spreadsheet
workbook. You can use Microsoft Excel_, OpenOffice Calc_, Gnumeric_,
or any other spreadsheet program.

Each row in your sheet describes a field in your form.

The spreadsheet must have the following columns:

heading
    The HTML heading to precede the group. Every time this value
    changes from row to row, HWIT will generate a new group. A blank
    cell means the field belongs to the current group.
group_id
    The unique id to attach to the current group.
fillany
    A digit which specifies exactly how many fields in this group must
    be completed for the group to be considered valid. May be blank.
name
    The name of the field. In the case of questionnaires, this is the
    text of the question.
editable
    May be TRUE or FALSE. Specifies whether the field is editable by
    the user.
mandatory
    May be TRUE or FALSE. Specifies whether the field must be filled
    by the user.
validator
    May be blank, but if supplied, this is the name of one of the typer
    classes or methods in the module ``hwit.checks``. This specifies
    how the content of the field is to be checked. The table below shows
    which ones to use. See the *Checks* section of the developer
    documentation for a complete explanation.
note
    A note to attach to the current group to explain its context.

..  table:: Validators in use with HWIT

    =========================   =====================   =========================================
    Type of data                Graphical control       Validator
    =========================   =====================   =========================================
    Truth value                 Checkbox/Radio button   hwit.checks.booltyper
    Non-negative whole number   Text box                hwit.checks.numbertyper.isPositiveInteger
    Year, month, day            Text box                hwit.checks.datetimetyper.isISODate
    Hours, minutes, seconds     Text box                hwit.checks.datetimetyper.isISOTime
    Date, time                  Text box                hwit.checks.datetimetyper.isISODateTime
    Email address               Text box                hwit.checks.emailtyper
    Survey vote                 Slider and list box     hwit.checks.scaletyper.isSevenValuedVote
    =========================   =====================   =========================================
   

Export as TSV
-------------

Use your spreadsheet program to export the worksheet as a
tab-separated values (TSV) file.

Your HWIT installation contains example form templates for you to study.
Load the file ``ref/scout_camp.tsv`` or ``ref/gui_test-template.tsv``
into a spreadsheet program to learn more.

Create the form
---------------

Import the template via the *Tools* menu as shown below:

..  image:: _static/hwit_import-200x150.png

You can adjust your template, and keep importing it, until you are happy
with the result. Then *File-Save* as a ``.hwit`` file.

Advanced features
-----------------

The templating mechanism gives you a simple way to create basic forms.
HWIT forms are text files, and very versatile. Advanced users will wish
to consult the *HWIT File Format* documentation and manually edit their
``.hwit`` form to enable specific features.

Analysing returned forms
~~~~~~~~~~~~~~~~~~~~~~~~

Having sent out your forms, and received them back properly completed, you
will want to collate the data. Place all the forms you get back into a
single directory (we call this an *inbox*). Launch the `HWIT` program.

Process the data
----------------

Select *Collate inbox* via the *Tools* menu as shown below:

..  image:: _static/hwit_collate-200x150.png

A dialog box will open, asking you to pick the location of the inbox.
Select the folder which contains all the ``.hwit`` files.

..  image:: _static/hwit_collate_browse-260x260.png

Click *OK*. The program will scan the contents of the inbox. A progress
bar will show you how far it has got:

..  image:: _static/hwit_collate_progress-300x110.png

The output is a *TSV* file which you can load back into your spreadsheet
program. You can use your spreadsheet's macro or filtering features to
present the data in a way which suits your application.

Batch processing
----------------

If you adopt HWIT for use in your regular business, you may decide to
automate your data gathering process. The HWIT library is written with
this in mind.

The wonderful and powerful Python_ language is the perfect choice for your
batch processing applications.

HWIT comes with some example scripts to demonstrate two common cases:

* Ingesting HWIT files into a database
* Visualising a HWIT data set

See the *Tools* section of the Developer Guide for more details.

Frequently Asked Questions
~~~~~~~~~~~~~~~~~~~~~~~~~~

What does HWIT stand for?
-------------------------

HWIT stands for *Here's what I think*.

How do I pronounce HWIT?
------------------------

HWIT is pronounced by English speakers as *Hewitt*.
It's *U8* if you're French. And sometimes *Half-wit* when things go wrong.

What is TSV?
------------

TSV stands for *Tab-Separated Values*. This is a data file format which saves
each row as a line in a text file. Each column value is separated from the
next by a *tab* character.

*TSV* is useful because it is simple. You can view it in any text editor and
load it into any spreadsheet program.

..  _Python: http://www.python.org
..  _pyQt: http://www.riverbankcomputing.co.uk/software/pyqt/intro
..  _Python download page: http://www.python.org/download
..  _Python for Windows: http://www.python.org/ftp/python/2.6.3/python-2.6.3.msi
..  _wxPython for Windows: http://www.wxpython.org/download.php#binaries
..  _HWIT File Format: hwit-spec.html 
..  _Excel: http://office.microsoft.com/excel 
..  _Calc: http://www.openoffice.org/product/calc.html
..  _Gnumeric: http://www.gnome.org/gnumeric
