from mozautoeslib import ESLib
try:
  import json
except:
  import simplejson as json
import re
import sys
import datetime

if __name__ == '__main__':
  eslib = ESLib('elasticsearch1.metrics.sjc1.mozilla.com:9200', 'bugs', 'bug_info')

  dupefinder = []

  while len(dupefinder) != 1:

    result = eslib.query({'date': '2011-04-13'})
    print "%d hits" % len(result)

    for bug in result:
      print 'checking bug ', bug['bug']
      dupefinder = eslib.query(bug, withSource=True)
      if len(dupefinder) > 1:
        print json.dumps(dupefinder[0], indent=2)
        print json.dumps(dupefinder[1], indent=2)
        eslib.delete_doc(dupefinder[0]['_id'])
        eslib.refresh_index()
        print '-----------------------------------------------------'

