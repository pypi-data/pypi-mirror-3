# -*- coding: utf-8 -*-
#
# File: testRDV_RendezVous.py
#
# Copyright (c) 2008 by Ecreall
# Generator: ArchGenXML Version 2.2 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Vincent Fretin <vincentfretin@ecreall.com>"""
__docformat__ = 'plaintext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

##code-section module-header #fill in your manual code here
##/code-section module-header

#
# Test-cases for class(es) 
#

from Testing import ZopeTestCase
from Products.rendezvous.config import *
from Products.rendezvous.tests.testPlone import testPlone

# Import the tested classes
from Products.rendezvous.content.RDV_RendezVous import RDV_RendezVous

##code-section module-beforeclass #fill in your manual code here
from Products.rendezvous.browser.RDV_RendezVousEdit import RDV_RendezVousEdit
from Products.rendezvous.browser.RDV_PropositionsEdit import RDV_PropositionsEdit
from zope.publisher.browser import TestRequest
from zope.component import getMultiAdapter
##/code-section module-beforeclass


class testRDV_RendezVous(testPlone):
    """Test-cases for class(es) ."""

    ##code-section class-header_testRDV_RendezVous #fill in your manual code here
    ##/code-section class-header_testRDV_RendezVous

    def afterSetUp(self):
        self.app.REQUEST.SESSION = {}
        self.setRoles('Manager')
        rdv_id = self.portal.invokeFactory('RDV_RendezVous', 'rdv1')
        self.rdv = getattr(self.portal, rdv_id)
        self.portal.portal_membership.addMember("johndoe", "passwd", ['Member'], [], properties={'name': 'John Doe', 'email': 'johndoe@example.com'})
        self.johndoe = self.portal.portal_membership.getMemberById('johndoe')

    # Manually created methods

    def test_DelDateWithPropositions(self):
        propositions = self._create_propositions()
        # remove one date
        expected_propositions = {'2008-11-28':['8:30'],
                                 '2008-11-29':[''],
        }
        self.rdv.setPropositionsByDates(expected_propositions)
        self.assertEquals(expected_propositions, self.rdv.getPropositionsByDates())

    def test_AddDate(self):
        request = self.app.REQUEST
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEquals([], view.getSelectedDates())
        request.set('rdvdate', '2008-11-27')
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEquals(['2008-11-27'], view.getSelectedDates())
        request.set('rdvdate', '2008-11-28')
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEquals(['2008-11-27', '2008-11-28'], view.getSelectedDates())
        request.set('rdvdate', '2008-11-29')
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEquals(['2008-11-27', '2008-11-28', '2008-11-29'], view.getSelectedDates())

    def test_manage_participants_in_proposition(self):
        prop_id = self.rdv.invokeFactory('RDV_Proposition', 'prop')
        prop = getattr(self.rdv, prop_id)
        prop.manageParticipant('johndoe', checked=True)
        self.assertEquals(('johndoe',), prop.getAvailable())
        prop.manageParticipant('johnsmith', True)
        self.assertEquals(('johndoe', 'johnsmith'), prop.getAvailable())
        prop.manageParticipant('johndoe', False)
        self.assertEquals(('johnsmith',), prop.getAvailable())

    def test_SaveChanges(self):
        request = self.app.REQUEST
        view = RDV_PropositionsEdit(self.rdv, request)
        props = {'2008-12-25': ['12:00', 'minuit', 'midi', '', ''],
                 '2008-12-19': ['13:00', '14:00', '', '', ''],
                 '2008-12-31': ['', '', '', '', ''] }
        request.form = props
        request.form['finish'] = 'Finish'
        view.saveChanges()
        self.assertEquals({'2008-12-25': ['12:00', 'minuit', 'midi'],
                           '2008-12-19': ['13:00', '14:00'],
                            '2008-12-31': ['']}, self.rdv.getPropositionsByDates())

    def _create_propositions(self):
        propositions = {'2008-11-27':['morning', 'evening'],
                        '2008-11-28':['8:30'],
                        '2008-11-29':[''],
        }

        self.rdv.setPropositionsByDates(propositions)
        return propositions

    def test_SetPropositions(self):
        propositions = self._create_propositions()
        self.assertEquals(propositions, self.rdv.getPropositionsByDates())

    def test_reedit_rendezvous(self):
        propositions = self._create_propositions()
        request = self.app.REQUEST
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEquals(propositions.keys(), view.getSelectedDates())

    def test_NbColumns(self):
        request = self.app.REQUEST
        view = RDV_PropositionsEdit(self.rdv, request)
        self.assertEquals(view.NB_COLUMNS, view.getNbColumns())

    def test_incColumns(self):
        request = self.app.REQUEST
        request.form['extend'] = 'Extends columns'
        view = RDV_PropositionsEdit(self.rdv, request)
        self.assertEquals(view.NB_COLUMNS, view.getNbColumns())
        view.saveChanges()
#        view.incNbColumns()
        self.assertEquals(view.NB_COLUMNS*2, view.getNbColumns())

    def test_DelDate(self):
        request = self.app.REQUEST
        # add two dates
        request.set('rdvdate', '2008-11-27')
        view = RDV_RendezVousEdit(self.rdv, request)
        request.set('rdvdate', '2008-11-28')
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEquals(['2008-11-27', '2008-11-28'], view.getSelectedDates())
        # remove one date
        request.set('rdvdate', '2008-11-27')
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEquals(['2008-11-28'], view.getSelectedDates())

    def test_add_other_dates(self):
        propositions = self._create_propositions()
        request = self.app.REQUEST
        request.set('rdvdate', '2008-11-30')
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEquals(sorted(list(propositions.keys()) + ['2008-11-30']), sorted(view.getSelectedDates()))

    def test_add_participant(self):
        self.rdv.addParticipant('johndoe')
        self.assertEquals(('johndoe',), self.rdv.getParticipants())

    def test_add_participant_twice(self):
        self.rdv.addParticipant('johndoe')
        self.rdv.addParticipant('johndoe')
        self.assertEquals(('johndoe',), self.rdv.getParticipants())

    def test_addParticipant(self):
        request = self.app.REQUEST
        view = RDV_PropositionsEdit(self.rdv, request)
        props = {'2008-12-25': ['12:00', 'minuit', 'midi', '', ''],
                 '2008-12-19': ['13:00', '14:00', '', '', ''],
                 '2008-12-31': ['', '', '', '', ''] }
        request.form = props
        request.form['finish'] = 'Finish'
        view.saveChanges()
        request = TestRequest()
        request.AUTHENTICATED_USER = self.johndoe
        propositions = self.rdv.getPropositionObjectsByDates()
        request.form = {'propositions': (propositions['2008-12-25'][0][1],)}
        view = getMultiAdapter((self.rdv, request), name='add-participation')
        view()
        prop = getattr(self.rdv, propositions['2008-12-25'][0][1])
        self.assertEquals(prop.getAvailable(), ('johndoe',))
        self.assertEquals(prop.getUnavailable(), ())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testRDV_RendezVous))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


