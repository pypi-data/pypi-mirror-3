Testing Utilities
==================


additional py.test options
---------------------------



.. program:: py.test

.. option:: --vcs {name}

  limit the testing for backends to the given vcs

.. option:: --local-remoting

  if given also test the local remoting

.. option:: --no-direct-api

  Don't run the normal local testing,
  useful for remote-only


pytest funcargs
-----------------

.. automodule:: tests.conftest
  :members:


Utility Classes
-----------------

.. currentmodule:: tests.helpers

.. autoclass:: VcsMan
  :members:

  .. attribute:: base

    :type: :class:`py.path.local`

    the base directory

  .. attribute:: vc

    The name of the managed vcs

  .. attribute:: backend

    :type: :class:`anyvc.backend.Backend`

    The backend instance giving access to the currently tested vcs

  .. attribute:: remote

    boolean telling if the remoting support is used

  .. attribute:: xspec

    A :class:`execnet.XSpec` telling remote python if remoting is used


.. autoclass:: WdWrap
  :members:
