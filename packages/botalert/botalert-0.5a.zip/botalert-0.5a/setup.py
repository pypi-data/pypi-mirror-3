#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

release_notes = r"""
===============
Release Notes :
===============

Release 0.4a:
=============

Alpha Version

Release 0.5a:
=============

Changed author's contact info.
"""

description = r"""
This script is still in alpha version, and may have some instabilities.
If you use it, you acknowledge doing it at your own risks and certify that you know what you are
doing.

The purpose of this script is to monitor /var/log/messages on a cron.daily basis for predefined
dropped packets, in order to detect "spambot" infected machines in your LAN.
An email is send only per detection.

First, you need to configure iptables or shorewall to drop packets originating from your LAN
towards port 25, if the destination server is not your own MTA (or your ISP's MTA).
Indeed, machines in your LAN are supposed to use your own (or your ISP's) smtp server as a relay,
and should never send mails directly.
(infected machines participating in spam bots usually send mails directly)
Of coarse, your smtp server itself still needs to be allowed to send mails, take care not to block
it while configuring your firewall.
Check also that the dropped packets are well logged, otherwise we would detect nothing.

Secondly, install (by typing the 'python setup.py install' command as root) this script on your linux
firewall, and adapt /etc/botalert.conf to your needs ("IN:" being the interface of your lan, "OUT:"
the outbound interface (not required to be defined). Leaving a variable empty means no corresponding
'matches' will be searched for.
You can define as many signals you want (other than [smtp]) by creating another signal section and
then add the sections you want to log in the "log:" variable of the [signals] section, as a comma
separated list. Indeed this script is pre-configured to detect spam bots, but you can detect anything
else if you know the protocol of what you want to detect, and then define it (and it needs to be
logged in the log file (defaults : /var/log/messages)).

This script has only been tested with shorewall and iptables logs, however, you can adapt the regex
to your needs. No need to edit the regex in botalert.py itself, instead you can add a "regex:"
variable in the [DEFAULT] section of /etc/botalert.conf, it will override the one in the script.

Type::

    python -m botalert.py -h

for help.

"""

setup(name='botalert',
      version='0.5a',
      author='Yves-Gwenael Bourhis',
      author_email='ygbourhis at gmail.com',
      description = 'parse logged dropped outgoing packets in order to detect bot infected machines',
      long_description = str("\n".join([description, release_notes])),
      license = 'GNU General Public License version 2.0',
      platforms = ['Linux'],
      py_modules = ['botalert'],
      data_files = [('/etc', ['botalert.conf', 'botalert.sample.conf']),
                    ('/etc/cron.daily', ['00botalert.cron']),
                    ],
      )
