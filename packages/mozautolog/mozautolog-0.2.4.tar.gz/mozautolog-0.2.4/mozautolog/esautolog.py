import json
import re

from mozautolog import AutologTestGroup
from mozautoeslib import ESLib


class ESAutologTestGroup(AutologTestGroup):
  """A subclass of AutologTestGroup which submits results directly to
     ElasticSearch.
  """

  def __init__(self, **kwargs):
    AutologTestGroup.__init__(self, **kwargs)
    self.eslib = ESLib(self.server, [self.read_index, self.write_index])

  def _add_doc(self, doc, doc_type, id=None):
    """add a document to elasticsearch"""

    self.eslib.doc_type = doc_type
    result = self.eslib.add_doc(doc, id)

    if not 'ok' in result or not result['ok'] or not '_id' in result:
      raise Exception(json.dumps(result))

    return result['_id']

  def _generate_testrun(self):
    """generate a testrun value for this testgroup"""

    if not self.product or not self.product.buildtype or \
       not self.product.revision or not self.product.tree or \
       not self.testgroup or not self.os:
      return

    # First, check if an item with this id alredy exists in the db, and 
    # if has a testrun attribute; if so, just re-use it.
    if self.id:
      try:
        query = self.eslib.query(include={ 'testgroup_id': self.id },
                                 doc_type = [self.doc_type])
        for testgroup in query:
          if 'testrun' in testgroup and testgroup['testrun']:
            self.testrun = testgroup['testrun']
            return
      except:
        # no matching records in ES
        pass

    # Now check all possible matches for other instances of this testrun.
    include = {'buildtype': self.product.buildtype,
               'revision': self.product.revision,
               'tree': self.product.tree,
               'testgroup': self.testgroup,
               'os': self.os
              }
    query = self.eslib.query(include=include,
                             doc_type = [self.doc_type])
    testruns = []
    for testgroup in query:
      if 'testrun' in testgroup and testgroup['testrun']:
        testruns.append(testgroup['testrun'])

    # Look at all the existing testrun values, and return a new value
    # which is 1 greater than the largest existing value.
    try:
      if len(testruns):
        testruns = sorted(testruns, key=lambda x: int(x[x.find('.') + 1:]))
        m = re.search('.*?\.(\d+)', testruns[-1])
        if m:
          self.testrun = "%s.%d" % (self.product.revision, (int(m.group(1)) + 1))
          return
    except:
      pass

    self.testrun = "%s.1" % (self.product.revision)

  def submit(self):
    if not self.testrun:
      self._generate_testrun()

    if self.dirty:
      json = self._to_json()
      testgroup_id = self._add_doc(json, self.doc_type, self.id)
      if not self.id:
        self.id = testgroup_id
        json.update({ 'testgroup_id': self.id })
        self._add_doc(json, self.doc_type, self.id)
      self.dirty = False

    for testsuite in self.testsuites:
      if testsuite.dirty:
        testsuite.testgroup_id = self.id
        json = testsuite._to_json()
        self._add_common_properties(json)
        testsuite_id = self._add_doc(json, self.testsuite_doc_type, testsuite.id)

        if not testsuite.id:
          testsuite.id = testsuite_id
          json.update({ 'testsuite_id': testsuite.id })
          self._add_doc(json, self.testsuite_doc_type, testsuite.id)

        for testfailure in testsuite.testfailures:
          if testfailure.dirty:
            testfailure.testgroup_id = self.id
            testfailure.testsuite_id = testsuite.id
            json = testfailure._to_json()
            self._add_common_properties(json)
            testfailure_id = self._add_doc(json, self.testfailure_doc_type, testfailure.id)
            if not testfailure.id:
              testfailure.id = testfailure_id
            testfailure.dirty = False

        if testsuite.testpasses:
          try:
            json = { }
            self._add_common_properties(json)
            for testpass in testsuite.testpasses:
              json[testpass.test] = int(testpass.duration)
            self._add_doc(json, testpass.doc_type)
          except:
            pass

        for perfdata in testsuite.perfdata:
          if perfdata.dirty:
            perfdata.testgroup_id = self.id
            perfdata.testsuite_id = testsuite.id
            json = perfdata._to_json()
            self._add_common_properties(json)
            json['testsuite'] = testsuite.testsuite
            perfdata_id = self._add_doc(json, perfdata.doc_type, perfdata.id)
            if not perfdata.id:
              perfdata.id = perfdata_id
            perfdata.dirty = False

        testsuite.dirty = False

    for talossuite in self.talossuites:
      if talossuite.dirty:
        talossuite.testgroup_id = self.id
        json = talossuite._to_json()
        self._add_common_properties(json)
        self._add_doc(json, self.testsuite_doc_type, talossuite.id)

        if not talossuite.id:
          talossuite.id = talossuite_id
          json.update({ 'testsuite_id': talossuite.id })
          self._add_doc(json, self.testsuite_doc_type, talossuite.id)

        talossuite.dirty = False
