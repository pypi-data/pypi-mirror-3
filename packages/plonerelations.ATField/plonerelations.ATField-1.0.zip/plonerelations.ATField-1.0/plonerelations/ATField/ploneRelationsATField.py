from logging import getLogger

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import Field, ObjectField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Widget import ReferenceWidget
from Products.CMFCore.utils import getToolByName

from plone.app.relations.interfaces import IRelationshipSource, IRelationshipTarget

logger = getLogger('plonerelations.ATField')
log = logger.warning


class PloneRelationsATField(ObjectField):
    """ An AT field which creates plone.relations"""
    _properties = Field._properties.copy()

    _properties.update({
        'type' : 'reference',
        'default' : None,
        'widget' : ReferenceWidget,

        'relationship' : None, # required
        'allowed_types' : (),  # a tuple of portal types, empty means allow all
        'allowed_types_method' :None,
        'relationship_interface' : None,

        })

    security = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, aslist=False, **kwargs):
        """get() returns the list of objects referenced under the relationship
        """
        res = IRelationshipSource(instance).getTargets(relation=self.relationship)

        # singlevalued ref fields return only the object, not a list,
        # unless explicitely specified by the aslist option

        if not self.multiValued:
            if len(res) > 1:
                log("%s references for non multivalued field %s of %s" % (len(res),
                                                                          self.getName(),
                                                                          instance))
            if not aslist:
                if res:
                    res = res[0]
                else:
                    res = None

        return res

    security.declarePrivate('getRaw')
    def getRaw(self, instance, aslist=False, **kwargs):
        """Return the list of UIDs referenced under this fields
        relationship
        """
        brains=self.get(instance, aslist=aslist, **kwargs)
        if brains is not None:
            if self.multiValued or aslist:
                brains=[i.UID() for i in brains]
            else:
                brains=brains.UID()

        return brains

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        if value is None:
            value = ()

        if not isinstance(value, (list, tuple)):
            value = value,

        value = filter(None,value)

        if not self.multiValued and len(value) > 1:
            raise ValueError, \
                  "Multiple values given for single valued field %r" % self

        #convert uids to objects if necessary
        objects = []

        uid_tool = getToolByName (instance,'uid_catalog')

        for v in value:
            if isinstance(v, basestring):
                results = uid_tool(UID=v)
                if results:
                    objects.append (results[0].getObject())
            else:
                objects.append(v)

        source = IRelationshipSource(instance)
        delRelationship = source.deleteRelationship
        oldTargets = source.getTargets(relation=self.relationship)

        # Delete relationships that are no longer wanted
        for target in oldTargets:
            if target not in objects:
                delRelationship(target, relation=self.relationship, multiple=True)


        kw = {}
        if self.relationship_interface:
            kw ['interfaces'] = (self.relationship_interface,)

        for obj in objects:
            if obj not in oldTargets:
                source.createRelationship(obj,relation=self.relationship,**kw)


registerField(PloneRelationsATField,
              title='Plone Relations ATField',
              description=('Used for storing references using plone.app.relations '))

registerPropertyType('relationship_interface', 'interface')


class ReversePloneRelationsATField(ObjectField):
    """ An AT field which creates plone.relations"""
    _properties = Field._properties.copy()

    _properties.update({
        'type' : 'reference',
        'default' : None,
        'widget' : ReferenceWidget,

        'relationship' : None, # required
        'allowed_types' : (),  # a tuple of portal types, empty means allow all
        'allowed_types_method' :None,
        'relationship_interface' : None,

        })

    security = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, aslist=False, **kwargs):
        """get() returns the list of objects referenced under the relationship
        """
        res = IRelationshipTarget(instance).getSources(relation=self.relationship)

        # singlevalued ref fields return only the object, not a list,
        # unless explicitely specified by the aslist option

        if not self.multiValued:
            if len(res) > 1:
                log("%s references for non multivalued field %s of %s" % (len(res),
                                                                          self.getName(),
                                                                          instance))
            if not aslist:
                if res:
                    res = res[0]
                else:
                    res = None

        return res

    security.declarePrivate('getRaw')
    def getRaw(self, instance, aslist=False, **kwargs):
        """Return the list of UIDs referenced under this fields
        relationship
        """
        return [i.UID() for i in self.get(instance, aslist, **kwargs)]

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        if value is None:
            value = ()

        if not isinstance(value, (list, tuple)):
            value = value,

        value = filter(None,value)

        if not self.multiValued and len(value) > 1:
            raise ValueError, \
                  "Multiple values given for single valued field %r" % self

        #convert uids to objects if necessary
        objects = []

        uid_tool = getToolByName (instance,'uid_catalog')

        for v in value:
            if isinstance(v, basestring):
                results = uid_tool(UID=v)
                if results:
                    objects.append (results[0].getObject())
            else:
                objects.append(v)

        target = IRelationshipTarget(instance)
        #delRelationship = source.deleteRelationship
        oldSources = target.getSources(relation=self.relationship)

        # Delete relationships that are no longer wanted
        for source in oldSources:
            if source not in objects:
                IRelationshipSource(source).deleteRelationship(target.target, relation=self.relationship, multiple=True)

        kw = {}
        if self.relationship_interface:
            kw['interfaces'] = (self.relationship_interface,)

        for obj in objects:
            if obj not in oldSources:
                IRelationshipSource(obj).createRelationship(target.target,relation=self.relationship,**kw)


registerField(ReversePloneRelationsATField,
              title='Reverse Plone Relations ATField',
              description=('Used for storing references using plone.app.relations '))
