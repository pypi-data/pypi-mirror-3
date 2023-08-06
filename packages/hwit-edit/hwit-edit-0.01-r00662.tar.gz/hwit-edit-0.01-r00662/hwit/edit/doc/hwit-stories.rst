:Author:    D Haynes
:Date:      June 2009

..  Titling
    ##++::==~~--''``

HWIT Design Reference
=====================

Elevator Pitch
~~~~~~~~~~~~~~

*For practitioners who need to provide statistics to support their work,*
**HWIT** *is Free desktop software that creates, fills out, validates and 
collates questionnaires and forms. Unlike web based solutions,* **HWIT**
*allows the flexibility to build sophisticated reporting processes without
requiring any IT infrastructure.*

User Roles
~~~~~~~~~~

Originator
    The Originator is the person who understands the need for the form.
    He provides many of the questions and he has a good idea of how he
    wants to use the data which comes back. We will assume no particular
    technical skill, but he will be familiar with the business domain.

Administrator
    The Administrator is responsible for the delivery of forms to users,
    and their timely collection. The task of batch processing may also
    fall to the Administrator, but he may have no interest in the
    contents or the outcome of analysis.

User
    The User is the person who fills out the form. We assume that this
    is in connection with some service provided to the User by the
    Originator, or associated party. The User will have basic knowledge
    of desktop PC applications, and perhaps some expectations about how
    a computer program is likely to work.

Developer
    The Developer is an author of the HWIT application.

HWIT User Stories
~~~~~~~~~~~~~~~~~

Originator creates form
""""""""""""""""""""""""

*An originator wants an easy way of specifying and creating a form*

..  sectionauthor:: tundish <tundish@thuswise.co.uk>

Must integrate tolerably with existing office apps. Enable string
substitution of prepopulated fields.

..  topic:: Tests

    #.  Check user-supplied illegal characters

Originator reviews form
"""""""""""""""""""""""

*An originator wants to be sure that certain fields will have to be filled in.*

..  sectionauthor:: tundish <tundish@thuswise.co.uk>

Any field may be mandatory. A group of fields may specify a required number of filled fields.

..  topic:: Tests

    #.  Check all mandatory fields are identified
    #.  Test conflict between empty/mandatory/editable
    #.  Test conflict between group fillany and mandatory

User checks form
""""""""""""""""

*A user wants to check a form to see if it needs any more filling in.*

..  sectionauthor:: tundish <tundish@thuswise.co.uk>

User opens the container and reads a report of

* what's filled in but not valid
* what's not filled in and must be
* what's not filled in but could be
* a date by which it all has to be done

..  topic:: Tests

    #.  Test not valid by type
    #.  Test mandatory and empty
    #.  Test empty and editable
    #.  Test statement of time remaining
    #.  Test expired date
    #.  Launch by drag and drop

User fills form
"""""""""""""""

*The user wants to go to the next part of the form which needs changing.*

..  sectionauthor:: tundish <tundish@thuswise.co.uk>

User selects *next*. Display shows fields and prompts on what"s required.

*   Allow re-editing filled-in mandatory fields
*   Display mandatory fields first?

..  topic:: Tests

    #.  Test mandatory fields come first
    #.  Test behaviour on emptying a mandatory field
    #.  Test behaviour on invalidating a checked field

Originator compares forms
"""""""""""""""""""""""""

*An originator wants an easy way of categorising returned
forms.*

..  sectionauthor:: tundish <tundish@thuswise.co.uk>

*   Provide a method for visualisation

..  topic:: Tests

    #.  Validate against public data set

Originator queries forms
""""""""""""""""""""""""

*The originator wants to query a bunch of forms for common responses*

..  sectionauthor:: tundish <tundish@thuswise.co.uk>

*   Populate a sqlite3 database

..  topic:: Tests

    #.  Validate against public data set

Developer evaluates data-driven fault
"""""""""""""""""""""""""""""""""""""

*A user has a 'problem' form, and the developer wants to
recreate/diagnose the fault.* 

..  sectionauthor:: tundish <tundish@thuswise.co.uk>

*   Categorise errors
*   Perform triage

