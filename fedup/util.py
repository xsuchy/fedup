# fedup.util - various shared utility functions for fedup
#
# Copyright (C) 2012 Red Hat Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Will Woods <wwoods@redhat.com>

import os
from shutil import rmtree
from subprocess import Popen, PIPE, CalledProcessError
from pipes import quote as shellquote
import logging
log = logging.getLogger('fedup.util')

try:
    from ctypes import cdll, c_bool
    selinux = cdll.LoadLibrary("libselinux.so.1")
    is_selinux_enabled = selinux.is_selinux_enabled
    is_selinux_enabled.restype = c_bool
except (ImportError, AttributeError, OSError):
    is_selinux_enabled = lambda: False

def call_output(cmd, *pargs, **kwargs):
    log.info("exec: `%s`", ' '.join(shellquote(a) for a in cmd))
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, *pargs, **kwargs)
    (out, err) = p.communicate()
    retcode = p.poll()
    return (retcode, out, err)

def call(cmd, *pargs, **kwargs):
    return call_output(cmd, *pargs, **kwargs)[0]

def check_output(cmd, *pargs, **kwargs):
    (retcode, out, err) = call_output(cmd, *pargs, **kwargs)
    if retcode:
        raise CalledProcessError(retcode, cmd, output=out)
    return out

def check_call(cmd, *pargs, **kwargs):
    check_output(cmd, *pargs, **kwargs)
    return 0

def listdir(d):
    for f in os.listdir(d):
        yield os.path.join(d, f)

def mkdir_p(d):
    try:
        os.makedirs(d)
    except OSError as e:
        if e.errno != 17:
            raise

def rm_f(f, rm=os.remove):
    if not os.path.lexists(f):
        return
    try:
        rm(f)
    except (IOError, OSError) as e:
        log.warn("failed to remove %s: %s", f, str(e))

def rm_rf(d):
    rm_f(d, rm=rmtree)
