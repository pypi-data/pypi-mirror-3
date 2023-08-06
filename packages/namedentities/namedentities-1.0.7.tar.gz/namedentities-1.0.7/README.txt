
Installation
============

::

    pip install namedentities
        
(You may need to prefix this with "sudo " to authorize installation.)

**NOTA BENE** Code runs successfully under Python 3, but packaging
seemingly doesn't work as yet.

Usage
=====

Python 2::
  
    from namedentities import named_entities
    
    u = u'both em\u2014and&#x2013;dashes&hellip;'
    print named_entities(u)
    
Python 3::

    from namedentities import named_entities
    
    u = 'both em\u2014and&#x2013;dashes&hellip;'
    print(named_entities(u))

    
Credits
=======

This is basically a packaging of Ian Beck's work
(described in http://beckism.com/2009/03/named_entities_python/)

Thank you, Ian!