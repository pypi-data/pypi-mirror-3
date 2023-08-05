
from cStringIO import StringIO
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY

from AccessControl import Unauthorized
from DateTime.DateTime import DateTime
from Products.ATContentTypes.lib.calendarsupport import rfc2445dt, vformat, foldLine, ICS_EVENT_END, ICS_EVENT_START
from Products.ATContentTypes.lib.calendarsupport import VCS_EVENT_START, VCS_EVENT_END
from Products.CMFCore.utils import getToolByName

from dateable.kalends import IRecurringEvent


def date_for_display(event):
    """ Return dict containing pre-calculated information for 
        building a <start>-<end> date string. Keys are
       'from_str' - date string for start date
       'to_str' - date string for end date
       'same_day' - event ends on the same day
    """

    toLocalizedTime = event.toLocalizedTime
    from_str = toLocalizedTime(event.start(), long_format=False)
    to_str = toLocalizedTime(event.end(), long_format=False)
    same_day = from_str==to_str

    if not event.getWholeDay():
        from_str = toLocalizedTime(event.start(), long_format=True)
        to_str = toLocalizedTime(event.end(), long_format=True)
    if from_str == to_str:
        result = dict(from_str=from_str, to_str=None, same_day=same_day)
    else:
        result = dict(from_str=from_str, to_str=to_str, same_day=same_day)
    if not event.getUseEndDate() and result.has_key('to_str'):
        del result['to_str']
    return result


def _dateForWholeDay(dt):
    """ Replacement for rfc2445dt() for events lasting whole day in 
        order to get the date string according to the current time zone.
        rfc2445dt() returns the date string according to UTC which is
        *not* what we want!
    """
    return dt.strftime('%Y%m%d')


def _dateStringsForEvent(event):
    # Smarter handling for all-day events
    data_dict = date_for_display(event)
    if event.getWholeDay():
        # For all-day events we must not include the time within
        # the date-time string
        start_str = _dateForWholeDay(event.start())[:8]
        if data_dict['same_day']:
            # one-day events end with the timestamp of the next day
            # (which is the start data plus 1 day)
            end_str = _dateForWholeDay(event.start() + 1)[:8]
        else:
            # all-day events lasting several days end at the next
            # day after the end date
            end_str = _dateForWholeDay(event.end() + 1)[:8]
    else:
        # default (as used in Plone)
        start_str = rfc2445dt(event.start())
        end_str = rfc2445dt(event.end())

    return start_str, end_str


def getICal(event):
    start_str, end_str = _dateStringsForEvent(event)
    out = StringIO()
    map = {
        'dtstamp'   : rfc2445dt(DateTime()),
        'created'   : rfc2445dt(DateTime(event.CreationDate())),
        'uid'       : event.UID(),
        'modified'  : rfc2445dt(DateTime(event.ModificationDate())),
        'summary'   : vformat(event.Title()),
        'startdate' : start_str,
        'enddate'   : end_str,
        }
    out.write(ICS_EVENT_START % map)

    description = event.Description()
    out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))

    location = event.getLocation()
    if location:
        out.write('LOCATION:%s\n' % vformat(location))

    try:
        atts = event.getAttachments()
    except (KeyError,AttributeError):
        atts = []
    res = []
    mtool = getToolByName(event, 'portal_membership')
    for d in range(len(atts)):
        try:
            obj = atts[d]
        except Unauthorized:
            continue
        if obj not in res:
            if mtool.checkPermission('View', obj):
                res.append(obj)
    if res:
        for r in res:
            out.write('ATTACH;VALUE=URI:%s\n' % r.absolute_url())

#    eventType = event.getEventType()
#    if eventType:
#        out.write('CATEGORIES:%s\n' % ','.join(eventType))

    # TODO  -- NO! see the RFC; ORGANIZER field is not to be used for non-group-scheduled entities
    # ORGANIZER;CN=%(name):MAILTO=%(email)

    # Attendees
    for att in event.getAttendees():
        if att['show']:
            out.write('ATTENDEE;CN="%s":invalid:nomail\n' % vformat(att['name']))

    # Recurrency
#    if IRecurringEvent.providedBy(event):
    # ATT: better check interface?
    if hasattr(event, 'frequency'):    
        d_map = ['MO','TU','WE','TH','FR','SA','SU']
        freq = event.getFrequency()
        if freq != -1:
            if freq == YEARLY:
                f_str = 'YEARLY'
            elif freq == MONTHLY:
                f_str = 'MONTHLY'
            elif freq == WEEKLY:
                f_str = 'WEEKLY'
            else: 
                f_str = 'DAILY'
            days = event.getWeekdays()
            bysetpos = event.getBysetpos()
            if days and bysetpos: 
                    d_str = ",".join([d_map[int(i)] for i in days])
                    rrule_str = 'RRULE:FREQ=%s;INTERVAL=%d;BYSETPOS=%s;BYDAY=%s' % (f_str, event.interval,bysetpos, d_str )
            else: 
                rrule_str = 'RRULE:FREQ=%s;INTERVAL=%d' % (f_str, event.interval)

            if event.until:
                rrule_str = "%s;UNTIL=%s" %(rrule_str, rfc2445dt(event.until))

            out.write("%s\n" % rrule_str) 

    # Contact information
    cn = []
    contact = event.contact_name()
    if contact:
        cn.append(contact)
    phone = event.contact_phone()
    if phone:
        cn.append(phone)
    email = event.contact_email()
    if email:
        cn.append(email)
    if cn:
        out.write('CONTACT:%s\n' % vformat(', '.join(cn)))

    url = event.event_url()
    if url:
        out.write('URL:%s\n' % url)

    # allow derived event types to inject additional data for iCal
    try:
        event.getICalSupplementary(out)
    except AttributeError:
        pass

    out.write(ICS_EVENT_END)
    return out.getvalue()


def getVCal(event):
    """get vCal data """

    start_str, end_str = _dateStringsForEvent(event)
    out = StringIO()
    map = {
        'dtstamp'   : rfc2445dt(DateTime()),
        'created'   : rfc2445dt(DateTime(event.CreationDate())),
        'uid'       : event.UID(),
        'modified'  : rfc2445dt(DateTime(event.ModificationDate())),
        'summary'   : vformat(event.Title()),
        'startdate' : start_str,
        'enddate'   : end_str,
        }
    out.write(VCS_EVENT_START % map)
    description = event.Description()
    if description:
        out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))
    location = event.getLocation()
    if location:
        out.write('LOCATION:%s\n' % vformat(location))

    # allow derived event types to inject additional data for iCal
    try:
        event.getVCalSupplementary(out)
    except AttributeError:
        pass

    out.write(VCS_EVENT_END)
    return out.getvalue()
