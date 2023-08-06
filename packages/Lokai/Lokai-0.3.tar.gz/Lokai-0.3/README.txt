Lokai
+++++++++++++++++++

.. rubric::A business process management tool that can be extended to
           support a range of business processes.

Lokai is a flexible business process management tool that enables
teams to work together, and places those teams in the context of a
wider business. A single instance of the tool can handle as many
projects or tasks as required, with no need to deploy separate project
or process specific environments that cannot share data.

The tool freely mixes documentation, activity management and data
access in ways that are appropriate to the project, process or task
in hand. There is no constraint on how this might be done, and
different tasks or projects may use different arrangements within the
same environment.

Access management allows people to see and manipulate data in ways
that are appropriate to their role and work. Team members may work on
more than one task or project. Managers may manage more than one
project. A person can be a team member on one project and a manager on
another.

The key to this flexibility is a hierarchical data model with
interlinking between sub-trees. The structure and the links are fully
user controlled.

Lokai is a web served application, written in Python.

The code itself is written in an extendable manner that allows a
great deal of flexibility in the type of data represented, and in the
presentation of that data. Each node in the hierarchy can be
different. At its simplest, this allows for activities and
documentation to be held in the same structure, so that everything
relevant to the project or process is to hand. Whatever data is being
handled, the user is presented with a consistent interface where
access rules and navigation are given.

Requirements
--------------------

Lokai requires Python 2.5 or higher. Python 3.0 is not yet supported.

Other dependencies:

  Posgtgresql

  SqlAlchemy (version 0.6)

  Werkzeug

  PyUtilib

  Docutils

  Reportlab

Lokai is developed under Linux and is currently being run under
Ubuntu. Lokai itself does not use C extensions and the intention is
that the development is independent of operating system. However, no
tests have been done on other operating systems, or on other
distributions.

Install
--------------------

Download the package tarball and unpack it. Go into the distribution
directory and run::

  python setup.py install

or, more simply, don't bother with the download and just type::

  pip install lokai

To build a workable instance:

  Create a working directory for your new instance. And change into it.

  Copy ``lk_config.ini`` from the ``config`` folder of
  the installation.

  Review the content of the ``.ini`` file. It should work out of the
  box. However, you might want to change the default database name to
  something other than ``lokai_soft``.

  Create the database::

    tb_migrate.py login.login_db=max

    tb_migrate.py lk_worker.nodes_db=max

  Copy ``initial_data.yml`` from the ``doc/initial_settings`` folder
  of the installation. This contains a basic administrator login and a
  starting node for the database.

  Use the initial data::

    lk_initial_data -f initial_data.yml

  For a quick hit, start the publisher stand alone::
  
    python -mlokai.lk_ui.publisher

  Now browse to localhost:8080.

  To configure and use the fcgi interface, please go to `our main site
  <http://lokai.redholm.com>`_.

Upgrade from version 0.2.0
--------------------------

If you have an existing installation you will need to upgrade the
database. This is simply a matter of going to the working directory
and running ::

    tb_migrate.py login.login_db=max

    tb_migrate.py lk_worker.nodes_db=max


Help
--------------------

Documentation is `available <http://lokai.redholm.com>`_. This is
sparse at the moment but more is coming.

License
--------------------

Lokai is distributed under the `Apache License, Version 2.0
<http://www.apache.org/licenses/LICENSE-2.0>`_.

