import py, pytest
from _pytest.mark import MarkGenerator as Mark

class TestMark:
    def test_markinfo_repr(self):
        from _pytest.mark import MarkInfo
        m = MarkInfo("hello", (1,2), {})
        repr(m)

    def test_pytest_exists_in_namespace_all(self):
        assert 'mark' in py.test.__all__
        assert 'mark' in pytest.__all__

    def test_pytest_mark_notcallable(self):
        mark = Mark()
        pytest.raises((AttributeError, TypeError), "mark()")

    def test_pytest_mark_bare(self):
        mark = Mark()
        def f():
            pass
        mark.hello(f)
        assert f.hello

    def test_pytest_mark_keywords(self):
        mark = Mark()
        def f():
            pass
        mark.world(x=3, y=4)(f)
        assert f.world
        assert f.world.kwargs['x'] == 3
        assert f.world.kwargs['y'] == 4

    def test_apply_multiple_and_merge(self):
        mark = Mark()
        def f():
            pass
        marker = mark.world
        mark.world(x=3)(f)
        assert f.world.kwargs['x'] == 3
        mark.world(y=4)(f)
        assert f.world.kwargs['x'] == 3
        assert f.world.kwargs['y'] == 4
        mark.world(y=1)(f)
        assert f.world.kwargs['y'] == 1
        assert len(f.world.args) == 0

    def test_pytest_mark_positional(self):
        mark = Mark()
        def f():
            pass
        mark.world("hello")(f)
        assert f.world.args[0] == "hello"
        mark.world("world")(f)

    def test_pytest_mark_reuse(self):
        mark = Mark()
        def f():
            pass
        w = mark.some
        w("hello", reason="123")(f)
        assert f.some.args[0] == "hello"
        assert f.some.kwargs['reason'] == "123"
        def g():
            pass
        w("world", reason2="456")(g)
        assert g.some.args[0] == "world"
        assert 'reason' not in g.some.kwargs
        assert g.some.kwargs['reason2'] == "456"

class TestFunctional:
    def test_mark_per_function(self, testdir):
        p = testdir.makepyfile("""
            import pytest
            @pytest.mark.hello
            def test_hello():
                assert hasattr(test_hello, 'hello')
        """)
        result = testdir.runpytest(p)
        result.stdout.fnmatch_lines(["*passed*"])

    def test_mark_per_module(self, testdir):
        item = testdir.getitem("""
            import pytest
            pytestmark = pytest.mark.hello
            def test_func():
                pass
        """)
        keywords = item.keywords
        assert 'hello' in keywords

    def test_marklist_per_class(self, testdir):
        item = testdir.getitem("""
            import pytest
            class TestClass:
                pytestmark = [pytest.mark.hello, pytest.mark.world]
                def test_func(self):
                    assert TestClass.test_func.hello
                    assert TestClass.test_func.world
        """)
        keywords = item.keywords
        assert 'hello' in keywords

    def test_marklist_per_module(self, testdir):
        item = testdir.getitem("""
            import pytest
            pytestmark = [pytest.mark.hello, pytest.mark.world]
            class TestClass:
                def test_func(self):
                    assert TestClass.test_func.hello
                    assert TestClass.test_func.world
        """)
        keywords = item.keywords
        assert 'hello' in keywords
        assert 'world' in keywords

    @pytest.mark.skipif("sys.version_info < (2,6)")
    def test_mark_per_class_decorator(self, testdir):
        item = testdir.getitem("""
            import pytest
            @pytest.mark.hello
            class TestClass:
                def test_func(self):
                    assert TestClass.test_func.hello
        """)
        keywords = item.keywords
        assert 'hello' in keywords

    @pytest.mark.skipif("sys.version_info < (2,6)")
    def test_mark_per_class_decorator_plus_existing_dec(self, testdir):
        item = testdir.getitem("""
            import pytest
            @pytest.mark.hello
            class TestClass:
                pytestmark = pytest.mark.world
                def test_func(self):
                    assert TestClass.test_func.hello
                    assert TestClass.test_func.world
        """)
        keywords = item.keywords
        assert 'hello' in keywords
        assert 'world' in keywords

    def test_merging_markers(self, testdir):
        p = testdir.makepyfile("""
            import pytest
            pytestmark = pytest.mark.hello("pos1", x=1, y=2)
            class TestClass:
                # classlevel overrides module level
                pytestmark = pytest.mark.hello(x=3)
                @pytest.mark.hello("pos0", z=4)
                def test_func(self):
                    pass
        """)
        items, rec = testdir.inline_genitems(p)
        item, = items
        keywords = item.keywords
        marker = keywords['hello']
        assert marker.args == ("pos0", "pos1")
        assert marker.kwargs == {'x': 3, 'y': 2, 'z': 4}

    def test_mark_other(self, testdir):
        pytest.raises(TypeError, '''
            testdir.getitem("""
                import pytest
                class pytestmark:
                    pass
                def test_func():
                    pass
            """)
        ''')

    def test_mark_dynamically_in_funcarg(self, testdir):
        testdir.makeconftest("""
            import pytest
            def pytest_funcarg__arg(request):
                request.applymarker(pytest.mark.hello)
            def pytest_terminal_summary(terminalreporter):
                l = terminalreporter.stats['passed']
                terminalreporter._tw.line("keyword: %s" % l[0].keywords)
        """)
        testdir.makepyfile("""
            def test_func(arg):
                pass
        """)
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "keyword: *hello*"
        ])


class Test_genitems:
    def test_check_collect_hashes(self, testdir):
        p = testdir.makepyfile("""
            def test_1():
                pass

            def test_2():
                pass
        """)
        p.copy(p.dirpath(p.purebasename + "2" + ".py"))
        items, reprec = testdir.inline_genitems(p.dirpath())
        assert len(items) == 4
        for numi, i in enumerate(items):
            for numj, j in enumerate(items):
                if numj != numi:
                    assert hash(i) != hash(j)
                    assert i != j

    def test_root_conftest_syntax_error(self, testdir):
        # do we want to unify behaviour with
        # test_subdir_conftest_error?
        p = testdir.makepyfile(conftest="raise SyntaxError\n")
        pytest.raises(SyntaxError, testdir.inline_genitems, p.dirpath())

    def test_example_items1(self, testdir):
        p = testdir.makepyfile('''
            def testone():
                pass

            class TestX:
                def testmethod_one(self):
                    pass

            class TestY(TestX):
                pass
        ''')
        items, reprec = testdir.inline_genitems(p)
        assert len(items) == 3
        assert items[0].name == 'testone'
        assert items[1].name == 'testmethod_one'
        assert items[2].name == 'testmethod_one'

        # let's also test getmodpath here
        assert items[0].getmodpath() == "testone"
        assert items[1].getmodpath() == "TestX.testmethod_one"
        assert items[2].getmodpath() == "TestY.testmethod_one"

        s = items[0].getmodpath(stopatmodule=False)
        assert s.endswith("test_example_items1.testone")
        print(s)


class TestKeywordSelection:
    def test_select_simple(self, testdir):
        file_test = testdir.makepyfile("""
            def test_one():
                assert 0
            class TestClass(object):
                def test_method_one(self):
                    assert 42 == 43
        """)
        def check(keyword, name):
            reprec = testdir.inline_run("-s", "-k", keyword, file_test)
            passed, skipped, failed = reprec.listoutcomes()
            assert len(failed) == 1
            assert failed[0].nodeid.split("::")[-1] == name
            assert len(reprec.getcalls('pytest_deselected')) == 1

        for keyword in ['test_one', 'est_on']:
            #yield check, keyword, 'test_one'
            check(keyword, 'test_one')
        check('TestClass.test', 'test_method_one')

    def test_select_extra_keywords(self, testdir):
        p = testdir.makepyfile(test_select="""
            def test_1():
                pass
            class TestClass:
                def test_2(self):
                    pass
        """)
        testdir.makepyfile(conftest="""
            def pytest_pycollect_makeitem(__multicall__, name):
                if name == "TestClass":
                    item = __multicall__.execute()
                    item.keywords['xxx'] = True
                    return item
        """)
        for keyword in ('xxx', 'xxx test_2', 'TestClass', 'xxx -test_1',
                        'TestClass test_2', 'xxx TestClass test_2',):
            reprec = testdir.inline_run(p.dirpath(), '-s', '-k', keyword)
            py.builtin.print_("keyword", repr(keyword))
            passed, skipped, failed = reprec.listoutcomes()
            assert len(passed) == 1
            assert passed[0].nodeid.endswith("test_2")
            dlist = reprec.getcalls("pytest_deselected")
            assert len(dlist) == 1
            assert dlist[0].items[0].name == 'test_1'

    def test_select_starton(self, testdir):
        threepass = testdir.makepyfile(test_threepass="""
            def test_one(): assert 1
            def test_two(): assert 1
            def test_three(): assert 1
        """)
        reprec = testdir.inline_run("-k", "test_two:", threepass)
        passed, skipped, failed = reprec.listoutcomes()
        assert len(passed) == 2
        assert not failed
        dlist = reprec.getcalls("pytest_deselected")
        assert len(dlist) == 1
        item = dlist[0].items[0]
        assert item.name == "test_one"


    def test_keyword_extra(self, testdir):
        p = testdir.makepyfile("""
           def test_one():
               assert 0
           test_one.mykeyword = True
        """)
        reprec = testdir.inline_run("-k", "-mykeyword", p)
        passed, skipped, failed = reprec.countoutcomes()
        assert passed + skipped + failed == 0
        reprec = testdir.inline_run("-k", "mykeyword", p)
        passed, skipped, failed = reprec.countoutcomes()
        assert failed == 1
