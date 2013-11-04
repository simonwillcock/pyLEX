pyLEX
=====

A python API wrapper for the SimCity 4 LEX (http://sc4devotion.com/csxlex/).

Usage:
```
import pyLEX

l = LEX(user_agent='My LEX bot')
recent_plugins = l.get_recent()
for plugin in recent_plugins:
    print plugin
```
