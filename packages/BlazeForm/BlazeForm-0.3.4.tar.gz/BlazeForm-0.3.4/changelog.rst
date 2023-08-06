Change Log
----------

0.3.4 released 2012-07-05
=========================

* form now has all_errors() method which returns form and field errors as (list,
    dict) tuple (respectively).
* update the way file uploads are checked for being sent.  Previously, we were
testing for the filename header to be None, but Werkzeug is sending it over as
an empty string in the FileStorage object now.  Could theoretically result in
behavior change, but only in narrow edge cases.

0.3.3 released 2011-11-16
=========================

* TextAreaElement now uses maxlength kwarg

0.3.2 released 2011-06-11
=========================

* fix broken distribution of 0.3.1

0.3.1 released 2011-06-11
=========================

* fixed bug in radio button rendering after validation error
