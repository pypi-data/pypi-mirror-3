from epics import ca

pvnamelist = [] # read_list_pvs()

for line  in open('fastconn_pvlist.txt','r').readlines():
    pvnamelist.append(line[:-1])

pvnamelist = pvnamelist[:20]
pvdata = {}

for name in pvnamelist:
    chid = ca.create_channel(name, connect=False) # note 1
    pvdata[name] = [chid, None]
    
ca.poll()  # polls for *all* channels

for name, data in pvdata.items():
    ca.connect_channel(data[0])

ca.poll()

for name, data in pvdata.items():
    ca.get(data[0], wait=False)  # note 2

ca.poll()

for name, data in pvdata.items():
    val = ca.get_complete(data[0])
    pvdata[name][1] = val

for name, data in pvdata.items():
    print name, data[1]
