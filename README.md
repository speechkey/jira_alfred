**Note:** This workflow is in **ALPHA**! It may do horrible, horrible things!

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
  2. Right-click on the workflow in Alfred and select "Show In Finder"
  3. Drag and drop your `jira.pem` into the folder opened in Finder.
  4. Using Alfred, run each of the following commands. You only need to do
     this once.
    1. `jira domain (+ your JIRA domain)`
    2. `jira consumer (+ your consumer key, entered in step #2)`
    3. `jira step 1`
    4. `jira step 2`
  5. You're done!