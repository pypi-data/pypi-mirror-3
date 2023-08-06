===========
Plastclient
===========

Plastclient is an API wrapper for Plast_.

Authentication
==============

OAuth
-----
All updates to Plast require OAuth 2 authentication. Plast is in active development, and key/secret pairs are granted individually. 
Please contact njb@smartm.no if you are interested in using Plast.

AccessKeys
----------
Applications using Plast may request additional accesskeys using the AccessKey API. These keys are used to set and assert ownership
to objects created in Plast, and may be devided to individual users, groups of users or however the application sees fit.

Installation
============

    $ pip install plastclient

Usage
=====

    from plastclient import PlastClient

    pc = PlastClient('http://plast.host.com', <oauth_key>, <oauth_secret>)
    
    states = pc.State.search('relativity')


General principles
==================
* All communication is REST.
* All states & statesets have a public view.
* All data returned as dictionaries.
* OAuth key/secret & plast_accesskey is required for all updates.

AccessKey
=========
Use to interact with accesskeys.

all
---
Get a list of all accesskeys belonging to your application.

    pc.AccessKey.all()
    
add
---
Create a new accesskey for you application.

    pc.AccessKey.add()
    
update
------
Update an accesskey's linked sets.

    pc.AccessKey.update(<accesskey>, statesets=[<set_uuid1>,<set_uuid2>], add=[<set_uuid3>], remove=[<set_uuid0>])

If *statesets* is provided *add* and *remove* are ignored.

* statesets - replaces existing sets with provided sets
* add - appends listed sets
* remove - removes listed sets

State
=====
Use to interact with states in Plast.

get
---

    pc.State.get(<state_uuid>)


get_list
--------
    
    pc.State.get_list([<state_uuid1>,<state_uuid2>])


add
----

    pc.State.add('state name', <accesskey>)

update
------

    pc.State.update(<state_uuid>, <accesskey>, name='updated name', desription='updated description')

search
------

    pc.State.search('searchtext')
    
StateSet
========
Use to interact with statesets.

get
---

    pc.StateSet.get(<set_uuid>)

add
---

    pc.StateSet.add('name of set', <accesskey>)
    
update
------

    pc.StateSet.update(<set_uuid>, <accesskey>, name='updated name', description='updated description', states=[<state_uuid1>,<state_uuid2>], disabled=False)

states
------
Get a fully detailed list of all states linked to this set.

    pc.StateSet.states(<set_uuid>)


Exception handling
==================
Controlled exceptions might occur - *permissions denied*, *not found*, etc. These exceptions are cought and re-thrown as a **PlastError**.

    try:
        pc.State.get(<non_existing_uuid>)
    except PlastError, e:
        print e

PlastError har 3 properties:

* url  - the failed url.
* code - the returned http statuscode.
* msg  - a message.


Changelog
=========

0.1.7
-----
* Added support for Place API
* Removed annoying print statement from State.update

0.1.6
-----
* Improved Stateset update protection and errorhandling.

0.1.5
-----
* Updated StateSet.update ignoring None values.

0.1.4dev
--------
* First public release of plastclient
* Still under active development

enjoy.

.. _Plast: http://www.smartm.no/
