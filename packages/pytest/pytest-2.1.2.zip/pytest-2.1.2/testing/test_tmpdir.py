import py, pytest

from _pytest.tmpdir import pytest_funcarg__tmpdir, TempdirHandler
from _pytest.python import FuncargRequest

def test_funcarg(testdir):
    item = testdir.getitem("""
            def pytest_generate_tests(metafunc):
                metafunc.addcall(id='a')
                metafunc.addcall(id='b')
            def test_func(tmpdir): pass
            """, 'test_func[a]')
    p = pytest_funcarg__tmpdir(FuncargRequest(item))
    assert p.check()
    bn = p.basename.strip("0123456789")
    assert bn.endswith("test_func_a_")
    item.name = "qwe/\\abc"
    p = pytest_funcarg__tmpdir(FuncargRequest(item))
    assert p.check()
    bn = p.basename.strip("0123456789")
    assert bn == "qwe__abc"

def test_ensuretemp(recwarn):
    #py.test.deprecated_call(py.test.ensuretemp, 'hello')
    d1 = py.test.ensuretemp('hello')
    d2 = py.test.ensuretemp('hello')
    assert d1 == d2
    assert d1.check(dir=1)

class TestTempdirHandler:
    def test_mktemp(self, testdir):
        config = testdir.Config()
        config.option.basetemp = testdir.mkdir("hello")
        t = TempdirHandler(config)
        tmp = t.mktemp("world")
        assert tmp.relto(t.getbasetemp()) == "world0"
        tmp = t.mktemp("this")
        assert tmp.relto(t.getbasetemp()).startswith("this")
        tmp2 = t.mktemp("this")
        assert tmp2.relto(t.getbasetemp()).startswith("this")
        assert tmp2 != tmp

class TestConfigTmpdir:
    def test_getbasetemp_custom_removes_old(self, testdir):
        p = testdir.tmpdir.join("xyz")
        config = testdir.parseconfigure("--basetemp=xyz")
        b = config._tmpdirhandler.getbasetemp()
        assert b == p
        h = b.ensure("hello")
        config._tmpdirhandler.getbasetemp()
        assert h.check()
        config = testdir.parseconfigure("--basetemp=xyz")
        b2 = config._tmpdirhandler.getbasetemp()
        assert b2.check()
        assert not h.check()

    def test_reparse(self, testdir):
        config2 = testdir.reparseconfig([])
        config3 = testdir.reparseconfig([])
        assert config2.basetemp != config3.basetemp
        assert not config2.basetemp.relto(config3.basetemp)
        assert not config3.basetemp.relto(config2.basetemp)

    def test_reparse_filename_too_long(self, testdir):
        config = testdir.reparseconfig(["--basetemp=%s" % ("123"*300)])


def test_basetemp(testdir):
    mytemp = testdir.tmpdir.mkdir("mytemp")
    p = testdir.makepyfile("""
        import pytest
        def test_1():
            pytest.ensuretemp("hello")
    """)
    result = testdir.runpytest(p, '--basetemp=%s' % mytemp)
    assert result.ret == 0
    assert mytemp.join('hello').check()
