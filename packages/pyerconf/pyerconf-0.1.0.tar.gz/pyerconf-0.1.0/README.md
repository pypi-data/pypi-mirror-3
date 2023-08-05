PyerConf
======

[PyerConf](http://devedge.bour.cc/wiki/PyerConf) is a pythonic hierarchical configuration parser.


###Requirements:
* [SimpleParse](http://pypi.python.org/pypi/SimpleParse)

###Compatility:
*	any python version

###Installation
	easy_install pyerconf

or

	wget http://devedge.bour.cc/resources/pyerconf/src/pyerconf.latest.tar.gz
	tar xvf pyerconf.latest.tar.gz
	cd pyerconf-* && ./setup.py install

Example
-------

	>>> import pyerconf
	>>> cfg = pyerconf.Config('./sample.cfg')
	>>> print cfg.strval
	this is a string
	>>> print cfg.orgchart.boss
	Mr Goldmine
	>>> print cfg.orgchart.head_office
	{'VP': 'Miz dho', 'CTO': 'John Bugs'}

	>>> print cfg.foobar
	AttributeError

About
-----

*PyerConf* is licensed under GNU GPL v3.<br/>
It is developped by Guillaume Bour &lt;guillaume@bour.cc&gt;
