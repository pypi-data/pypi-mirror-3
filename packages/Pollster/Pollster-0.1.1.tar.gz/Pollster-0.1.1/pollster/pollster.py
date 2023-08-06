import datetime
import urllib2
from urllib import urlencode

try:
    import json
except ImportErorr:
    import simplejson as json


class PollsterException(Exception):
  pass


class Pollster(object):

    API_SERVER = 'elections.huffingtonpost.com'
    API_BASE = '/pollster/api'

    def _build_request_url(self, path, params={}):
        url = "http://%s%s/%s" % (self.API_SERVER, self.API_BASE, path)
        if params:
          url += "?%s" % urlencode(params)
        print url
        return url

    def _invoke(self, path, params={}):
        url = self._build_request_url(path, params)
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            res = e.read()
            msg = "An error occurred. URL: %s" % url
            try:
                msg = json.loads(res)
                if msg.has_key('errors'):
                    msg = msg['errors'][0]
            except:
                pass
            raise PollsterException, msg

        if response.msg == 'OK':
            return json.loads(response.read())

        raise PollsterException('Invalid response returned: %s', response.msg)

    def charts(self, **kwargs):
        return [Chart(result) for result in self._invoke('charts', kwargs)]

    def chart(self, slug, **kwargs):
        result = self._invoke('charts/%s' % slug, kwargs)
        return Chart(result)

    def polls(self, **kwargs):
        return [Poll(result) for result in self._invoke('polls', kwargs)]


class Chart(object):

    def __init__(self, result):
        valid = ['last_updated',
                 'title',
                 'url',
                 'estimates',
                 'poll_count',
                 'topic',
                 'state',
                 'slug', ]
        for key, val in result.iteritems():
            if key in valid:
                setattr(self, key, val)

        if result.has_key('estimates_by_date'):
            self._estimates_by_date = result['estimates_by_date']

    def polls(self, **kwargs):
        kwargs['chart'] = self.slug
        return Pollster().polls(**kwargs)

    def estimates_by_date(self):
        if hasattr(self, '_estimates_by_date'):
            return self._estimates_by_date
        else:
            try:
                chart = Pollster().chart(slug=self.slug)
                self._estimates_by_date = chart._estimates_by_date
                return self.estimates_by_date()
            except IndexError:
                raise PollsterException("Can't find chart with slug: %s", self.slug)


    def __repr__(self):
        return '<Chart: %s>' % self.title


class Poll(object):

    def __init__(self, result):
        valid = ['id',
                 'pollster',
                 'start_date',
                 'end_date',
                 'method',
                 'source',
                 'questions',
                 'survey_houses',
                 'sponsors' ]
        for key, val in result.iteritems():
            setattr(self, key, val)

    def __repr__(self):
        return '<Poll: %s (%s - %s)>' % (self.pollster, self.start_date, self.end_date)
