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

"""Provides information about the running context of the application."""


class IApplicationContext(object):
    """C{IApplicationContext} provides information about the running context
    of the application. Each context is shared by all applications that are
    open for one user. In a web-environment this corresponds to a HttpSession.

    @author: Vaadin Ltd.
    @author: Richard Lincoln
    @version: 1.0.1
    """

    def getBaseDirectory(self):
        """Returns application context base directory.

        Typically an application is deployed in a such way that is has an
        application directory. For web applications this directory is the root
        directory of the web applications. In some cases applications might not
        have an application directory.

        @return: The application base directory or C{None} if the application
                has no base directory.
        """
        raise NotImplementedError


    def getApplications(self):
        """Returns a collection of all the applications in this context.

        Each application context contains all active applications for one user.

        @return: A collection containing all the applications in this context.
        """
        raise NotImplementedError


    def addTransactionListener(self, listener):
        """Adds a transaction listener to this context. The transaction
        listener is called before and after each each request related to this
        session except when serving static resources.

        The transaction listener must not be C{None}.
        """
        raise NotImplementedError


    def removeTransactionListener(self, listener):
        """Removes a transaction listener from this context.

        @param listener:
                   the listener to be removed.
        @see: ITransactionListener
        """
        raise NotImplementedError


    def generateApplicationResourceURL(self, resource, urlKey):
        """Generate a URL that can be used as the relative location of e.g. an
        L{ApplicationResource}.

        This method should only be called from the processing of a UIDL
        request, not from a background thread. The return value is null if used
        outside a suitable request.

        @deprecated: this method is intended for terminal implementation only
                    and is subject to change/removal from the interface (to
                    L{AbstractCommunicationManager})

        @param resource:
        @param urlKey:
                   a key for the resource that can later be extracted from a URL
                   with L{getURLKey}
        """
        raise NotImplementedError


    def isApplicationResourceURL(self, context, relativeUri):
        """Tests if a URL is for an application resource (APP/...).

        @deprecated: this method is intended for terminal implementation only
                    and is subject to change/removal from the interface (to
                    L{AbstractCommunicationManager})
        """
        raise NotImplementedError


    def getURLKey(self, context, relativeUri):
        """Gets the identifier (key) from an application resource URL. This key
        is the one that was given to L{generateApplicationResourceURL} when
        creating the URL.

        @deprecated: this method is intended for terminal implementation only
                    and is subject to change/removal from the interface (to
                    L{AbstractCommunicationManager})
        """
        raise NotImplementedError


class ITransactionListener(object):
    """Interface for listening to transaction events. Implement this interface
    to listen to all transactions between the client and the application.
    """

    def transactionStart(self, application, transactionData):
        """Invoked at the beginning of every transaction.

        The transaction is linked to the context, not the application so if
        you have multiple applications running in the same context you need
        to check that the request is associated with the application you are
        interested in. This can be done looking at the application parameter.

        @param application:
                   the Application object.
        @param transactionData:
                   the Data identifying the transaction.
        """
        raise NotImplementedError


    def transactionEnd(self, application, transactionData):
        """Invoked at the end of every transaction.

        The transaction is linked to the context, not the application so if
        you have multiple applications running in the same context you need
        to check that the request is associated with the application you are
        interested in. This can be done looking at the application parameter.

        @param application:
                   the application object.
        @param transactionData:
                   the data identifying the transaction.
        """
        raise NotImplementedError
