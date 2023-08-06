from cothread.catools import caget as co_caget

from epics import ca
from epics import caget as py_caget, PV
import time


pvname_list = []
for i in open('PVlist.txt', 'r').readlines():
    pvname_list.append(i[:-1])
pvname_list = pvname_list[:200]
NRUNS = 10

def use_cothread(pvname_list, nruns):
    t0 = time.time()
    for i in range(nruns):
        vals = co_caget(pvname_list)
    print 'cothread get(pvlist) ', len(vals), nruns, time.time()-t0

# vals = []
# ;pvdata = {}
# for i in flist:
#     name = i[:-1]
#     chid = ca.create_channel(name, connect=False, auto_cb=False)
#     pvdata[name] = [chid, None]
# 
# for name, data in pvdata.items():
#     ca.connect_channel(data[0])
# 
# ca.poll()
# for name, data in pvdata.items():
#     ca.get(data[0], wait=False)
# 
# ca.poll()
# for name, data in pvdata.items():
#     val = ca.get_complete(data[0])
#     pvdata[name][1] = val
# 
# 
# for name, data in pvdata.items():
#     print name, data
        
def use_pvs(pvname_list, nruns):
    t0 = time.time()
    pvs = [PV(pname) for pname in pvname_list]
    
    for i in range(nruns):
        vals = [p.get() for p in pvs]
 
    print 'pyepics PV.get()', len(vals), nruns, time.time()-t0

use_pvs(pvname_list, 10)
# use_cothread(pvname_list, 10)

