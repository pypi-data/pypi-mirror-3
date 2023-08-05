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

from twisted.python import failure, log
from twisted.application import service
from twisted.internet import defer
from buildbot.process.properties import Properties
from buildbot.util import ComparableMixin
from buildbot.changes import changes

def isScheduler(sch):
    "Check that an object is a scheduler; used for configuration checks."
    return isinstance(sch, BaseScheduler)

class BaseScheduler(service.MultiService, ComparableMixin):
    """
    Base class for all schedulers; this provides the equipment to manage
    reconfigurations and to handle basic scheduler state.  It also provides
    utility methods to begin various sorts of builds.

    Subclasses should add any configuration-derived attributes to
    C{base.Scheduler.compare_attrs}.
    """

    compare_attrs = ('name', 'builderNames', 'properties')

    def __init__(self, name, builderNames, properties):
        """
        Initialize a Scheduler.

        @param name: name of this scheduler (used as a key for state)
        @type name: unicode

        @param builderNames: list of builders this scheduler may start
        @type builderNames: list of unicode

        @param properties: properties to add to builds triggered by this
        scheduler
        @type properties: dictionary

        @param consumeChanges: true if this scheduler wishes to be informed
        about the addition of new changes.  Defaults to False.  This should
        be passed explicitly from subclasses to indicate their interest in
        consuming changes.
        @type consumeChanges: boolean
        """
        service.MultiService.__init__(self)
        self.name = name
        "name of this scheduler; used to identify replacements on reconfig"

        errmsg = ("The builderNames argument to a scheduler must be a list "
                  "of Builder names.")
        assert isinstance(builderNames, (list, tuple)), errmsg
        for b in builderNames:
            assert isinstance(b, basestring), errmsg
        self.builderNames = builderNames
        "list of builder names to start in each buildset"

        self.properties = Properties()
        "properties that are contributed to each buildset"
        self.properties.update(properties, "Scheduler")
        self.properties.setProperty("scheduler", name, "Scheduler")

        self.schedulerid = None
        """ID of this scheduler; set just before the scheduler starts, and set
        to None after stopService is complete."""

        self.master = None
        """BuildMaster instance; set just before the scheduler starts, and set
        to None after stopService is complete."""

        # internal variables
        self._change_subscription = None
        self._change_consumption_lock = defer.DeferredLock()
        self._objectid = None

    ## service handling

    def _setUpScheduler(self, schedulerid, master, manager):
        # this is called by SchedulerManager *before* startService
        self.schedulerid = schedulerid
        self.master = master

    def startService(self):
        service.MultiService.startService(self)

    def stopService(self):
        d = defer.maybeDeferred(self._stopConsumingChanges)
        d.addCallback(lambda _ : service.MultiService.stopService(self))
        return d

    def _shutDownScheduler(self):
        # called by SchedulerManager *after* stopService is complete
        self.schedulerid = None
        self.master = None

    ## state management

    @defer.deferredGenerator
    def getState(self, *args, **kwargs):
        """
        For use by subclasses; get a named state value from the scheduler's
        state, defaulting to DEFAULT.

        @param name: name of the value to retrieve
        @param default: (optional) value to return if C{name} is not present
        @returns: state value via a Deferred
        @raises KeyError: if C{name} is not present and no default is given
        @raises TypeError: if JSON parsing fails
        """
        # get the objectid, if not known
        if self._objectid is None:
            wfd = defer.waitForDeferred(
                self.master.db.state.getObjectId(self.name,
                                        self.__class__.__name__))
            yield wfd
            self._objectid = wfd.getResult()

        wfd = defer.waitForDeferred(
            self.master.db.state.getState(self._objectid, *args, **kwargs))
        yield wfd
        yield wfd.getResult()

    @defer.deferredGenerator
    def setState(self, key, value):
        """
        For use by subclasses; set a named state value in the scheduler's
        persistent state.  Note that value must be json-able.

        @param name: the name of the value to change
        @param value: the value to set - must be a JSONable object
        @param returns: Deferred
        @raises TypeError: if JSONification fails
        """
        # get the objectid, if not known
        if self._objectid is None:
            wfd = defer.waitForDeferred(
                self.master.db.state.getObjectId(self.name,
                                        self.__class__.__name__))
            yield wfd
            self._objectid = wfd.getResult()

        wfd = defer.waitForDeferred(
            self.master.db.state.setState(self._objectid, key, value))
        yield wfd
        wfd.getResult()

    ## status queries

    # TODO: these aren't compatible with distributed schedulers

    def listBuilderNames(self):
        "Returns the list of builder names"
        return self.builderNames

    def getPendingBuildTimes(self):
        "Returns a list of the next times that builds are scheduled, if known."
        return []

    ## change handling

    def startConsumingChanges(self, fileIsImportant=None, change_filter=None,
                              onlyImportant=False):
        """
        Subclasses should call this method from startService to register to
        receive changes.  The BaseScheduler class will take care of filtering
        the changes (using change_filter) and (if fileIsImportant is not None)
        classifying them.  See L{gotChange}.  Returns a Deferred.

        @param fileIsImportant: a callable provided by the user to distinguish
        important and unimportant changes
        @type fileIsImportant: callable

        @param change_filter: a filter to determine which changes are even
        considered by this scheduler, or C{None} to consider all changes
        @type change_filter: L{buildbot.changes.filter.ChangeFilter} instance

        @param onlyImportant: If True, only important changes, as specified by
        fileIsImportant, will be added to the buildset.
        @type onlyImportant: boolean

        """
        assert fileIsImportant is None or callable(fileIsImportant)

        # register for changes with master
        assert not self._change_subscription
        def changeCallback(change):
            # ignore changes delivered while we're not running
            if not self._change_subscription:
                return

            if change_filter and not change_filter.filter_change(change):
                return
            if fileIsImportant:
                try:
                    important = fileIsImportant(change)
                    if not important and onlyImportant:
                        return
                except:
                    log.err(failure.Failure(),
                            'in fileIsImportant check for %s' % change)
                    return
            else:
                important = True

            # use change_consumption_lock to ensure the service does not stop
            # while this change is being processed
            d = self._change_consumption_lock.acquire()
            d.addCallback(lambda _ : self.gotChange(change, important))
            def release(x):
                self._change_consumption_lock.release()
            d.addBoth(release)
            d.addErrback(log.err, 'while processing change')
        self._change_subscription = self.master.subscribeToChanges(changeCallback)

        return defer.succeed(None)

    def _stopConsumingChanges(self):
        # (note: called automatically in stopService)

        # acquire the lock change consumption lock to ensure that any change
        # consumption is complete before we are done stopping consumption
        d = self._change_consumption_lock.acquire()
        def stop(x):
            if self._change_subscription:
                self._change_subscription.unsubscribe()
                self._change_subscription = None
            self._change_consumption_lock.release()
        d.addBoth(stop)
        return d

    def gotChange(self, change, important):
        """
        Called when a change is received; returns a Deferred.  If the
        C{fileIsImportant} parameter to C{startConsumingChanges} was C{None},
        then all changes are considered important.

        @param change: the new change object
        @type change: L{buildbot.changes.changes.Change} instance
        @param important: true if this is an important change, according to
        C{fileIsImportant}.
        @type important: boolean
        @returns: Deferred
        """
        raise NotImplementedError

    ## starting bulids

    def addBuildsetForLatest(self, reason='', external_idstring=None,
                        branch=None, repository='', project='',
                        builderNames=None, properties=None):
        """
        Add a buildset for the 'latest' source in the given branch,
        repository, and project.  This will create a relative sourcestamp for
        the buildset.

        This method will add any properties provided to the scheduler
        constructor to the buildset, and will call the master's addBuildset
        method with the appropriate parameters.

        @param reason: reason for this buildset
        @type reason: unicode string
        @param external_idstring: external identifier for this buildset, or None
        @param branch: branch to build (note that None often has a special meaning)
        @param repository: repository name for sourcestamp
        @param project: project name for sourcestamp
        @param builderNames: builders to name in the buildset (defaults to
            C{self.builderNames})
        @param properties: a properties object containing initial properties for
            the buildset
        @type properties: L{buildbot.process.properties.Properties}
        @returns: (buildset ID, buildrequest IDs) via Deferred
        """
        d = self.master.db.sourcestamps.addSourceStamp(
                branch=branch, revision=None, repository=repository,
                project=project)
        d.addCallback(self.addBuildsetForSourceStamp, reason=reason,
                                external_idstring=external_idstring,
                                builderNames=builderNames,
                                properties=properties)
        return d

    def addBuildsetForChanges(self, reason='', external_idstring=None,
            changeids=[], builderNames=None, properties=None):
        """
        Add a buildset for the combination of the given changesets, creating
        a sourcestamp based on those changes.  The sourcestamp for the buildset
        will reference all of the indicated changes.

        This method will add any properties provided to the scheduler
        constructor to the buildset, and will call the master's addBuildset
        method with the appropriate parameters.

        @param reason: reason for this buildset
        @type reason: unicode string
        @param external_idstring: external identifier for this buildset, or None
        @param changeids: nonempty list of changes to include in this buildset
        @param builderNames: builders to name in the buildset (defaults to
            C{self.builderNames})
        @param properties: a properties object containing initial properties for
            the buildset
        @type properties: L{buildbot.process.properties.Properties}
        @returns: (buildset ID, buildrequest IDs) via Deferred
        """
        assert changeids is not []

        # attributes for this sourcestamp will be based on the most recent
        # change, so fetch the change with the highest id
        d = self.master.db.changes.getChange(max(changeids))
        def chdict2change(chdict):
            if not chdict:
                return None
            return changes.Change.fromChdict(self.master, chdict)
        d.addCallback(chdict2change)
        def create_sourcestamp(change):
            return self.master.db.sourcestamps.addSourceStamp(
                    branch=change.branch,
                    revision=change.revision,
                    repository=change.repository,
                    project=change.project,
                    changeids=changeids)
        d.addCallback(create_sourcestamp)
        d.addCallback(self.addBuildsetForSourceStamp, reason=reason,
                                external_idstring=external_idstring,
                                builderNames=builderNames,
                                properties=properties)
        return d

    def addBuildsetForSourceStamp(self, ssid, reason='', external_idstring=None,
            properties=None, builderNames=None):
        """
        Add a buildset for the given, already-existing sourcestamp.

        This method will add any properties provided to the scheduler
        constructor to the buildset, and will call the master's
        L{BuildMaster.addBuildset} method with the appropriate parameters, and
        return the same result.

        @param reason: reason for this buildset
        @type reason: unicode string
        @param external_idstring: external identifier for this buildset, or None
        @param properties: a properties object containing initial properties for
            the buildset
        @type properties: L{buildbot.process.properties.Properties}
        @param builderNames: builders to name in the buildset (defaults to
            C{self.builderNames})
        @returns: (buildset ID, buildrequest IDs) via Deferred
        """
        # combine properties
        if properties:
            properties.updateFromProperties(self.properties)
        else:
            properties = self.properties

        # apply the default builderNames
        if not builderNames:
            builderNames = self.builderNames

        # translate properties object into a dict as required by the
        # addBuildset method
        properties_dict = properties.asDict()

        # add the buildset
        return self.master.addBuildset(
                ssid=ssid, reason=reason, properties=properties_dict,
                builderNames=builderNames, external_idstring=external_idstring)
