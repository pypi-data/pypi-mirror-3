from zope import interface
from zope.schema import Choice

from horae.groupselect import interfaces


class GroupedChoice(Choice):
    """ Grouped Choice field
    """
    interface.implements(interfaces.IGroupedChoice)

    def __init__(self, groups, **kw):
        super(GroupedChoice, self).__init__(**kw)
        assert interfaces.IGroups.providedBy(groups)
        self.groups = groups
