
jtmpl
================================================================================

jtmpl is a commandline app for quickly running jsontemplate. This lets you generate templated files without having to code, making jsontemplate more useful for build processes, system administration, and static HTML page generation.

jtmpl happens to be implemented in python, but you don't need to be using python in your project to take advantage of it.


For more about JSON Template, see:

http://json-template.googlecode.com



An Example
================================================================================

jtmpl is useful for when you have some type of form you want filled out with a data file that you already have. The data should be in JSON or easily convertable to JSON.

The example included with json-template is a long story about a music app, but let's make a quick address book and a letter we want to send to all the people in the address book::

	{.repeated section names}
	
	Dear {@},
	
	I think you are really awesome.
	
	Sincerely,
	{my_name}
	
	--------------------------- CUT HERE --------------------------------
	
	{.end}

That was the "template file". Here's the JSON data::

	{
		"my_name": "Poppy",
		"names": [
			"Meghan",
			"Andy",
			"Josh",
			"Eden",
			"Andy",
			"Mateusz"
		]
	}

Put the template into letter.jtmpl.txt and the json data into names.json and run it like this::

	$ jtmpl names.json letter.jtmpl.txt

you will get::

	Dear Meghan,
	
	I think you are really awesome.
	
	Sincerely,
	Poppy
	
	--------------------------- CUT HERE --------------------------------
	
	
	Dear Andy,
	
	I think you are really awesome.
	
	Sincerely,
	Poppy
	
	--------------------------- CUT HERE --------------------------------
	
	
	Dear Josh,
	
	I think you are really awesome.
	
	Sincerely,
	Poppy
	
	--------------------------- CUT HERE --------------------------------
	
	
	Dear Andy,
	
	I think you are really awesome.
	
	Sincerely,
	Poppy
	
	--------------------------- CUT HERE --------------------------------
	
	
	Dear Eden,
	
	I think you are really awesome.
	
	Sincerely,
	Poppy
	
	--------------------------- CUT HERE --------------------------------
	
	
	Dear Mateusz,
	
	I think you are really awesome.
	
	Sincerely,
	Poppy
	
	--------------------------- CUT HERE --------------------------------


See the JSON Template documentation if you want to do anything more complicated.

http://json-template.googlecode.com



