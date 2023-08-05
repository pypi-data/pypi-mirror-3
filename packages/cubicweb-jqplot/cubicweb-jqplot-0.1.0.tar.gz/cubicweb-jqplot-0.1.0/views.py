# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.
"""basic plot views based on jqplot (http://www.jqplot.com)
"""

__docformat__ = "restructuredtext en"
_ = unicode

from logilab.common.date import datetime2ticks
#from logilab.mtconverter import xml_escape

from cubicweb import NoSelectableObject
from cubicweb.view import AnyRsetView
from cubicweb.utils import json_dumps, JSString, js_dumps
#from cubicweb.appobject import objectify_selector
from cubicweb.selectors import multi_columns_rset, match_kwargs

def filterout_nulls(abscissa, plot):
    filtered = []
    for x, y in zip(abscissa, plot):
        if x is None or y is None:
            continue
        filtered.append( (x, y) )
    return sorted(filtered)


class JQPlotRsetView(AnyRsetView):
    __regid__ = 'jqplot.default'
    __select__ = multi_columns_rset() & match_kwargs('series_options')

    onload = '''
%(id)s = $.jqplot("%(id)s", %(data)s, {
    seriesDefaults: {
        rendererOptions: {fillToZero: true}
    },
    series: [%(series)s],
    legend: %(legend)s,
    axesDefaults:{useSeriesColor: true},
    axes: %(axes)s,
    cursor:%(cursor)s,
    highlighter:%(highlighter)s
});
    '''

    default_legend = {'show': True,
                      'placement': 'outsideGrid',
                      }
    default_axes = {'xaxis': {'autoscale': True},
                    }
    default_cursor = {'show': True,
                      'zoom': True,
                      'showTooltip': True,
                      }
    default_highlighter = {'show': True,
                           'sizeAdjust': 7.5,
                           }
    renderers = {'bar': (JSString('$.jqplot.BarRenderer'),
                         'plugins/jqplot.barRenderer.min.js'),
                 'pie': (JSString('$.jqplot.PieRenderer'),
                         'plugins/jqplot.pieRenderer.min.js'),
                 'donut': (JSString('$.jqplot.DonutRenderer'),
                         'plugins/jqplot.donutRenderer.min.js'),
                 'ohlc': (JSString('$.jqplot.OHLCRenderer'),
                          'plugins/jqplot.ohlcRenderer.js'),
                 }

    axis_renderers = {'linear': (JSString('$.jqplot.LinearAxisRenderer'), None),
                      'date': (JSString('$.jqplot.DateAxisRenderer'),
                               'plugins/jqplot.dateAxisRenderer.min.js'),
                      'category': (JSString('$.jqplot.CategoryAxisRenderer'),
                                   'plugins/jqplot.categoryAxisRenderer.min.js'),
                      }

    tick_renderers = {'tick': (JSString('$.jqplot.CanvasAxisTickRenderer'),
                               ['plugins/jqplot.canvasTextRenderer.min.js',
                                'plugins/jqplot.dateAxisRenderer.min.js',
                                'plugins/jqplot.canvasAxisTickRenderer.min.js']),
                      }


    def call(self, series_options=None, divid=None,
             axes=None, legend=None, cursor=None, highlighter=None,
             width=None, height=None,
             displayfilter=False, mainvar=None):
        if self._cw.ie_browser():
            self._cw.add_js('excanvas.js')
        self._cw.add_js('jquery.jqplot.js')
        self._cw.add_css('jquery.jqplot.min.css')
        data, js_series_options = self.get_series(series_options)
        if legend is None:
            legend = self.default_legend
        assert not (cursor and highlighter)
        if cursor:
            self._cw.add_js('plugins/jqplot.cursor.min.js')
            cursor = self.default_cursor
            highlighter = {}
        else:
            self._cw.add_js('plugins/jqplot.highlighter.js')
            highlighter_ = self.default_highlighter
            if isinstance(highlighter, dict):
                highlighter_ = highlighter_.copy()
                highlighter_.update(highlighter)
            highlighter = highlighter_
        if axes is None:
            axes = self.default_axes
        axes = axes.copy()
        for axis, options in axes.iteritems():
            if 'renderer' in options:
                options = options.copy()
                options['renderer'] = self.renderer(self.axis_renderers,
                                                    options['renderer'])
                axes[axis] = options
            if 'tickRenderer' in options:
                options = options.copy()
                options['tickRenderer'] = self.renderer(self.tick_renderers,
                                                        options['tickRenderer'])
                axes[axis] = options
        if divid is None:
            divid = self._cw.form('divid') or u'figure%s' % self._cw.varmaker.next()
        self._cw.html_headers.add_onload(self.onload % {
            'id': divid,
            'data': json_dumps(data),
            'series': ','.join(js_series_options),
            'legend': js_dumps(legend),
            'axes': js_dumps(axes),
            'cursor': js_dumps(cursor),
            'highlighter': js_dumps(highlighter),
            })
        self.div_holder(divid, width, height)
        if displayfilter and not 'fromformfilter' in self._cw.form:
            self.form_filter(divid, mainvar)

    def form_filter(self, divid, mainvar):
        try:
            filterform = self._cw.vreg['views'].select(
                'facet.filtertable', self._cw, rset=self.cw_rset,
                mainvar=mainvar, view=self, **self.cw_extra_kwargs)
        except NoSelectableObject:
            return
        filterform.render(self.w, vid=self.__regid__, divid=divid)

    def div_holder(self, divid, width, height):
        style = u''
        if width:
            if isinstance(width, int):
                width = '%spx' % width
            style += 'width: %s;' % width
        if height:
            if isinstance(height, int):
                height = '%spx' % height
            style += 'height: %s;' % height
        self.w(u'<div id="%s" style="%s"></div>' % (divid, style))

    def iter_series(self):
        if self.cw_rset.description[0][0] in ('Date', 'Datetime', 'TZDatetime'):
            abscissa = [datetime2ticks(row[0]) for row in self.cw_rset]
        else:
            abscissa = [row[0] for row in self.cw_rset]
        nbcols = len(self.cw_rset.rows[0])
        for col in xrange(1, nbcols):
            yield filterout_nulls(abscissa, (row[col] for row in self.cw_rset))

    def get_series(self, series_options):
        series = []
        js_series_options = []
        for i, serie in enumerate(self.iter_series()):
            if serie:
                if series_options:
                    options = series_options[i]
                else:
                    options = {}
                if 'renderer' in options:
                    options = options.copy()
                    options['renderer'] = self.renderer(self.renderers,
                                                        options['renderer'])
                series.append(serie)
                js_series_options.append(js_dumps(options))
                if 'pointLabels' in options:
                    self._cw.add_js('plugins/jqplot.pointLabels.min.js')
            else:
                self.info('serie %s has no value and will be removed', i)
        return series, js_series_options

    def renderer(self, renderers, name):
        jsstr, jsfiles = renderers[name]
        if jsfiles:
            self._cw.add_js(jsfiles)
        return jsstr


class JQPlotView(JQPlotRsetView):
    __regid__ = 'jqplot.default'
    __select__ = match_kwargs('series')

    def iter_series(self):
        return self.cw_extra_kwargs['series']


class JQPlotPieView(JQPlotRsetView):
    __regid__ = 'jqplot.pie'
    __select__ = multi_columns_rset(2) # XXX second column are numbers

    onload = '%(id)s = $.jqplot("%(id)s", %(data)s, %(options)s);'
    default_renderer = 'pie'
    default_legend = {'show': True,
                      'placement': 'e',
                      }
    default_options = {'showDataLabels': True}

    def call(self, renderer=None, options=None, divid=None, legend=None, colors=None,
             width=450, height=300, displayfilter=False, mainvar=None):
        if self._cw.ie_browser():
            self._cw.add_js('excanvas.js')
        self._cw.add_js('jquery.jqplot.js',)
        self._cw.add_css('jquery.jqplot.min.css')
        data = self.cw_rset.rows
        if legend is None:
            legend = self.default_legend
        if divid is None:
            divid = u'figure%s' % self._cw.varmaker.next()
        if renderer is None:
            renderer = self.default_renderer
        serie_options = {'renderer': self.renderer(self.renderers, renderer)}
        if options is None:
            options = self.default_options
        serie_options['rendererOptions']= options
        options = {'series': [serie_options],
                   'legend': legend,
                   }
        if colors is not None:
            options['seriesColors'] = colors
        self._cw.html_headers.add_onload(self.onload % {
            'id': divid,
            'data': json_dumps([data]),
            'options': js_dumps(options)})
        self.div_holder(divid, width, height)
        if displayfilter and not 'fromformfilter' in self._cw.form:
            self.form_filter(divid, mainvar)


class JQPlotDonutView(JQPlotRsetView):
    __regid__ = 'jqplot.donut'
    default_render = 'donut'
