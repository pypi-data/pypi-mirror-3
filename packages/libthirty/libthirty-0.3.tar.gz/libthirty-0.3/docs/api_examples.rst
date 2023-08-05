API Examples
============

::

    >>> from libthirty import Resource
    >>> from libthirty import Authenticate
    >>> is_authenticated = Authenticate('user', 'password')
    >>> res = Resource('repository', 'thirtyloops')
    >>> # This exposes the resource to all manipulation
    >>> res.fields
    ['user', 'pasword', 'location']
    >>> res.location = 'gitosis@git.30loops.net'
    >>> res.save()   # --> saves the resource state
    >>> res.delete() # --> delete the resource state
    >>> app = Resource('app', 'thirtyloops')
    >>> job = app.deploy(backends=['eu': 2, 'us': 4])
    >>> job.location
    https://30loops.net/api/30loops/logbook/<logbook_id>/
    >>> job.status
    Pending
    >>> c = Access('account', 'user', 'password')
    >>> jobs = Jobqueue()
    >>> jobs.pending
    ['job1', 'job2']
    >>> jobs.current
    job details ...

Examples explained
------------------

The user can use the API mainly to manipulate resource state and to trigger
actions to the resource. Furthermore there are a few auxiliary functions to
manage the account and the jobqueue.

As a first step the user needs to create an authentication object using
:py:class:`libthirty.Authenticate`. This should be done as a first step, since
this object is referenced throughout the rest of the code.

The most common object is :py:class:`libthirty.Resource`. It exposes the
configuration state of the resource and the actions it can perform. If a
resource object gets instantiated, the api makes a request to the platform to
determine capabilities of this resource. With this information the constructor
creates a new resource object. 

The state of a resource is exposed as fields to the instance. The state is
manipulated using ``save`` and ``delete`` methods. Actions are wrapped as
method fields and take ``**kwargs`` as argument.

Initiating an action returns a job object. This object can be queried to
determine the progress and success of the action. Each user can query also the
jobqueue of that account. The jobqueue exposes a series of handy function to
navigate the jobqueue.
