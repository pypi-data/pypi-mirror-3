from webunit import webunittest
import unittest

# Todo: Test access control for hidden projects. Viewer shouldn't be able to
# see other's memberships of hidden projects, unless also a member. Shouldn't
# be able to see hidden projects in list, index (startswith), and search
# unless a member. 

def suite():
    import consent.test.customer.kui.welcome
    import consent.test.customer.kui.submitproposal
#    import consent.test.customer.kui.admin
#    import consent.test.customer.kui.person
#    import consent.test.customer.kui.project
#    import consent.test.customer.kui.member
#    import consent.test.customer.kui.service
#    import consent.test.customer.kui.api
    suites = [
        consent.test.customer.kui.welcome.suite(),
        consent.test.customer.kui.submitproposal.suite(),
#        consent.test.customer.kui.admin.suite(),
#        consent.test.customer.kui.person.suite(),
#        consent.test.customer.kui.project.suite(),
#        consent.test.customer.kui.member.suite(),
#        consent.test.customer.kui.service.suite(),
#        consent.test.customer.kui.api.suite(),
    ]
    return unittest.TestSuite(suites)

