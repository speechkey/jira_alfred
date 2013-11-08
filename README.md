**Note:** This workflow is in **ALPHA**! It may do horrible, horrible things!

[Alfred][] is a fantastic app for OS X (similar to [Gnome Do][]) and I set
out to create a JIRA workflow.

## Goals

- Self contained, no dependencies to install.
- Use [OAuth1][] instead of basic auth (no saving passwords anywhere)
- At a minimum, allow us to search for tickets, presenting the top results
  and a link to see more.

## Hiccups

Right off the bat, there are a few problems:

- Alfred doesn't source your profile, meaning any `$PATH` customizations
  will not get loaded. Normally, for a portable python script you would use the
  `#!/usr/bin/env python` [shebang][], but that won't work for non-system
  Python.
- The joy of workflow's is that they're (usually) self-contained and one-click
  to install. We'll need to include our dependencies.
- JIRA's API is convoluted, and only supports OAuth1 with RSA-SHA1
  signing. Most libraries use [PyCrypto] to handle RSA-SHA1, which is painful
  to install and is not pure Python.
- Alfred's [feedback][] is [XML][], so we'll want to abstract that away a bit.

So, in short:

- We'll have to make our script work with the system python, covering any
  Apple-introduced bugs.
- We'll have to bundle all of our dependencies as a plain [.zip] or as an
  [.egg].
- We'll need to find or create a pure-python package for RSA-SHA1 to replace
  PyCrypto.

## Getting Rid Of PyCrypto

There's a great pre-existing library for JIRA, simply called [jira-python][].
It's built on top of [requests][], [requests-oauthlib][], [tlslite][] and 
[PyCrypto][]. PyCrypto is required by requests-oauthlib and is used to sign
requests, but as mentioned above it is unfortunately not pure Python. tlslite
on the other hand *is* pure python, and *optionally* uses native extensions
for acceleration. It also happens to implement the RSA-SHA1 signing we need
for our OAuth requests.

The downside is that requests-oauthlib and the [oauthlib][] library it's
built on don't really provide any way of adding new signing methods. The only
solution at this point without actually modifying oauthlib is to monkey patch
it, replacing the old signing method with our new one that's based on tlslite
instead of PyCrypto.

    :::python
    def _pure_python_rsa_sha1(base_string, rsa_private_key):
        """
        An alternative, pure-python RSA-SHA1 signing method, using
        the tlslite library.
        """
        import base64
        from tlslite.utils import keyfactory

        private_key = keyfactory.parsePrivateKey(rsa_private_key)
        signature = private_key.hashAndSign(base_string.encode('ascii'))

        # This *must* be unicode, since oauthlib refuses to work with
        # anything else.
        return unicode(base64.b64encode(signature))

    # Monkey patch the built-in RSA-SHA1 signing method, since the
    # package offers no proper extension mechanism.
    from oauthlib.oauth1.rfc5849 import signature
    signature.sign_rsa_sha1 = _pure_python_rsa_sha1


## Building

1. Clone the repo
2. Inside a virtualenv (the makefile will trample your local packages due
   to limitations of pip) run "make all"
3. You're done! There will be a jira_alfred.alfredworkflow file you can double
   click to install.


## Installing

JIRA does not make this horribly straightforward, but it's not obscenely
complex either.

### Step 1 - Generate A Key-Pair

  RSA-SHA1 requires a public+private key-pair to securely sign your messages.
  I strongly recommend creating a new key-pair that can be shared with your
  co-workers.

    :::shell-session
    $ openssl genrsa -out jira.pem 1024
    $ openssl rsa -in jira.pem -pubout -out jira.pub

  You'll need `jira.pem` (the private key) and `jira.pub` (the public key)
  for the next two steps.

### Step 2 - Installing On JIRA

  Follow JIRA's [own guide][1] to setting up an OAuth application. You only
  need to configure *Incoming Authentication*. Where it asks you for a public
  key use the contents of `jira.pub`, generated in the last step. For your
  consumer key, enter whatever you want. You'll need the consumer key in
  the next step.

  If you share your private key and consumer key with your coworkers, then
  step 1 and step 2 can be skipped.

### Step 3 - Setup The Workflow

  1. Double-click the jira_alfred.alfredworkflow file to import it.
  2. Using Alfred, run `jira settings`
  3. Drag and drop your `jira.pem` into the folder opened in Finder.
  4. Using Alfred, run each of the following commands. You only need to do
     this once.
    1. `jira domain (+ your JIRA domain)`
    2. `jira consumer (+ your consumer key, entered in step #2)`
    3. `jira step 1`
    4. `jira step 2`
  5. You're done!


[oauth1]: http://en.wikipedia.org/wiki/OAuth
[Alfred]: http://www.alfredapp.com/
[Gnome Do]: http://do.cooperteam.net/
[PyCrypto]: https://www.dlitz.net/software/pycrypto/
[.zip]: http://docs.python.org/2/library/zipimport.html
[.egg]: http://stackoverflow.com/questions/2051192/what-is-a-python-egg
[feedback]: http://www.alfredforum.com/topic/5-generating-feedback-in-workflows/
[XML]: http://en.wikipedia.org/wiki/XML
[shebang]: http://en.wikipedia.org/wiki/Shebang_(Unix)

[jira-python]: http://jira-python.readthedocs.org/en/latest/
[requests]: http://www.python-requests.org/en/latest/
[requests-oauthlib]: https://github.com/requests/requests-oauthlib
[tlslite]: https://pypi.python.org/pypi/tlslite
[oauthlib]: https://github.com/idan/oauthlib

[1]: https://confluence.atlassian.com/display/JIRA044/Configuring+OAuth+Authentication+for+an+Application+Link