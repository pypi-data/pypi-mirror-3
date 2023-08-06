from flea import TestAgent

import string
from shutil import rmtree
from tempfile import mkdtemp

from swab import Swab, show_variant, record_goal, generate_id, record_trial_tag

class SwabTestBase(object):

    def setUp(self):
        self.datadir = mkdtemp()

    def tearDown(self):
        rmtree(self.datadir)

class TestSwab(SwabTestBase):

    def test_identity_set_and_preserved(self):

        def app(environ, start_response):
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return []

        s = Swab(self.datadir)

        agent = TestAgent(s.middleware(app))
        r = agent.get('/')

        assert 'swab=' in r.response.get_header('Set-Cookie'), \
                "Swab cookie not set on first request"

        r = r.get('/')
        assert 'swab=' not in r.response.get_header('Set-Cookie'), \
                "Swab cookie reset on subsequent request"

    def test_override_identity(self):

        def app(environ, start_response):
            environ['swab.id'] = '1234567890'
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return []

        s = Swab(self.datadir)
        agent = TestAgent(s.middleware(app))
        assert 'swab=1234567890;' in agent.get('/').response.get_header('Set-Cookie')

    def test_show_variants_produces_all_variants(self):

        def app(environ, start_response):
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [show_variant('exp', environ)]

        s = Swab(self.datadir)
        s.addexperiment('exp', string.digits, 'goal')

        variants = set()
        for i in range(100):
            agent = TestAgent(s.middleware(app))
            variants.add(''.join(agent.get('/').response.content))
        assert len(variants) == 10

    def test_show_variant_returns_requested_variant(self):

        def app(environ, start_response):
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [show_variant('exp', environ)]

        s = Swab(self.datadir)
        s.addexperiment('exp', ['a', 'b'], 'goal')

        variants = set()
        for i in range(100):
            agent = TestAgent(s.middleware(app))
            variants.add(''.join(agent.get('/?swab.exp=a').response.content))
        assert variants == set('a')

    def test_show_variant_does_not_error_if_called_before_start_response(self):

        def app(environ, start_response):
            response = [show_variant('exp', environ)]
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return response

        s = Swab(self.datadir)
        s.addexperiment('exp', ['a', 'b'], 'goal')

        TestAgent(s.middleware(app)).get('/').response.body

    def test_variants_are_chosen_independently(self):
        s = Swab(self.datadir)
        s.addexperiment('foo', ['v1', 'v2'], 'goal')
        s.addexperiment('bar', ['v1', 'v2'], 'goal')
        for i in range(100):
            env = {'swab.id': generate_id(), 'swab.swab': s, 'QUERY_STRING': ''}
            a = show_variant('foo', env, record=False)
            b = show_variant('bar', env, record=False)
            if a != b:
                break
        else:
            raise AssertionError("Expected different variants to be chosen")

    def test_caching_headers_added(self):

        def app(environ, start_response):
            show_variant('exp', environ)
            start_response('200 OK', [
                ('Content-Type', 'text/plain'),
                ('Last-Modified', 'x'),
                ('ETag', 'x'),
                ('Expires', 'x'),
                ('Cache-Control', 'cache me!'),
            ])
            return []

        s = Swab(self.datadir)
        s.addexperiment('exp', ['a', 'b'], 'goal')
        r = TestAgent(s.middleware(app)).get('/')
        headers = dict(r.response.headers)

        assert 'Content-Type' in headers
        assert 'Last-Modified' not in headers
        assert 'Etag' not in headers
        assert 'Expires' not in headers
        assert headers['Cache-Control'] == 'no-cache'


class TestResults(SwabTestBase):

    def test_results_page_renders(self):

        def app(environ, start_response):
            response = [show_variant('exp', environ)]
            record_goal('goal', environ)
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return response

        s = Swab(self.datadir)
        s.addexperiment('exp', ['variant1', 'variant2'], 'goal')
        r = TestAgent(s.middleware(app))
        r.get('/')

        assert 'A/B test results summary' in r.get('/swab/results').response.body
        assert 'variant1' in r.get('/swab/results').response.body

    def test_goals_without_trials_ignored(self):
        s = Swab(self.datadir)
        s.addexperiment('exp', ['variant1', 'variant2'], 'goal')
        env = {'swab.id': generate_id(),
               'swab.swab': s,
               'QUERY_STRING': '',}

        record_goal('goal', env)
        r = TestAgent(s.middleware(None))
        r = r.get('/swab/results')
        for row in r('table tr'):
            try:
                assert row('td')[0].text == '0'
            except IndexError:
                # Header row
                continue

class TestSwabJS(SwabTestBase):

    def test_record_trial_tag(self):
        s = Swab(self.datadir)
        env = {'swab.id': generate_id(),
               'swab.swab': s,
               'SERVER_NAME': 'localhost',
               'SERVER_PORT': '80',
               'SCRIPT_NAME': '',
               'PATH_INFO': '/',
               'QUERY_STRING': ''
              }
        s.addexperiment('exp', ['a', 'b'], 'goal')
        assert record_trial_tag('exp', env) == '''<script>document.write(unescape('%3Cscript src="http://localhost/swab/r.js' + '?e=exp;s={0}"%3E%3C/script%3E'))</script>'''.format(env['swab.id'])

    def test_tag_not_generated_if_variant_forced(self):
        s = Swab(self.datadir)
        env = {'swab.id': generate_id(),
               'swab.swab': s,
               'SERVER_NAME': 'localhost',
               'SERVER_PORT': '80',
               'SCRIPT_NAME': '',
               'PATH_INFO': '/',
               'QUERY_STRING': 'swab.exp=a',
              }
        s.addexperiment('exp', ['a', 'b'], 'goal')
        assert record_trial_tag('exp', env) == ''

    def test_javascript_response_not_cachable(self):
        def app(environ, start_response):
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return []

        s = Swab(self.datadir)
        s.addexperiment('exp', ['a', 'b'], 'goal')
        agent = TestAgent(s.middleware(app))
        r = agent.get('/swab/r.js?e=exp')
        s.addexperiment('exp', ['a', 'b'], 'goal')
        assert r.response.get_header('Cache-Control') == 'no-cache'

