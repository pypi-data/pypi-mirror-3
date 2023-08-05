# Copyright (C) 2011 Vaadin Ltd.
# Copyright (C) 2011 Richard Lincoln
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Note: This is a modified file from Vaadin. For further information on
#       Vaadin please visit http://www.vaadin.com.

"""Defines a web application context for Muntjac applications."""

from muntjac.terminal.gwt.server.abstract_web_application_context import \
        AbstractWebApplicationContext

from muntjac.util import clsname


class WebApplicationContext(AbstractWebApplicationContext):
    """Web application context for Muntjac applications.

    This is automatically added as a L{HttpSessionBindingListener}
    when added to a L{HttpSession}.

    @author: Vaadin Ltd.
    @author: Richard Lincoln
    @version: 1.0.4
    """

    def __init__(self):
        """Creates a new Web Application Context."""
        super(WebApplicationContext, self).__init__()

        self.session = None
        self._reinitializingSession = False

        # Stores a reference to the currentRequest. None it not inside
        # a request.
        self._currentRequest = None


    def __getstate__(self):
        result = self.__dict__.copy()
        del result['session']
        del result['_reinitializingSession']
        del result['_currentRequest']
        return result


    def __setstate__(self, d):
        self.__dict__ = d
        self.session = None
        self._reinitializingSession = False
        self._currentRequest = None


    def startTransaction(self, application, request):
        self._currentRequest = request
        super(WebApplicationContext, self).startTransaction(application,
                request)


    def endTransaction(self, application, request):
        super(WebApplicationContext, self).endTransaction(application,
                request)
        self._currentRequest = None


    def valueUnbound(self, event):
        if not self._reinitializingSession:
            # Avoid closing the application if we are only reinitializing
            # the session. Closing the application would cause the state
            # to be lost and a new application to be created, which is not
            # what we want.
            super(WebApplicationContext, self).valueUnbound(event)


    def reinitializeSession(self):
        """Discards the current session and creates a new session with
        the same contents. The purpose of this is to introduce a new
        session key in order to avoid session fixation attacks.
        """
        oldSession = self.getHttpSession()
        # Stores all attributes (security key, reference to this context
        # instance) so they can be added to the new session
        attrs = dict()
        attrs.update(oldSession.values)

        # Invalidate the current session, set flag to avoid call to
        # valueUnbound
        self._reinitializingSession = True
        oldSession.invalidate()
        self._reinitializingSession = False

        # Create a new session
        newSession = self._currentRequest.session()

        # Restores all attributes (security key, reference to this context
        # instance)
        for name, val in attrs.iteritems():
            newSession.setValue(name, val)

        # Update the "current session" variable
        self.session = newSession


    def getBaseDirectory(self):
        """Gets the application context base directory.

        @see: L{ApplicationContext.getBaseDirectory}
        """
        realPath = self.getResourcePath(self.session, '/')
        if realPath is None:
            return None
        return realPath


    def getHttpSession(self):
        """Gets the http-session application is running in.

        @return: HttpSession this application context resides in.
        """
        return self.session


    @classmethod
    def getApplicationContext(cls, session, servlet):
        """Gets the application context for an HttpSession.

        @param session:
                   the HTTP session.
        @return: the application context for HttpSession.
        """
        cx = servlet.getSessionAttribute(session,
                clsname(WebApplicationContext), None)

        if cx is None:
            cx = WebApplicationContext()
            servlet.setSessionAttribute(session,
                clsname(WebApplicationContext), cx)

        if cx.session is None:
            cx.session = session

        return cx


    def addApplication(self, application):
        self.applications.add(application)


    def getApplicationManager(self, application, servlet):
        """Gets communication manager for an application.

        If this application has not been running before, a new manager is
        created.

        @return: CommunicationManager
        """
        mgr = self.applicationToAjaxAppMgrMap.get(application)

        if mgr is None:
            # Creates new manager
            mgr = servlet.createCommunicationManager(application)
            self.applicationToAjaxAppMgrMap[application] = mgr

        return mgr
