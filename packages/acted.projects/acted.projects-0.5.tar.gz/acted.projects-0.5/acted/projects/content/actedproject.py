# -*- coding: utf-8 -*-

"""Definition of the ACTED Project content type
"""


from zope.interface import implements, directlyProvides

from Products.Archetypes.public import * 
from Products.ATExtensions.ateapi import *

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from acted.projects import projectsMessageFactory as _
from acted.projects.interfaces import IACTEDProject
from acted.projects.config import PROJECTNAME
#from archetypes.multifile.MultiFileField import MultiFileField
#from archetypes.multifile.MultiFileWidget import MultiFileWidget
#from iw.fss.FileSystemStorage import FileSystemStorage
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from DateTime.DateTime import *
from Products.Archetypes.public import FloatField, DecimalWidget
from acted.projects.config import ACTED_COUNTRIES
from acted.projects.config import ACTED_SECTORS
from acted.projects.config import ACTED_DONORS
from acted.projects.config import ACTED_YEARS

import re


ACTEDProjectSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.TextField(
        name='description',
        widget=atapi.TextAreaWidget(
        label=_(u'Project Description'),
        visible={'view': 'hidden', 'edit': 'hidden' }
      ),
      required=False,
      searchable=True
    ),


    atapi.StringField(
        name='projectCode',
        widget=atapi.StringWidget(
        label=_(u'Project Code'),
        maxlength=20,
        size=20
      ),
      required=False,
      searchable=True
    ),

    atapi.IntegerField(
        name='projectYear',
        widget=atapi.SelectionWidget(
        label=_(u'Year of Contract Signature'),
        format='select'
      ),
      vocabulary=ACTED_YEARS,
      enforceVocabulary=True,
      required=True,
      searchable=False
    ),



    atapi.StringField(
        name='projectCountry',
        widget=atapi.SelectionWidget(
        label=_(u'Country'),
        format='select'
      ),
      vocabulary=ACTED_COUNTRIES,
      enforceVocabulary=True,
      required=False,
      searchable=True
    ),



    atapi.StringField(
        name='projectDonor',
        widget=atapi.MultiSelectionWidget(
        label=_(u'Donor'),
        format='select',
        size=25
      ),
#      accessor='getProjectDonor',
      vocabulary=ACTED_DONORS,
      enforceVocabulary=True,
      required=False,
      searchable=False
    ),




    atapi.StringField(
        name='projectSectors',
        widget=atapi.MultiSelectionWidget(
        label=_(u'Sectors'),
        format='select',
        size='10'
      ),
      vocabulary=ACTED_SECTORS,
      required=False,
      searchable=True
    ),

    atapi.StringField(
        name='projectStatus',
        widget=atapi.SelectionWidget(
            label=_(u'Status'),
            format='select'
      ),
      vocabulary=['Ongoing','Complete'],
      required=False,
      searchable=False
    ),

    atapi.StringField(
      name='projectBudget',
      widget=atapi.StringWidget(
          label=_(u'Budget'),
          maxlength=20,
          size=20
      ),
      required=False,
      searchable=False
    ),


    atapi.ReferenceField(
        name='projectReferences',
        widget=ReferenceBrowserWidget(
            label=_(u'Reference Files'),
      ),
      required=False,
      searchable=False,
      multiValued=True,
      allow_sorting=True,
      relationship='WorksWith',
      allowed_types=('Document','File','Image','Folder')
    )



))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

ACTEDProjectSchema['title'].storage = atapi.AnnotationStorage()
ACTEDProjectSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(ACTEDProjectSchema, moveDiscussion=False)

class ACTEDProject(base.ATCTContent):
    """Details about a particular ACTED Project"""
    implements(IACTEDProject)

    meta_type = "ACTED Project"
    schema = ACTEDProjectSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    # this added on 13 Nov to fix adding new projects problem when
    # a project has one donor with a unicode name and one without
    # also changed was the coding delaration at line 1

    def setProjectDonor(self,value):
        retArr = []
        for donor in value:
            retArr.append(donor)
        self.getField('projectDonor').set(self, retArr)


"""
    def getProjectDonor(self):
        theDonors = self.getField('projectDonor').get(self)
        retval = ''
        for theDonor in theDonors:
            theDonor = re.sub('^-* ', '', theDonor)
            retval = retval + theDonor + ', '
        return retval[:-4]
"""

atapi.registerType(ACTEDProject, PROJECTNAME)
