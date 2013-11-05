pyLEX
=====

A python API wrapper for the SimCity 4 LEX (http://sc4devotion.com/csxlex/).

This is being worked on as a learning project for Python, and a lot of
inspiration, structure and in some instances, blocks of code, have been 
taken from the Python Reddit API Wrapper (https://github.com/praw-dev/praw).

Usage
-------
```
import pyLEX

l = LEX(user_agent='My LEX bot')
recent_plugins = l.get_recent()
for plugin in recent_plugins:
    print plugin
```

.. end_usage

License
-------

All of the code contained here is licensed by
`the GNU GPLv3 <https://github.com/simonwillcock/pyLEX/blob/master/license>`_.

.. end_license