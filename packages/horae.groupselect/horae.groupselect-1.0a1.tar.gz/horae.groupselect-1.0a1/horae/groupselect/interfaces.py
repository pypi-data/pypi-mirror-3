from zope import interface
from zope.schema._bootstrapfields import Field
from zope.schema.interfaces import IChoice


class IGroupedChoice(IChoice):
    """ Grouped Choice field
    """

    groups = Field(
        title=u"Groups provider",
        description=u"The :py:class:`IGroups` provides the groups for the values in the vocabulary",
        required=True,
        default=None
    )


class IGroups(interface.Interface):
    """ Groups provider
    """

    def groups(vocabulary):
        """
        Converts the given vocabulary into a list of groups::

            return (('Group 1', (term1, term2, term3)),
                    ('Group 2', (term6, term5, term6)),)
        """
