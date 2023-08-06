=========
Reference
=========

.. currentmodule:: xworkflows

The XWorkflow library has two main aspects:

- Defining a workflow;
- Using a workflow on an object.

Defining a workflow
-------------------

A workflow is defined by subclassing the :class:`Workflow` class, and setting
a few specific attributes::

    class MyWorkflow(xworkflows.Workflow):

        # The states in the workflow
        states = (
            ('init', _(u"Initial state")),
            ('ready', _(u"Ready")),
            ('active', _(u"Active")),
            ('done', _(u"Done")),
            ('cancelled', _(u"Cancelled")),
        )

        # The transitions between those states
        transitions = (
            ('prepare', 'init', 'ready'),
            ('activate', 'ready', 'active'),
            ('complete', 'active', 'done'),
            ('cancel', ('ready', 'active'), 'cancelled'),
        )

        # The initial state of objects using that workflow
        initial_state = 'init'

Those attributes will be transformed into similar attributes with friendlier APIs:

- :attr:`~Workflow.states` is defined as a list of two-tuples
  and converted into a :class:`~base.StateList`
- :attr:`~Workflow.transitions` is defined as a list of three-tuples
  and converted into a :class:`~base.TransitionList`
- :attr:`~Workflow.initial_state` is defined as the :attr:`~base.State.name`
  of the initial :class:`~base.State` of the :class:`Workflow` and converted into
  the appropriate :class:`~base.State`

Accessing :class:`Workflow` states and transitions
""""""""""""""""""""""""""""""""""""""""""""""""""

The :attr:`~Workflow.states` attribute, a :class:`~base.StateList` instance,
provides a mixed dictionary/object API::

  >>> MyWorkflow.states.init
  State('init')
  >>> MyWorkflow.states.init.title
  u"Initial state"
  >>> MyWorkflow.states['ready']
  State('ready')
  >>> 'active' in MyWorkflow.states
  True
  >>> MyWorkflow.states.init in MyWorkflow.states
  True
  >>> list(MyWorkflow.states)  # definition order is kept
  [State('init'), State('ready'), State('active'), State('done'), State('cancelled')]

The :attr:`~Workflow.transitions` attribute of a
:class:`Workflow` is a :class:`~base.TransitionList` instance,
exposing a mixed dictionary/object API::

        >>> MyWorkflow.transitions.prepare
        Transition('prepare', [State('init')], State('ready'))
        >>> MyWorkflow.transitions['cancel']
        Transition('cancel', [State('ready'), State('actuve')], State('cancelled'))
        >>> 'activate' in MyWorkflow.transitions
        True
        >>> MyWorkflow.transitions.available_from(MyWorkflow.states.ready)
        [Transition('activate'), Transition('cancel')]
        >>> list(MyWorkflow.transitions)  # Definition order is kept
        [Transition('prepare'), Transition('activate'), Transition('complete'), Transition('cancel')]



Using a workflow
----------------

The process to apply a :class:`Workflow` to an object is quite straightforward:

- Inherit from :class:`WorkflowEnabled`
- Define one or more class-level attributes as ``foo = SomeWorkflow()``

These attributes will be transformed into :class:`~base.StateProperty` objects,
acting as a wrapper around the :class:`~base.State` held in the object's internal :attr:`__dict__`.

For each transition of each related :class:`Workflow`, the :class:`~base.WorkflowEnabledMeta` metaclass
will add or enhance a method for each transition, according to the following rules:

- If a class method is decorated with :func:`transition('XXX') <transition>` where ``XXX`` is the name of a transition,
  that method becomes the :class:`~base.ImplementationWrapper` for that transition
- For each remaining transition, if a method exists with the same name *and* is decorated with
  the :func:`~transition` decorator, it will be used for the :class:`~base.ImplementationWrapper`
  of the transition. Methods with a transition name but no decorator will raise a :exc:`TypeError` -- this ensures that
  all magic is somewhat explicit.
- For all transitions which didn't have an implementation in the class definition, a new method is added to the class
  definition.
  They have the same name as the transition, and a :func:`~base.noop` implementation.
  :exc:`TypeError` is raised if a non-callable attribute already exists for a transition name.


Accessing the current state
"""""""""""""""""""""""""""

For a :class:`WorkflowEnabled` object, each ``<attr> = SomeWorkflow()`` definition
is translated into a :class:`~base.StateProperty` object, which adds a few functions
to a plain attribute:

- It checks that any value set is a valid :class:`~base.State` from the related :class:`Workflow`::

      >>> obj = MyObject()
      >>> obj.state = State('foo')
      Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
      ValueError: Value State('foo') is not a valid state for workflow MyWorkflow.

- It defaults to the :attr:`~Workflow.initial_state` of the :class:`Workflow` if no
  value was set::

    >>> obj = MyObject()
    >>> obj.state
    State('init')

- It wraps retrieved values into a :class:`~base.StateWrapper`, which adds
  a few extra attributes:

  - Access to the related workflow::

      >>> obj.state.workflow
      <Workflow: MyWorkflow>

  - List of accessible transitions::

      >>> obj.state.transitions
      [Transition('accept')]

  - Easy testing of the current value::

      >>> obj.state.is_init
      True
      >>> obj.state.is_ready
      False

  - Native equivalence to the :attr:`state's name <base.State.name>`::

      >>> obj.state == 'init'
      True
      >>> obj.state == 'ready'
      False
      >>> obj.state in ['init', 'ready']
      True

    .. note:: This behavior should only be used when accessing the :class:`~base.State`
              objects from the :attr:`Workflow.states` list is impossible, e.g comparison
              with external data (URL, database, ...).

              Using :class:`~base.State` objects or the :attr:`is_XXX` attributes protects
              from typos in the code (:exc:`AttributeError` would be raised), whereas
              raw strings provide no such guarantee.


Using transitions
-----------------

Defining a transition implementation
""""""""""""""""""""""""""""""""""""

In order to link a state change with specific code, a :class:`WorkflowEnabled` object
must simply have a method decorated with the :func:`transition` decorator.

If that method cannot be defined with the name of the related :class:`~base.Transition`,
the name of that :class:`~base.Transition` should be passed as first argument to the
:func:`transition` decorator::

  class MyObject(xworkflows.WorkflowEnabled):

      state = MyWorkflow()

      @xworkflows.transition()
      def accept(self):
          pass

      @xworkflows.transition('cancel')
      def do_cancel(self):
          pass


Once decorated, any call to that method will perfom the following steps:

#. Check that the current :class:`~base.State` of the object is a valid source for
   the target :class:`~base.Transition` (raises :exc:`InvalidTransitionError` otherwise);
#. Checks that the optional :func:`~base.ImplementationWrapper.check` hook, if defined, returns ``True``
   (raises :exc:`ForbiddenTransition` otherwise);
#. Run the optional :func:`~base.ImplementationWrapper.before` hook, if defined;
#. Call the code of the function;
#. Change the :class:`~base.State` of the object;
#. Call the :func:`Workflow.log_transition` method of the related :class:`Workflow`;
#. Run the optional :func:`~base.ImplementationWrapper.after` hook, if defined.


Transitions for which no implementation was defined will have a basic :func:`~base.noop` implementation.


Controlling transitions
"""""""""""""""""""""""

According to the order above, preventing a :class:`~base.State` change can be done:

- By returning ``False`` in a custom :func:`~base.ImplementationWrapper.check` hook;
- By raising any exception in the custom :func:`~base.ImplementationWrapper.before` hook;
- By raising any exception in the actual implementation.


Additional control over the transition implementation can be obtained via hooks.
Three hooks are available, and are bound to the implementation at the :func:`transition` level::

    @xworkflows.transition(check=some_fun, before=other_fun, after=something_else)
    def accept(self):
        pass

- ``check``: this function is called just after the :class:`~base.State` check, and should return ``True`` if the transition can proceed;
- ``before``: this function is called just before running the actual implementation.
  It receives the same ``*args`` and ``**kwargs`` as those passed to the actual implementation;
- ``after``: this function is called just after the :class:`~base.State` has been updated.
  Its arguments are:

  - ``res``: the return value of the actual implementation;
  - ``*args`` and ``**kwargs``: the arguments passed to the actual implementation.


Checking transition availability
""""""""""""""""""""""""""""""""


Some programs may need to display *available* transitions, without calling them.
Instead of checking manually the :class:`state <base.State>` of the object and calling
the appropriate :func:`~base.ImplementationWrapper.check` method if defined, you should simply call ``myobj.some_transition.is_available()``:

.. sourcecode:: python

    class MyObject(WorkflowEnabled):
        state = MyWorkflow
        x = 13

        def check(self):
            return self.x == 42

        @transition(check=check)
        def accept(self):
            pass

        @transition()
        def cancel(self):
            pass

.. sourcecode:: pycon

    >>> obj = MyObject()
    >>> obj.accept.is_available()  # Forbidden by 'check'
    False
    >>> obj.cancel.is_available()  # Forbidden by current state
    False
    >>> obj.x = 42
    >>> obj.accept.is_available()
    True


Logging transitions
"""""""""""""""""""


The :func:`~Workflow.log_transition` method of a :class:`Workflow`
allows logging each :class:`~base.Transition` performed by an object using that
:class:`Workflow`.

This method is called with the following arguments:

- ``transition``: the :class:`~base.Transition` just performed
- ``from_state``: the :class:`~base.State` in which the object was just before the transition
- ``instance``: the :class:`object` to which the transition was applied
- ``*args``: the arguments passed to the transition implementation
- ``**kwargs``: the keyword arguments passed to the transition implementation

The default implementation logs (with the :mod:`logging` module) to the ``xworkflows.transitions`` logger.

This behaviour can be overridden on a per-workflow basis: simply override the :func:`Workflow.log_transition` method.


Advanced customization
""""""""""""""""""""""

In order to perform advanced tasks when running transitions, libraries may hook
directly at the :class:`~base.ImplementationWrapper` level.

For this, custom :class:`Workflow` classes should override the
:attr:`Workflow.implementation_class` attribute with their custom subclass and add
extra behaviour there.

Possible customizations would be:

- Wrapping implementation call and state update in a database transaction
- Persisting the updated object after the transition
- Adding workflow-level hooks to run before/after the transition
- Performing the same sanity checks for all objects using that :class:`Workflow`

