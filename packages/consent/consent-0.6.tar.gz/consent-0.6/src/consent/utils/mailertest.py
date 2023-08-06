import unittest

import consent.utils.mailer

class TestSend(unittest.TestCase):
    tags = [ 'cli' ]
    disable = True

    def test_send(self):
        to = ['consent-admin@localhost']
        from_address = to[0]
        subject = 'Testing the consent email system'
        consent.utils.mailer.send(from_address, to, subject, subject)
        # have to test the result by eye ...

if __name__ == '__main__':
    unittest.main()
