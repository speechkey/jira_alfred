#!/usr/bin/env python
# -*- coding: utf-8 -*-
def _pure_python_rsa_sha1(base_string, rsa_private_key):
    """
    An alternative, pure-python RSA-SHA1 signing method, using
    the tlslite library.
    """
    import base64
    from tlslite.utils import keyfactory

    private_key = keyfactory.parsePrivateKey(rsa_private_key)
    signature = private_key.hashAndSign(base_string.encode('ascii'))

    return unicode(base64.b64encode(signature))

# Monkey patch the built-in RSA-SHA1 signing method, since the
# package offers no proper extension mechanism.
from oauthlib.oauth1.rfc5849 import signature
signature.sign_rsa_sha1 = _pure_python_rsa_sha1

import os.path
import urlparse
import functools

import requests
from jira.client import JIRA
from oauthlib.oauth1 import SIGNATURE_RSA
from requests_oauthlib import OAuth1

from alpy import ScriptFilter

JIRA_REQUEST_TOKEN = '/plugins/servlet/oauth/request-token'
JIRA_ACCESS_TOKEN = '/plugins/servlet/oauth/access-token'
JIRA_AUTHORIZE = '/plugins/servlet/oauth/authorize'


def requires_auth(f):
    @functools.wraps(f)
    def _f(self, *args, **kwargs):
        required_settings = [
            'consumer_key',
            'root',
            'access_token',
            'access_token_secret'
        ]

        for setting in required_settings:
            if self.get(setting) is None:
                return [
                    ({
                        'arg': 'not_used',
                        'valid': 'no'
                    }, {
                        'title': 'Not Authenticated!',
                        'subtitle': 'You haven\'t finished the setup!',
                        'icon': 'icon.png'
                    })
                ]

            return f(self, *args, **kwargs)

    return _f


def requires_pem(f):
    @functools.wraps(f)
    def _f(self, *args, **kwargs):
        if not self.rsa_key:
            return [
                ({
                    'arg': 'not_used',
                    'valid': 'no'
                }, {
                    'title': 'No jira.pem file!',
                    'subtitle': (
                        'You need to add a jira.pem file to this'
                        ' workflow!'
                    ),
                    'icon': 'icon.png'
                })
            ]
        return f(self, *args, **kwargs)

    return _f


class JiraAlfred(ScriptFilter):
    """
    Usage:
        JiraAlfred settings
        JiraAlfred set <key> <value> [--no-set]
        JiraAlfred get <key>
        JiraAlfred search <query>
        JiraAlfred step (1|2)
    """
    def main(self, args):
        if args['set']:
            return self.sub_set(args)
        elif args['get']:
            return self.sub_get(args)
        elif args['step']:
            if args['1']:
                return self.sub_step_1(args)
            elif args['2']:
                return self.sub_step_2(args)
        elif args['settings']:
            return self.sub_settings(args)
        elif args['search']:
            return self.sub_search(args)

    def sub_set(self, args):
        """
        Utility sub-method to set a key.
        """
        if not args['--no-set']:
            self.set(args['<key>'], args['<value>'])

        return [
            ({
                'arg': args['<value>']
            }, {
                'title': 'Set {key} to {value}'.format(
                    key=args['<key>'],
                    value=args['<value>']
                ),
                'icon': 'icon.png'
            })
        ]

    def sub_get(self, args):
        """
        Utility sub-method to get a key.
        """
        value = self.get(args['<key>'], default='')

        return [
            ({
                'arg': value
            }, {
                'title': value,
                'icon': 'icon.png'
            })
        ]

    @requires_pem
    def sub_step_1(self, args):
        """
        Step one & two of the 3-legged OAuth1 authentication.
        """
        oauth = OAuth1(
            self.get('consumer_key'),
            signature_method=SIGNATURE_RSA,
            signature_type='auth_header',
            rsa_key=self.rsa_key
        )

        # Fetch the request token and token_secret...
        r = requests.post(
            self.jira_request_token,
            # FIXME: Verify must be False because openssl doesn't
            #        have access to cacerts.
            verify=False,
            auth=oauth
        )

        token_and_secret = dict(urlparse.parse_qsl(r.content))

        # Store the token and token_secret, we'll need them for the
        # next step when we get the access tokens.
        self.set('request_token', token_and_secret['oauth_token'])
        self.set(
            'request_token_secret',
            token_and_secret['oauth_token_secret']
        )

        url = self.jira_auth_token + '?oauth_token={0}'.format(
            token_and_secret['oauth_token']
        )

        return [
            ({
                'arg': url
            }, {
                'title': 'Open JIRA Authentication Page',
                'icon': 'icon.png'
            })
        ]

    @requires_pem
    def sub_step_2(self, args):
        """
        Step three of the 3-legged OAuth1 authentication.
        """
        oauth = OAuth1(
            self.get('consumer_key'),
            signature_method=SIGNATURE_RSA,
            rsa_key=self.rsa_key,
            resource_owner_key=self.get('request_token'),
            resource_owner_secret=self.get('request_token_secret')
        )

        r = requests.post(
            self.jira_access_token,
            verify=False,
            auth=oauth
        )

        access = dict(urlparse.parse_qsl(r.text))
        if access.get('oauth_problem'):
            # A problem occured with the OAuth1 authentication.
            return [({
                'arg': 'not_used',
                'valid': 'no'
            }, {
                'title': 'Could not authenticate!',
                'subtitle': 'Did you forget to do step 1?',
                'icon': 'icon.png'
            })]

        self.set('access_token', access['oauth_token'])
        self.set('access_token_secret', access['oauth_token_secret'])

        return [
            ({
                'arg': 'not_used'
            }, {
                'title': 'Success!',
                'icon': 'icon.png'
            })
        ]

    @requires_pem
    @requires_auth
    def sub_search(self, args):
        jira = JIRA(options={
            'server': self.get('root'),
            'verify': False
        }, oauth={
            'access_token': self.get('access_token'),
            'access_token_secret': self.get('access_token_secret'),
            'consumer_key': self.get('consumer_key'),
            'key_cert': self.rsa_key
        })

        results = jira.search_issues(
            args['<query>'],
            maxResults=15,
            fields=[
                'summary',
                'status',
                'assignee'
            ]
        )

        if not results:
            # If we don't return anything, Alfred will default
            # search, which just looks crummy.
            return [
                ({
                    'valid': 'no'
                }, {
                    'title': 'No Results',
                    'subtitle': 'Nothing could be found for that search term.',
                    'icon': 'icon.png'
                })
            ]

        # We found at least one result.
        return [
            ({
                'arg': self.get('root') + '/browse/' + r.key
            }, {
                'title': '{key} - {summary}'.format(
                    key=r.key,
                    summary=r.fields.summary
                ),
                'subtitle': '{status} - Assigned to {assignee}'.format(
                    status=r.fields.status.name,
                    assignee=r.fields.assignee.displayName
                ),
                'icon': 'icon.png'
            })
            for r in results
        ]

    def sub_settings(self, args):
        """
        Return
        """
        return [
            ({
                'arg': self.non_volatile_path
            }, {
                'title': 'Open JIRA Settings Folder',
                'icon': 'icon.png'
            })
        ]


    @property
    def rsa_key(self):
        rsa_path = os.path.join(
            self.non_volatile_path,
            'jira.pem'
        )

        if not os.path.isfile(rsa_path):
            return None

        with open(rsa_path, 'rb') as fin:
            return fin.read()

    @property
    def jira_request_token(self):
        return self.get('root') + JIRA_REQUEST_TOKEN

    @property
    def jira_auth_token(self):
        return self.get('root') + JIRA_AUTHORIZE

    @property
    def jira_access_token(self):
        return self.get('root') + JIRA_ACCESS_TOKEN


ja = JiraAlfred()
ja._main()
