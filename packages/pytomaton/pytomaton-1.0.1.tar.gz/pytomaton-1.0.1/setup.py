from setuptools import setup, find_packages

import os

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
# (from http://packages.python.org/an_example_pypi_project/setuptools.html)
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'pytomaton',
    version = '1.0.1',
    author = 'Will Haldean Brown',
    author_email = 'will.h.brown@gmail.com',
    description = 'A more convenient and succinct way of expressing state machines in Python',
    license = 'MIT',
    keywords = 'automaton state machine library',
    url = 'https://github.com/haldean/pytomaton',
    test_suite = 'pytomaton.tests',
    packages = find_packages(),
    classifiers = [
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Topic :: Software Development :: Libraries',
      ],
    long_description = '''pytomaton: State Machines in Python
=========

Brief
-----
Often, a state machine is a convenient way to implement a stateful protocol, but
they often involve a lot of messy boilerplate for managing how you transition
from one state to the next, or what exactly happens when you enter a state.
`pytomaton` was created to reduce this boilerplate code.  
  
Just as in a theoretical automaton, a `pytomaton.statemachine` has a list of
states, a start state. At any given time, a state machine is in one single
state. The programmer can invoke `statemachine.transition(new_state_name)` to
transition to a new state; when this happens, the state machine checks to see if
there are any actions which are triggered by this transition. Currently, actions
can be triggered by entering a specific state (`on_enter`), or by transitioning
from one specific state to another (`on_transition`). Methods are decorated as
being triggered by transitions, as shown in the example below.

Example
-------

    from pytomaton import statemachine, on_transition, on_enter

    class ConnectionMachine(statemachine):
      states = ['waiting_for_connection', 'waiting_for_ready', 'all_ready']
      start_state = 'waiting_for_connection'

      def on_connect(self):
        self.transition('waiting_for_ready')

      @on_transition('waiting_for_connection', 'waiting_for_ready')
      def send_ready_prompt(self):
        self.broadcast('are you ready?')

      def receive_ready_confirm(self):
        if self.all_ready():
          self.transition('all_ready')

      @on_enter('all_ready')
      def send_all_ready(self):
        self.broadcast('everyone is ready!')

In this example, we define a `ConnectionMachine` that has three states. It
starts in the `waiting_for_connection` state. When a user connects, in
transitions to the `waiting_for_ready` state, which triggers a call to
`send_ready_prompt`. When a user confirms that they're ready, we transition to
the `on_ready` state, which triggers a call to `send_all_ready`.''',
    )
