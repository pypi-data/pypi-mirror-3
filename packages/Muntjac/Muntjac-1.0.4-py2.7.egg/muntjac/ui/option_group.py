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

from muntjac.ui.abstract_select import AbstractSelect
from muntjac.data.container import IContainer

from muntjac.event.field_events import \
    BlurEvent, IBlurListener, IBlurNotifier, FocusEvent, \
    IFocusListener, IFocusNotifier

from muntjac.terminal.gwt.client.ui.v_option_group import VOptionGroup


class OptionGroup(AbstractSelect, IBlurNotifier, IFocusNotifier):
    """Configures select to be used as an option group."""

    CLIENT_WIDGET = None #ClientWidget(VOptionGroup, LoadStyle.EAGER)

    def __init__(self, *args):
        self._disabledItemIds = set()

        self._htmlContentAllowed = False

        args = args
        nargs = len(args)
        if nargs == 0:
            super(OptionGroup, self).__init__()
        elif nargs == 1:
            caption, = args
            super(OptionGroup, self).__init__(caption)
        elif nargs == 2:
            if isinstance(args[1], IContainer):
                caption, dataSource = args
                super(OptionGroup, self).__init__(caption, dataSource)
            else:
                caption, options = args
                super(OptionGroup, self).__init__(caption, options)
        else:
            raise ValueError, 'too many arguments'


    def paintContent(self, target):
        target.addAttribute('type', 'optiongroup')
        if self.isHtmlContentAllowed():
            target.addAttribute(VOptionGroup.HTML_CONTENT_ALLOWED, True)
        super(OptionGroup, self).paintContent(target)


    def paintItem(self, target, itemId):
        super(OptionGroup, self).paintItem(target, itemId)
        if not self.isItemEnabled(itemId):
            target.addAttribute('disabled', True)


    def changeVariables(self, source, variables):
        super(OptionGroup, self).changeVariables(source, variables)

        if FocusEvent.EVENT_ID in variables:
            self.fireEvent(FocusEvent(self))

        if BlurEvent.EVENT_ID in variables:
            self.fireEvent(BlurEvent(self))


    def addListener(self, listener, iface=None):
        if (isinstance(listener, IBlurListener) and
                (iface is None or issubclass(iface, IBlurListener))):
            self.registerListener(BlurEvent.EVENT_ID, BlurEvent,
                    listener, IBlurListener.blurMethod)

        if (isinstance(listener, IFocusListener) and
                (iface is None or issubclass(iface, IFocusListener))):
            self.registerListener(FocusEvent.EVENT_ID, FocusEvent,
                    listener, IFocusListener.focusMethod)

        super(OptionGroup, self).addListener(listener, iface)


    def addCallback(self, callback, eventType=None, *args):
        if eventType is None:
            eventType = callback._eventType

        if issubclass(eventType, BlurEvent):
            self.registerCallback(BlurEvent, callback,
                    BlurEvent.EVENT_ID, *args)

        elif issubclass(eventType, FocusEvent):
            self.registerCallback(FocusEvent, callback,
                    FocusEvent.EVENT_ID, *args)
        else:
            super(OptionGroup, self).addCallback(callback, eventType, *args)


    def removeListener(self, listener, iface=None):
        if (isinstance(listener, IBlurListener) and
                (iface is None or issubclass(iface, IBlurListener))):
            self.withdrawListener(BlurEvent.EVENT_ID, BlurEvent, listener)

        if (isinstance(listener, IFocusListener) and
                (iface is None or issubclass(iface, IFocusListener))):
            self.withdrawListener(FocusEvent.EVENT_ID, FocusEvent, listener)

        super(OptionGroup, self).removeListener(listener, iface)


    def removeCallback(self, callback, eventType=None):
        if eventType is None:
            eventType = callback._eventType

        if issubclass(eventType, BlurEvent):
            self.withdrawCallback(BlurEvent, callback, BlurEvent.EVENT_ID)

        elif issubclass(eventType, FocusEvent):
            self.withdrawCallback(FocusEvent, callback, FocusEvent.EVENT_ID)

        else:
            super(OptionGroup, self).removeCallback(callback, eventType)


    def setValue(self, newValue, repaintIsNotNeeded=None):
        if repaintIsNotNeeded is not None and repaintIsNotNeeded is True:
            # Check that value from changeVariables() doesn't contain unallowed
            # selections: In the multi select mode, the user has selected or
            # deselected a disabled item. In the single select mode, the user
            # has selected a disabled item.
            if self.isMultiSelect():
                currentValueSet = self.getValue()
                newValueSet = newValue
                for itemId in currentValueSet:
                    if (not self.isItemEnabled(itemId)
                            and not (itemId in newValueSet)):
                        self.requestRepaint()
                        return

                for itemId in newValueSet:
                    if (not self.isItemEnabled(itemId)
                            and not (itemId in currentValueSet)):
                        self.requestRepaint()
                        return
            else:
                if newValue is None:
                    newValue = self.getNullSelectionItemId()

                if not self.isItemEnabled(newValue):
                    self.requestRepaint()
                    return

        super(OptionGroup, self).setValue(newValue, repaintIsNotNeeded)


    def setItemEnabled(self, itemId, enabled):
        """Sets an item disabled or enabled. In the multiselect mode, a disabled
        item cannot be selected or deselected by the user. In the single
        selection mode, a disable item cannot be selected.

        However, programmatical selection or deselection of an disable item is
        possible. By default, items are enabled.

        @param itemId:
                   the id of the item to be disabled or enabled
        @param enabled:
                   if true the item is enabled, otherwise the item is disabled
        """
        if itemId is not None:

            if enabled:
                self._disabledItemIds.remove(itemId)
            else:
                self._disabledItemIds.add(itemId)

            self.requestRepaint()


    def isItemEnabled(self, itemId):
        """Returns true if the item is enabled.

        @param itemId:
                   the id of the item to be checked
        @return: true if the item is enabled, false otherwise
        @see: L{setItemEnabled}
        """
        if itemId is not None:
            return not (itemId in self._disabledItemIds)

        return True


    def setHtmlContentAllowed(self, htmlContentAllowed):
        """Sets whether html is allowed in the item captions. If set to true,
        the captions are passed to the browser as html and the developer is
        responsible for ensuring no harmful html is used. If set to false, the
        content is passed to the browser as plain text.

        @param htmlContentAllowed:
                 true if the captions are used as html, false if used as plain
                 text
        """
        self._htmlContentAllowed = htmlContentAllowed
        self.requestRepaint()


    def isHtmlContentAllowed(self):
        """Checks whether captions are interpreted as html or plain text.

        @return: true if the captions are used as html, false if used as plain
                 text
        @see: L{setHtmlContentAllowed}
        """
        return self._htmlContentAllowed
