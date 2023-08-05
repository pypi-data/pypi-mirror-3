"""
tests.test_connections
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from dingus import Dingus

from nydus.db import Cluster, create_cluster
from nydus.db.routers import BaseRouter
from nydus.db.backends import BaseConnection

from . import BaseTest, dingus_calls_to_dict

class DummyConnection(BaseConnection):
    def __init__(self, resp='foo', **kwargs):
        self.resp = resp
        super(DummyConnection, self).__init__(**kwargs)

    def foo(self, *args, **kwargs):
        return self.resp

class DummyRouter(BaseRouter):
    def get_db(self, cluster, func, key=None, *args, **kwargs):
        # Assume first argument is a key
        if key == 'foo':
            return [1]
        return [0]

class ClusterTest(BaseTest):
    def test_create_cluster(self):
        c = create_cluster({
            'engine': DummyConnection,
            'router': DummyRouter,
            'hosts': {
                0: {'resp': 'bar'},
            }
        })
        self.assertEquals(len(c), 1)
        
    def test_init(self):
        c = Cluster(
            hosts={0: BaseConnection(num=1)},
        )
        self.assertEquals(len(c), 1)
    
    def test_proxy(self):
        c = DummyConnection(num=1, resp='bar')
        p = Cluster(
            hosts={0: c},
        )
        self.assertEquals(p.foo(), 'bar')

    def test_disconnect(self):
        c = Dingus()
        p = Cluster(
            hosts={0: c},
        )
        p.disconnect()
        calls = dingus_calls_to_dict(c.calls)
        self.assertTrue('disconnect' in calls)

    def test_with_router(self):
        c = DummyConnection(num=0, resp='foo')
        c2 = DummyConnection(num=1, resp='bar')

        # test dummy router
        r = DummyRouter()
        p = Cluster(
            hosts={0: c, 1: c2},
            router=r,
        )
        self.assertEquals(p.foo(), 'foo')
        self.assertEquals(p.foo('foo'), 'bar')

        # test default routing behavior
        p = Cluster(
            hosts={0: c, 1: c2},
        )
        self.assertEquals(p.foo(), ['foo', 'bar'])
        self.assertEquals(p.foo('foo'), ['foo', 'bar'])

    def test_get_conn(self):
        c = DummyConnection(alias='foo', num=0, resp='foo')
        c2 = DummyConnection(alias='foo', num=1, resp='bar')

        # test dummy router
        r = DummyRouter()
        p = Cluster(
            hosts={0: c, 1: c2},
            router=r,
        )
        self.assertEquals(p.get_conn(), c)
        self.assertEquals(p.get_conn('foo'), c2)

        # test default routing behavior
        p = Cluster(
            hosts={0: c, 1: c2},
        )
        self.assertEquals(p.get_conn(), [c, c2])
        self.assertEquals(p.get_conn('foo'), [c, c2])
    
    def test_map(self):
        c = DummyConnection(num=0, resp='foo')
        c2 = DummyConnection(num=1, resp='bar')

        # test dummy router
        r = DummyRouter()
        p = Cluster(
            hosts={0: c, 1: c2},
            router=r,
        )
        with p.map() as conn:
            foo = conn.foo()
            bar = conn.foo('foo')
            self.assertEquals(foo, None)
            self.assertEquals(bar, None)

        self.assertEquals(bar, 'bar')
        self.assertEquals(foo, 'foo')

        # test default routing behavior
        p = Cluster(
            hosts={0: c, 1: c2},
        )
        with p.map() as conn:
            foo = conn.foo()
            bar = conn.foo('foo')
            self.assertEquals(foo, None)
            self.assertEquals(bar, None)

        self.assertEquals(foo, ['foo', 'bar'])
        self.assertEquals(bar, ['foo', 'bar'])


class FlakeyConnection(DummyConnection):

    retryable_exceptions = [Exception]

    def foo(self):
        if hasattr(self, 'already_failed'):
            super(FlakeyConnection, self).foo()
        else:
            self.already_failed = True
            raise Exception('boom!')


class RetryableRouter(DummyRouter):
    retryable = True

    def __init__(self):
        self.kwargs_seen = []
        super(RetryableRouter, self).__init__()

    def get_db(self, cluster, func, key=None, *args, **kwargs):
        self.kwargs_seen.append(kwargs)
        return [0]


class ImposterRouter(DummyRouter):
    retryable = True

    def get_db(self, cluster, func, key=None, *args, **kwargs):
        return range(5)


class ScumbagConnection(DummyConnection):

    retryable_exceptions = [Exception]

    def foo(self):
        raise Exception("Says it's a connection / Never actually connects.")


class RetryClusterTest(BaseTest):

    def build_cluster(self, connection=FlakeyConnection, router=RetryableRouter):
        return create_cluster({
            'engine': connection,
            'router': router,
            'hosts': {
                0: {'resp': 'bar'},
            }
        })

    def test_retry_router_when_receives_error(self):
        cluster = self.build_cluster()

        cluster.foo()
        self.assertEquals({'retry_for': 0}, cluster.router.kwargs_seen.pop())

    def test_protection_from_infinate_loops(self):
        cluster = self.build_cluster(connection=ScumbagConnection)
        self.assertRaises(Exception, cluster.foo)

    def test_retryable_router_returning_multiple_dbs_raises_ecxeption(self):
        cluster = self.build_cluster(router=ImposterRouter)
        self.assertRaisesRegexp(Exception, 'only supported by routers',
                                cluster.foo)
