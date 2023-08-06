===================
infrae.maildrophost
===================

``infrae.maildrophost`` is used to configure a maildrophost server and
`MaildropHost`_ product using the same configuration, and create a
management script for the maildrophost server.

In addition to those tasks, it used to download and install
`MaildropHost`_ when it was not distributed as an egg. If you are
looking for those features, please have a look at the version 1.x of
this recipe.

Example in buildout::

  [buildout]
  parts =
      maildrophost
      instance

  [maildrophost]
  recipe = infrae.maildrophost
  smtp_host = localhost
  smtp_port = 25

  [instance]
  ...
  eggs +=
     Products.MaildropHost
  zope-conf-additional +=
  <product-config maildrophost>
    config-path-application ${maildrophost:configuration}
  </product-config>


This will create the configuration file ``maildrophost.cfg`` for the
daemon, and put a start/stop script in the ``bin`` directory of the
buildout tree.

Spool and PID files are put by default in the ``var/maildrop``
directory, so data is preserved when update (if there is any data).

Settings
========

You can customize some of settings of `MaildropHost`_:

``mail_dir``
  Directory to use as *home directory* for the deamon. By default it's
  ``${buildout:directory}/var/maildrop`` It will be created if it
  doesn't exists.

``spool_dir``
  Directory to use as a spool. By default it will be
  ``${mail_dir}/spool``. The directory will be created if it doesn't
  exist already.

``pid_file``
  PID file to use for the daemon. By default it will be
  ``${mail_dir}/maildrop.pid``.

``smtp_host``
  SMTP server to use. Default to localhost.

``smtp_port``
  Port to use. Default to default SMTP port, 25.

``login``
  If the SMTP server require authentication, login to use.

``password``
  If the SMTP server require authentication, password to use.

``tls``
  If 1, `MaildropHost`_ will be speaking to a TLS enabled SMTP server.

``batch``
  Set ``MAILDROP_BATCH``.

``add_messageid``
  Add a message id to the sent mail.

``pool_interval``
  Must be an integer which define the interval in seconds between two
  check for new mail in the spool directory. Default is 120 seconds.

``wait_interval``
  Must be an interger or float which say how much time the daemon
  should wait between sending two mails to the mail server.


Latest version
==============

The latest version is available in a `Subversion repository
<https://svn.infrae.com/buildout/infrae.maildrophost/trunk>`_.

.. _MaildropHost: http://www.dataflake.org/software/maildrophost
