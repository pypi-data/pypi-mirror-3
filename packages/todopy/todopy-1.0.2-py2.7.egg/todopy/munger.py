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
import re

class ContextRemover(object):
    """Munger class that removes contexts from output
    
    >>> from model import Model
    >>> m = Model()
    >>> m.extend(["foo @fooctx", "bar @barctx @fooctx", "@fooctx foobar@example.com"])
    >>> list([t.todo for t in ContextRemover(m)])
    ['foo', 'bar', 'foobar@example.com']
    >>> len(ContextRemover(m)) == len(m)
    True
    >>> ContextRemover(m).total() == len(m)
    True
    """
    def __init__(self, model):
        self.model = model

    def __iter__(self):
        class Iter(object):
            def __init__(self, model):
                self.iter = iter(model)
            def __iter__(self):
                return self
            def next(self):
                t = self.iter.next()
                t.todo = re.sub(r'(?<!\w)@\w+', '', t.todo).strip()
                return t
        return Iter(self.model)

    def __len__(self):
        return len(self.model)

    def total(self):
        return self.model.total()


class ProjectRemover(object):
    """Munger class that removes projects from output
    
    >>> from model import Model
    >>> m = Model()
    >>> m.extend(["foo +fooproj", "bar +barproj", "+fooproj foobar 1+x=5"])
    >>> list([t.todo for t in ProjectRemover(m)])
    ['foo', 'bar', 'foobar 1+x=5']
    >>> len(ProjectRemover(m)) == len(m)
    True
    >>> ProjectRemover(m).total() == len(m)
    True
    """
    def __init__(self, model):
        self.model = model

    def __iter__(self):
        class Iter(object):
            def __init__(self, model):
                self.iter = iter(model)
            def __iter__(self):
                return self
            def next(self):
                t = self.iter.next()
                t.todo = re.sub(r'(?<!\w)\+\w+', '', t.todo).strip()
                return t
        return Iter(self.model)

    def __len__(self):
        return len(self.model)

    def total(self):
        return self.model.total()
