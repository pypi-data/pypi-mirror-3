================================================================================
Installing pyamp
================================================================================

.. highlight:: console
   :linenothreshold: 1000


In order to install pyamp on a machine running Ubuntu 10.04 run the following
commands::

    $ cd /opt
    $ sudo svn checkout http://pyamp.googlecode.com/svn/trunk/pyamp
    $ sudo chown -R $USERNAME:$USERNAME pyamp
    $ cd pyamp
    $ python setup.py build
    $ sudo python setup.py install


.. highlight:: python
   :linenothreshold: 1000
