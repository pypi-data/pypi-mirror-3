# Copyright (C) 2012 Bob Bowles <bobjohnbowles@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module abstracts the languages that are implemented in the Reversi
package. When a new language translation is available, the .mo file is inserted
in the appropriate sub-directory, indexed by language_REGION tags. This file is
edited to add the language to the languageIds dictionary. The languageIds
defined here are used to pull in the translations at run time.

The entries in the languageIds dictionary are of the form
    {language_REGION: description},
where the description is *in an appropriate language*.

NB: It is therefore important that these text strings are **NOT** translated by
gettext."""

import gettext, os

# this is the list of available translations
languageIds = {'en_GB': 'English',
               'fr_FR': 'Français',
               'zh_CN': '中文',
               } # note these are NOT translated

# the domain for languages
domain = 'Reversi'

# set the locale directory according to installation
# aim: choose C:\Python32\locale for windows
#             /usr/share/locale for Posix
#             ../../locale if neither of the above work (development default)
localedir = os.path.join('..', '..', 'locale') # development location is default
testPath = ''
if os.name == 'nt':
    testPath = os.path.join('C:', 'Python32', 'locale') # TODO needs fixing
elif os.name == 'posix':
    testPath = os.path.join('/', 'usr', 'share', 'locale')

# a crude test of the language directory tree.
if os.path.exists(os.path.join(testPath,
                               'en_GB',
                               'LC_MESSAGES',
                               'Reversi.mo')): localedir = testPath
#print('Selected locale directory is ' + localedir)

# make the translations
languages = dict.fromkeys(languageIds)
for language in languageIds.keys():
    languages[language] = gettext.translation(domain,
                                              localedir=localedir,
                                              languages=[language],
                                              #fallback=True
                                              )

# set up a default language in case none gets picked
gettext.install(domain, localedir)
