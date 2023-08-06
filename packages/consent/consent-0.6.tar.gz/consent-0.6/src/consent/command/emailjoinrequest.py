from dm.command.emailbase import EmailCommand
from consent.dictionarywords import *

class EmailJoinCommand(EmailCommand):

    messageType = ''

    def __init__(self, site, person):
        super(EmailJoinCommand, self).__init__()
        self.site = site
        self.person = person

    def getParams(self):
        baseUrl = 'http://%s%s' % (self.dictionary[DOMAIN_NAME], self.dictionary[URI_PREFIX])
        return {
            'siteName': self.dictionary[SYSTEM_SERVICE_NAME].decode('utf-8'),
            'siteLabel': self.site.getLabelValue(),
            'siteUrl': '%s/sites/%s/' % (baseUrl, self.site.id),
            'personUrl': '%s/people/%s/' % (baseUrl, self.person.name),
            'personLabel': self.person.getLabelValue(),
            'approveUrl': '%s/sites/%s/members/%s/approve/' % (baseUrl, self.site.id, self.person.name),
            'rejectUrl': '%s/sites/%s/members/%s/reject/' % (baseUrl, self.site.id, self.person.name),
        }

    def execute(self):
        super(EmailJoinCommand, self).execute()
        # Log the result.
        if self.isDispatchedOK:
            msg = "%s mail sent for site %s, person %s" % (self.messageType, self.site.id, self.person.name)
            self.logger.info(msg)
        else:
            msg = "%s mail could not be sent for site %s, person %s" % (self.messageType, self.site.id, self.person.name)
            self.logger.warn(msg)


class EmailJoinRequest(EmailJoinCommand):
       
    messageType = 'Join'     
    messageTemplate = """Greetings,

A request has been made to join one of your sites.

Site: %(siteLabel)s
%(siteUrl)s

Person: %(personLabel)s
%(personUrl)s

You may wish to log in and respond to this request.

Approve this request:
%(approveUrl)s

Reject this request:
%(rejectUrl)s

Regards,

The %(siteName)s Team
"""

    def getMessageToList(self):
        emails = []
        adminRole = self.registry.roles['Administrator']
        for member in self.site.members:
            if member.role == adminRole:
                emails.append(member.person.email)
        return emails

    def getMessageSubject(self):
        subject =  '%s membership request' % self.site.id
        return self.wrapMessageSubject(subject)


class EmailJoinApprove(EmailJoinCommand):
        
    messageType = 'Approve' 
    messageTemplate = """Greetings,

Congratualations, the following membership request has been approved by the site administrator:

Site: %(siteLabel)s
%(siteUrl)s

Person: %(personLabel)s
%(personUrl)s

Role: %(roleName)s

You should now be able to access the site when you log into your account.

Regards,

The %(siteName)s Team
"""

    def getParams(self):
        params = super(EmailJoinApprove, self).getParams()
        params['roleName'] = self.site.members[self.person].role.name
        return params

    def getMessageToList(self):
        if self.person is None:
            return []
        return [self.person.email]

    def getMessageSubject(self):
        subject =  '%s membership request approved' % self.site.id
        return self.wrapMessageSubject(subject)


class EmailJoinReject(EmailJoinCommand):
        
    messageType = 'Reject' 
    messageTemplate = """Greetings,

Sorry, the following membership request has been rejected by the site administrator:

Site: %(siteLabel)s
%(siteUrl)s

Person: %(personLabel)s
%(personUrl)s

Regards,

The %(siteName)s Team
"""

    def getMessageToList(self):
        if self.person is None:
            return []
        return [self.person.email]

    def getMessageSubject(self):
        subject =  '%s membership request rejected' % self.site.id
        return self.wrapMessageSubject(subject)

