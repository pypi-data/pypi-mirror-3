# toCSS

This module provides a function that converts a {dict} into valid and formatted CSS code presented by a string. <br />
The resulting string can be added to an existing file. <br />
In addition, toCSS supports:

* Extended syntax including nested rules
* Mminification for color notation:
	* RGB notation into a HEX triplet.
	* Reducing the 6-digit HEX triplet up to 3-digit

##Synopsis
	string toCSS (dict object [, bool minify = False])

##Installation

*1. Install using [Setuptools] (http://pypi.python.org/pypi/setuptools):*

Download the module from: http://pypi.python.org/pypi/toCSS/

	# python setup.py install

Or run using [easy_install] (http://packages.python.org/distribute/easy_install.html):

	# easy_install toCSS

*Include:*

	from toCSS import *

NOTE: If you have not installed [setuptools] (http://pypi.python.org/pypi/setuptools) you should read about [Distribute] (http://packages.python.org/distribute/).

*Distribute installation:*

	curl -O http://python-distribute.org/distribute_setup.py
	python distribute_setup.py
	easy_install pip

*2. Install using the compilation:*
Create a *.py* file and include:

	from toCSS import *

Then you will get a file named *print_r.pyc* and place the one in your installation/working directory

## Use
*For example you could use the following code:*

	from toCSS import *

	with open('file.css', 'a', encoding='utf-8') as file:
		file.write(toCSS({
			'html': {
				'background': 'red',
				'body': {
					'color' : 'rgb(255, 255, 255)',
					'div > p': {
						'color': 'green',
						'border': '#000008'
					}
				}
			},
			'input' : {
				'border' : '1px solid #110011'
			}
		}))

*Result:*

	#file.css:

	html {
		background: red;
	}

	html body {
		color: #FFF;
	}

	html body div > p {
		color: green;
		border: #000008;
	}

	input {
		border: #101;
	}


* License
    The toCSS module is licensed under the MIT (MIT_LICENSE.txt) license.

* Copyright (c) 2011 [Alexander Guinness] (https://github.com/monolithed)
