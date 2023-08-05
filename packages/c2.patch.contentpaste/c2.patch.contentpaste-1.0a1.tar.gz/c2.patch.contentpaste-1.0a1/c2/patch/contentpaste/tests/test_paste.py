# coding: utf-8

import os
import unittest

from DateTime import DateTime
from Testing import ZopeTestCase as ztc
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from archetypes.referencebrowserwidget.tests.base import FunctionalTestCase
from Products.Five.testbrowser import Browser
from Products.PloneTestCase.setup import portal_owner, default_password


import c2.patch.contentpaste
PACKAGE_NAME = "c2.patch.contentpaste"


class TestPasteFuncs(FunctionalTestCase):
    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(c2.patch.contentpaste)
            # zcml.load_config('configure.zcml',
            #                  c2.patch.contentpaste)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass
    
    def afterSetUp(self):
        self.mtool = self.portal.portal_membership
        qi = self.portal.portal_quickinstaller
        qi.installProduct(PACKAGE_NAME)
        self.setRoles(['Manager'])
        wtool = self.portal.portal_workflow
        self.portal.invokeFactory('Folder', 'folder1')
        self.folder1 = getattr(self.portal, 'folder1')
        self.folder1.invokeFactory('Document', 'doc1')
        self.folder1.invokeFactory('Event', 'event1')
        doc1 = getattr(self.folder1, 'doc1')
        event1 = getattr(self.folder1, 'event1')
        doc1.setTitle('DOC1')
        doc1.setText('This is main text!!')
        doc1.setSubject(['TAG1', 'TAG2'])
        doc1.setEffectiveDate(DateTime('2010/10/27 06:50'))
        wtool.doActionFor(doc1, 'publish')
        doc1.reindexObject()
        event1.setTitle('EVENT1')
        event1.setText('This is event body text!!')
        event1.setSubject(['TAG1', 'TAG3'])
        event1.setEffectiveDate(DateTime('2010/10/27 18:50'))
        event1.setStartDate(DateTime('2012/01/01'))
        event1.setEndDate(DateTime('2012/01/02'))
        event1.setAttendees(['kara_d', 'zenich'])
        event1.setEventUrl('http://www.cmscom.jp/')
        wtool.doActionFor(event1, 'publish')
        event1.reindexObject()

        self.doc1 = doc1
        self.event1 = event1
        self.wtool = wtool
        self.setRoles([])
        
        browser = Browser()
        self.portal.error_log._ignored_exceptions = ()
        self.portal_url = self.portal.absolute_url()

        browser.open(self.portal_url + "/login_form")
        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()
        self.browser = browser

    def beforeTearDown(self):
        self.setRoles([])
        self.browser.open(self.portal_url + "/logout")

    def test_copy_menu_not_in_edit(self):
        # TODO : This test no good, because can not control roles.
        self.setRoles([])
        self.browser.open(self.portal_url + "/folder1/doc1")
        self.failUnless("/object_copy" not in self.browser.contents)

        self.setRoles(["Manager"])
        self.browser.open(self.portal_url + "/folder1/doc1")
        self.failUnless("/object_copy" in self.browser.contents)


    
    def test_duplicate_menu_in_edit(self):
        self.mtool.deleteLocalRoles(self.portal, portal_owner)
        self.setRoles(['Contributor'])
        self.browser.open(self.portal_url + "/folder1/doc1")
        self.failUnless("/@@content-past" in self.browser.contents)
    
    def test_duplicate_menu_not_in_folder(self):
        self.setRoles(['Manager'])
        self.browser.open(self.portal_url + "/folder1")
        self.failUnless("/@@content-past" not in self.browser.contents)
        

    def test_duplicate_page(self):
        self.setRoles(['Manager'])

        self.browser.open(self.portal_url + "/folder1/doc1/@@content-paste")

        self.failUnless('copy_of_doc1' in self.folder1.objectIds())
        copy_of_doc1 = getattr(self.folder1, 'copy_of_doc1')
        self.assertEqual(copy_of_doc1.Title(), 'copy_of_DOC1')
        self.assertEqual(copy_of_doc1.getText(), '<p>This is main text!!</p>')
        self.assertEqual(copy_of_doc1.Subject(), ('TAG1', 'TAG2'))
        self.assertEqual(copy_of_doc1.getEffectiveDate(), None)
        self.assertEqual(self.wtool.getInfoFor(copy_of_doc1, 'review_state'), 
                                        'private')

    
    def test_duplicate_event(self):
        self.setRoles(['Manager'])

        self.browser.open(self.portal_url + "/folder1/event1/@@content-paste")

        self.failUnless('copy_of_event1' in self.folder1.objectIds())
        copy_of_event1 = getattr(self.folder1, 'copy_of_event1')
        self.assertEqual(copy_of_event1.Title(), 'copy_of_EVENT1')
        self.assertEqual(copy_of_event1.getText(), '<p>This is event body text!!</p>')
        self.assertEqual(copy_of_event1.Subject(), ('TAG1', 'TAG3'))
        self.assertEqual(copy_of_event1.getEffectiveDate(), None)
        self.assertEqual(copy_of_event1.getRawStartDate(), DateTime('2012/01/01'))
        self.assertEqual(copy_of_event1.getRawEndDate(), DateTime('2012/01/02'))
        self.assertEqual(copy_of_event1.getAttendees(), ('kara_d', 'zenich'))
        self.assertEqual(copy_of_event1.getRawEventUrl(), "http://www.cmscom.jp/")
        self.assertEqual(self.wtool.getInfoFor(copy_of_event1, 'review_state'), 
                                        'private')


unittest.makeSuite(TestPasteFuncs)