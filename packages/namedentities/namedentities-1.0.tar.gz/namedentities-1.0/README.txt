
Installation
============

::

    pip install namedentities
    
Failing that, fall back to the older approach::

    easy_install namedentities
    
(You may need to begin these with "sudo " to authorize installation.)

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