# -*- coding:utf-8 -*-

import pstats
import sys

def check_stats(func):
        def _func(obj, *a, **k):
                if obj.stats:
                        return func(obj, *a, **k)
        return _func

class Stats(object):
        def __init__(self):
                self.stats = None

        def add_stats(self, *a):
                if self.stats:
                        self.stats.add(*a)
                        self.stats.calc_callees()
                else:
                        self.create(*a)

        def create(self, *a):
                encoding = sys.getfilesystemencoding()
                a = [i.encode(encoding) for i in a]
                try:
                        self.stats = pstats.Stats(*a)
                except ValueError:
                        # try hotshot.stats
                        import hotshot.stats
                        self.stats = hotshot.stats.load(*a)

                self.stats.calc_callees()

#------------for call graph-------------
                self.init_data()

        def init_data(self):
                self.id_dict = {}
                self.id_list = []
                self.call_map = []
                self.cpu_time = 0.0
                self.nc = 0
                self.pnc = 0
                stats = self.stats.stats
                for i, (func, (cc, nc, tt, ct, cs)) in enumerate(stats.iteritems()):
                        if cs.has_key(('profile', 0, 'profiler')) == True:
                                self.cpu_time += ct
                        self.nc += nc
                        self.pnc += cc
                        self.id_list.append( (func,cc,nc,tt,ct,cs) )
                        self.id_dict[func] = i
                for i in xrange(len(self.id_list)):
                        self.call_map.append([])
                for i, (func,cc,nc,tt,ct,cs) in enumerate(self.id_list):
                        for j in cs.iterkeys():
                                self.call_map[self.id_dict[j]].append(i)
#------------for call graph-------------

        @check_stats
        def save(self, path):
                of = open(path, 'w+')
                tmp_file = self.stats.stream
                self.stats.stream = of
                self.stats.print_stats()
                of.close()
                self.stats.stream = tmp_file


        @check_stats
        def get_callers(self, func):
                stats = self.stats.stats
                cc, nc, tt, ct, callers = stats[func]
                ret = []
                for f in callers:
                        (cc, nc, tt, ct, cs) = stats[f]
                        ret.append((f, callers[f], ct))
                #cc, nc, tt, ct, cs = stats[func]
                #ret.append((func,nc,tt))
                return self.__make_record(ret)

        @check_stats
        def get_callees(self, func):
                stats = self.stats.stats
                callees = self.stats.all_callees[func]
                tot = 0.0
                ret = []
                for i in callees:
                        cc, nc, tt, ct, cs = stats[i]
                        ret.append((i, callees[i], ct*callees[i]/float(cc)))
                cc, nc, tt, ct, cs = stats[func]
                ret.append((func,nc,tt))
                return self.__make_record(ret)

        def __make_record(self, data):
                ret = {}
                for i,(func, cnt, ct) in enumerate(data):
                        fln = pstats.func_strip_path(func)
                        ret[func] = (i, fln, cnt, ct)
                return ret

        def get_cur_stats(self, idx):
                return self.__make_record(self.stats.stats[idx])

        def get_stats(self):
                stats = self.stats.stats
                ret = {}
                for i, (func, (cc, nc, tt, ct, cs)) in enumerate(stats.iteritems()):
                        fln = pstats.func_strip_path(func)
                        ret[func] = (i, fln, (cc, tt, ct, nc))
                return ret

if __name__ == '__main__':
        s = Stats()
        s.add_stats('vp.prof')
