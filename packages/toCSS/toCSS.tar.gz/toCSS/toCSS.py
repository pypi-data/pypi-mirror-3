"""
- toCSS
- This module provides a function that converts a {dict}
- into valid and formatted CSS code presented by a string.
- In addition, toCSS supports extended syntax including nested rules
- and minification for color notation:
-   RGB notation into a HEX triplet
-   Reducing the 6-digit HEX triplet up to 3-digit
- @author: Alexander Guinness <monolithed@gmail.com>
- @param {data} dict
- @param {minify} bool
- @return {string} string
- @import re
- @version: 1.0
- @license MIT
- @date: Fri Jan 06 02:00:00 2012
"""

__all__ = ["toCSS"]

import re

class main:
	def __init__(self, value):
		self.parse(value)

	data = {}

	def parse(self, data, rule = []):
		"""
		- This function takes a {dict} and recursively bypasses branches.
		- Keys are collected in the 'CSS-rules' and properties are stored in a list.
		-
		- Original dict:
		- 'a' : {
		- 	'b' : {
		- 		'property': 'value',
				...
		- 	}
		- }
		-
		- Output dict:
		- 'a b' : ['property: value;', ...]
		-
		- @param {data} dict
		- @param {rule} list
		- @return The result is stored in the {data} dict
		"""

		if rule:
			self.data[rule] = []

		for key, value in data.items():
			if hasattr(value, 'items'):
				self.parse(value, '%s%s ' % (rule or '', key))
			else:
				self.data[rule].append('\t%s: %s;\n' % (key, self.format_colors(value)))

	def format_colors(self, color):
		"""
		- This function is responsible for minimizing the CSS colors
		- rgb (255, 255, 255) -> #FFFFFF - > #FFF
		- @param {color} str
		- @return {string} str
		"""

		def to_short_hex(text):
			"""
			- Reduces the 6-digit HEX triplet up to 3-digit
			- #110011 -> #101
			- @param {text} str
			- @return {string} str
			"""
			return ''.join(
				'#' + i[1::2] for i in re.findall(r'#[\da-fA-F]{6}\b', text) if i[1::2] == i[2::2]
			) or text

		def rgb_to_hex(text):
			"""
			- Convert RGB notation into a HEX triplet
			- rgb (255, 255, 255) -> #FFFFFF
			- @param {text} str
			- @return {string} str
			"""
			return re.sub('rgb\s*\({0},{0},{0}\)'.format('\s*(\d{1,3})\s*'), (
				lambda match : '#%s' % ''.join('%02X' % int(i) for i in match.groups())
			), text)

		return to_short_hex(rgb_to_hex(color))

	def minify(self, text):
		"""
		- Minification
		- Original string:
		- a {
		-	property: value;
		- }
		-
		- Output string:
		- a { property: value; }
		-
		- @param {text} str
		- @return {string} str
		"""
		return re.sub(r'[\n\t]|\s{2,}', ' ', text)

	def build(self, rule, minify):
		"""
		- The final conversion of the {dict} into a string
		- Original dict:
		- 'a b' : ['property: value;', ...]
		-
		- Output string:
		- a b {
		-	property: value;
		-   ...
		- }
		-
		- @param {color} dict
		- @param {minify} str
		- @return {string} str
		"""
		for key, value in sorted(self.data.items()):
			if key: rule.extend([key, '{\n', ''.join(value), '}\n\n'])

		rule = ''.join(rule)

		return minify and self.minify(rule) or rule

def toCSS(value, minify = 0):
	return main(value).build([], minify)
