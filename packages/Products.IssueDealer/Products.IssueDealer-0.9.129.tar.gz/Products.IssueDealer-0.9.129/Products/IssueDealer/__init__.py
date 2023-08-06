import id_config
import Globals, ZODB, OFS
from Products import HTMLTools
import AccessControl
import utilities

issue_dealer_globals = globals()

def add_publisher(klass, method):
    """Adds a publisher."""
    issue_dealer.issue_dealer.publishers_.append({'meta_type':klass.meta_type,
                       'method':method.__name__})
    setattr(issue_dealer.issue_dealer, method.__name__, method)

def add_gateway(klass, method):
    """Adds a gateway."""
    issue_dealer.issue_dealer.gateways_.append({'meta_type':klass.meta_type,
                       'method':method.__name__})
    setattr(issue_dealer.issue_dealer, method.__name__, method)


def make_app():
    AccessControl.SecurityManagement.newSecurityManager(None, AccessControl.User.system)
    app = ZODB.ZApplication.ZApplicationWrapper(Globals.DB, 'Application',
      OFS.Application.Application, (), Globals.VersionNameName)
    AccessControl.SecurityManagement.noSecurityManager()
    return app()

import issue_dealer

def initialize(context): 
    """Initialize the Issue Dealer product."""
    try:
        """Try to register the product."""
        context.registerClass(
            issue_dealer.issue_dealer,
            constructors = (
                issue_dealer.manage_add_issue_dealer_form,
                issue_dealer.manage_add_issue_dealer),
            )

    except:
        import sys, traceback, string
        type, val, tb = sys.exc_info()
        sys.stderr.write(string.join(
            traceback.format_exception(type, val, tb), ''))
        del type, val, tb

import report
