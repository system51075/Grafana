#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import json
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        container = ''
        freeme = ''
        useme = ''
        state = ''
        task = ''

        j = dict()

        # print type(j)

        if self.path == '/metrics':
            urls = [  # -> FOR NODE STATIC
                'http://11.11.22.56:8088/ws/v1/cluster/nodes',
                'http://11.11.22.56:8088/ws/v1/cluster/appstatistics',
                'http://11.11.22.56:50070/jmx?qry=Hadoop:service=NameNode,name=FSNamesystemState'
                    ,
                'http://11.11.22.56:50070/jmx?qry=java.lang:type=Memory'
                    ,
                'http://11.11.22.56:50070/jmx?qry=Hadoop:service=NameNode,name=JvmMetrics'
                    ,
                'http://11.11.22.56:8088/ws/v1/cluster/metrics',
                ]

                     #  -> FOR APP

            gc = ''

            for url in urls:
                f = urllib.urlopen(url)
                data = json.load(f)

                # print data

                d1 = dict()
                if 'beans' in data:
                    for (idx, val) in enumerate(data['beans']):
                        d1.update(val)
                    for i in d1:
                        if type(d1[i]) == int or type(d1[i]) == float:
                            mt = 'HD_GC_' + str(i) + '{val="' + str(i) \
                                + '"} ' + str(d1[i]) + '\n'
                            gc += mt

                j.update(data)

            # print type(j)

            for i in j['nodes']['node']:
                node = str.replace(str.replace(str(i['nodeHTTPAddress'
                                   ]), 'data-node', ''), ':8042', '')
                if str(i['state']) == 'RUNNING':
                    x = 1
                else:
                    x = 0
                mt_availMemoryMB = 'HD_availMemoryMB{node="' + node \
                    + '",code="5xx"} ' + str(i['availMemoryMB']) + '\n'
                mt_numContainers = 'HD_numContainers{node="' + node \
                    + '",code="5xx"} ' + str(i['numContainers']) + '\n'
                mt_usedMemoryMB = 'HD_usedMemoryMB{node="' + node \
                    + '",code="5xx"} ' + str(i['usedMemoryMB']) + '\n'
                mt_state = 'HD_state{node="' + node + '",code="5xx"} ' \
                    + str(x) + '\n'
                freeme += mt_availMemoryMB
                container += mt_numContainers
                useme += mt_usedMemoryMB
                state += mt_state
                node = '#HDFS METRICS - toanpt3' + '\n' + freeme \
                    + container + useme + state
            for i in j['appStatInfo']['statItem']:
                mt_taskinf = 'HD_task{state="' + str(i['state']) \
                    + '",code="5xx"} ' + str(i['count']) + '\n'
                task += mt_taskinf
            t = ''
            for i in j['clusterMetrics']:

                # print j['clusterMetrics'][i]

                mt2 = 'HD_MT_' + str(i) + '{val="' + str(i) + '"} ' \
                    + str(j['clusterMetrics'][i]) + '\n'
                
                t += mt2


            # print  task
                # HD_task{state="ACCEPTED",code="5xx"} 1
                # HD_task{state="RUNNING",code="5xx"} 28

            total = node + task + gc + t
            self.wfile.write(total)


HTTPServer(('', 8089), MyHandler).serve_forever()
