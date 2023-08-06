#!/usr/bin/env python
"""
Fetch free/busy information from Exchange Web Services.
"""

import ewsclient.monkey # patch suds to work with Exchange

import os
import suds.client
import logging
import json
import datetime
import dateutil.tz

from collections import defaultdict
from pyramid.view import view_config
from suds.transport.https import WindowsHttpAuthenticated

log = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    tzlocal = dateutil.tz.tzlocal()
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.replace(tzinfo=self.tzlocal).isoformat()
        return json.JSONEncoder.default(self, obj)

def connect(domain, username, password):
    transport = WindowsHttpAuthenticated(username=username,
            password=password)
    client = suds.client.Client("https://%s/EWS/Services.wsdl" % domain,
            transport=transport,
            plugins=[ewsclient.AddService()])
    return client

def expanddl(client, email):
    mailbox = client.factory.create('Mailbox')
    mailbox.EmailAddress = email
    mailbox.MailboxType = 'PublicDL' # optional but suds includes this element by default 
    expanded = client.service.ExpandDL(mailbox)
    return expanded

def freebusy(client,
             dl_name, 
             tz_bias=300, 
             get_display_name=lambda x: x):
    """Fetch free/busy information as a JSON-serializable structure.
    
    dl_name: Distribution list of desired calendars
    tz_bias: Time zone offset from UTC
    get_display_name: Return a display name (shown on the calendar) given 
        an e-mail addres (the part before the @)
    """

    tz = client.factory.create('t:TimeZone')

    # Minutes difference from UTC
    tz.Bias = tz_bias

    # Should be correct for US time zones with DST
    tz.StandardTime.Bias = 0
    tz.StandardTime.Time = '02:00:00'
    tz.StandardTime.DayOrder = 1
    tz.StandardTime.Month = 11
    tz.StandardTime.DayOfWeek = 'Sunday'

    tz.DaylightTime.Bias = -60
    tz.DaylightTime.Time = '02:00:00'
    tz.DaylightTime.DayOrder = 2
    tz.DaylightTime.Month = 3
    tz.DaylightTime.DayOfWeek = 'Sunday'

    fb = client.factory.create('t:FreeBusyViewOptions')
    fb.TimeWindow.StartTime = datetime.datetime.now().isoformat()
    fb.TimeWindow.EndTime = (datetime.datetime.now() +
            datetime.timedelta(hours=8)).isoformat()
    fb.MergedFreeBusyIntervalInMinutes = 15
    fb.RequestedView = 'DetailedMerged'

    expanded = expanddl(client, dl_name)

    md = client.factory.create('MailboxDataArray')

    for box in expanded.ExpandDLResponseMessage.DLExpansion.Mailbox:
        mde = client.factory.create('t:MailboxData')
        mde.Email.Address = box.EmailAddress
        mde.AttendeeType = 'Room'
        mde.ExcludeConflicts = 'false'
        md.MailboxData.append(mde)
    
    # look out for mismatched tag...
    # XXX this would be the time to not ask for free/busy information
    # for hidden rooms
    availability = client.service.GetUserAvailability(tz, md, fb)

    names = [x.Name for x in expanded[0][2][2]]
    events = []

    for name, appointments in zip(names, availability.FreeBusyResponseArray.FreeBusyResponse):
        if not hasattr(appointments.FreeBusyView, 'CalendarEventArray'):
            continue
        if get_display_name(name) is None:
            continue
        for i, a in enumerate(appointments.FreeBusyView.CalendarEventArray.CalendarEvent):
                details = a.CalendarEventDetails
                try:
                    event = dict(
                            start=a.StartTime,
                            end=a.EndTime,
                            busy=a.BusyType,
                            id=getattr(details, 'ID', i),
                            subject=getattr(details, 'Subject', ''),
                            location=getattr(details, 'Location', ''),
                            private=details.IsPrivate,
                            user=name)
                    # details.IsPrivate == True --> no ID, Subject, Location
                    events.append(event)
                except AttributeError, e:
                    log.warn("%r %r", e, a)

    # sort names after associating with free/busy responses
    displaynames = {}
    for n in names:
        displaynames[n] = get_display_name(n)
    sorted_names = sorted(names, key=lambda x: (x.split('_')[0], 
                                                displaynames[x]))
    sorted_names = list(n for n in sorted_names if displaynames[n])
    return dict(names=sorted_names, events=events, displaynames=displaynames)

last_freebusy_info = defaultdict(lambda: None)

@view_config(route_name='freebusy')
def freebusy_view(request):
    global last_freebusy_info
    domain = request.registry.settings['ews_domain']
    username = request.registry.settings['ews_user']
    password = request.registry.settings['ews_pass']
    dl = request.registry.settings['ews_dl']
    try:
        client = connect(domain, username, password)
        info = freebusy(client,
                        dl)
        last_freebusy_info[dl] = info
    except Exception, e:
        log.warn(e)
        log.warn("LOGIN AS %s %s", domain, username)
        info = last_freebusy_info[dl]
    request.response.content_type = 'application/json'
    request.response.body = json.dumps(info,
               cls=DateTimeEncoder, sort_keys=True, indent=2)
    return request.response

if __name__ == "__main__":
    # Pass desired distribution list as first and only argument.
    import sys
    domain = os.environ.get('EWS_DOMAIN')
    username = os.environ.get('EWS_USER')
    password = os.environ.get('EWS_PASS')
    client = connect(domain, username, password)
    sys.stdout.write(json.dumps(freebusy(client, sys.argv[1]),
               cls=DateTimeEncoder, sort_keys=True, indent=2))

