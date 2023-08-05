import time
import logging
from cgi import escape

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publication.zopepublication import ZopePublication, Cleanup
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import adapts, queryUtility
from zope.interface import Interface
from zope.security.proxy import removeSecurityProxy
from zope.cachedescriptors.property import Lazy
from ZODB.utils import p64, u64, tid_repr, oid_repr
from ZODB.Connection import Connection
from ZODB.interfaces import IDatabase
from persistent import Persistent
from persistent.TimeStamp import TimeStamp
import transaction
import simplejson

from zodbbrowser import __version__, __homepage__
from zodbbrowser.interfaces import IObjectHistory, IValueRenderer
from zodbbrowser.state import ZodbObjectState
from zodbbrowser.diff import compareDictsHTML


log = logging.getLogger("zodbbrowser")


class ZodbHelpView(BrowserView):
    """Zodb help view"""

    version = __version__
    homepage = __homepage__


class ZodbObjectAttribute(object):

    def __init__(self, name, value, tid=None):
        self.name = name
        self.value = value
        self.tid = tid

    def rendered_name(self):
        return IValueRenderer(self.name).render(self.tid)

    def rendered_value(self):
        return IValueRenderer(self.value).render(self.tid)

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self.name,
                                   self.value, self.tid)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return (self.name, self.value, self.tid) == (other.name, other.value,
                                                     other.tid)

    def __ne__(self, other):
        return not self.__eq__(other)


class ZodbInfoView(BrowserView):
    """Zodb browser view"""

    adapts(Interface, IBrowserRequest)

    template = ViewPageTemplateFile('templates/zodbinfo.pt')
    confirmation_template = ViewPageTemplateFile('templates/confirm_rollback.pt')

    version = __version__
    homepage = __homepage__

    @property
    def readonly(self):
        jar = self.jar
        return jar.isReadOnly()

    def __call__(self):
        try:
            return self.render()
        finally:
            if self.readonly:
                resources = transaction.get()._resources
                if resources:
                    msg = ["Aborting changes made to:"]
                    for r in resources:
                        if isinstance(r, Connection):
                            for o in r._registered_objects:
                                msg.append("  oid=%s %s" % (oid_repr(o._p_oid), repr(o)))
                        else:
                            msg.append("  %s" % repr(r))
                    log.warning("\n".join(msg))
                transaction.abort()

    def render(self):
        self.obj = self.selectObjectToView()
        self.history = IObjectHistory(self.obj)
        self.latest = True
        if self.request.get('tid'):
            self.state = ZodbObjectState(self.obj,
                                         p64(int(self.request['tid'], 0)),
                                         _history=self.history)
            self.latest = False
        else:
            self.state = ZodbObjectState(self.obj, _history=self.history)

        if 'CANCEL' in self.request:
            self._redirectToSelf()
            return ''

        if 'ROLLBACK' in self.request:
            rtid = p64(int(self.request['rtid'], 0))
            self.requestedState = self._tidToTimestamp(rtid)
            if self.request.get('confirmed') == '1':
                self.history.rollback(rtid)
                transaction.get().note('Rollback to old state %s'
                                        % self.requestedState)
                self._redirectToSelf()
                return ''
            # will show confirmation prompt
            return self.confirmation_template()

        return self.template()

    def _redirectToSelf(self):
        self.request.response.redirect(self.getUrl())

    def selectObjectToView(self):
        obj = None
        if 'oid' not in self.request:
            obj = self.findClosestPersistent()
            # Sanity check: if we're running in standalone mode,
            # self.context is a Folder in the just-created MappingStorage,
            # which we're not interested in.
            if obj is not None and obj._p_jar is not self.jar:
                obj = None
        if obj is None:
            if 'oid' in self.request:
                oid = int(self.request['oid'], 0)
            else:
                oid = self.getRootOid()
            obj = self.jar.get(p64(oid))
        return obj

    def findClosestPersistent(self):
        obj = removeSecurityProxy(self.context)
        while not isinstance(obj, Persistent):
            try:
                obj = obj.__parent__
            except AttributeError:
                return None
        return obj

    def getRequestedTid(self):
        if 'tid' in self.request:
            return self.request['tid']
        else:
            return None

    def getRequestedTidNice(self):
        if 'tid' in self.request:
            return self._tidToTimestamp(p64(int(self.request['tid'], 0)))
        else:
            return None

    def getObjectId(self):
        return self.state.getObjectId()

    def getObjectType(self):
        cls = getattr(self.obj, '__class__', None)
        if type(self.obj) is not cls:
            return '%s - %s' % (type(self.obj), cls)
        else:
            return str(cls)

    def getStateTid(self):
        return u64(self.state.tid)

    def getStateTidNice(self):
        return self._tidToTimestamp(self.state.tid)

    def getRootOid(self):
        root = self.jar.root()
        try:
            root = root[ZopePublication.root_name]
        except KeyError:
            pass
        return u64(root._p_oid)

    def locate_json(self, path):
        return simplejson.dumps(self.locate(path))

    @Lazy
    def jar(self):
        db = queryUtility(IDatabase, name='<target>')
        if db is not None:
            conn = db.open()
            self.request.hold(Cleanup(conn.close))
            return conn
        try:
            return self.request.annotations['ZODB.interfaces.IConnection']
        except (KeyError, AttributeError):
            obj = self.findClosestPersistent()
            if obj is None:
                raise Exception("ZODB connection not available for this request")
            return obj._p_jar

    def locate(self, path):
        not_found = object() # marker

        # our current position
        #   partial -- path of the last _persistent_ object
        #   here -- path of the last object traversed
        #   oid -- oid of the last _persistent_ object
        #   obj -- last object traversed
        partial = here = '/'
        oid = self.getRootOid()
        obj = self.jar.get(p64(oid))

        steps = path.split('/')

        if steps and steps[0]:
            # 0x1234/sub/path -> start traversal at oid 0x1234
            try:
                oid = int(steps[0], 0)
            except ValueError:
                pass
            else:
                partial = here = hex(oid)
                try:
                    obj = self.jar.get(p64(oid))
                except KeyError:
                    oid = self.getRootOid()
                    return dict(error='Not found: %s' % steps[0],
                                partial_oid=oid,
                                partial_path='/',
                                partial_url=self.getUrl(oid))
                steps = steps[1:]

        for step in steps:
            if not step:
                continue
            if not here.endswith('/'):
                here += '/'
            here += step.encode('utf-8')
            try:
                child = obj[step]
            except Exception:
                child = getattr(obj, step, not_found)
                if child is not_found:
                    return dict(error='Not found: %s' % here,
                                partial_oid=oid,
                                partial_path=partial,
                                partial_url=self.getUrl(oid))
            obj = child
            if isinstance(obj, Persistent):
                partial = here
                oid = u64(obj._p_oid)
        if not isinstance(obj, Persistent):
            return dict(error='Not persistent: %s' % here,
                        partial_oid=oid,
                        partial_path=partial,
                        partial_url=self.getUrl(oid))
        return dict(oid=oid,
                    url=self.getUrl(oid))

    def getUrl(self, oid=None, tid=None):
        if oid is None:
            oid = self.getObjectId()
        url = "@@zodbbrowser?oid=0x%x" % oid
        if tid is None and 'tid' in self.request:
            url += "&tid=" + self.request['tid']
        elif tid is not None:
            url += "&tid=0x%x" % tid
        return url

    def getBreadcrumbs(self):
        breadcrumbs = []
        state = self.state
        seen_root = False
        while True:
            url = self.getUrl(state.getObjectId())
            if state.isRoot():
                breadcrumbs.append(('/', url))
                seen_root = True
            else:
                if breadcrumbs:
                    breadcrumbs.append(('/', None))
                if not state.getName() and state.getParentState() is None:
                    # not using hex() because we don't want L suffixes for
                    # 64-bit values
                    breadcrumbs.append(('0x%x' % state.getObjectId(), url))
                    break
                breadcrumbs.append((state.getName() or '???', url))
            state = state.getParentState()
            if state is None:
                if not seen_root:
                    url = self.getUrl(self.getRootOid())
                    breadcrumbs.append(('/', None))
                    breadcrumbs.append(('...', None))
                    breadcrumbs.append(('/', url))
                break
        return breadcrumbs[::-1]

    def getPath(self):
        return ''.join(name for name, url in self.getBreadcrumbs())

    def getBreadcrumbsHTML(self):
        html = []
        for name, url in self.getBreadcrumbs():
            if url:
                html.append('<a href="%s">%s</a>' % (escape(url, True),
                                                     escape(name)))
            else:
                html.append(escape(name))
        return ''.join(html)

    def listAttributes(self):
        attrs = self.state.listAttributes()
        if attrs is None:
            return None
        return [ZodbObjectAttribute(name, value, self.state.requestedTid)
                for name, value in sorted(attrs)]

    def listItems(self):
        items = self.state.listItems()
        if items is None:
            return None
        return [ZodbObjectAttribute(name, value, self.state.requestedTid)
                for name, value in items]

    def _loadHistoricalState(self):
        results = []
        for d in self.history:
            try:
                interp = ZodbObjectState(self.obj, d['tid'],
                                         _history=self.history)
                state = interp.asDict()
                error = interp.getError()
            except Exception, e:
                state = {}
                error = '%s: %s' % (e.__class__.__name__, e)
            results.append(dict(state=state, error=error))
        results.append(dict(state={}, error=None))
        return results

    def listHistory(self):
        """List transactions that modified a persistent object."""
        state = self._loadHistoricalState()
        results = []
        for n, d in enumerate(self.history):
            short = (str(time.strftime('%Y-%m-%d %H:%M:%S',
                                       time.localtime(d['time']))) + " "
                     + d['user_name'] + " "
                     + d['description'])
            url = self.getUrl(tid=u64(d['tid']))
            current = (d['tid'] == self.state.tid and
                       self.state.requestedTid is not None)
            curState = state[n]['state']
            oldState = state[n + 1]['state']
            diff = compareDictsHTML(curState, oldState, d['tid'])

            results.append(dict(short=short, utid=u64(d['tid']),
                                href=url, current=current,
                                error=state[n]['error'],
                                diff=diff, **d))

        # number in reverse order
        for i in range(len(results)):
            results[i]['index'] = len(results) - i

        return results

    def _tidToTimestamp(self, tid):
        if isinstance(tid, str) and len(tid) == 8:
            return str(TimeStamp(tid))
        return tid_repr(tid)
