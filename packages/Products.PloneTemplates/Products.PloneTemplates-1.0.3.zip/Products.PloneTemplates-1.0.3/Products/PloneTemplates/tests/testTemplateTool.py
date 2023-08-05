from Testing import ZopeTestCase
from Products.PloneTemplates.tests import PloneTemplatesTestcase
from DateTime import DateTime
from Products.Archetypes.utils import shasattr

from Products.CMFCore.permissions import setDefaultRoles

from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.PloneTemplates.TemplateSchema import PloneTemplatesMixinSchema
from Products.PloneTemplates.config import *
from Products.Archetypes.ClassGen import generateMethods
from Products.CMFCore.permissions import ModifyPortalContent, View

# A test class defines a set of tests
class TestTemplateTool(PloneTemplatesTestcase.PloneTemplatesTestCase):

    # The afterSetUp method can be used to define test class variables
    # and perform initialisation before tests are run. The beforeTearDown() 
    # method can also be used to clean up anything set up in afterSetUp(),
    # though it is less commonly used since test always run in a sandbox
    # that is cleared after the test is run.
    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.memberareaCreationFlag = 1   
        self.addMember('fred', 'Fred Flintstone', 'fred@bedrock.com', ['Member', 'Manager'], '2002-01-01')
        self.addMember('barney', 'Barney Rubble', 'barney@bedrock.com', ['Member'], '2002-01-01')
        self.addMember('brubble', 'Bambam Rubble', 'bambam@bambam.net', ['Member' ], '2003-12-31')
        self.login('fred')
        self.portal.invokeFactory('Folder', 'f1')
        self.f1 = self.portal.f1
        self.tt = self.portal.PloneTemplates_tool


    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),}) 

    def injectSchema(self):
        # inject the mixinschema
        ATFolder.schema = ATFolderSchema + PloneTemplatesMixinSchema
        generateMethods(ATFolder, ATFolder.schema.fields())
        
    def testTemplateSchema(self):
        self.injectSchema()

        # now create a folder
        self.portal.invokeFactory('Folder', 'folder1')
        
        folder = self.portal.folder1
        folder.setInheritTemplates('0')
        
        self.failUnless(folder.getInheritTemplates(), '0')
    
    def testFetchTemplates(self):
        self.injectSchema()
        self.portal.invokeFactory('Folder', 'folder1')
        folder1 = self.portal.folder1
        
        folder1.invokeFactory('Folder', 'folder2')
        folder2 = folder1.folder2

        folder2.invokeFactory('Folder', 'folder3')
        folder3 = folder2.folder3


        # create some templates
        self.f1.invokeFactory('Template', 'tmp1')
        self.f1.invokeFactory('Template', 'tmp2')
        self.f1.invokeFactory('Template', 'tmp3')
        
        # set references on the folders
        folder1.setTemplates([self.f1.tmp1])
        folder1.setInheritTemplates('1')
        
        folder2.setTemplates([self.f1.tmp2])
        folder2.setInheritTemplates('1')
        
        folder3.setTemplates([self.f1.tmp3])
        folder3.setInheritTemplates('0')
        
        self.failUnless(self.tt.fetchTemplates(folder1), [self.f1.tmp1])
        self.failUnless(self.tt.fetchTemplates(folder2), [self.f1.tmp1,self.f1.tmp2])
        self.failUnless(self.tt.fetchTemplates(folder3), [self.f1.tmp3])
        
    def testFetchTemplateWithPermissions(self):
        self.injectSchema()
        self.portal.invokeFactory('Folder', 'folder1')
        folder1 = self.portal.folder1
        
        folder1.invokeFactory('Folder', 'folder2')
        folder2 = folder1.folder2

        folder2.invokeFactory('Folder', 'folder3')
        folder3 = folder2.folder3


        # create some templates
        self.f1.invokeFactory('Template', 'tmp1')
        self.f1.invokeFactory('Template', 'tmp2')
        self.f1.invokeFactory('Template', 'tmp3')
        
        # set references on the folders
        folder1.setTemplates([self.f1.tmp1])
        folder1.setInheritTemplates('1')
        
        folder2.setTemplates([self.f1.tmp2])
        folder2.setInheritTemplates('1')
        
        folder3.setTemplates([self.f1.tmp3])
        folder3.setInheritTemplates('0')
        
        # now set local roles
        # make sure members cannot see tmp2
        self.f1.tmp2.manage_permission(View, ['Manager'], acquire=0)
        
        self.login('barney')
        self.failUnless(self.tt.fetchTemplates(folder2), [self.f1.tmp1])
        
# This boilerplate method sets up the test suite
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # Add our test class here - you can add more test classes if you wish,
    # and they will be run together.
    suite.addTest(makeSuite(TestTemplateTool))
    return suite
