from Products.Five.browser import BrowserView
from dateable.kalends import IRecurringEvent, IRecurrence
from p4a.common.dtutils import dt2DT
from kss.core import KSSView, kssaction
from datetime import datetime
from p4a.ploneevent import PloneEventMessageFactory as _

FREQ = {0: 'year',
        1: 'month',
        2: 'week',
        3: 'day',
        4: 'hour',
        5: 'minute',
        6: 'second',
    }


CALVOCAB = {0: (_(u'year'), _(u'years')),
            1: (_(u'month'), _(u'months')),
            2: (_(u'week'), _(u'weeks')),
            3: (_(u'day'), _(u'days')),
            }

class EventView(BrowserView):

    def same_day(self):
        return self.context.start().Date() == self.context.end().Date()

    def short_start_date(self):
        return self.context.toLocalizedTime(self.context.start(), long_format=0)

    def long_start_date(self):
        return self.context.toLocalizedTime(self.context.start(), long_format=1)

    def start_time(self):
        return self.context.toLocalizedTime(self.context.start(), long_format=0, time_only=1)

    def short_end_date(self):
        return self.context.toLocalizedTime(self.context.end(), long_format=0)

    def long_end_date(self):
        return self.context.toLocalizedTime(self.context.end(), long_format=1)

    def end_time(self):
        return self.context.toLocalizedTime(self.context.end(), long_format=0, time_only=1)

    def isRecurring(self):
        if not IRecurringEvent.providedBy(self.context):
            return False
        rrule = IRecurrence(self.context, None).getRecurrenceRule()
        if rrule is None:
            return False
        return True

    def rrule(self):
        return IRecurrence(self.context, None).getRecurrenceRule()

    def rrule_freq(self):
        rrule = self.rrule()
        if rrule is None:
            return ''
        freq = CALVOCAB[rrule._freq]
        if rrule._interval == 1:
            return freq[0]
        else:
            return freq[1]

    def rrule_interval(self):
        rrule = self.rrule()
        if rrule is not None:
            return rrule._interval
        return 0

    def rrule_count(self):
        rrule = self.rrule()
        if rrule is not None:
            return rrule._count
        return 0

    def rrule_end(self):
        rrule = self.rrule()
        if rrule is not None and rrule._until:
            return self.context.toLocalizedTime(dt2DT(rrule._until), long_format=0)
        return ''


class RecurrenceView(KSSView):

    @kssaction
    def updateRecurUI(self, frequency,interval):
        # build HTML
        content ='Repeats every %s  %s '
        core = self.getCommandSet('core')

        #check to see if single interval
        frequency = int(frequency)
        interval  = int(interval)
        if frequency == -1:
            caltext = 'day/week/month/year.'
            interval = ''
            display = 'none'
        elif interval > 1:
            caltext = CALVOCAB[frequency][1]
            display = 'block'
        elif interval == 0:
            caltext = 'day/week/month/year.'
            interval = ''
            display = 'block'
        else:
            caltext = CALVOCAB[frequency][0]
            interval = ''
            display = 'block'

        core.setStyle('#archetypes-fieldname-interval', name='display', value=display)
        core.setStyle('#archetypes-fieldname-until', name='display', value=display)
        core.setStyle('#archetypes-fieldname-count', name='display', value=display)
        content = content % (interval, caltext)
        core.replaceInnerHTML('#interval_help', content)
