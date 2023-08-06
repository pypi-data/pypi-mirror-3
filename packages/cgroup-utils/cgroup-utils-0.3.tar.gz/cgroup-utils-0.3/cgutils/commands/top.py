# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# See the COPYING file for license information.
#
# Copyright (c) 2011,2012 peo3 <peo314159265@gmail.com>
#
# This code is based on ui.py of iotop 0.4
# Copyright (c) 2007 Guillaume Chazarain <guichaz@gmail.com>

import sys
import curses
import select
import time
import errno

from cgutils import cgroup
from cgutils import command
from cgutils import host
from cgutils import formatter

class CGTopStats:
    SUBSYSTEMS = ['cpuacct', 'blkio', 'memory']
    FILTERS   = {
        'cpuacct': ['stat'],
        'blkio':   ['io_service_bytes'],
        'memory':  ['usage_in_bytes', 'memsw.usage_in_bytes', 'stat'],
        }

    def __init__(self, options):
        self.options = options

        def collect_by_name(cg, store):
            if cg.name not in store:
                store[cg.name] = []
            store[cg.name].append(cg)
    
        # Collect cgroups by group name (path)
        cgroups = {}
        for name in self.SUBSYSTEMS:
            try:
                root_cgroup = cgroup.scan_cgroups(name, self.FILTERS[name])
                cgroup.walk_cgroups(root_cgroup, collect_by_name, cgroups)
            except EnvironmentError, e:
                print >> sys.stderr, e
        self.cgroups = cgroups
        if options.hide_root:
            del self.cgroups['<root>']

        self.hostcpuinfo = host.CPUInfo()

        self.delta = {}
        self.prev = {}

        self.delta['cpu'] = 0
        self.delta['time'] = 0

    def _get_skelton_stats(self, name, n_procs):
        return {
            'name': name,
            'n_procs': n_procs,
            'cpu.user': 0.0,
            'cpu.system': 0.0,
            'bio.read':  0.0,
            'bio.write': 0.0,
            'mem.total': 0,
            'mem.rss': 0,
            'mem.swap':  0,
            }

    def get_cgroup_stats(self):
        cgroup_stats = []
        for cgroup_list in self.cgroups.values():
            cpu = mem = bio = None
            pids = []
            for _cgroup in cgroup_list:
                subsys_name = _cgroup.subsystem.name
                if subsys_name == 'cpuacct':
                    cpu = _cgroup
                elif subsys_name == 'memory':
                    mem = _cgroup
                elif subsys_name == 'blkio':
                    bio = _cgroup
                _cgroup.update()
                pids += _cgroup.pids

            n_procs = len(set(pids))
            if not self.options.show_empty and n_procs == 0:
                continue
            
            active = False
            stats = self._get_skelton_stats(_cgroup.fullname, n_procs)

            if cpu:
                def percent(delta):
                    return float(delta)*100/self.delta['cpu']
                    
                if self.delta['cpu'] and cpu in self.delta:
                    stats['cpu.user']   = percent(self.delta[cpu]['user'])
                    stats['cpu.system'] = percent(self.delta[cpu]['system'])
                if (stats['cpu.user'] + stats['cpu.system']) > 0.0:
                    active = True

            if bio:
                def byps(delta):
                    return float(delta)/self.delta['time']
                if self.delta['time'] and bio in self.delta:
                    stats['bio.read']  = byps(self.delta[bio]['read'])
                    stats['bio.write'] = byps(self.delta[bio]['write'])
                if (stats['bio.read'] + stats['bio.write']) > 0.0:
                    active = True

            if mem:
                if mem in self.delta:
                    stats['mem.total'] = self.delta[mem]['total']
                    stats['mem.rss']   = self.delta[mem]['rss']
                    if 'swap' in self.delta[mem]:
                        stats['mem.swap']  = self.delta[mem]['swap']
                if [stats['mem.total'], stats['mem.rss'], \
                    stats['mem.swap']].count(0) != 3:
                    active = True
            if not self.options.show_inactive and not active:
                pass
            else:
                cgroup_stats.append(stats)
        return cgroup_stats

    def __conv_blkio_stats(stats):
        n_reads = n_writes = 0L
        for k, v in stats['io_service_bytes'].iteritems():
            if k == 'Total': continue
            n_reads += v['Read']
            n_writes += v['Write']
        return {
            'read': n_reads,
            'write': n_writes,
            }

    def __conv_memory_stats(stats):
        _stats = {}
        _stats['total'] = stats['usage_in_bytes']
        if 'memsw.usage_in_bytes' in stats:
            _stats['swap']  = stats['memsw.usage_in_bytes'] - _stats['total']
        _stats['rss'] = stats['stat']['rss']
        return _stats

    def __conv_cpu_stats(stats):
        return {
            'user': stats['stat']['user'],
            'system': stats['stat']['system'],
            }

    _convert = {
        'memory': __conv_memory_stats,
        'cpuacct': __conv_cpu_stats,
        'blkio': __conv_blkio_stats,
        }

    def __calc_delta(current, previous):
        delta = {}
        for name, value in current.iteritems():
            if isinstance(value, long):
                delta[name] = value - previous[name]
        return delta

    _diff = {
        long: lambda a, b: a - b,
        int: lambda a, b: a - b,
        float: lambda a, b: a - b,
        dict: __calc_delta,
        }

    def _update_delta(self, key, new):
        if key in self.prev:
            self.delta[key] = self._diff[new.__class__](new, self.prev[key])
        self.prev[key] = new

    def update(self):
        # Read stats from cgroups and calculate deltas
        removed_group_names = []
        for name, cgroup_list in self.cgroups.iteritems():
            try:
                for _cgroup in cgroup_list:
                    _cgroup.update()
                    stats = _cgroup.get_stats()
                    if self.options.debug:
                        print(stats)
                    stats = self._convert[_cgroup.subsystem.name](stats)
                    self._update_delta(_cgroup, stats)
            except IOError, e:
                if e.args and e.args[0] == errno.ENOENT:
                    removed_group_names.append(name)

        for name in removed_group_names:
            del self.cgroups[name]

        # Calculate delta of host total CPU usage
        cpu_total_usage = self.hostcpuinfo.get_total_usage()
        self._update_delta('cpu', cpu_total_usage)

        # Calculate delta of time
        self._update_delta('time', time.time())

class CGTopUI:
    SORTING_KEYS = [
        'cpu.user',
        'cpu.system',
        'bio.read',
        'bio.write',
        'mem.total',
        'mem.rss',
        'mem.swap',
        'n_procs',
        'name',
    ]

    def __init__(self, win, cgstats, options):
        self.cgstats = cgstats
        self.options = options

        self.sorting_key = 'cpu.user'
        self.sorting_reverse = True

        self._init_display_params()
        self._init_subsys_title()
        self._init_item_titles()

        if not self.options.batch:
            self.win = win
            self.resize()
            try:
                curses.use_default_colors()
                curses.start_color()
                curses.curs_set(0)
            except curses.error:
                # This call can fail with misconfigured terminals, for example
                # TERM=xterm-color. This is harmless
                pass

    def reverse_sorting(self):
        self.sorting_reverse = not self.sorting_reverse

    def adjust_sorting_key(self, delta):
        now = self.SORTING_KEYS.index(self.sorting_key)
        new = now + delta
        new = max(0, new)
        new = min(len(CGTopUI.SORTING_KEYS) - 1, new)
        self.sorting_key = self.SORTING_KEYS[new]

    def handle_key(self, key):
        def toggle_show_inactive():
            self.options.show_inactive = not self.options.show_inactive

        def toggle_show_zero():
            self.options.show_zero = not self.options.show_zero

        def toggle_show_empty():
            self.options.show_empty = not self.options.show_empty

        key_bindings = {
            ord('q'):
                lambda: sys.exit(0),
            ord('Q'):
                lambda: sys.exit(0),
            ord('r'):
                lambda: self.reverse_sorting(),
            ord('R'):
                lambda: self.reverse_sorting(),
            ord('i'):
                toggle_show_inactive,
            ord('I'):
                toggle_show_inactive,
            ord('z'):
                toggle_show_zero,
            ord('Z'):
                toggle_show_zero,
            ord('e'):
                toggle_show_empty,
            ord('E'):
                toggle_show_empty,
            curses.KEY_LEFT:
                lambda: self.adjust_sorting_key(-1),
            curses.KEY_RIGHT:
                lambda: self.adjust_sorting_key(1),
            curses.KEY_HOME:
                lambda: self.adjust_sorting_key(-len(self.SORTING_KEYS)),
            curses.KEY_END:
                lambda: self.adjust_sorting_key(len(self.SORTING_KEYS)),
        }

        action = key_bindings.get(key, lambda: None)
        action()

    def resize(self):
        self.height, self.width = self.win.getmaxyx()

    def run(self):
        iterations = 0
        poll = select.poll()
        if not self.options.batch:
            poll.register(sys.stdin.fileno(), select.POLLIN|select.POLLPRI)
        while self.options.iterations is None or \
              iterations < self.options.iterations:


            bef = time.time()
            self.cgstats.update()
            aft = time.time()

            debug_msg = "%.1f msec to collect statistics" % ((aft-bef)*1000,)
            self.refresh_display(debug_msg)

            if self.options.iterations is not None:
                iterations += 1
                if iterations >= self.options.iterations:
                    break
            elif iterations == 0:
                iterations = 1

            try:
                events = poll.poll(self.options.delay_seconds * 1000.0)
            except select.error, e:
                if e.args and e.args[0] == errno.EINTR:
                    events = 0
                else:
                    raise
            if not self.options.batch:
                self.resize()
            if events:
                key = self.win.getch()
                self.handle_key(key)

    def _init_display_params(self):
        subsys_sep_size = 2
        self.SUBSYS_SEP = ' '*subsys_sep_size
        item_sep_size   = 1
        self.ITEM_SEP   = ' '*item_sep_size
        self.ITEM_WIDTHS = {
            'cpuacct':   formatter.max_width_cpu,
            'blkio':     formatter.max_width_blkio,
            'memory':    formatter.max_width_memory,
            'cpu.user':  formatter.max_width_cpu,
            'cpu.system':formatter.max_width_cpu,
            'bio.read':  formatter.max_width_blkio,
            'bio.write': formatter.max_width_blkio,
            'mem.total': formatter.max_width_memory,
            'mem.rss':   formatter.max_width_memory,
            'mem.swap':  formatter.max_width_memory,
            'n_procs':   3,
            'name':      0}
        self.N_ITEMS = {'cpuacct':2, 'blkio': 2,
                        'memory': 3, 'n_procs': 1, 'name': 1}

    def _init_subsys_title(self):
        title_list = []
        for name in self.cgstats.SUBSYSTEMS:
            width = self.ITEM_WIDTHS[name]*self.N_ITEMS[name] + self.N_ITEMS[name] - 1
            title = '[' + name.upper().center(width-2) + ']'
            title_list.append(title)
        self.SUBSYS_TITLE = self.SUBSYS_SEP.join(title_list)

    def _init_item_titles(self):
        w = self.ITEM_WIDTHS
        sep = self.ITEM_SEP
        titles = []
        titles.append(sep.join([
            'USR'.center(w['cpu.user']),
            'SYS'.center(w['cpu.system']),
            ]))
        titles.append(sep.join([
            'READ'.center(w['bio.read']),
            'WRITE'.center(w['bio.write']),
            ]))
        titles.append(sep.join([
            'TOTAL'.center(w['mem.total']),
            'RSS'.center(w['mem.rss']),
            'SWAP'.center(w['mem.swap']),
            ]))
        titles.append(sep.join([
            '#'.rjust(w['n_procs']),
            'NAME'.rjust(w['name']),
            ]))
        self.ITEM_TITLE = self.SUBSYS_SEP.join(titles)
        self.KEY2TITLE = {
            'cpu.user':  'USR',
            'cpu.system':'SYS',
            'bio.read':  'READ',
            'bio.write': 'WRITE',
            'mem.total': 'TOTAL',
            'mem.rss':   'RSS',
            'mem.swap':  'SWAP',
            'n_procs':   '#',
            'name':      'NAME',
        }

    def refresh_display(self, debug_msg):
        def format(stats):
            w = self.ITEM_WIDTHS
            sep = self.ITEM_SEP
            strs = []

            item2formatters = {
                'cpu.user':  formatter.percent,
                'cpu.system':formatter.percent,
                'bio.read':  formatter.bytepersec,
                'bio.write': formatter.bytepersec,
                'mem.total': formatter.byte,
                'mem.rss':   formatter.byte,
                'mem.swap':  formatter.byte,
            }

            def to_s(name):
                if not self.options.show_zero and stats[name] == 0:
                    return ' '.rjust(w[name])
                else:
                    return item2formatters[name](stats[name]).rjust(w[name])
            strs.append(sep.join([to_s('cpu.user'), to_s('cpu.system'), ]))
            strs.append(sep.join([to_s('bio.read'), to_s('bio.write'), ]))
            strs.append(sep.join([to_s('mem.total'), to_s('mem.rss'),
                                  to_s('mem.swap'), ]))
            strs.append(sep.join([
                str(stats['n_procs']).rjust(w['n_procs']),
                stats['name']]
                ))
            return self.SUBSYS_SEP.join(strs)

        cgroup_stats = self.cgstats.get_cgroup_stats()
        cgroup_stats.sort(key=lambda st: st[self.sorting_key],
                          reverse=self.sorting_reverse)
        lines = [format(s) for s in  cgroup_stats]

        if self.options.batch:
            print debug_msg
            print self.SUBSYS_TITLE
            print self.ITEM_TITLE
            for l in lines:
                print l
            sys.stdout.flush()
            return

        self.win.erase()
        n_lines = 0
        if self.options.debug:
            self.win.addstr(debug_msg[:self.width])
            n_lines += 1

        self.win.hline(n_lines, 0, ord(' ') | curses.A_REVERSE, self.width)
        n_lines += 1
        attr = curses.A_REVERSE
        self.win.addstr(self.SUBSYS_TITLE, attr)

        self.win.hline(n_lines, 0, ord(' ') | curses.A_REVERSE, self.width)
        n_lines += 1
        status_msg = ''
        key_title = self.KEY2TITLE[self.sorting_key]
        pre, post = self.ITEM_TITLE.split(key_title)
        self.win.addstr(pre, curses.A_REVERSE)
        self.win.addstr(key_title, curses.A_BOLD|curses.A_REVERSE)
        self.win.addstr(post, curses.A_REVERSE)

        rest_lines = self.height - n_lines - int(bool(status_msg))
        num_lines = min(len(lines), rest_lines)
        for i in xrange(num_lines):
            try:
                self.win.insstr(i + n_lines, 0, lines[i].encode('utf-8'))
            except curses.error:
                exc_type, value, traceback = sys.exc_info()
                value = '%s win:%s i:%d line:%s' % \
                        (value, self.win.getmaxyx(), i, lines[i])
                value = str(value).encode('string_escape')
                raise exc_type, value, traceback
        if status_msg:
            self.win.insstr(self.height - 1, 0, status_msg, curses.A_BOLD)
        self.win.refresh()

class Command(command.Command):
    NAME = 'top'

    parser = command.Command.parser
    parser.add_option('-i', '--show-inactive', action='store_true',
                      dest='show_inactive', default=False,
                      help='Show inactive groups [False]')
    parser.add_option('-z', '--show-zero', action='store_true',
                      dest='show_zero', default=False,
                      help='Show zero numbers [False]')
    parser.add_option('-e', '--show-empty', action='store_true',
                      dest='show_empty', default=False,
                      help='Hide empty groups [False]')
    parser.add_option('-r', '--hide-root', action='store_true',
                      dest='hide_root', default=False,
                      help='Hide the root group [False]')
    parser.add_option('-b', '--batch', action='store_true', dest='batch',
                      help='non-interactive mode')
    parser.add_option('-n', '--iter', type='int', dest='iterations',
                      metavar='NUM',
                      help='Number of iterations before ending [infinite]')
    parser.add_option('-d', '--delay', type='float', dest='delay_seconds',
                      help='Delay between iterations [3 second]',
                      metavar='SEC', default=3)


    def _run_window(self, win):
        cgstats = CGTopStats(self.options)
        ui = CGTopUI(win, cgstats, self.options)
        ui.run()

    def run(self, args):
        if self.options.batch:
            return self._run_window(None)
        else:
            return curses.wrapper(self._run_window)

