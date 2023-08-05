==========
Overview
==========

Checkit is a tool for validating executable specifications 
created with BDD style grammar. It aims to:

1. Enable you to define BDD style specifications in python code.
2. Provide a simple tool for validating your specifications.

To this end, checkit uses `nose <http://somethingaboutorange.com/mrl/projects/nose>`_ 
to enable you to create specs with keywords like "Describe", "it" and "should". 
It also provides a "**checkit**" command that seemlessly integrates with nose 
(specifically the nosetests command) to validate your software against the specs 
you created.


Features
==========

* encourages "specification by example" by promoting the use of appropriate grammar
* uses customizable options to make nose discover and run your specs


Requirements
=============

* `nose <http://somethingaboutorange.com/mrl/projects/nose>`_ 

The requirements for using checkit are auto-installed if you 
use pip or easy_install.


Installation
==============

The easiest way to install checkit is with ``pip install checkit`` 
or with ``easy_install checkit``. Alternatively, you may 
`download <http://pypi.python.org/pypi/checkit>`_ the 
source package from PyPI, extract it and install it using 
``python setup.py install``.


What you get
=============

When you install the package, the only tangible thing you get is the 
"**checkit**" command. It uses nose to discover and execute specifications 
using flexible matching rules so that you are not limited to using distracting 
unittest (test focused) constructs like "def test..." or name your files 
"test...py".

The other non-tangible benefit you get is that you no longer have to 
subject yourself to the unnecessary cruft needed for unittest 
test cases. You can now create a spec like this::

    > cat coolthingy_specs.py
    class DescribeCoolThingy(object):
        
        def it_is_cool(self):
            pass
            
        def it_should_not_heat_up(self):
            pass

Or even::

    > cat awesomedude_specs.py
    class AwesomeDudeSpecs():
    
        def should_smile_often(self):
            pass

Finally, when you want to validate your software against the specs, 
simply run the command "checkit" in your project directory like so::

    > checkit
    ...
    ----------------------------------------------------------------------
    Ran 3 tests in 0.006s

    OK

Since `checkit` is merely a wrapper around `nose`, it accepts all the parameters that 
`nose` tipically takes. For more information, run::

    > checkit --help


Feedback
==========

I welcome any questions or feedback about bugs and suggestions on how to 
improve checkit. Let me know what you think about checkit. I am on twitter 
`@RudyLattae <http://twitter.com/RudyLattae>`_ . I appreciate constructive 
criticsms or high fives :)

Do you have suggestions for improvement? Then please create an 
`issue <https://bitbucket.org/rudylattae/checkit/issues>`_ with details 
of what you would like to see. I'll take a look at it and work with you to either kill 
the idea or implement it.
