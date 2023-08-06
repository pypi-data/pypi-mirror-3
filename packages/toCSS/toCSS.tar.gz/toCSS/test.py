# coding = utf-8

import unittest, logging
from toCSS import *

logging.basicConfig(level = logging.DEBUG)

obj = {
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
		'border' : '1px solid #111111'
	}
}

class test_case(unittest.TestCase):
	def test_file(self):
		with open('file.css', 'a', encoding='utf-8') as file:
			file.write(toCSS(obj))
		print('1. File.css saved!\n')

	def test_string(self):
		print(toCSS(obj))

if __name__ == '__main__':
	unittest.main()
