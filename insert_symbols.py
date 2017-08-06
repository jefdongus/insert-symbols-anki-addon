""" 
Current Status:
- Does not work if field contains tables, lists, etc.
""" 


from aqt import editor
from aqt import utils

from anki.hooks import wrap

import sys
import os

""" 
  Replacement:
----------------------------
Any tags that are not closed get moved to the end.

Before:	<li>aa<u>a:del</u>ta:bbb</li>
After:	<li>aa<u>a[[delta]]</u>bbb</li>

Before:	<li>aaa:del<u>ta:bb</u>b</li>
After:	<li>aaa[[delta]]<u>bb</u>b</li>

Before:	<li>h<u>i:d<b>el<i>t</i>a:asd</b></u></li>
After:	<li>h<u>i[[delta]]<b>asd</b></u></li>

Replacement occurs if the character typed (A) is the last character of a
keyword or (B) is a whitespace character that creates a keyword immediately
preceeding it. 

In scenario A replacement occurs regardless of what character is before the 
keyword, but in scenario B replacement only occurs if the character before the 
keyword is whitespace or part of a formatting tag.

The text to replace could be nested deep inside the DOM. For example, here only
the line containing the list element should be replaced:

<div>
  <table style="font-size: 1em; width: 100%; border-collapse: collapse;">
    <thead>
      <tr>
        <th align="left" style="width: 100%; padding: 5px;border-bottom: 2px solid #00B3FF">aaa</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="text-align: 100; padding: 5px;border-bottom: 1px solid #B0B0B0">
          <ul style="margin-left: 20px; ">
            <li>h<u>i:</u><b><u>de</u><i style="text-decoration: underline; ">l</i><u>t</u>a:asdf</b></li>
          </ul>
        </td>
      </tr>
    </tbody>
  </table>
</div>

"""

def my_setup(self, note, hide=True, focus=False):
	self.is_prev_text = ""
	self.is_keypress = False

	if self.note:
		"""
		Loads Javascript file. Originally did this so that I could hot-reload the JS file, but apparently I couldn't
		get the eval'ed JS to update any variables or any HTML files, so the original plan of doing everything in JS
		didn't work out. Not sure if I'm doing something wrong or just a limitation of the system.
		"""

		cur_dir = os.getcwd()
		idx = cur_dir.find("Anki2")
		if idx > -1:
			cur_dir = cur_dir[ : idx + 5]
		with open(cur_dir + "/addons/insert_symbols/init_script.js", "r") as js_file:
			js = js_file.read()
			self.web.eval(js)

		""" 
		Pretty hacky right now. Checks if last character entered was a whitespace by comparing to keycode of SPACE and
		ENTER, which I'm not sure if is cross-platform.
		"""

		# self.web.eval("""
		# 	function is_OnKeypress(evt) {
		# 		py.run("is_k");
		# 	}

		# 	function is_OnKeyup(evt) {
		# 		if (evt.which == 13 || evt.which == 32) {
		# 			py.run("is_w:"+ currentField.innerHTML);
		# 		} else {
		# 			py.run("is_c:"+ currentField.innerHTML);
		# 		//	py.run("is_u:"+ currentField.innerHTML);
		# 		}
		# 	}

		# 	// Using keyup event b/c that fires after the <div> is updated.
		# 	$(".field").keypress(is_OnKeypress);
		# 	$(".field").keyup(is_OnKeyup);

		# 	/*========== Debugging Code ==========*/

		# 	$("body").append('<div class="debug"></div>');

		# 	function is_WriteToErr(evt) {
		# 		if (String.fromCharCode(evt.charCode) == '`') {
		# 			is_DebugErr($("body").html());
		# 		}
		# 	}

		# 	function is_DebugDiv(str) {
		# 		py.run("debug_div:"+ str);
		# 	}

		# 	function is_DebugErr(str) {
		# 		py.run("debug_err:"+ str);
		# 	}

		# 	//is_DebugErr($("body").html())

		# 	""")

def my_bridge(self, str, _old=None):
	if str.startswith("is_k"):
		self.is_keypress = True
	if str.startswith("is_c:"):
		(_, value) = str.split(":", 1)
		is_check_keyword(self, value, False)
	if str.startswith("is_w:"):
		(_, value) = str.split(":", 1)
		is_check_keyword(self, value, True)
	#if str.startswith("is_u:"):
	#	(_, value) = str.split(":", 1)
	#	is_update(self, value)
	if str.startswith("debug_err"):
		(_, value) = str.split(":", 1)
		sys.stderr.write(value)
	if str.startswith("debug_div"):
		(_, value) = str.split(":", 1)
		self.web.eval('$(".debug").html("%s")' % value)

#def is_update(self, div_text):
#	self.web.eval('$(".debug").html("Ran is_update()")')
#	self.is_prev_text = div_text

# Scans the active <div> for the correct location to call is_match().
def is_check_keyword(self, div_text, is_whitespace):

	# Quick check to make sure that we are only running during keypresses.
	if not self.is_keypress:
		self.is_prev_text = div_text
		return
	self.is_keypress = False

	# Looks for where the latest character was inserted by comparing the old and new Strings backwards, because it
	# looked painful to get cursor position from the <div> if it contained child nodes. TODO parse forward instead
	# so that we can parse HTML tags & special characters.

	i = len(div_text) - 1
	j = len(self.is_prev_text) - 1

	while (i > 0 and j >= 0):
		if div_text[i] != self.is_prev_text[j]:
			if is_whitespace:
				#sys.stderr.write('Calling is_match() with text:%s pos:%i' % (self.is_prev_text, j))

				# If whitespace was inserted, then self.is_prev_text[j] should point to charater before whitespace 
				# at point of difference. Haven't thought about whether this fails to edge cases or not yet.
				(matched, new_text) = is_match(self, self.is_prev_text, j, is_MATCH_TBL)
			else:
				(matched, new_text) = is_match(self, div_text, i, is_MATCH_TBL)

			if matched:
				#self.web.eval('$(".debug").html("Matched:%s")' % new_text)
				self.web.eval("""
					document.execCommand("selectAll", false, null);
					document.execCommand("insertHTML", false, "%s");
					""" % new_text)
				self.is_prev_text = new_text
				return
			else:
				#self.web.eval('$(".debug").html("Ran check_keyword() but no match")')
				break
		i -= 1
		j -= 1

	self.is_prev_text = div_text

# Given the position where the last character was inserted, attempt to replace the prior text with a replacement
# from the MATCHES list.
# MATCHES is a list of tuples of the format (TEXT_TO_REPLACE, REPLACEMENT) with the assumption that the text
# is already escaped for HTML.
def is_match(self, div_text, pos, matches):
	for (key, val) in matches:
		i = pos
		j = len(key) - 1
		while (i >= 0 and j >= 0):
			if div_text[i] != key[j]:
				#sys.stderr.write('Ending early with i=%i j=%i' % (i, j))
				break 
			i -= 1
			j -= 1

		# At end of either div_text or key. If key is still remaining, then there was no match.
		if j >= 0:
			#sys.stderr.write('Ending early with i=%i j=%i' % (i, j))
			continue
		else:
			return (True, div_text[:i + 1] + val + div_text[pos + 1:])
	return (False, None)


editor.Editor.setNote = wrap(editor.Editor.setNote, my_setup, 'after')
editor.Editor.bridge = wrap(editor.Editor.bridge, my_bridge, 'before')


# Strings to replace.
is_MATCH_TBL = [
	# Arrows
	('-&gt;', 		'\u2192'),
	(':N:', 		'\u2191'),
	(':S:', 		'\u2193'),
	(':E:', 		'\u2192'),
	(':W:', 		'\u2190'),

	# Math symbols
	(':geq:', 		'\u2265'),
	(':leq:', 		'\u2264'),
	('&gt;&gt;', 	'\u226B'),
	('&lt;&lt;',	'\u2264'),
	(':pm:', 		'\u00B1'),
	(':infty:', 	'\u221E'),
	(':approx:',	'\u2248'),
	(':neq:', 		'\u2260'),

	# Fractions
	(':1/2:', 		'\u00BD'),
	(':1/3:',		'\u2153'),
	(':2/3:', 		'\u2154'),
	(':1/4:',		'\u00BC'),
	(':3/4:', 		'\u00BE'),

	# Greek letters (lowercase)
	(':alpha:', 	'\u03B1'),
	(':beta:', 		'\u03B2'),
	(':gamma:', 	'\u03B3'),
	(':delta:', 	'\u03B4'),
	(':episilon:', 	'\u03B5'),
	(':zeta:', 		'\u03B6'),
	(':eta:', 		'\u03B7'),
	(':theta:', 	'\u03B8'),
	(':iota:', 		'\u03B9'),
	(':kappa:', 	'\u03BA'),
	(':lambda:', 	'\u03BB'),
	(':mu:', 		'\u03BC'),
	(':nu:', 		'\u03BD'),
	(':xi:', 		'\u03BE'),
	(':omicron:', 	'\u03BF'),
	(':pi:', 		'\u03C0'),
	(':rho:', 		'\u03C1'),
	(':sigma:', 	'\u03C3'),
	(':tau:', 		'\u03C4'),
	(':upsilon:', 	'\u03C5'),
	(':phi:', 		'\u03C6'),
	(':chi:', 		'\u03C7'),
	(':psi:', 		'\u03C8'),
	(':omega:', 	'\u03C9'),

	# Greek letters (uppercase)
	(':Alpha:', 	'\u0391'),
	(':Beta:', 		'\u0392'),
	(':Gamma:', 	'\u0393'),
	(':Delta:', 	'\u0394'),
	(':Episilon:', 	'\u0395'),
	(':Zeta:', 		'\u0396'),
	(':Eta:', 		'\u0397'),
	(':Theta:', 	'\u0398'),
	(':Iota:', 		'\u0399'),
	(':Kappa:', 	'\u039A'),
	(':Lambda:', 	'\u039B'),
	(':Mu:', 		'\u039C'),
	(':Nu:', 		'\u039D'),
	(':Xi:', 		'\u039E'),
	(':Omicron:', 	'\u039F'),
	(':Pi:', 		'\u03A0'),
	(':Rho:', 		'\u03A1'),
	(':Sigma:', 	'\u03A3'),
	(':Tau:', 		'\u03A4'),
	(':Upsilon:', 	'\u03A5'),
	(':Phi:', 		'\u03A6'),
	(':Chi:', 		'\u03A7'),
	(':Psi:', 		'\u03A8'),
	(':Omega:', 	'\u03A9')
]
