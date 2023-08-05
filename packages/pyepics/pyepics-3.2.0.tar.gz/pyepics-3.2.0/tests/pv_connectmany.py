import epics
import time
import debugtime

dt = debugtime.debugtime()
dt.add('test of fast connection to many PVs')
pvnames = []
pvs = []
for line  in open('PVlist.txt','r').readlines():
    pvnames.append(line[:-1])


dt.add('Read PV list:  Will connect to %i PVs' % len(pvnames))

for name in pvnames:
    p = epics.PV(name)
    pvs.append(p)
    

time.sleep(0.1)

for p in pvs:
    if not p.connected:
        p.connect()

print '======================='
for p in pvs:
    if not p.connected:
        print p


time.sleep(0.01)

