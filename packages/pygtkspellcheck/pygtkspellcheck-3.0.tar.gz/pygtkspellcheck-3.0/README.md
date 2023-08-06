# About
PyGtkSpellCheck is a spellchecking library written in pure Python for Gtk based 
on [Enchant](http://www.abisource.com/projects/enchant/).
It supports both Gtk's Python bindings,
[PyGObject](https://live.gnome.org/PyGObject/) and
[PyGtk](http://www.pygtk.org/), and for both Python 
2 and 3 with automatic switching and binding autodetection. For automatic 
translation of the user interface it can use GEdit's translation files.

# Features
* Localized names of the available languages.
* Supports word, line and multiline ignore regexes.
* Support for ignore custom tags on Gtk's TextBuffer.
* Enable and disable of spellchecking with preferences memory.
* Support for hotswap of Gtk's TextBuffers.
* PyGObject and PyGtk compatible with automatic detection.
* Python 2 and 3 support.
* As Enchant, support for Hunspell (LibreOffice) and Aspell (GNU) dictionaries.

# Documentation
You can find the documentation at http://pygtkspellcheck.readthedocs.org/ .

# Homepage
You can find the project page at http://koehlma.github.com/projects/pygtkspellcheck.html .

# License 
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
