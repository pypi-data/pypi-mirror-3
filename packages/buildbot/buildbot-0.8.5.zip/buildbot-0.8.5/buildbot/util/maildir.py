# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members


# This is a class which watches a maildir for new messages. It uses the
# linux dirwatcher API (if available) to look for new files. The
# .messageReceived method is invoked with the filename of the new message,
# relative to the top of the maildir (so it will look like "new/blahblah").

import os
from twisted.python import log, runtime
from twisted.application import service, internet
from twisted.internet import reactor, defer
dnotify = None
try:
    import dnotify
except:
    log.msg("unable to import dnotify, so Maildir will use polling instead")

class NoSuchMaildir(Exception):
    pass

class MaildirService(service.MultiService):
    """I watch a maildir for new messages. I should be placed as the service
    child of some MultiService instance. When running, I use the linux
    dirwatcher API (if available) or poll for new files in the 'new'
    subdirectory of my maildir path. When I discover a new message, I invoke
    my .messageReceived() method with the short filename of the new message,
    so the full name of the new file can be obtained with
    os.path.join(maildir, 'new', filename). messageReceived() should be
    overridden by a subclass to do something useful. I will not move or
    delete the file on my own: the subclass's messageReceived() should
    probably do that.
    """
    pollinterval = 10  # only used if we don't have DNotify

    def __init__(self, basedir=None):
        """Create the Maildir watcher. BASEDIR is the maildir directory (the
        one which contains new/ and tmp/)
        """
        service.MultiService.__init__(self)
        if basedir:
            self.setBasedir(basedir)
        self.files = []
        self.dnotify = None

    def setBasedir(self, basedir):
        # some users of MaildirService (scheduler.Try_Jobdir, in particular)
        # don't know their basedir until setServiceParent, since it is
        # relative to the buildmaster's basedir. So let them set it late. We
        # don't actually need it until our own startService.
        self.basedir = basedir
        self.newdir = os.path.join(self.basedir, "new")
        self.curdir = os.path.join(self.basedir, "cur")

    def startService(self):
        service.MultiService.startService(self)
        if not os.path.isdir(self.newdir) or not os.path.isdir(self.curdir):
            raise NoSuchMaildir("invalid maildir '%s'" % self.basedir)
        try:
            if dnotify:
                # we must hold an fd open on the directory, so we can get
                # notified when it changes.
                self.dnotify = dnotify.DNotify(self.newdir,
                                               self.dnotify_callback,
                                               [dnotify.DNotify.DN_CREATE])
        except (IOError, OverflowError):
            # IOError is probably linux<2.4.19, which doesn't support
            # dnotify. OverflowError will occur on some 64-bit machines
            # because of a python bug
            log.msg("DNotify failed, falling back to polling")
        if not self.dnotify:
            t = internet.TimerService(self.pollinterval, self.poll)
            t.setServiceParent(self)
        self.poll()

    def dnotify_callback(self):
        log.msg("dnotify noticed something, now polling")

        # give it a moment. I found that qmail had problems when the message
        # was removed from the maildir instantly. It shouldn't, that's what
        # maildirs are made for. I wasn't able to eyeball any reason for the
        # problem, and safecat didn't behave the same way, but qmail reports
        # "Temporary_error_on_maildir_delivery" (qmail-local.c:165,
        # maildir_child() process exited with rc not in 0,2,3,4). Not sure
        # why, and I'd have to hack qmail to investigate further, so it's
        # easier to just wait a second before yanking the message out of new/

        reactor.callLater(0.1, self.poll)


    def stopService(self):
        if self.dnotify:
            self.dnotify.remove()
            self.dnotify = None
        return service.MultiService.stopService(self)

    @defer.deferredGenerator
    def poll(self):
        assert self.basedir
        # see what's new
        for f in self.files:
            if not os.path.isfile(os.path.join(self.newdir, f)):
                self.files.remove(f)
        newfiles = []
        for f in os.listdir(self.newdir):
            if not f in self.files:
                newfiles.append(f)
        self.files.extend(newfiles)
        for n in newfiles:
            try:
                wfd = defer.waitForDeferred(self.messageReceived(n))
                yield wfd
                wfd.getResult()
            except:
                log.msg("while reading '%s' from maildir '%s':" % (n, self.basedir))
                log.err()

    def moveToCurDir(self, filename):
        """
        Call this from messageReceived to start processing the message; this
        moves the message file to the 'cur' directory and returns an open file
        handle for it.

        @param filename: unqualified filename of the message
        @returns: open file
        """
        if runtime.platformType == "posix":
            # open the file before moving it, because I'm afraid that once
            # it's in cur/, someone might delete it at any moment
            path = os.path.join(self.newdir, filename)
            f = open(path, "r")
            os.rename(os.path.join(self.newdir, filename),
                      os.path.join(self.curdir, filename))
        elif runtime.platformType == "win32":
            # do this backwards under windows, because you can't move a file
            # that somebody is holding open. This was causing a Permission
            # Denied error on bear's win32-twisted1.3 buildslave.
            os.rename(os.path.join(self.newdir, filename),
                      os.path.join(self.curdir, filename))
            path = os.path.join(self.curdir, filename)
            f = open(path, "r")

        return f

    def messageReceived(self, filename):
        """Process a received message.  The filename is relative to self.newdir.
        Returns a Deferred."""
        raise NotImplementedError
