**Note:** This workflow is in **ALPHA**! It may do horrible, horrible things!

[Alfred][] is a fantastic app for OS X (similar to [Gnome Do][]) and I set
out to create a JIRA workflow.

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