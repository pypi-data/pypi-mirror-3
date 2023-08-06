Introduction
============

haufe.hrs.configuration provides a central configuration service for
Zope-based application with a pseudo-hierarchical configuration mechanism.

Features
========

* configurations based on INI files

* configurations are pseudo-hierarchical (section names can be
  dotted-names  (like ``cms.somepath``, ``foo.bat.something.else``)

* all valid configuration options are defined through a model
  (an INI-style file defining sections, their options, their types and default
  values). The model is used for performing type-checking and providing defaults

* models and configuration files can be loaded all-in-one or incremental
  into the configuration service

* optional supervision of changes to the configuration file (a change
  of a configuration file can trigger an immediate reload of the configuration)

* very simple API

* ZCML directives for defining the location of models and configuration files

* integrates easily with Zope 2 and Zope 3

* can be used outside Zope (pure Python applications) - the package has only 
  a minor number of dependencies to other zope.* packages

* good test coverage


Defining a model
================

A model definition may look like this::

    [cms]
    HRSCheckoutPath=string,default=42
    HRSCheckoutURL=string
    HRSImportPath=string
    HRSImportClientPath=string
    HRSPreviewPath=string
    HRSPreviewClientPath=string
    CvtSGMLtoRtfPath=string
    CvtSGMLtoRtfMaxWait=int
    ADB2StartURLbase=string
    ADB2Version=int
    ToolboxStartURLbase=string
    NormenDBStartURLbase=string
    VADBStartURLbase=string
    LauflistenStartURL=string
    HRS2UIStartURLbase=string
    MedienStartURLbase=string

    [cms.db]
    datenbank1=
    datenbank2=
    datenbank3= 

You see that the syntax is pretty simple. The syntax is always::

    <optionname> = <type>, [default=<default-value>]

<optionname> is mandatory. <type> defaults to 'string' and can be omitted
(other types are 'int', 'list', 'float', 'complex' or 'bool').  The '=' is mandatory
(otherwise Python's configuration parser will spit out an error.  An optional
default can be defined (otherwise None will be used). Hint: a string as default value
must use quotes.


A related configuration file may look like this::

    [cms]
    HRSCheckout = /foo/bar
    adb2version = 44
    hrscheckoutpath = 12
    port = 22


    [toolbox]
    partition_id = Toolbox
    nginx_baseurl = http://weiss.nix.de/

For values of the configuration are accessible through dotted-names like::

   cms.ADB2Version
   cms.HRSCheckoutURL
   cms.db.datenbank 

Usage
=====

From Python::

    from haufe.hrs.configuration import ConfigurationService

    service = ConfigurationService(watch=True)
    service.registerModel('example/model')
    service.loadConfiguration('example/sample_config/all-in-one.ini')
    print service.getConfiguration()
    print service.get('cms.ADB2Version')
    print service.get('datenbank', domain='cms.db')


ZCML integration
================           

``haufe.hrs.configuration`` provides two ZCML directives ``haufe:registerModel``
and ``haufe:registerConfiguration``::

    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:haufe="http://namespaces.haufe.de/haufe">

      <haufe:registerModel
          model="haufe/hrs/configuration/tests/model"
      />

      <haufe:registerConfiguration
          configuration="haufe/hrs/configuration/tests/example-config.ini"
      />

    </configure>

The path names for ``model`` and ``configuration`` can be absolute paths, paths
relative to the location of the current ZCML file or a path string containing
environment variables (will be substituted automatically).

Credits
=======
The implementation is based on the ``cfgparse`` module by Dann Gass


Author
======
``haufe.hrs.configuration`` was written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
and ZOPYX Ltd. & Co. KG, Tuebingen, Germany.


License
=======
``haufe.hrs.configuration`` is licensed under the Zope Public License 2.1.
See the included ZPL.txt file.


Contact
-------

| ZOPYX Ltd. & Co. KG
| Andreas Jung
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com

