#
# Skeleton ZopeTestCase
#

import os, sys
if __name__ == '__main__':
    sys.stderr = sys.stdout
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
ZopeTestCase.installProduct('IssueDealer')
ZopeTestCase.installProduct('ZCTextIndex')

# Setup core sessions
app = ZopeTestCase.app()
ZopeTestCase.utils.setupCoreSessions(app)
ZopeTestCase.closeConnections()

class fake_authenticated_user:

    def __init__(self, username, roles=[]):
        self.id = self.username = username
        self.roles = roles

    def getId(self):
        return self.id
        
class IssueDealerTest(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        '''Add object to default fixture'''
        # Set up sessioning objects
        sdm = self.app.session_data_manager
        self.app.REQUEST.set('SESSION', sdm.getSessionData())
        self.session = self.app.REQUEST.SESSION
        self.app.REQUEST['AUTHENTICATED_USER'] = fake_authenticated_user('morten')
        # Setup an Issue Dealer
        dispatcher = self.folder.manage_addProduct['IssueDealer']
        dispatcher.manage_add_issue_dealer('test_dealer')
        self.issue_dealer = self.folder['test_dealer']
        # Set user defaults
        # Setup IM session
        session = self.issue_dealer.sessions.manage_addSession()
        self.issue_dealer.get_user_preferences().issue_dealer_session = session.id

    def afterClear(self):
        '''Clean up after myself'''
        try: del self.issue_dealer
        except AttributeError: pass

    def testGetIssueDealer(self):
        self.issue_dealer.get_issue_dealer().meta_type == 'Issue Dealer'

    def testGetUniqueID(self):
        self.issue_dealer.get_unique_id()

class TestIssueAdd(IssueDealerTest):

    def testIssueAdd(self):
        '''Test adding of Issues'''
        self.issue_dealer.manage_add_issue(title='Test issue',
                                            contents="""
           Issue contents.  Issues are things that spring out
           from other issues.""")

class TestIssue(IssueDealerTest):

    def afterSetUp(self):
        IssueDealerTest.afterSetUp.im_func(self)
        self.issue = self.issue_dealer.manage_add_issue(title='Test issue',
                                            contents="""
           Issue contents.  Issues are things that spring out
           from other issues.""")

    def testRenderSTX(self):
        self.issue.render_stx_as_html()

    def testRenderText(self):
        self.issue.render_contents_as_text()

    def testIssueEdit(self):
        self.issue.manage_edit(title='Title',
                               contents='Contents',
                               state='open',
                               type='info',
                               owner='morten',
                               importance=1)

    def testRenderHTMLLink(self):
        self.issue.render_html_title_and_link()

    def testRenderContents(self):
        self.issue.render_contents()

    def testRenderImportanceWidget(self):
        self.issue.render_importance_level_widget()

    def testRenderImportance(self):
        assert self.issue.importance != 'Unknown'

    def testStateImportanceTitleSort(self):
        self.issue.get_state_importance_title_sort()

    def testGetOpenGoals(self):
        assert len(self.issue.get_open_goals()) == 0

    def testClosedGoals(self):
        assert len(self.issue.get_closed_goals()) == 0

    def testOpenProblems(self):
        assert len(self.issue.get_open_problems()) == 0

    def testClosedProblems(self):
        assert len(self.issue.get_closed_problems()) == 0

    def testOpenQuestions(self):
        assert len(self.issue.get_open_questions()) == 0

    def testClosedQuestions(self):
        assert len(self.issue.get_closed_questions()) == 0

    def testRelations(self):
        assert len(self.issue.get_relations()) == 0

    def testRenderOwner(self):
        assert self.issue.render_owner() == 'Morten'

class TestBase(TestIssue):

    def testCreateLink(self):
        self.issue.create_hyperlink('javascript:alert("Yo");',
                                    "Title")

    def testGetParents(self):
        assert len(self.issue.get_parents()) == 5

    def testRenderBreadcrumbs(self):
        return self.issue.render_breadcrumbs()

    def testRenderContextBreadcrumbs(self):
        return self.issue.render_context_breadcrumbs()

    def testRenderJavascriptBreadcrumbs(self):
        return self.issue.render_javascript_breadcrumbs()

    def testGetTitle(self):
        self.issue.get_title()

    def testGetIssues(self):
        assert len(self.issue.get_issues()) == 0

    def testGetOpenSuspendedIssues(self):
        assert len(self.issue.get_open_suspended_issues()) == 0

    def testGetClosedDiscardedIssues(self):
        assert len(self.issue.get_closed_discarded_issues()) == 0

    def testGetDeletedIssues(self):
        assert len(self.issue.get_deleted_issues()) == 0

    def testGetNumberOfIssues(self):
        assert self.issue.get_number_of_issues() == 0

    def testGetParentURL(self):
        self.issue.get_parent_url()

    def testCatalogSearch(self):
        assert len(self.issue.catalog_search(meta_type='Issue')) == 1

    def testGetUser(self):
        self.issue.get_user()

    def testGetUserNames(self):
        self.issue.get_usernames()

    def testRenderSearchImportanceLevelWidget(self):
        self.issue.render_search_importance_level_widget()

    def testRenderSearchOrderWidget(self):
        self.issue.render_search_sort_order_widget()

    def testIsIssue(self):
        assert self.issue.is_issue()

class TestBase(TestIssue):

    def testContextSearch(self):
        self.issue.manage_add_issue(title='Nested issue 1')
        self.issue.manage_add_issue(title='Nested issue 2')
        # 3 because we get the container and the issues
        assert len(self.issue.catalog_search(path=self.issue.absolute_url(relative=1))) == 3


class testRelation(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        TestIssue.afterSetUp.im_func(self)
        self.issue2 = self.issue_dealer.manage_add_issue(title="Another Issue, relations",
                                            contents="""Issues can
                                            have relations""")
        self.relation = self.issue.manage_add_relation(relation_=self.issue2.id,
                                       title="A test relation")

    def testGetRelatedObject(self):
        assert self.relation.get_related_object().id == self.issue2.id

    def testRenderHTMLTitleAndLink(self):
        self.relation.render_html_title_and_link()


if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestSomeProduct))
        return suite

