Introduction
============

``horae.groupselect`` provides a grouped ``Dropdown`` widget for
`zope.formlib <http://pypi.python.org/pypi/zope.formlib>`_ using
the default ``optgroup`` elements provided by HTML.

Usage
=====

To use a grouped dropdown widget the previously used ``Choice`` field
of the schema has to be replaced by a ``GroupedChoice`` field provided
in ``horae.groupedselect.field``. A ``GroupedChoice`` field takes the
exactly same parameters as the stock ``Choice`` field but additionally
an instance of a groups provider (implementing
``horae.groupedselect.interfaces.IGroups``) has to be provided over the
parameter ``groups``. The mentioned groups provider converts the
vocabulary of the field into a list of groups.

Imagine field to select a country and you would like to group them by
region::

    from zope import interface, implements
    from zope.schema import vocabulary
    
    from horae.groupedselect import field, interfaces
    
    class Country(object):
        def __init__(self, region, country):
            self.region = region
            self.country = country
    
    class CountryGroups(object):
        implements(interfaces.IGroups)
    
        def groups(self, vocabulary):
            """
            Converts the given vocabulary into a list of groups:
    
                return (('Group 1', (term1, term2, term3)),
                        ('Group 2', (term6, term5, term6)),)
            """
            groups = {}
            for term in vocabulary:
                if not term.value.region in groups:
                    groups[term.value.region] = ()
                groups[term.value.region] = groups[term.value.region] + \
                    (term,)
            return groups.items()
    
    class ICountrySelection(interface.Interface):
        
        country = field.GroupedChoice(
            title = u'Country',
            vocabulary = vocabulary.SimpleVocabulary((
                # ...
                vocabulary.SimpleTerm(
                    Country(u'Europe', u'Switzerland'),
                    'ch',
                    u'Switzerland'
                ),
                vocabulary.SimpleTerm(
                    Country(u'Europe', u'Germany'),
                    'de',
                    u'Germany'
                ),
                vocabulary.SimpleTerm(
                    Country(u'Europe', u'Austria'),
                    'at',
                    u'Austria'
                ),
                vocabulary.SimpleTerm(
                    Country(u'Europe', u'France'),
                    'fr',
                    u'France'
                ),
                # ...
                vocabulary.SimpleTerm(
                    Country(u'North America', u'USA'),
                    'us',
                    u'USA'
                ),
                vocabulary.SimpleTerm(
                    Country(u'Europe', u'Canada'),
                    'ca',
                    u'Canada'
                ),
                # ...
            )),
            groups = CountryGroups()
        )

Dependencies
============

* `zope.schema <http://pypi.python.org/pypi/zope.schema>`_
* `zope.formlib <http://pypi.python.org/pypi/zope.formlib>`_
