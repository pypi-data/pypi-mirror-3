from plone.app.portlets.browser.interfaces import IManageColumnPortletsView


class IManagePortletPagePortletsView(IManageColumnPortletsView):
    """Marker interface for editing portlets on a portlet page.

    By deriving from IManageColumnPortletsView, we get some generic
    portlet management UI.
    """
