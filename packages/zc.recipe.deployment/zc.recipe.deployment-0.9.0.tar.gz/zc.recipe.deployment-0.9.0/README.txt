***********************
Unix Deployment Support
***********************

.. contents::

The zc.recipe.deployment recipe provides support for deploying
applications with multiple processes on Unix systems. (Perhaps support
for other systems will be added later.) It creates directories to hold
application instance configuration, log and run-time files.  It also
sets or reads options that can be read by other programs to find out
where to place files:

crontab-directory
    The name of the directory in which cron jobs should be placed.
    This is /etc/cron.d.

etc-directory
    The name of the directory where configuration files should be
    placed.  This is /etc/NAME, where NAME is the deployment
    name.

log-directory
    The name of the directory where application instances should write
    their log files.  This is /var/log/NAME, where NAME is
    the deployment name.

logrotate-directory
    The name of the directory where logrotate configuration files
    should be placed, typically, /etc/logrotate.d.

run-directory
    The name of the directory where application instances should put
    their run-time files such as pid files and inter-process
    communication socket files.  This is /var/run/NAME, where
    NAME is the deployment name.

rc-directory
    The name of the directory where run-control scripts should be
    installed.  This is /etc/init.d.

The etc, log, and run directories are created in such a way that the
directories are owned by the user specified in the user option and are
writable by the user and the user's group.
