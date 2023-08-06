
from matricks import Matricks

def convert(old_m):
    """\
Convert pre 0.2.14 matricks instances (ala restored from pickle) to
new format.
"""
    data = list(old_m._data)
    data.insert(0, old_m.getLabels())
    return Matricks(data)
