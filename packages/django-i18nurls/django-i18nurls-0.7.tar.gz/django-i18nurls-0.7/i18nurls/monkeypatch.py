def monkeypatch_class(name, bases, namespace):
    # Source:
    # http://mail.python.org/pipermail/python-dev/2008-January/076194.html
    assert len(bases) == 1, "Exactly one base class required"
    base = bases[0]
    for name, value in namespace.iteritems():
        if name != "__metaclass__":
            setattr(base, name, value)
    return base
