"""
Simple WSGI A/B testing.

(c) 2010-11 Oliver Cope.

See ``README.txt`` for usage instructions etc.
"""

import os
import re
from math import sqrt, exp
from random import Random
from struct import unpack_from
from time import time
from datetime import datetime
from collections import defaultdict
from hashlib import md5
from functools import partial
from urllib import quote_plus
from pkg_resources import resource_filename
from pesto import to_wsgi
from pesto.response import Response
from pesto.request import Request
from pesto.cookie import Cookie
from pesto.wsgiutils import static_server, mount_app
from pestotools.genshi import GenshiRender

from genshi.template.loader import TemplateLoader
templateloader = TemplateLoader(os.path.join(os.path.dirname(__file__), 'templates'))
render = GenshiRender(templateloader)

is_bot_ua = re.compile("|".join([
    r"findlinks",
    r"ia_archiver",
    r"ichiro",
    r".*bot\b",
    r".*crawler\b",
    r".*spider\b",
    r".*seeker\b",
    r".*fetch[oe]r\b",
    r".*wget",
    r".*plukkie",
    r".*Nutch",
    r".*InfoLink",
    r".*indy library",
    r".*yandex",
    r".*ezooms\b",
    r".*jeeves\b",
    r".*mediapartners-google",
    r".*jakarta Commons",
    r".*java/",
    r".*mj12",
    r".*speedy",
    r".*bot_",
    r".*pubsub",
    r".*facebookexternalhit",
    r".*feedfetcher-Google",
    r".*pflab",
    r".*metauri",
    r".*shopwiki",
    r".*libcurl",
    r".*resolver",
    r".*service",
    r".*postrank",
    r"^.{0,4}$",
]), re.I).match

class Swab(object):
    """
    Simple WSGI A/B testing
    """

    def __init__(self, datadir, wsgi_mountpoint='/swab'):

        """
        Create a new Swab test object

        :param datadir: Path to data storage directory
        :param wsgi_mountpoint: The path swab-specific views and resources will
                                be served from by the middleware.
        """
        self.datadir = datadir
        self.experiments = {}
        self.experiments_by_goal = {}
        self.wsgi_mountpoint = wsgi_mountpoint
        makedir(self.datadir)

        # Function evaluted to determine whether to include a user in experiments.
        # Users not included will always see the default variant (ie the first listed)
        self.include_test = lambda experiment, environ: True
        self.exclude_test = lambda experiment, environ: False

    def include(self, experiment, environ):
        return self.include_test(experiment, environ) and not self.exclude_test(experiment, environ)

    def middleware(self, app, cookie_domain=None, cookie_path=None, cache_control=True):
        """
        Middleware that sets a random identity cookie for tracking users.

        The identity can be overwritten by setting ``environ['swab.id']``
        before start_response is called. On egress this middleware will then
        reset the cookie if required.

        :param app: The WSGI application to wrap

        :param cookie_domain: The domain to use when setting cookies. If
                              ``None`` this will not be set and the browser
                              will default to the domain used for the request.

        :param cache_control: If ``True``, replace the upstream application's
                              cache control headers for any request where
                              show_variant is invoked.
        """

        swabapp = mount_app({
            '/results': self.results_app,
            '/r.js': self.record_trial_app,
            '/static': static_server(os.path.join(os.path.dirname(__file__), 'static')),
        })

        def middleware(environ, start_response):

            environ['swab.swab'] = self
            environ['swab.id'] = initswabid = getswabid(environ)
            environ['swab.experiments_invoked'] = set()
            if initswabid is None:
                environ['swab.id'] = generate_id()

            if environ['PATH_INFO'][:len(self.wsgi_mountpoint)] == self.wsgi_mountpoint:
                environ['SCRIPT_NAME'] += self.wsgi_mountpoint
                environ['PATH_INFO'] = environ['PATH_INFO'][len(self.wsgi_mountpoint):]
                return swabapp(environ, start_response)

            def my_start_response(status, headers, exc_info=None,
                                  _cache_headers=set(['cache-control',
                                                      'expires', 'etag',
                                                      'last-modified'])):
                swabid = getswabid(environ)
                if swabid == initswabid and swabid is not None:
                    return start_response(status, headers, exc_info)

                if swabid is None:
                    swabid = generate_id()
                    environ['swab.id'] = swabid

                _cookie_path = cookie_path or environ.get('SCRIPT_NAME') or '/'
                cookie = Cookie(
                    'swab', swabid, path=_cookie_path,
                    domain=cookie_domain, http_only=True,
                    maxage=365,
                )
                if cache_control and environ.get('swab.experiments_invoked'):
                    headers = [(k, v) for k, v in headers if k.lower() not in _cache_headers]
                    headers.append(('Cache-Control', 'no-cache'))
                headers.append(("Set-Cookie", str(cookie)))
                return start_response(status, headers, exc_info)

            return app(environ, my_start_response)

        return middleware

    def addexperiment(self, name, variants=None, goal=None):
        exp = self.experiments[name] = Experiment(name)
        if variants:
            exp.add(*variants)

        goal = goal if goal is not None else name
        self.experiments_by_goal.setdefault(goal, []).append(exp)

        makedir(os.path.join(self.datadir, name))
        return self.experiments[name]

    def results_app(self, environ, start_response):
        request = Request(environ)
        data = self.collect_experiment_data()
        for exp in data:

            # Take the first listed variant as the control - though ideally the
            # user would be able to select which variant is the control.
            vdata = data[exp]['variants']

            control = request.get('control.' + exp, self.experiments[exp].control)
            control_total = vdata[control]['t']
            control_rates = vdata[control]['r']
            data[exp]['control'] = control

            for variant in vdata:
                total = vdata[variant]['t']
                rates = vdata[variant]['r']
                vdata[variant]['z'] = {}
                vdata[variant]['confidence'] = {}
                for goal in rates:
                    vdata[variant]['z'][goal] = zscore(rates[goal], total, control_rates[goal], control_total)
                    vdata[variant]['confidence'][goal] = cumulative_normal_distribution(vdata[variant]['z'][goal])

        return render.as_response(
            resource_filename('swab', 'templates/results.html'), {
                'request': request,
                'experiments': self.experiments.values(),
                'data': data,
            }
        )(environ, start_response)

    def record_trial_app(self, environ, start_response):
        request = Request(environ)
        experiment = request.query.get('e')
        try:
            record_trial(experiment, environ)
        except KeyError:
            pass
        return Response(
            [],
            cache_control="no-cache",
        )(environ, start_response)


    def collect_experiment_data(self):
        """
        Return collected experiment data from the log files
        """
        data = {}

        for exp in self.experiments.values():
            expdir = os.path.join(self.datadir, exp.name)
            goals = sorted([goal for goal, experiments in self.experiments_by_goal.items() if exp in experiments])
            data[exp.name] = {
                'goals': goals,
                'variants': {},
            }

            for variant in exp.variants:
                path = partial(os.path.join, expdir, variant)
                data[exp.name]['variants'][variant] = {
                    # Total trials
                    't': 0,

                    # Counts for each goal
                    'c': {},

                    # Rate for each goal
                    'r': {},
                }
                trial_identities = get_identities(path('__all__'))
                trialc = len(trial_identities)
                data[exp.name]['variants'][variant]['t'] = trialc
                for goal in goals:
                    conv_identities = trial_identities.intersection(get_identities(path(goal)))
                    convc = len(conv_identities)
                    data[exp.name]['variants'][variant]['c'][goal] = convc
                    data[exp.name]['variants'][variant]['r'][goal] = float(convc) / trialc if trialc else float('nan')
        return data

class Experiment(object):

    def __init__(self, name):
        assert '/' not in name
        self.name = name
        self.variants = []

    def add(self, *variants):
        for v in variants:
            assert '/' not in v
            self.variants.append(v)

    @property
    def control(self):
        """
        The control variant for this experiment, will always be the first listed
        """
        return self.variants[0]

def getswabid(environ):
    """
    Return the unique identifier from the WSGI environment if present,
    otherwise return ``None``.
    """
    try:
        return environ['swab.id']
    except KeyError:
        pass
    cookie = Request(environ).cookies.get('swab')
    if cookie:
        environ['swab.id'] = cookie.value
        return cookie.value
    return None

def generate_id():
    """
    Return a unique id
    """
    return os.urandom(12).encode('base64').strip()

def get_rng(swabid, experiment):
    seed = md5(swabid.decode('base64'))
    seed.update(experiment)
    r = Random()
    r.seed(unpack_from('l', seed.digest()))
    return r

def show_variant(experiment, environ, record=False):
    """
    Return the variant name that ``environ`` is assigned to within ``experiment``

    If ``record`` is true, write a line to the log file indicating that the
    variant was shown. (No deduping is done - the log line is always written. A
    page with ``show_variant`` might record multiple hits on reloads etc)

    :param experiment: Name of the experiment
    :param environ: WSGI environ
    :param record: If ``True``, record a trial for the experiment in the log
                   file
    """
    swab = environ['swab.swab']
    variants = swab.experiments[experiment].variants
    swabid = getswabid(environ)

    if not swab.include(experiment, environ):
        return variants[0]

    environ.setdefault('swab.experiments_invoked', set()).add(experiment)

    request = Request(environ)
    variant = request.query.get('swab.' + experiment)
    if variant is not None and variant in variants:
        return variant

    r = get_rng(swabid, experiment)

    variant = r.choice(variants)
    if not record or is_bot(environ):
        return variant

    path = os.path.join(swab.datadir, experiment, variant, '__all__')
    try:
        f = open(path, 'a')
    except IOError:
        makedir(os.path.dirname(path))
        f = open(path, 'a')

    try:
        f.write(_logline(getswabid(environ)))
    finally:
        f.close()
    return variant

record_trial = partial(show_variant, record=True)

def record_trial_tag(experiment, environ):
    request = Request(environ)
    if 'swab.' + experiment in request.query:
        return ''
    swab = environ['swab.swab']
    return '''<script>document.write(unescape('%3Cscript src="{0}' + '?e={1};s={2}"%3E%3C/script%3E'))</script>'''.format(
        request.make_uri(path_info=swab.wsgi_mountpoint + '/' + 'r.js', query=''),
        quote_plus(experiment),
        getswabid(environ),
    )

def is_bot(environ):
    """
    Return True if the request is from a bot.
    Uses rather simplistic tests based on user agent and header signatures, but
    should still catch most well behaved bots.
    """
    if is_bot_ua(environ.get('HTTP_USER_AGENT', '')):
        return True
    if 'HTTP_ACCEPT_LANGUAGE' not in environ:
        return True
    return False

def _logline(swabid):
    return '%-14.2f:%s\n' % (time(), swabid)

def _logentries(path):
    with open(path, 'r') as f:
        for line in f:
            try:
                t, id = line.strip().split(':')
            except ValueError:
                continue
            yield float(t.strip()), id

def record_goal(goal, environ, experiment=None):
    """
    Record a goal conversion by adding a record to the file at
    ``swab-path/<experiment>/<variant>/<goal>``.

    If experiment is not specified, all experiments linked to the named goal
    are looked up.

    This doesn't use any file locking, but we should be safe on any posix
    system as we are appending each time to the file.
    See http://www.perlmonks.org/?node_id=486488 for a discussion of the issue.
    """

    if is_bot(environ):
        return

    swab = environ['swab.swab']
    if experiment is None:
        experiments = swab.experiments_by_goal.get(goal, [])
    else:
        experiments = [swab.experiments[experiment]]
    for experiment in experiments:
        if not swab.include(experiment.name, environ):
            continue

        variant = show_variant(experiment.name, environ, record=False)
        path = os.path.join(swab.datadir, experiment.name, variant, goal)
        try:
            f = open(path, 'a')
        except IOError:
            makedir(os.path.dirname(path))
            f = open(path, 'a')

        try:
            f.write(_logline(getswabid(environ)))
        finally:
            f.close()

def makedir(path):
    """
    Create a directory at ``path``. Unlike ``os.makedirs`` don't raise an error if ``path`` already exists.
    """
    try:
        os.makedirs(path)
    except OSError, e:
        # Path already exists or cannot be created
        if not os.path.isdir(path):
            raise

def count_entries(path):
    """
    Count the number of entries in ``path``. Entries are deduplicated so that
    only one conversion is counted per identity.
    """
    return len(get_identities(path))

def get_identities(path):
    """
    Return unique identity entries in ``path``
    """
    if not os.path.isfile(path):
        return set()

    return set(identity for t, identity in _logentries(path))

def zscore(p, n, pc, nc):
    """
    Calculate the zscore of probability ``p`` over ``n`` tests, compared to control probability ``pc`` over ``nc`` tests

    See http://20bits.com/articles/statistical-analysis-and-ab-testing/.
    """
    try:
        return (p - pc) / sqrt(
            (p * (1 - p) / n)
            + (pc * (1 - pc) / nc)
        )
    except ZeroDivisionError:
        return float('nan')

def cumulative_normal_distribution(z):
    """
    Return the confidence level from calculating of the cumulative normal
    distribution for the given zscore.

    See http://abtester.com/calculator/ and http://www.sitmo.com/doc/Calculating_the_Cumulative_Normal_Distribution
    """

    b1 =  0.319381530
    b2 = -0.356563782
    b3 =  1.781477937
    b4 = -1.821255978
    b5 =  1.330274429
    p  =  0.2316419
    c  =  0.39894228

    if z >= 0.0:
        t = 1.0 / (1.0 + p * z)
        return 1.0 - c * exp(-z * z / 2.0) * t * (t * (t * (t * (t * b5 + b4) + b3) + b2) + b1)
    else:
        t = 1.0 / (1.0 - p * z)
        return c * exp(-z * z / 2.0) * t * (t *(t * (t * (t * b5 + b4) + b3) + b2) + b1)

