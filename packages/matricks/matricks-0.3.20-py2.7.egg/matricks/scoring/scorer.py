class Scorer(object):
    """\
Scorer Class

Base class for Scorer object classes, such as Choi and GodelPositional.
"""
    def __init__(self, *arg, **kwarg):
        pass

    def __call__(self, v):
        """\
Dummy function that will always return ``None``.  The `scored` method
will, by default, omit rows for which the score is ``None``, so using this
will likely result in an empty ``Matrics`` instance.
"""
        return None

