import sys
import time
import stmplib
import epics

pvname = '13IDC::minDataMBuf'
trippoint = 10.0

mail_to    = ('park@hpcat.aps.anl.gov', 'park@hpcat.aps.anl.gov')
mail_from  = 'gsecars@cars.uchicago.edu'
subj       = "Memory problem"
greet      = "Hi,"
sig        = "That is all.\n--Bob"


def alarmHandler(pvname=None, value=None, char_value=None,
                 comparison=None,trip_point=None,**kw):

    s = smtplib.SMTP('millenia.cars.aps.anl.gov')
    mail_msg = ("From: %s\r\nSubject: %s\r\n%s\n   %s%s" %
                (mail_from, subj, greet, text, sig))
    
    
    s.sendmail(mail_from,mail_to, mail_msg)
    s.quit()

    #sys.stdout.write( 'Alarm! %s at %s ! \n' %( pvname,  time.ctime()))
    #sys.stdout.write( 'Alarm  Comparison =%s  \n' %( comparison))
    #sys.stdout.write( 'Alarm  TripPoint      =%s  \n' %( repr(trip_point)))
    #sys.stdout.write( 'Current Value         =%s  \n' %(char_value))    

epics.Alarm(pvname = pvname, 
            comparison = '<',
            trip_point = trippoint,
            callback = alarmHandler,
            alert_delay=120.0)


while True:
    try:
        epics.ca.poll()
    except KeyboardInterrupt:
        break
