#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE included in the packaging of
## this file.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##

from __future__ import with_statement

from ConfigParser import SafeConfigParser
from optparse import OptionParser
from copy import deepcopy
import os, re, sys, smtplib
from email.mime.text import MIMEText

defaults = {"config" : r"/etc/botalert.conf",
            "logfile" : r"/var/log/messages",
            "mailserver" : "localhost",}
defaults["configname"] = os.path.basename(defaults["config"])
defaults["regex"] = (r"^.*(logdrop|DROP).*"
                     r"IN=(?P<IN>\w+\d+)?.*"
                     r"OUT=(?P<OUT>\w+\d+)?.*"
                     r"(MAC=(?P<MAC>[\w\d:]+))?.*"
                     r"SRC=(?P<SRC>[\w\d.]+)?.*"
                     r"DST=(?P<DST>[\w\d.]+)?.*"
                     r"PROTO=(?P<PROTO>\w+)?.*"
                     r"SPT=(?P<SPT>\d+)?.*"
                     r"DPT=(?P<DPT>\d+)?.*"
                     r"$")

curdir = os.path.realpath(os.curdir)
filedir = os.path.realpath(os.path.dirname(__file__))
curdirconfig = os.path.join(curdir, defaults["configname"])
filedirconfig = os.path.join(filedir, defaults["configname"])


class CleverConfigParser(SafeConfigParser):
    def cleverItems(self, section, **kwargs):
        items = self.items(section, **kwargs)
        for item in self.defaults().items():
                if item in items:
                    items.remove(item)
        return items
    def cleanItems(self, section, **kwargs):
        items = self.cleverItems(section, **kwargs)
        itemscopy = deepcopy(items)
        for item in itemscopy:
            if not len(item[1].strip()):
                items.remove(item)
        return items
    def cleverOptions(self, section, **kwargs):
        options = self.options(section, **kwargs)
        for option in self.defaults().keys():
            if option in options:
                options.remove(option)
        return options

class AlertConfigParser(CleverConfigParser):
    def signals(self):
        sigkeys = self.get("signals","log").split(',')
        while '' in sigkeys:
            sigkeys.remove('')
        signals = {}.fromkeys(sigkeys)
        for key in signals:
            _signal = self.cleanItems(key)
            signals[key] = dict(_signal)
        return signals
    def recipients(self):
        recpts = self.cleanItems('recipients')
        recpts = dict(recpts)
        for key, value in recpts.items():
            if key.upper() not in ["FROM"]:
                values = value.split(',')
                while '' in values:
                    values.remove('')
                recpts[key] = values
        return recpts

def updateConfAndDefaults():
    config = AlertConfigParser()
    config.optionxform = str
    config.read(defaults["config"])
    defaults.update(config.defaults())
    return (config, defaults)

def getLogs():
    with open(defaults["logfile"], 'r') as logfile:
        logs = logfile.readlines()
    for logindex, log in enumerate(logs):
        logs[logindex] = log.strip()
    return logs

def getMatches(signals,logs):
    reg = re.compile(defaults['regex'])
    matches = {}.fromkeys(signals.keys())
    for matchkey, signal in zip(matches.keys(), signals.values()):
        matches[matchkey]={}
        for log in logs:
            res = reg.search(log)
            if res:
                resdict = res.groupdict()
                _match = True
                for sigkey,sigvalue in signal.items():
                    resdict_value = resdict.get(sigkey)
                    if not isinstance(sigvalue, str) or not isinstance(resdict_value,str):
                        _match = False
                    else:
                        if not sigvalue.upper() == resdict_value.upper():
                            _match = False
                if _match:
                    matches[matchkey][resdict['SRC']] = matches[matchkey].get(resdict['SRC'],[])
                    matches[matchkey][resdict['SRC']].append(resdict)
    return matches

def countIpMatches(matches, signal, IP):
    matched_IPs = 0
    if matches.get(signal):
        if matches[signal].get(IP):
            IP = matches[signal][IP]
            qty = len(IP)
            if qty:
                matched_IPs += qty
    return matched_IPs

def countSignalMatches(matches, signal):
    matched_signals = 0
    if matches.get(signal):
        for IP in matches[signal]:
            qty = countIpMatches(matches, signal, IP)
            if qty:
                matched_signals += qty
    return matched_signals

def countAllMatches(matches):
    matched_signals = 0
    for signal in matches:
        qty = countSignalMatches(matches, signal)
        if qty:
            matched_signals += qty
    return matched_signals

def getDestsIp(matches, signal, IP):
    dests = {}
    if matches.get(signal):
        if matches[signal].get(IP):
            for match in matches[signal][IP]:
                dest = match.get('DST')
                if dest:
                    dests[dest] = dests.get(dest, 0)
                    dests[dest] += 1
    return dests

def allertsToText(matches):
    message = ""
    for signame in matches:
        for ip in matches[signame]:
            message += "%s made %d %s attemp(s):\n" % (ip, countIpMatches(matches, signame, ip), signame)
            trafic = getDestsIp(matches, signame, ip)
            for dest, attepmts in trafic.items():
                message += "\t%3d attempt(s) towards %s\n" % (attepmts, dest)
            message += "\n"
    return message.strip(' \n\t')

def makeMail(message, recipients):
    msg = MIMEText(message)
    sender = recipients.pop('From')
    msg['Subject'] = "botalert message"
    msg['From'] = sender
    for key, values in recipients.items():
        msg[key] = ','.join(values)
    finalrecipients = []
    for frcpt in recipients:
        finalrecipients.extend(recipients[frcpt])
    return (sender, finalrecipients, msg)

if __name__ == "__main__":
    configexists = False
    logsexists = False

    #Do we have a config file?:
    if os.path.exists(defaults["config"]):
        pass
        configexists = True
    elif os.path.exists(curdirconfig):
        defaults["config"] = curdirconfig
        configexists = True
    elif os.path.exists(filedirconfig):
        defaults["config"] = curdirconfig
        configexists = True

    if configexists:
        config, defaults = updateConfAndDefaults()

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config",
                      metavar="CONFIG_FILE", default=defaults["config"],
                      help="read configuration from CONFIG_FILE [default: %default]")
    parser.add_option("-l", "--logfile", dest="logfile", default=defaults["logfile"],
                      help="log file to parse [default: %default] (default can be overridden in the CONFIG_FILE)")
    parser.add_option("-s", "--sendmail", dest="sendmail", action="store_true",
                      help="send alert mail")

    (options, args) = parser.parse_args()

    #do we still have a config file?:
    if not os.path.exists(options.config):
        configexists = False

    #Do we have a new logfile from arguments?:
    if options.logfile != defaults["logfile"]:
        new_options_logfile = True
    else:
        new_options_logfile = False

    #Do we receive another config file from arguments? And if yes do we have to update config?
    if defaults["config"] != options.config:
        defaults["config"] = options.config
        config, defaults = updateConfAndDefaults()

    #Do we use logfile from config file or from arguments?:
    if new_options_logfile:
        defaults["logfile"] = options.logfile

    #If we have a config file, What signals shall we log?:
    signals = config.signals()

    #Does the logfile exist?:
    if os.path.exists(defaults["logfile"]):
        logsexists = True
        logs = getLogs()

    #We have both a config file and log file, so lets work:
    matches = None
    if configexists and logsexists:
        matches = getMatches(signals,logs)
    else:
        #else we quit and display the help message.
        sys.exit(parser.print_help())

    #do we have matchs?
    if matches:
        matched_signals = countAllMatches(matches)
        recipients = config.recipients()
        message = allertsToText(matches)
        sender, finalrecipients, mail = makeMail(message, recipients)

    #Do we have to send result by email?:
    if options.sendmail:
        smtpserver = defaults.get('mailserver')
        if matched_signals and smtpserver:
            smtp = smtplib.SMTP(smtpserver)
            smtp.sendmail(sender, finalrecipients, mail.as_string())
            smtp.quit()
    else:
        #else we display the result on the standard output
        if matches:
            print message
        else:
            print "Nothing Detected"
