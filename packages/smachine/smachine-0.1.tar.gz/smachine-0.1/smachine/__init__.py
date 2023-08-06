__version__ = '0.1'

class StateException(Exception):
    pass

class StateMachineMetaClass(type):
    def __new__(cls, name, bases, attrs):
        def switch(state):
            def wrapped(self, *args, **kwargs):
                return self._transition(state, *args, **kwargs)
            return wrapped

        for state in attrs['states']:
            attrs[state] = switch(state)

        return super(StateMachineMetaClass, cls).__new__(cls, name, bases, attrs)


class StateMachine(object):
    """
    Simple state machine creating methods for state transitions named after states
    in :attr:`states`.
    
    If present, tries to call :meth:`on_leave_<current_state>` and 
    :meth:`on_enter_<new_state>` methods.
    
    Both :meth:`on_leave_<current_state>` and :meth:`on_enter_<new_state>` receive
    a ``from_state`` and ``to_state`` keyword argument. If any method returns
    false the transition is aborted.
    
    Raises :class:`StateException` on an illegal transition. 
    
    :example:
    
    ::
        
        class TestMachine(StateMachine):
            state = None
            states = ['green','yellow','red']
            transitions = {
                None: ['green'],
                'green': ['yellow', 'red'],
                'yellow': ['green', 'red'],
                'red': ['yellow']
            }
            
            def __init__(self):
                self.green()
    
    """
    __metaclass__ = StateMachineMetaClass
    state = None
    """ Starting state """
    states = []
    """ All possible states """
    transitions = {}
    """ Mapping possible state transitions """
    _next = []
    """ FIFO queue for next states """

    def _can(self, from_state, to_state):
        return to_state in self.transitions[from_state]
    def _cannot(self, from_state, to_state):
        return not self._can(from_state, to_state)
    def can(self, state):
        """ Check if a transition to ``state`` is legal """
        return self._can(self.state, state)
    def cannot(self, state):
        """ Check if a transition to ``state`` is illegal """
        return not self.can(state)
    
    def push(self, state, *args, **kwargs):
        try:
            if self._cannot(self._next[-1][0], state):
                raise StateException
        except IndexError:
            if self._cannot(self.state, state):
                raise StateException
        self._next.append((state, args, kwargs))                

    def next(self):
        try:
            [to_state, args, kwargs] = self._next.pop(0)
            return self._transition(to_state, *args, **kwargs)
        except IndexError:
            raise StateError, "No next state available"
    
    def _leave_state(self, from_state, to_state, *args, **kwargs):
        on_leave = getattr(self, 'on_leave_%s' % from_state, None)        
        if callable(on_leave):
            return on_leave(from_state=from_state, to_state=to_state, *args, **kwargs)
        return True

    def _enter_state(self, from_state, to_state, *args, **kwargs):
        on_enter = getattr(self, 'on_enter_%s' % to_state, None)
        if callable(on_enter):
            return on_enter(from_state=self.state, to_state=to_state, *args, **kwargs)
        return True

    def on_transition(self, *args, **kwargs):
        pass
    
    def _transition(self, new_state, *args, **kwargs):
        if self.cannot(new_state):
            raise StateException
        
        abort = self._leave_state(self.state, new_state, *args, **kwargs) == False
        abort = abort or self._enter_state(self.state, new_state, *args, **kwargs) == False
        
        if not abort:
            self.on_transition(self.state, new_state, *args, **kwargs)  
            self.state = new_state
        return not abort


