# jinja-builder
#
# a simple jinja2 based JinjaBuilder class for scons
#
# Copyright (C) 2011 Stefan Zimmermann <zimmermann.code@googlemail.com>
#
# jinja-builder is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jinja-builder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with jinja-builder.  If not, see <http://www.gnu.org/licenses/>.

import jinja2

from SCons.Builder import BuilderBase
from SCons.Action import Action

__all__ = 'JinjaBuilder',

class JinjaBuilder(BuilderBase):
  def __init__(self, jinja_loader, jinja_context = {}):
    BuilderBase.__init__(
      self,
      action = Action(self.__action),
      src_suffix = '.jinja',
      suffix = '',
      )

    self.__jinja_env = jinja2.Environment(loader = jinja_loader)
    self.__context = jinja_context

  def __action(self, target, source, env):
    context = dict(self.__context)
    try: context.update(env['JINJACONTEXT'])
    except KeyError: pass

    open(str(target[0]), 'w').write(
      self.__jinja_env.from_string(open(str(source[0])).read())
      .render(context).encode())
