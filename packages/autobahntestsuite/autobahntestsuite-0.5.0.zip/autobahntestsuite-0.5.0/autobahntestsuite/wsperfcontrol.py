###############################################################################
##
##  Copyright 2012 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys, json, pprint

from twisted.internet import reactor

from autobahn.websocket import WebSocketClientFactory, \
                               WebSocketClientProtocol, \
                               connectWS

from autobahn.util import newid


class WsPerfControlProtocol(WebSocketClientProtocol):

   WSPERF_CMD = """message_test:uri=%(uri)s;token=%(token)s;size=%(size)d;count=%(count)d;quantile_count=%(quantile_count)d;timeout=%(timeout)d;binary=%(binary)s;sync=%(sync)s;rtts=%(rtts)s;correctness=%(correctness)s;"""

   def sendNext(self):
      if self.current == len(self.tests):
         return True
      test = self.tests[self.current]
      cmd = self.WSPERF_CMD % test
      if self.factory.debugWsPerf:
         print "Starting test for testee %s" % test['name']
         print cmd
      sys.stdout.write('.')
      self.sendMessage(cmd)
      self.current += 1

   def setupTests(self):
      for server in self.factory.spec['servers']:
         for size in self.factory.spec['sizes']:
            id = newid()
            test = {'uri': server['uri'].encode('utf8'),
                    'name': server['name'].encode('utf8'),
                    'count': size[0],
                    'quantile_count': self.factory.spec['options']['quantile_count'],
                    'timeout': size[2],
                    'binary': 'true' if size[3] else 'false',
                    'sync': 'true' if size[4] else 'false',
                    'rtts': 'true' if self.factory.spec['options']['rtts'] else 'false',
                    'correctness': 'exact' if size[5] else 'length',
                    'size': size[1],
                    'token': id}
            self.tests.append(test)
            self.testdefs[id] = test
      sys.stdout.write("Running %d tests against %d servers: " % (len(self.factory.spec['sizes']), len(self.factory.spec['servers'])))

   def toMicroSec(self, value):
      return ("%." + str(self.factory.digits) + "f") % round(float(value), self.factory.digits)

   def getMicroSec(self, result, field):
      return self.toMicroSec(result['data'][field])

   def onTestsComplete(self):
      print " All tests finished."
      print
      if self.factory.debugWsPerf:
         self.pp.pprint(self.testresults)
      if self.factory.outfile:
         outfile = open(self.factory.outfile, 'w')
      else:
         outfile = sys.stdout
      outfile.write(self.factory.sep.join(['name', 'outcome', 'count', 'size', 'min', 'median', 'max', 'avg', 'stddev']))

      quantile_count = self.factory.spec['options']['quantile_count']

      for i in xrange(quantile_count):
         outfile.write(self.factory.sep)
         outfile.write("q%d" % i)
      outfile.write('\n')
      for test in self.tests:
         result = self.testresults[test['token']]

         outcome = result['data']['result']
         if outcome == 'connection_failed':
            outfile.write(self.factory.sep.join([test['name'], 'UNREACHABLE']))
            outfile.write('\n')
         elif outcome == 'time_out':
            outfile.write(self.factory.sep.join([test['name'], 'TIMEOUT']))
            outfile.write('\n')
         elif outcome == 'fail':
            outfile.write(self.factory.sep.join([test['name'], 'FAILED']))
            outfile.write('\n')
         elif outcome == 'pass':
            outfile.write(self.factory.sep.join([str(x) for x in [test['name'],
                                                                 'PASSED',
                                                                 test['count'],
                                                                 test['size'],
                                                                 self.getMicroSec(result, 'min'),
                                                                 self.getMicroSec(result, 'median'),
                                                                 self.getMicroSec(result, 'max'),
                                                                 self.getMicroSec(result, 'avg'),
                                                                 self.getMicroSec(result, 'stddev'),
                                                                 ]]))
            for i in xrange(quantile_count):
               outfile.write(self.factory.sep)
               if result['data'].has_key('quantiles'):
                  outfile.write(self.toMicroSec(result['data']['quantiles'][i][1]))
            outfile.write('\n')
         else:
            raise Exception("unknown case outcome '%s'" % outcome)
      if self.factory.outfile:
         print "Test data written to %s." % self.factory.outfile
      reactor.stop()

   def onOpen(self):
      self.pp = pprint.PrettyPrinter(indent = 3)
      self.tests = []
      self.testdefs = {}
      self.testresults = {}
      self.current = 0
      self.setupTests()
      self.sendNext()

   def onMessage(self, msg, binary):
      if not binary:
         try:
            o = json.loads(msg)
            if o['type'] == u'test_complete':
               if self.sendNext():
                  self.onTestsComplete()
            elif o['type'] == u'test_data':
               if self.factory.debugWsPerf:
                  self.pp.pprint(o)
               self.testresults[o['token']] = o
         except ValueError, e:
            pass


class WsPerfControlFactory(WebSocketClientFactory):

   protocol = WsPerfControlProtocol
