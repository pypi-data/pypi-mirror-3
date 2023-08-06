# syntax: given
# torture test from http://www.python.org/dev/peps/pep-3150/#id32

b = {}
a = b[f(a)] = x given:
    x = 42
    def f(x):
        return x
assert "x" not in locals()
assert "f" not in locals()
assert a == 42
assert d[42] == 42 given:
    d = b
assert "d" not in locals()
y = y given:
    x = 42
    def f(): pass
    y = locals("x"), f.__name__
assert "x" not in locals()
assert "f" not in locals()
assert y == (42, "f")


class X:
    b = {}
    a = b[f(a)] = x given:
        x = 42
        def f(x):
            return x
    assert "x" not in locals()
    assert "f" not in locals()
    assert a == 42
    assert d[42] == 42 given:
        d = b
    assert "d" not in locals()
    y = y given:
        x = 42
        def f(): pass
        y = locals("x"), f.__name__
    assert "x" not in locals()
    assert "f" not in locals()
    assert y == (42, "f")


def f():
    b = {}
    a = b[f(a)] = x given:
        x = 42
        def f(x):
            return x
    assert "x" not in locals()
    assert "f" not in locals()
    assert a == 42
    assert d[42] == 42 given:
        d = b
    assert "d" not in locals()
    y = y given:
        x = 42
        def f(): pass
        y = locals("x"), f.__name__
    assert "x" not in locals()
    assert "f" not in locals()
    assert y == (42, "f")
f()
