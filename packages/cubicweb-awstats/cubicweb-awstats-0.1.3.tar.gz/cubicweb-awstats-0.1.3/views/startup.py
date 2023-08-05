# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-awstats startup views """


import os
import os.path as osp
import re
from datetime import datetime, timedelta
import urllib

from logilab.mtconverter import xml_escape
from logilab.common.textutils import BYTE_UNITS

from cubicweb.view import StartupView
from cubicweb.web.views import forms
from cubicweb.web.formfields import StringField, DateField
from cubicweb.web import formwidgets as fwdgs, httpcache

from cubes.awstats.utils import SECTIONSPEC, SECTIONLABELS, \
     extract_stats_dict, ORIGIN_LABELS

def extract_available_time_periods(form, **attrs):
    """ extract available time periods from list of awstats files """
    periods = []
    selected_domain = form._cw.form.get('domain', '')
    awstats_dir = form._cw.vreg.config['awstats-dir']
    periodicity = form._cw.vreg.config['awstats-periodicity']
    size = {
        'hour':10,
        'day':8,
        'month':6,
        }
    for filename in os.listdir(awstats_dir):
        match = re.search('awstats(\d{%s})\.?%s.txt' % (size[periodicity], selected_domain),
                          filename)
        if match:
            periods.append((specific_format('time_period', match.group(1)),
                            match.group(1)))
    return sorted(periods)

def extract_available_domains(form, **attrs):
    """ extract available domains from list of awstats files """
    domains = []
    awstats_dir = form._cw.vreg.config['awstats-dir']
    for filename in os.listdir(awstats_dir):
        match = re.search('awstats(\d{2})(\d{4})\.?(.*).txt', filename)
        if match and match.group(3) not in domains:
            domains.append(match.group(3))
    return sorted(domains)

def use_as_sort_key(value):
    """ use value as sort value, try it as an int, else just use value """
    try:
        return int(value)
    except ValueError:
        return value


def specific_format(header, value):
    """ guess from a header and value how to display it"""
    if value is None:
        return
    elif header == 'bandwidth':
        return convert_to_bytes(int(value))
    elif header == 'time_period' and len(value) in (6,8,10):
        if len(value) == 8: # day
            return datetime.strptime(value, '%m%Y%d').strftime('%Y/%m/%d')
        elif len(value) == 6: # month
            return datetime.strptime(value, '%m%Y').strftime('%Y/%m')
        elif len(value) == 10: # hour
            return datetime.strptime(value, '%m%Y%d%H').strftime('%Y/%m/%d %H:00')
    elif value and value.startswith('http://'):
        return '<a href="%s">%s</a>' % (value, value)
    elif re.search('^\d{14}$', value):
        return datetime.strptime(value, '%Y%m%d%H%M%S%f').strftime('%d/%m/%Y %H:%M')
    elif re.search('^\d{8}$', value):
        try:
            return datetime.strptime(value, '%Y%m%d').strftime('%d/%m/%Y')
        except ValueError:
            pass
    return xml_escape(urllib.unquote(value).decode('utf8'))

def convert_to_bytes(value):
    """ display bandwidth data using a human readable notation """
    ordered = [(size, label) for label, size in BYTE_UNITS.items()]
    ordered.sort(reverse=True)
    for size, label in ordered:
        if value / size != 0:
            return '%s %s' % (value / size, label)

class AwstatsRefreshForm(forms.FieldsForm):
    """Form to filter and select what stats are being displayed"""
    __regid__ = 'select-awstats'
    domain = StringField(widget=fwdgs.Select(attrs={'onchange':'this.form.submit()'}),
                         label=_('Domain:'),
                         choices=extract_available_domains)
    # TODO - use calendar widget
    time_period = StringField(widget=fwdgs.Select(attrs={'onchange':'this.form.submit()'}),
                        label=_('Period:'),
                         choices=extract_available_time_periods)
    limit = StringField(widget=fwdgs.Select(attrs={'onchange':'this.form.submit()'}),
                        label=_('Number of results :'),
                         choices=[u'%s' % i for i in (10,25,50,100)])
    section = StringField(widget=fwdgs.Select(attrs={'onchange':'this.form.submit()'}),
                          label=_('Show section :'),
                          choices=[('',''),]+[(label, value) for value, label in SECTIONLABELS.items()])
    form_buttons = [fwdgs.SubmitButton(label=_('Apply'))]

    @property
    def action(self):
        return self._cw.build_url('', vid='awstats')

class AwstatsView(StartupView):
    """ Simple HTML export of the stats in awstats files """
    __regid__ = 'awstats'

    def call(self):
        """ main call """
        _ = self._cw._
        req = self._cw

        form = self._cw.vreg['forms'].select('select-awstats', self._cw)
        form.render(w=self.w)

        domain = req.form.get('domain', '')
        time_period = req.form.get('time_period', extract_available_time_periods(form)[0][1])
        limit = int(req.form.get('limit', 10))

        filename = 'awstats%s%s.txt' % (time_period, domain and '.%s' % domain)
        awstats_dir = self._cw.vreg.config['awstats-dir']
        try:
            stats_dict = extract_stats_dict(osp.join(awstats_dir, filename))
        except IOError:
            fallback_time_period = extract_available_time_periods(form)[0][1]
            filename = 'awstats%s%s.txt' % (fallback_time_period,
                                            domain and '.%s' % domain)
            stats_dict = extract_stats_dict(osp.join(awstats_dir, filename))

        self.w(u'<div id="awstats">')
        self.w(u'<h1>%s : %s</h1>' % (_('Domain'), domain or 'default'))
        self.w(u'<h2>%s : %s</h2>' % (_('Time period'),
                                      specific_format('time_period', time_period)))
        if req.form.get('section'):
            self.generic_table(req.form.get('section'), stats_dict, limit)
        else:
            self.render_navigation(stats_dict)
            for key, value in SECTIONSPEC.items():
                self.generic_table(key, stats_dict, limit)
        self.w(u'</div>')

    def render_navigation(self, stats_dict):
        """ render navigation according to which sections are present """
        _ = self._cw._
        self.w(u'<div>')
        self.w(u'<table id="navigation">')
        for key in SECTIONSPEC.keys():
            if key in stats_dict.keys() and stats_dict[key].values():
                self.w(u'<tr><td><a href="#%s">%s</a></td></tr>' % (key, _(SECTIONLABELS[key])))
        self.w(u'</table>')
        self.w(u'</div>')

    def generic_table(self, section_name, stats_dict, limit):
        """ generic table from a section in awstats """
        _ = self._cw._
        if section_name not in stats_dict.keys() or not stats_dict[section_name].values():
            return
        self.w(u'<a name="%s"/>' % section_name)
        self.w(u'<h3>%s</h3>' % _(SECTIONLABELS[section_name]))
        self.w(u'<div><table class="listing">')
        self.w(u'<tr class="header">')
        for header in SECTIONSPEC[section_name]:
            self.w(u'<th scope="col">%s</th>' % xml_escape(header))
        self.w(u'</tr><tbody>')

        for index, item in enumerate(self.order_values(section_name, stats_dict)):
            self.w(u'<tr>')
            for tdindex, header in enumerate(SECTIONSPEC[section_name]):
                if tdindex:
                    self.w(u'<td class="data">%s</td>' % specific_format(header, item.get(header)))
                elif header == 'origin':
                    self.w(u'<td scope="row">%s</td>' % specific_format(header,
                                                                        ORIGIN_LABELS[item.get(header)]))
                else:
                    self.w(u'<td scope="row">%s</td>' % specific_format(header, item.get(header)))
            self.w(u'</tr>')
            if index > limit:
                break
        self.w(u'</tbody></table></div><br/>')

    def order_values(self, section_name, stats_dict):
        """ extract data in ordered fashion """
        if "hour" in SECTIONSPEC[section_name] :
            order_key = "hour"
            reverse = False
        elif "hits" in SECTIONSPEC[section_name]:
            order_key = "hits"
            reverse = True
        else:
            order_key = SECTIONSPEC[section_name][1]
            reverse = True
        return sorted(stats_dict[section_name].values(), reverse=reverse, key=lambda i: int(i[order_key]))


class WebStatsRefreshForm(forms.FieldsForm):
    """Form to filter and select what stats are being displayed"""
    __regid__ = 'select-webstats'
    start = DateField(label=_('Start:'),)
    stop = DateField(label=_('Stop:'),)
    limit = StringField(label=_('Number of results :'),
                         choices=[u'%s' % i for i in (10,25,50,100,200,500)])
    form_buttons = [fwdgs.SubmitButton(label=_('Apply'))]

    @property
    def action(self):
        return self._cw.build_url('', vid='webstats')

class StatPeriodsView(StartupView):
    """ Web stats view - build from StatPeriods and Hits in cubicweb

    `column_types_aggr` enables you to combine results by type
    For example BlogEntry and MicroBlogEntries in one table and Cards in separate table :

    column_types_aggr = (('MicroBlogEntry', 'BlogEntry'),
                        ('Card'))
    """
    __regid__ = 'webstats'
    column_types_aggr = None
    http_cache_manager = httpcache.NoHTTPCacheManager

    def call(self):
        _ = self._cw._
        req = self._cw
        self.w(u'<div id="statperiod">')

        form = self._cw.vreg['forms'].select('select-webstats', self._cw)
        form.render(w=self.w)
        start = req.form.get('start', '')
        if not start:
            start = (datetime.now()  - timedelta(days=30)).strftime('%Y/%m/%d')
        stop = req.form.get('stop', '')
        if not stop:
            stop = datetime.now().strftime('%Y/%m/%d')
        limit = int(req.form.get('limit', 10))

        self.w(u'<h1>%s</h1>' % _('Web stats'))
        duration = datetime.strptime(stop, '%Y/%m/%d')-datetime.strptime(start, '%Y/%m/%d')
        self.w(u'<h2>%s</h2>' % _('from %(start)s to %(stop)s (%(duration)s days)' % {'start':start,
                                                                                 'stop': stop,
                                                                                 'duration':duration.days}))
        self.description()
        self.w(u'<h3><a href="%s">%s</a></h3>' % (self._cw.build_url(rql='Any X ORDERBY S WHERE X is StatPeriod, X start S, X stop E HAVING E-S >= 20'),
                                         _('Navigate previous statistics by month')))
        rset = self._cw.execute('DISTINCT Any T WHERE X is Hits, X hit_type T')
        for index, hit_type in enumerate(rset):
            self.w(u'<h3>%s</h3>' % hit_type[0])
            rql = 'Any X, SUM(C) GROUPBY X ORDERBY 2 DESC %(limit)s WHERE H stats_about X, ' \
                  'H hit_type "%(type)s", H count C, H period P, P start >= "%(start)s", P stop <= "%(stop)s" '\
                  '' %  {'type': hit_type[0],
                         'limit': 'LIMIT %s' % limit,
                         'start': start,
                         'stop': stop,
                         }
            if self.column_types_aggr:
                self.w(u'<table class="webstats"><tr>')
                for etypes in self.column_types_aggr:
                    self.w(u'<td class="webstats">')
                    typedrql = rql + ', X is in (%s)' % ','.join(etypes)
                    rset = self._cw.execute(typedrql)
                    self.generate_table_form(rset, etypes)
                    nolimit_rql = typedrql.replace('LIMIT %s' % limit, '')
                    self.w(u'<a href="%s">Export CSV</a>' % self._cw.build_url(rql=nolimit_rql,
                                                                                vid='csvexport'))
                    self.w(u'</td>')
                self.w(u'</tr></table>')
            else:
                rset = self._cw.execute(rql)
                self.generate_table_form(rset)
                nolimit_rql = rql.replace('LIMIT %s' % limit, '')
                self.w(u'<a href="%s">Export CSV</a>' % self._cw.build_url(rql=nolimit_rql,
                                                                           vid='csvexport'))
        self.w(u'</div>')


    def generate_table_form(self, rset, etypes=None):
        self.w(self._cw.view('table', rset, 'null'))

    def description(self):
        pass
