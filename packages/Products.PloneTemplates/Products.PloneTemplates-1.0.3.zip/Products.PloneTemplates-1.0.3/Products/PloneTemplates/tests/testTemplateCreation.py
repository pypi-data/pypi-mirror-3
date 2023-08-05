from Testing import ZopeTestCase
from Products.PloneTemplates.tests import PloneTemplatesTestcase
from DateTime import DateTime
from Products.Archetypes.utils import shasattr

from Products.CMFCore.permissions import setDefaultRoles

# A test class defines a set of tests
class TestTemplateCreation(PloneTemplatesTestcase.PloneTemplatesTestCase):

    # The afterSetUp method can be used to define test class variables
    # and perform initialisation before tests are run. The beforeTearDown() 
    # method can also be used to clean up anything set up in afterSetUp(),
    # though it is less commonly used since test always run in a sandbox
    # that is cleared after the test is run.
    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.memberareaCreationFlag = 1   
        self.addMember('fred', 'Fred Flintstone', 'fred@bedrock.com', ['Member', 'Manager'], '2002-01-01')
        self.addMember('barney', 'Barney Rubble', 'barney@bedrock.com', ['Member', 'Editor'], '2002-01-01')
        self.addMember('brubble', 'Bambam Rubble', 'bambam@bambam.net', ['Member'], '2003-12-31')
        self.login('fred')
        self.portal.invokeFactory('Folder', 'f1')
        self.f1 = self.portal.f1


    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),}) 
        
    def testAddTemplate(self):
        self.portal.invokeFactory('Template', 'tmp')
        self.failUnless(shasattr(self.portal, 'tmp'))
            
    def testEditTemplate(self):
        self.portal.invokeFactory('Template', 'tmp')
        tmp = self.portal.tmp
        tmp.setTitle('Some title')
        tmp.setDescription('Some description')
        tmp.setUsage('<p>Some usage text</p>')
        tmp.setShowUsage(True)
        
        self.failUnlessEqual(tmp.Title(), 'Some title')
        self.failUnlessEqual(tmp.Description(), 'Some description')
        self.failUnlessEqual(tmp.getUsage(), '<p>Some usage text</p>')
        self.failUnlessEqual(tmp.getShowUsage(), True)
        
        
    def testTemplateInstantiation(self):
        self.portal.invokeFactory('Template', 'tmp')
        tmp = self.portal.tmp
        
        #create some contents in the template
        tmp.invokeFactory('Document', 'doc1')
        tmp.invokeFactory('Link', 'link1')
        self.f1.manage_addLocalRoles('barney', ('Owner',))
        
        self.login('barney')
        
        # invoke instantiateTemplate.cpy
        self.f1.instantiateTemplate(templateUID=tmp.UID())

        #check for the contents
        contents=self.f1.objectIds()
        self.failUnless('doc1' in contents)
        self.failUnless('link1' in contents)
        
        #check ownership
        self.assertEqual(self.f1.doc1.getOwnerTuple()[1], 'barney')
        self.assertEqual(self.f1.link1.getOwnerTuple()[1], 'barney')
        
        #check creator
        self.failIf('barney' not in self.f1.doc1.Creators())
        self.failIf('barney' not in self.f1.link1.Creators())
        
    def testAutoIcon(self):
        self.portal.invokeFactory('Template', 'tmp')
        tmp = self.portal.tmp
        
        #create some contents in the template
        tmp.invokeFactory('Document', 'doc1')
        tmp.invokeFactory('Link', 'link1')
        
        icon = tmp.getAutoIcon()
        self.failUnlessEqual(icon, 'document_icon.gif')
        
    def testAutoIconType(self):
        self.portal.invokeFactory('Template', 'tmp')
        tmp = self.portal.tmp
        
        #create some contents in the template
        tmp.invokeFactory('Document', 'doc1')
        tmp.invokeFactory('Link', 'link1')
        
        type = tmp.getAutoIconType()
        self.failUnlessEqual(type, 'Document')
        
        
# This boilerplate method sets up the test suite
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # Add our test class here - you can add more test classes if you wish,
    # and they will be run together.
    suite.addTest(makeSuite(TestTemplateCreation))
    return suite
