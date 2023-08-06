import Products.Five.viewlet.viewlet


class Javascripts(Products.Five.viewlet.viewlet.ViewletBase):
    def render(self):
        scripts = \
            ['<script src="/++resource++zc.datetimewidget/%s" '
                               'type="text/javascript"></script>' % fn
                for fn in ['calendar.js',
                           'datetimewidget.js',
                           'languages/calendar-en.js',
                           'calendar-setup.js']]

        return '\n'.join(scripts)

class Css(Products.Five.viewlet.viewlet.ViewletBase):
    def render(self):
        return """<style media="all" type="text/css">
            <!--
                @import url("/++resource++zc.datetimewidget/calendar-system.css");
            -->
         </style>"""

