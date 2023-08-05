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

def nop(string, *args, **kwargs):
    return string

class ConsoleFormatter(object):
    def __init__(self, color=False):
        if color:
            import termcolor
            self.formatter = termcolor.colored
            import colorama
            colorama.init()
        else:
            self.formatter = nop

    def color_for(self, priority):
        colors = {
                'A': 'red',
                'B': 'yellow',
                'C': 'magenta',
                'D': 'cyan',
                'E': 'green'
                }
        if priority in colors:
            return colors[priority]
        return 'white'

    def format_todo(self, todo):
        return self.formatter(u"{} {}".format(todo.id, todo.todo), self.color_for(todo.priority()))

    def format(self, model):
        shown = len(model)
        total = model.total()
        formatted = []
        for todo in model:
            formatted.append(self.format_todo(todo))
        suffix = u'' if shown == 1 else u's'
        final = u"\n".join(formatted) + u"""
--
TODO: {} of {} task{} shown
""".format(shown, total, suffix)
        return final.encode('utf-8')
