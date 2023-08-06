import datetime

from mozautoeslib import ESLib


class AutologBuildLog(object):

  def __init__(self, machine=None, builder=None, revision=None,
               starttime=None, buildid=None, platform=None, tree=None,
               success=None, buildtype=None, buildname=None, total=None,
               steps=None, server=None, index='autolog', doc_type='buildlogs',
               id=None, logurl=None, buildername=None, **kw):
    self.machine = machine
    self.builder = builder
    self.revision = revision
    self.starttime = starttime
    self.buildid = buildid
    self.platform = platform
    self.tree = tree
    self.success = success
    self.buildtype = buildtype
    self.buildname = buildname
    self.total = total
    self.steps = steps
    self.id = id
    self.logurl = logurl
    self.buildername = buildername
    self.kw = kw

    if server:
      self.server = str(server) 
    else:
      self.server = 'elasticsearch1.metrics.scl3.mozilla.com:9200'

    if isinstance(index, list) and len(index) == 1:
      index = [index[0], index[0]]
    if isinstance(index, basestring):
      index = [index, index]

    self.read_index = index[0]
    self.write_index = index[1]

    self.doc_type = doc_type

    if self.starttime:
      self.date = datetime.datetime.utcfromtimestamp(int(self.starttime)).strftime('%Y-%m-%d')
    else:
      self.date = datetime.datetime.now().strftime('%Y-%m-%d')

  def _add_doc(self, doc, doc_type, id=None):
    """add a document to elasticsearch"""

    self.eslib.doc_type = doc_type
    result = self.eslib.add_doc(doc, id)

    if not 'ok' in result or not result['ok'] or not '_id' in result:
      raise Exception(json.dumps(result))

    return result['_id']

  def _to_json(self):
    data = {
      'machine': self.machine,
      'date': self.date,
      'builder': self.builder,
      'buildername': self.buildername,
      'revision': self.revision,
      'starttime': self.starttime,
      'buildid': self.buildid,
      'platform': self.platform,
      'tree': self.tree,
      'success': self.success,
      'buildtype': self.buildtype,
      'buildname': self.buildname,
      'total': self.total,
      'logurl': self.logurl,
      'steps': self.steps
    }
    for key in self.kw:
      data[key] = self.kw[key]
    return data

  def submit(self):
    self.eslib = ESLib(self.server, [self.read_index, self.write_index])

    json = self._to_json()
    build_id = self._add_doc(json, self.doc_type, self.id)
    if not self.id:
      self.id = build_id
