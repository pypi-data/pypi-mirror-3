"""Classes for supporting performing actuation with sMAP.

sMAP services with actuation components should place actuators at the
leaves of their resource tree, replacing SmapPoint instances.
Generally, the steps necessary to provide actuation is simply to
subclass the appropriate actuator class (Binary, NState, or
Continuous), and then implement the get_state and set_state methods.

Services wishing to use access control should additionally use SSL for
authentication, and annotate their get and set methods with the
appropriate capabilities necessary to access those resources.
"""
import time
import urlparse
import core

class SmapActuator(core.Timeseries):
    """Base class for actuators, which deals with HTTP.

    @lock a threading.RLock instance.  If provided, will acquire
       before calling get_ or set_state.
    @unit the value for the UnitofMeasure sMAP field
    @pushfn a function which will be called whenver the state of the
       actuator changes
    @read_limit a value, in seconds, of how often get_state may be
       called.  if not none, the class will call get_state at once per
       given interval, and otherwise return the last read value.
    @write_limit the same as read_limit, but for set_state.  If
       set_state is called more frequently than this limit, the server
       will return an HTTP error code.
    """
    def __init__(self, *args, **kwargs):
        self.lock = kwargs.pop('lock', None)
        self.read_limit = kwargs.pop('read_limit', None)
        self.write_limit = kwargs.pop('write_limit', None)
        core.Timeseries.__init__(self, *args, **kwargs)

    def _call_locked(self, fn):
        """Call a function.  If this actuator was created with a lock, we'll
call the function holding that lock.  Otherwise, we'll make a call
that could be concurrent if multiple threads hold references to this
object"""
        if self.lock != None:
            with self.lock:
                return fn()
        else:
            return fn()

    def valid_state(self, state):
        """Determine if a given state is valid for a particular actuator.
        @prototype
        """
        return False

    def parse_state(self, state):
        """Parse a string representation of a state
        @prototype
        """
        return state

    def change(self, request, new_state):
        new_state = self.parse_state(new_state)
        if self.valid_state(new_state):
            self._call_locked(lambda: self.set_state(request, new_state))
            self.add(new_state)

    def http_get(self, request, resource, query=None):
        if len(resource) == 0:
            query = urlparse.parse_qs(query)
            if len(query.get('state', [])) == 1:
                self.change(request, query['state'][0])
                
            rv = {
                'Version' : 1,
                'ControlerType' : self.control_type,
                'CurrentState' : self._call_locked(lambda: self.get_state(request))
                }
            if self.unit:
                rv['UnitofMeasure'] = self.unit

            rv.update(self.control_description)
            return rv
        elif resource[0] == 'reading':
            return {
                'Version' : 1,
                'Reading' : self._call_locked(lambda: self.get_state(request)),
                'ReadingTime' : time.time()
                }
        elif resource[0] == 'formatting':
            return {
                'Version' : 1,
                'UnitofMeasure' : self.unit,
                'UnitofTime' : 'second',
                'MeterType' : '',
                }
        else:
            return None


class BinaryActuator(SmapActuator):
    """A BinaryActuator is a controller which has only two states,
generally "on" and "off".  It is essentially a simplified version of
an NStateActuator.

State here are static and can't be configured.
    """
    def valid_state(self, state):
        return reduce(lambda x,y: x or state in y, 
                      self.control_description['States'], 
                      False)

    def __init__(self, **kwargs):
        self.control_type = 'binary'
        self.control_description = {
            'States' : [['0', 'off'], ['1', 'on']]
            }
        SmapActuator.__init__(self, **kwargs)


class NStateActuator(SmapActuator):
    """NStateActuators have a discrete number of states which they can be
in.  Although there may be restrictions on which state transisitions
are possible, this profile does not express any of them.
    """
    def valid_state(self, state):
        return int(state) in self.control_description['States']
    
    def __init__(self, states, **kwargs):
        self.control_type = 'nstate'
        self.control_description = {
            'States' : states,
            }
        SmapActuator.__init__(self, **kwargs)


class ContinuousActuator(SmapActuator):
    """A ContinuousActuator allows a set point to be adjusted within a
continuous interval.  Minimum and maximum values in the range must be
specified.
    """
    def valid_state(self, state):
        return state >= self.control_description['States'][0] and \
            state <= self.control_description['States'][1]

    def parse_state(self, state):
        return float(state)

    def __init__(self, range=None, **kwargs):
        self.control_type = 'continuous'
        self.control_description = {
            'States' : range,
            }
        SmapActuator.__init__(self, **kwargs)


class GuardBandActuator(SmapActuator):
    """A GuardBandActuator actually consists of two points -- "high" and
"low", which are adjusted in parallel.
    """
    def __init__(self, **kwargs):
        self.control_type = 'guardband'
        SmapActuator.__init__(self, **kwargs)


if __name__ == '__main__':
    import uuid
    ts = SmapActuator(uuid.uuid1(), '')
    print ts
#     import threading
#     import SmapHttp
#     from SmapAuthorization import authenticated

#     class MyActuator(BinaryActuator):
#         def __init__(self):
#             BinaryActuator.__init__(self, lock=threading.Lock())
#             self.state = 0

#         def get_state(self, request):
#             return self.state

#         @authenticated(["CAP_SECURE"])
#         def set_state(self, request, state):
#             print "Setting state to", state
#             self.state = state

#     class MyOtherActuator(ContinuousActuator):
#         def get_state(self, request):
#             return self.state
#         def set_state(self, request, state):
#             print "Setting state to", state
#             self.state = state
    
#     a = MyActuator()
#     b = MyOtherActuator(range=[0, 5])
#     SmapHttp.start_server({'a': a, 'b': b}, port=8000, handler=SmapHttp.SslSmapHandler)
