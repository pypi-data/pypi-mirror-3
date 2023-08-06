'''
===============
Data Structures
===============

The main objects in Py-Tutor are represented as nested structures that resemble 
and can be easily serialized as JSON. This design allows easy communication 
between subsystems, which can be different modules in a program, or different 
subprocesses in a local machine or in remote servers. JSON is a safe and 
interoperable format for which implementations exists for many different 
languages. We use the :mod:`pyson` library to provide most of functionality to 
manipulate and (de)serialize these data structures.

This section describes how these data structures are defined and used to 
represent different objects across the Py-Tutor system. They are formally 
defined using a **schema** specified in Python code using the :mod:`pyson` 
library. 

Messages
========

.. automodule:: tutor.schemas.messages

Basic objects
=============

.. automodule:: tutor.schemas.objects
'''
