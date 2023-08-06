from pprint import pprint
import unittest

from ginsfsm.gobj import (
    GObj,
    EventNotAcceptedError,
    EventError,
    StateError,
    DestinationError,
    ParentError,
    GObjError,
    QueueError,
    )

########################################################
#       Child
########################################################
def ac_query_and_direct_response(self, event):
    data = event.data
    if data == 'query1':
        return self.send_event(self.parent, 'EV_RESP_OK', response='OK')
    else:
        return self.send_event(self.parent, 'EV_RESP_ERROR', response='ERROR')

def ac_query_and_broadcast_response(self, event):
    data = event.data
    if data == 'query3':
        self.broadcast_event('EV_RESP_OK', response='OK')
    else:
        self.broadcast_event('EV_RESP_ERROR', response='ERROR')


FSM_CHILD = {
    'output_list': ('EV_RESP_OK', 'EV_RESP_ERROR'),
    'event_list': ('EV_QUERY_BY_DIRECT', 'EV_QUERY_BY_BROADCAST'),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_QUERY_BY_DIRECT',    ac_query_and_direct_response,    None),
            ('EV_QUERY_BY_BROADCAST', ac_query_and_broadcast_response, None),
        ),
    }
}

class ChildGClass(GObj):
    def __init__(self):
        GObj.__init__(self, FSM_CHILD)
        self.start_up()

    def start_up(self):
        ''' Create gobj childs, initialize something...
        '''

########################################################
#       Parent
########################################################

def ac_response_ok(self, event):
    self.response = event.response
    return 'Done'

def ac_response_error(self, event):
    self.response = event.response
    return 'Done'

def ac_consult(self, event):
    return self.send_event(self.cons, event)


FSM_PARENT = {
    'output_list': (),
    'event_list': ('EV_QUERY_BY_DIRECT', 'EV_QUERY_BY_BROADCAST', 'EV_RESP_OK',
                   'EV_RESP_ERROR'),
    'state_list': ('ST_IDLE', 'ST_WAIT_RESP'),
    'machine': {
        'ST_IDLE':
        (
            ('EV_QUERY_BY_DIRECT',      ac_consult,     'ST_WAIT_RESP'),
            ('EV_QUERY_BY_BROADCAST',   ac_consult,     'ST_WAIT_RESP'),
        ),

        'ST_WAIT_RESP':
        (
            ('EV_RESP_OK',    ac_response_ok,           'ST_IDLE'),
            ('EV_RESP_ERROR', ac_response_error,        'ST_IDLE'),
        ),
    }
}

class ParentGClass(GObj):
    def __init__(self):
        GObj.__init__(self, FSM_PARENT)
        self.start_up()

    def start_up(self):
        ''' Create gobj childs, initialize something...
        '''
        self.cons = ChildGClass()
        self.add_child(self.cons)


########################################################
#       Tests
########################################################
class TestGObj(unittest.TestCase):
    def setUp(self):
        self.gobj_parent = ParentGClass()
        self.gobj_parent.set_trace_mach(True, pprint, level=-1)

    def test_send_event_name_to_itself(self):
        ret = self.gobj_parent.send_event(self.gobj_parent,
            'EV_QUERY_BY_DIRECT', data='query1')
        self.assertEqual(ret, 'Done')
        self.assertEqual(self.gobj_parent.response, 'OK')

        ret = self.gobj_parent.send_event(self.gobj_parent,
            'EV_QUERY_BY_DIRECT', data='query2')
        self.assertEqual(ret, 'Done')
        self.assertEqual(self.gobj_parent.response, 'ERROR')

    def test_send_event_to_itself(self):
        ret = self.gobj_parent.send_event(self.gobj_parent,
            'EV_QUERY_BY_DIRECT', data='query1')
        self.assertEqual(ret, 'Done')
        self.assertEqual(self.gobj_parent.response, 'OK')

        ret = self.gobj_parent.send_event(self.gobj_parent,
            'EV_QUERY_BY_DIRECT', data='query2')
        self.assertEqual(ret, 'Done')
        self.assertEqual(self.gobj_parent.response, 'ERROR')

    def test_send_event_name_to_child(self):
        ret = self.gobj_parent.send_event(self.gobj_parent.cons,
            'EV_QUERY_BY_DIRECT', data='query1')
        self.assertEqual(ret, EventNotAcceptedError)

        ret = self.gobj_parent.send_event(self.gobj_parent.cons,
            'EV_QUERY_BY_DIRECT', data='query2')
        self.assertEqual(ret, EventNotAcceptedError)

    def test_send_event_to_child(self):
        ret = self.gobj_parent.send_event(self.gobj_parent.cons,
            'EV_QUERY_BY_DIRECT', data='query1')
        self.assertEqual(ret, EventNotAcceptedError)

        ret = self.gobj_parent.send_event(self.gobj_parent.cons,
            'EV_QUERY_BY_DIRECT', data='query2')
        self.assertEqual(ret, EventNotAcceptedError)

    def test_send_event_name_to_none(self):
        self.assertRaises(DestinationError, self.gobj_parent.send_event,
            None, 'EV_QUERY_BY_DIRECT', data='query1')
        self.assertRaises(GObjError, self.gobj_parent.send_event,
            'pepe', 'EV_QUERY_BY_DIRECT', data='query1')

    def test_send_event_to_none(self):
        ret = self.gobj_parent.send_event(self.gobj_parent.cons,
            'EV_QUERY_BY_DIRECT', data='query1')
        self.assertEqual(ret, EventNotAcceptedError)

        ret = self.gobj_parent.send_event(self.gobj_parent.cons,
            'EV_QUERY_BY_DIRECT', data='query2')
        self.assertEqual(ret, EventNotAcceptedError)

    def test_send_event_to_named_gobj(self):
        self.assertRaises(GObjError, self.gobj_parent.send_event,
            'destination', 'EV_QUERY_BY_DIRECT')

    def test_event_factory(self):
        self.assertRaises(EventError, self.gobj_parent.event_factory,
            self.gobj_parent, 1)
        self.assertRaises(GObjError, self.gobj_parent.event_factory,
            1, 'EV_QUERY_BY_DIRECT')

        event = self.gobj_parent.event_factory(None, 'EV_QUERY_BY_DIRECT',
                                               data='query1')
        self.assertRaises(GObjError, self.gobj_parent.event_factory,
            1, event)

        event = self.gobj_parent.event_factory(None, event, data2='query2')
        self.assertEqual(event.destination, None)
        self.assertEqual(event.data, 'query1')
        self.assertEqual(event.data2, 'query2')
        event = self.gobj_parent.event_factory(self.gobj_parent, event)
        self.assertEqual(event.destination, self.gobj_parent)

    def test_post_event(self):
        self.assertRaises(QueueError, self.gobj_parent.post_event,
            self.gobj_parent, 'EV_QUERY_BY_DIRECT', data='query1')

        self.assertRaises(QueueError, self.gobj_parent.post_event,
            self.gobj_parent, 'EV_QUERY_BY_DIRECT', data='query1')

    def test_broadcast_event1(self):
        self.gobj_parent.cons.subscribe_event(
            'EV_RESP_OK', self.gobj_parent)
        ret = self.gobj_parent.send_event(
            self.gobj_parent, 'EV_QUERY_BY_BROADCAST', data='query3')
        self.assertEqual(self.gobj_parent.response, 'OK')
        self.gobj_parent.cons.delete_subscription(
            'EV_RESP_OK', self.gobj_parent)

    def test_broadcast_event2(self):
        self.gobj_parent.cons.subscribe_event(
            ('EV_RESP_OK','EV_RESP_ERROR'), self.gobj_parent)
        ret = self.gobj_parent.send_event(self.gobj_parent,
                'EV_QUERY_BY_BROADCAST', data='query4')
        self.assertEqual(self.gobj_parent.response, 'ERROR')
        self.gobj_parent.cons.delete_subscription(
            ('EV_RESP_OK','EV_RESP_ERROR'), self.gobj_parent)

    def test_subscribe_event_and_delete_subscription(self):
        self.assertRaises(GObjError, self.gobj_parent.cons.subscribe_event,
            'EV_RESP_OK', 1)
        self.assertRaises(GObjError, self.gobj_parent.cons.subscribe_event,
            'EV_RESP_OK', 'gobj')
        self.assertRaises(EventError, self.gobj_parent.cons.subscribe_event,
            'EV_XXX', self.gobj_parent)

        self.gobj_parent.cons.subscribe_event(
            'EV_RESP_OK', self.gobj_parent
        )
        self.assertTrue(self.gobj_parent.cons.delete_subscription(
            'EV_RESP_OK', self.gobj_parent))

        self.assertFalse(self.gobj_parent.cons.delete_subscription(
            'EV_RESP_OK', self.gobj_parent))

        self.gobj_parent.cons.subscribe_event(
            ('EV_RESP_OK', 'EV_RESP_ERROR'), self.gobj_parent
        )
        self.assertTrue(self.gobj_parent.cons.delete_subscription(
            ('EV_RESP_OK', 'EV_RESP_ERROR'), self.gobj_parent))

        self.assertRaises(EventError, self.gobj_parent.cons.subscribe_event,
            ('EV_RESP_OK', 1), self.gobj_parent)

    def test_add_child(self):
        self.assertRaises(ParentError,
            self.gobj_parent.add_child, self.gobj_parent.cons)

    def test_remove_child(self):
        self.gobj_parent.remove_child(self.gobj_parent.cons)
        self.assertRaises(KeyError,
            self.gobj_parent.remove_child, self.gobj_parent.cons)

    def test_register_gobj(self):
        self.assertTrue(
            self.gobj_parent.register_gobj(self.gobj_parent) == None)
    def test_deregister_gobj(self):
        self.assertTrue(
            self.gobj_parent.deregister_gobj(self.gobj_parent) == None)
    def test_search_gobj(self):
        self.assertTrue(
            self.gobj_parent.search_gobj(self.gobj_parent) == None)

    def test_set_trace_mach(self):
        # trace_mach already set in setUp()
        prev = self.gobj_parent.set_trace_mach(True, pprint)
        self.assertEqual(prev, True)
        prev = self.gobj_parent.set_trace_mach(False)
        self.assertEqual(prev, True)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
