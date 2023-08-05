import os
import tempfile
from StringIO import StringIO
from nose.tools import assert_raises, with_setup, assert_equals
from nose import SkipTest
from distutils.spawn import find_executable
from webassets import Bundle, Environment
from webassets.exceptions import FilterError
from webassets.filter import Filter, get_filter, register_filter, JavaMixin
from helpers import TempEnvironmentHelper

# Sometimes testing filter output can be hard if they generate
# unpredictable text like temp paths or timestamps. doctest has
# the same problem, so we just steal it's solution.
from doctest import _ellipsis_match as doctest_match


class TestFilter:
    """Test the API ``Filter`` provides to descendants.
    """

    def test_auto_name(self):
        """Test the automatic generation of the filter name.
        """
        assert type('Foo', (Filter,), {}).name == 'foo'
        assert type('FooFilter', (Filter,), {}).name == 'foo'
        assert type('FooBarFilter', (Filter,), {}).name == 'foobar'

        assert type('Foo', (Filter,), {'name': 'custom'}).name == 'custom'
        assert type('Foo', (Filter,), {'name': None}).name == None

    def test_get_config(self):
        """Test the ``get_config`` helper.
        """
        m = Environment(None, None)
        f = Filter()
        f.set_environment(m)
        get_config = f.get_config

        # For the purposes of the following tests, we use two test
        # names which we expect to be undefined in os.env.
        NAME = 'FOO%s' % id(object())
        NAME2 = 'FOO%s' % id(NAME)
        assert NAME != NAME2
        assert not NAME in os.environ and not NAME2 in os.environ

        try:
            # Test raising of error, and test not raising it.
            assert_raises(EnvironmentError, get_config, NAME)
            assert get_config(NAME, require=False) == None

            # Start with only the environment variable set.
            os.environ[NAME] = 'bar'
            assert get_config(NAME) == 'bar'
            assert get_config(env=NAME, setting=False) == 'bar'
            assert_raises(EnvironmentError, get_config, setting=NAME, env=False)

            # Set the value in the environment as well.
            m.config[NAME] = 'foo'
            # Ensure that settings take precedence.
            assert_equals(get_config(NAME), 'foo')
            # Two different names can be supplied.
            assert get_config(setting=NAME2, env=NAME) == 'bar'

            # Unset the env variable, now with only the setting.
            del os.environ[NAME]
            assert get_config(NAME) == 'foo'
            assert get_config(setting=NAME, env=False) == 'foo'
            assert_raises(EnvironmentError, get_config, env=NAME)
        finally:
            if NAME in os.environ:
                del os.environ[NAME]

    def test_equality(self):
        """Test the ``unique`` method used to determine equality.
        """
        class TestFilter(Filter):
            def unique(self):
                return getattr(self, 'token', 'bar')
        f1 = TestFilter();
        f2 = TestFilter();

        # As long as the two tokens are equal, the filters are
        # considered to be the same.
        assert f1 == f2
        f1.token = 'foo'
        assert f1 != f2
        f2.token = 'foo'
        assert f1 == f2

        # However, unique() is only per class; two different filter
        # classes will never match...
        class AnotherFilter(TestFilter):
            # ...provided they have a different name.
            name = TestFilter.name + '_2'
            def unique(self):
                return 'foo'
        g = AnotherFilter()
        assert f1 != g

    def test_java_mixin_error_handling(self):
        """The mixin class for java-based external tools.

        Test the codepath that deals with errors raised by the
        external tool.
        """
        class TestFilter(Filter, JavaMixin):
            def setup(self):
                # This is not going to be a valid jar
                self.jar = tempfile.mkstemp()[1]
                self.java_setup()
            def input(self, _in, out, *a, **kw):
                self.java_run(_in, out, [])
        # Run the filter, which will result in an error
        try:
           f1 = TestFilter()
           f1.setup()
           assert_raises(FilterError, f1.input, StringIO(), StringIO())
        finally:
           os.unlink(f1.jar)


def test_register_filter():
    """Test registration of custom filters.
    """
    # Needs to be a ``Filter`` subclass.
    assert_raises(ValueError, register_filter, object)

    # A name is required.
    class MyFilter(Filter):
        name = None
        def output(self, *a, **kw): pass
    assert_raises(ValueError, register_filter, MyFilter)

    # The same filter cannot be registered under multiple names.
    MyFilter.name = 'foo'
    register_filter(MyFilter)
    MyFilter.name = 'bar'
    register_filter(MyFilter)

    # But the same name cannot be registered multiple times.
    assert_raises(KeyError, register_filter, MyFilter)

    # A filter needs to have at least one of the input or output methods.
    class BrokenFilter(Filter):
        name = 'broken'
    assert_raises(TypeError, register_filter, BrokenFilter)


def test_get_filter():
    """Test filter resolving.
    """
    # By name - here using one of the builtins.
    assert isinstance(get_filter('jsmin'), Filter)
    assert_raises(ValueError, get_filter, 'notafilteractually')

    # By class.
    class MyFilter(Filter): pass
    assert isinstance(get_filter(MyFilter), MyFilter)
    assert_raises(ValueError, get_filter, object())

    # Passing an instance doesn't do anything.
    f = MyFilter()
    assert id(get_filter(f)) == id(f)

    # Passing a lone callable will give us a a filter back as well.
    assert hasattr(get_filter(lambda: None), 'output')

    # Arguments passed to get_filter are used for instance creation.
    assert get_filter('sass', scss=True).use_scss == True
    # However, this is not allowed when a filter instance is passed directly,
    # or a callable object.
    assert_raises(AssertionError, get_filter, f, 'test')
    assert_raises(AssertionError, get_filter, lambda: None, 'test')


def test_callable_filter():
    """Simple callables can be used as filters.

    Regression: Ensure that they actually work.
    """
    def my_filter(_in, out):
        assert _in.read() == 'initial value'
        out.write('filter was here')
    with TempEnvironmentHelper() as helper:
        helper.create_files({'in': 'initial value'})
        b = helper.mkbundle('in', filters=my_filter, output='out')
        b.build()
        assert helper.get('out') == 'filter was here'


class TestBuiltinFilters(TempEnvironmentHelper):

    default_files = {
        'foo.css': """
            h1  {
                font-family: "Verdana"  ;
                color: #FFFFFF;
            }
        """,
        'foo.js': """
        function foo(bar) {
            var dummy;
            document.write ( bar ); /* Write */
        }
        """
    }

    def test_gzip(self):
        self.create_files({'in': 'a'*100})
        self.mkbundle('in', filters='gzip', output='out.css').build()
        # GZip contains a timestamp (which additionally Python only
        # supports changing beginning with 2.7), so we can't compare
        # the full string.
        assert self.get('out.css')[:3] == '\x1f\x8b\x08'
        assert len(self.get('out.css')) == 24

    def test_cssprefixer(self):
        try:
            import cssprefixer
        except ImportError:
            raise SkipTest()
        self.create_files({'in': """a { border-radius: 1em; }"""})
        self.mkbundle('in', filters='cssprefixer', output='out.css').build()
        assert self.get('out.css') == 'a {\n    -webkit-border-radius: 1em;\n    -moz-border-radius: 1em;\n    border-radius: 1em\n    }'

    def test_cssmin(self):
        try:
            self.mkbundle('foo.css', filters='cssmin', output='out.css').build()
        except EnvironmentError:
            # cssmin is not installed, that's ok.
            raise SkipTest()
        assert self.get('out.css') == """h1{font-family:"Verdana";color:#FFF}"""

    def test_cssutils(self):
        try:
            import cssutils
        except ImportError:
            raise SkipTest()
        self.mkbundle('foo.css', filters='cssutils', output='out.css').build()
        assert self.get('out.css') == """h1{font-family:"Verdana";color:#FFF}"""

    def test_clevercss(self):
        try:
            import clevercss
        except ImportError:
            raise SkipTest()
        self.create_files({'in': """a:\n    color: #fff.darken(50%)"""})
        self.mkbundle('in', filters='clevercss', output='out.css').build()
        assert self.get('out.css') == """a {\n  color: #7f7f7f;\n}"""

    def test_coffeescript(self):
        if not find_executable('coffee'):
            raise SkipTest()
        self.create_files({'in': "alert \"I knew it!\" if elvis?"})
        self.mkbundle('in', filters='coffeescript', output='out.js').build()
        assert self.get('out.js') == """if (typeof elvis !== "undefined" && elvis !== null) {
  alert("I knew it!");
}
"""
    def test_uglifyjs(self):
        if not find_executable('uglifyjs'):
            raise SkipTest()
        self.mkbundle('foo.js', filters='uglifyjs', output='out.js').build()
        print self.get('out.js')
        assert self.get('out.js') == "function foo(a){var b;document.write(a)}"

    def test_less(self):
        if not find_executable('lessc'):
            raise SkipTest()
        self.mkbundle('foo.css', filters='less', output='out.css').build()
        assert self.get('out.css') == 'h1 {\n  font-family: "Verdana";\n  color: #ffffff;\n}\n'

    def test_jsmin(self):
        self.mkbundle('foo.js', filters='jsmin', output='out.js').build()
        assert self.get('out.js') in (
            # Builtin jsmin
            "\nfunction foo(bar){var dummy;document.write(bar);}",
            # jsmin from PyPI
            "function foo(bar){var dummy;document.write(bar);}",
        )

    def test_rjsmin(self):
        try:
            import rjsmin
        except ImportError:
            raise SkipTest()
        self.mkbundle('foo.js', filters='rjsmin', output='out.js').build()
        assert self.get('out.js') == "function foo(bar){var dummy;document.write(bar);}"

    def test_jspacker(self):
        self.mkbundle('foo.js', filters='jspacker', output='out.js').build()
        assert self.get('out.js').startswith('eval(function(p,a,c,k,e,d)')

    def test_yui_js(self):
        try:
            import yuicompressor
        except ImportError:
            raise SkipTest()
        self.mkbundle('foo.js', filters='yui_js', output='out.js').build()
        assert self.get('out.js') == "function foo(a){var b;document.write(a)};"

    def test_yui_css(self):
        try:
            import yuicompressor
        except ImportError:
            raise SkipTest()
        self.mkbundle('foo.css', filters='yui_css', output='out.css').build()
        assert self.get('out.css') == """h1{font-family:"Verdana";color:#fff}"""


class TestClosure(TempEnvironmentHelper):

    default_files = {
        'foo.js': """
        function foo(bar) {
            var dummy;
            document.write ( bar ); /* Write */
        }
        """
    }

    def setup(self):
        try:
            import closure
        except ImportError:
            raise SkipTest()

        TempEnvironmentHelper.setup(self)

    def test_closure(self):
        self.mkbundle('foo.js', filters='closure_js', output='out.js').build()
        assert self.get('out.js') == 'function foo(bar){var dummy;document.write(bar)};\n'

    def test_optimization(self):
        self.m.config['CLOSURE_COMPRESSOR_OPTIMIZATION'] = 'SIMPLE_OPTIMIZATIONS'
        self.mkbundle('foo.js', filters='closure_js', output='out.js').build()
        assert self.get('out.js') == 'function foo(a){document.write(a)};\n'

    def test_extra_args(self):
        self.m.config['CLOSURE_EXTRA_ARGS'] = ['--output_wrapper', 'hello: %output%']
        self.mkbundle('foo.js', filters='closure_js', output='out.js').build()
        assert self.get('out.js') == 'hello: function foo(bar){var dummy;document.write(bar)};\n'


class TestCssRewrite(TempEnvironmentHelper):

    def test(self):
        self.create_files({'in.css': '''h1 { background: url(sub/icon.png) }'''})
        self.create_directories('g')
        self.mkbundle('in.css', filters='cssrewrite', output='g/out.css').build()
        assert self.get('g/out.css') == '''h1 { background: url(../sub/icon.png) }'''

    def test_change_folder(self):
        """Test the replace mode of the cssrewrite filter.
        """
        self.create_files({'in.css': '''h1 { background: url(old/sub/icon.png) }'''})
        try:
            from collections import OrderedDict
        except ImportError:
            # Without OrderedDict available, use a simplified version
            # of this test.
            cssrewrite = get_filter('cssrewrite', replace=dict((
                ('o', '/error/'),       # o does NOT match the old/ dir
                ('old', '/new/'),       # this will match
            )))
        else:
            cssrewrite = get_filter('cssrewrite', replace=OrderedDict((
                ('o', '/error/'),       # o does NOT match the old/ dir
                ('old', '/new/'),       # this will match
                ('old/sub', '/error/'), # the first match is used, so this won't be
                ('new', '/error/'),     # neither will this one match
            )))
        self.mkbundle('in.css', filters=cssrewrite, output='out.css').build()
        assert self.get('out.css') == '''h1 { background: url(/new/sub/icon.png) }'''


class TestSass(TempEnvironmentHelper):

    default_files = {
        'foo.css': """
            h1  {
                font-family: "Verdana"  ;
                color: #FFFFFF;
            }
        """,
        'foo.sass': """h1
            font-family: "Verdana"
            color: #FFFFFF
        """,
    }

    def setup(self):
        if not find_executable('sass'):
            raise SkipTest()
        TempEnvironmentHelper.setup(self)

    def test_sass(self):
        sass = get_filter('sass', debug_info=False)
        self.mkbundle('foo.sass', filters=sass, output='out.css').build()
        assert self.get('out.css') == """/* line 1 */\nh1 {\n  font-family: "Verdana";\n  color: white;\n}\n"""

    def test_sass_import(self):
        """Test referencing other files in sass.
        """
        sass = get_filter('sass', debug_info=False)
        self.create_files({'import-test.sass': '''@import foo.sass'''})
        self.mkbundle('import-test.sass', filters=sass, output='out.css').build()
        print repr(self.get('out.css'))
        assert doctest_match("""/* line 1, ...foo.sass */\nh1 {\n  font-family: "Verdana";\n  color: white;\n}\n""", self.get('out.css'))

    def test_scss(self):
        # SCSS is a CSS superset, should be able to compile the CSS file just fine
        scss = get_filter('scss', debug_info=False)
        self.mkbundle('foo.css', filters=scss, output='out.css').build()
        assert self.get('out.css') == """/* line 2 */\nh1 {\n  font-family: "Verdana";\n  color: #FFFFFF;\n}\n"""

    def test_debug_info_option(self):
        # The debug_info argument to the sass filter can be configured via
        # a global SASS_DEBUG_INFO option.
        self.m.config['SASS_DEBUG_INFO'] = False
        self.mkbundle('foo.sass', filters=get_filter('sass'), output='out.css').build(force=True)
        assert not '-sass-debug-info' in self.get('out.css')

        # However, an instance-specific debug_info option takes precedence.
        self.mkbundle('foo.sass', filters=get_filter('sass', debug_info=True), output='out.css').build(force=True)
        assert '-sass-debug-info' in self.get('out.css')

        # If the value is None (the default), then the filter will look
        # at the debug setting to determine whether to include debug info.
        self.m.config['SASS_DEBUG_INFO'] = None
        self.m.debug  = True
        self.mkbundle('foo.sass', filters=get_filter('sass'),
                      output='out.css', debug=False).build(force=True)
        assert '-sass-debug-info' in self.get('out.css')
        self.m.debug  = False
        self.mkbundle('foo.sass', filters=get_filter('sass'),
                      output='out.css').build(force=True)
        assert not '-sass-debug-info' in self.get('out.css')

    def test_as_output_filter(self):
        """The sass filter can be configured to work as on output filter,
        first merging the sources together, then applying sass.
        """
        # To test this, split a sass rules into two files.
        sass_output = get_filter('sass', debug_info=False, as_output=True)
        self.create_files({'p1': 'h1', 'p2': '\n  color: #FFFFFF'})
        self.mkbundle('p1', 'p2', filters=sass_output, output='out.css').build()
        assert self.get('out.css') == """/* line 1 */\nh1 {\n  color: white;\n}\n"""

    def test_custom_include_path(self):
        """Test a custom include_path.
        """
        sass_output = get_filter('sass', debug_info=False, as_output=True,
                                 includes_dir=self.path('includes'))
        self.create_files({
            'includes/vars.sass': '$a_color: #FFFFFF',
            'base.sass': '@import vars.sass\nh1\n  color: $a_color'})
        self.mkbundle('base.sass', filters=sass_output, output='out.css').build()
        assert self.get('out.css') == """/* line 2 */\nh1 {\n  color: white;\n}\n"""


class TestCompass(TempEnvironmentHelper):

    default_files = {
        'foo.scss': """
            h1  {
                font-family: "Verdana"  ;
                color: #FFFFFF;
            }
        """,
        'import.scss': """
        @import "foo.scss";
        """,
        'foo.sass': """h1
            font-family: "Verdana"
            color: #FFFFFF
        """
    }

    def setup(self):
        if not find_executable('compass'):
            raise SkipTest()
        TempEnvironmentHelper.setup(self)

    def test_compass(self):
        self.mkbundle('foo.sass', filters='compass', output='out.css').build()
        assert doctest_match("""/* ... */\nh1 {\n  font-family: "Verdana";\n  color: white;\n}\n""", self.get('out.css'))

    def test_compass_with_imports(self):
        self.mkbundle('import.scss', filters='compass', output='out.css').build()
        assert doctest_match("""/* ... */\nh1 {\n  font-family: "Verdana";\n  color: #FFFFFF;\n}\n""", self.get('out.css'))

    def test_compass_with_scss(self):
        # [bug] test compass with scss files
        self.mkbundle('foo.scss', filters='compass', output='out.css').build()
        assert doctest_match("""/* ... */\nh1 {\n  font-family: "Verdana";\n  color: #FFFFFF;\n}\n""", self.get('out.css'))

    def test_images_dir(self):
        # [bug] Make sure the compass plugin can reference images. It expects
        # paths to be relative to env.directory.
        self.create_files({'datauri.scss': 'h1 { background: inline-image("test.png") }', 'test.png': 'foo'})
        self.mkbundle('datauri.scss', filters='compass', output='out.css').build()
        assert doctest_match("""/* ... */\nh1 {\n  background: url('data:image/png;base64,Zm9v');\n}\n""", self.get('out.css'))

    def test_images_url(self):
        # [bug] Make sure the compass plugin outputs the correct urls to images
        # when using the image-url helper.
        self.m.url = 'http://assets.host.com/the-images'
        self.create_files({'imguri.scss': 'h1 { background: image-url("test.png") }'})
        self.mkbundle('imguri.scss', filters='compass', output='out.css').build()
        assert doctest_match("""/* ... */\nh1 {\n  background: url('http://assets.host.com/the-images/test.png');\n}\n""", self.get('out.css'))


class TestJST(TempEnvironmentHelper):

    default_files = {
        'templates/foo.jst': "<div>Im a normal .jst template.</div>",
        'templates/bar.html': "<div>Im an html jst template.  Go syntax highlighting!</div>"
    }

    def setup(self):
        TempEnvironmentHelper.setup(self)
    
    def test_jst(self):
        self.mkbundle('templates/*', filters='jst', output='out.js').build()
        contents = self.get('out.js')
        assert 'Im a normal .jst template' in contents
        assert 'Im an html jst template.  Go syntax highlighting!' in contents
    
    def test_compiler_config(self):
        self.m.config['JST_COMPILER'] = '_.template'
        self.mkbundle('templates/*', filters='jst', output='out.js').build()
        assert '_.template' in self.get('out.js')
    
    def test_namespace_config(self):
        self.m.config['JST_NAMESPACE'] = 'window.Templates'
        self.mkbundle('templates/*', filters='jst', output='out.js').build()
        assert 'window.Templates' in self.get('out.js')
    
    def test_nested_naming(self):
        self.create_files({'templates/foo/bar/baz.jst': """<span>In your foo bars.</span>"""})
        self.mkbundle('templates/foo/bar/*', 'templates/bar.html', filters='jst', output='out.js').build()
        assert '\'foo/bar/baz\'' in self.get('out.js')

    def test_single_template(self):
        self.create_files({'baz.jst': """<span>Baz?</span>"""})
        self.mkbundle('*.jst', filters='jst', output='out.js').build()
        assert '\'baz\'' in self.get('out.js')

    def test_option_bare(self):
        """[Regression] Test the JST_BARE option can be set to False.
        """
        self.create_files({'baz.jst': """<span>Baz?</span>"""})
        self.m.config['JST_BARE'] = False
        self.mkbundle('*.jst', filters='jst', output='out.js').build()
        assert self.get('out.js').startswith('(function()')
