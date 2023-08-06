import os
from multiprocessing.queues import Empty, Queue


class QueueFeeder(object):
    '''A queue which can be used with epoll'''    
    def __init__(self, queue=None, address=None):
        self._queue = queue if queue is not None else Queue()
        self.socket = server_socket()

    def put(self, obj):
        self._queue.put(obj)
        self.socket.send('.')

    def get(self, block=True):
        obj = self._queue.get(block=block)
        self.socket.read(1)
        return obj

    def fileno(self):
        return self.socket.fileno()
    
    
class QueueClient(object):
    
    def __init__(self, queue, socket=None):
        self._queue = queue
        self.socket = socket
        
    
        
    
class TestSelectableQueue(object):
    def test_queues_object(self):
        q = SelectableQueue()
        q.put(1)
        q.put(2)
        assert q.get() == 1
        assert q.get() == 2
        with py.test.raises(Empty):
            q.get(False)
    
    def test_not_selectable_when_empty(self):
        q = SelectableQueue()
        r, _, _ = select([q], [], [], 0)
        assert r == []

    def test_selectable(self):
        q = SelectableQueue()
        q.put(1)
        r, _, _ = select([q], [], [], 0)
        assert r == [q]

    def test_not_selectable_after_emptied(self):
        q = SelectableQueue()
        q.put(1)
        q.get()
        r, _, _ = select([q], [], [], 0)
        assert r == []
