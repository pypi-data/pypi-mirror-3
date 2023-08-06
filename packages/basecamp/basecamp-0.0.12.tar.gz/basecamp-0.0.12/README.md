Basecamp Python Client
======================

Description
-----------
This module provides an (almost) complete wrapper around the Basecamp API
(http://developer.37signals.com/basecamp/). It is written in Python and 
based upon the excellent ElementTree package 
(http://effbot.org/zone/element-index.htm). 

Licended under the MIT License

Usage
-----
<pre>
# Import ElementTree and the Basecamp module.
import elementtree.ElementTree as ET
from basecamp import Basecamp

bc = Basecamp('https://example.basecamphq.com', 'API_KEY')

# Fetch one todo list from its ID
xml = bc.todo_list(14499317)
items = ET.fromstring(xml).findall('todo-items/todo-item')

# Let's use the ElementTree API to access data via path expressions:
for item in items:
    print item.find("content").text
</pre>

Original Code
-------------
This code is built from the code of Quentin Pleplé (http://qpleple.com/) forked from github at (https://github.com/qpleple/basecamp-python-client) 

Which code is built from the code of Jochen Kupperschmidt <webmaster@nwsnet.de> (see http://homework.nwsnet.de/products/3cd4) under the MIT Licence.

And added some suggestions from Greg Allard (see http://codespatter.com/2009/04/01/getting-basecamp-api-working-with-python).
