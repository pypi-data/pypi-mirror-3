
from os.path import join

from ._factory import _refdir, _reffactory


__all__ = ['hxb2', 'nl4_3']


# annoyingly, glob doesn't support curly bracket {fa,gb}-style wildcards
# so use this bracket-hack
hxb2 = _reffactory(join(_refdir, 'hxb2'), 'HXB2_%s.[fg][ab]')
nl4_3 = _reffactory(join(_refdir, 'nl4-3'), 'NL4_3_%s.fa')
