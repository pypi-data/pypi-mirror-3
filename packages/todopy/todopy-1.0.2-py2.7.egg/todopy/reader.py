# vim: set fileencoding=utf-8 :
# Todo.txt manager in Python
# Copyright (C) 2011 Ilkka Laukkanen <ilkka.s.laukkanen@gmail.com>
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
import os.path
from model import Model
import codecs

class FileReader(object):
    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        class Iter(object):
            def __init__(self, f):
                self.f = f
            def __iter__(self):
                return self
            def next(self):
                try:
                    return self.f.next().strip()
                except StopIteration:
                    self.f.close()
                    raise StopIteration()
        if os.path.exists(self.filename):
            return Iter(codecs.open(self.filename, mode='r', encoding='utf-8'))
        return iter([])
