# -*- coding: utf-8 -*-
import os.path, sys, os
from hgapi import hgapi

def example_hook(repo, user, start, end):
    """Small, stupid example hook that verifies
    that the code is really, really tested. For sure.
    """
    for rev in xrange(start, end + 1):
        print 
        if not "TESTED!!!!" in repo[rev].desc:
            print("Abort: Code not tested!\n")
            print("Comment was: %s" % (repo[rev].desc,)) 
            return True

def has_multiple_heads(repo, user, start, end):
    """Check if multiple heads are being added"""
    heads = repo.hg_heads()
    count = 0
    for rev in xrange(start, end + 1):
        if repo[rev].node in heads:
            count += 1
    print("Found %d heads\n" % (count+1,))
    return count > 1
    

def adds_branch(repo, user, start, end):
    """Check if a set of changes adds a new branch
    Returns True if any revision in repo[start:end] does
    not share branch with any parent"""
    heads = repo.hg_heads()
    
    for rev in xrange(start, end + 1):
        revbranch = repo[rev].branch
        one_parent_ok = False
        for parent in repo[rev].parents:
            if repo[parent].branch == revbranch:
                one_parent_ok = True
        if not one_parent_ok:
            print("Rev %s adds a branch" % (repo[rev].node))
            return True
    return False

def _get_user(env):
    """Get username from, in order: REMOTE_USER, 
    USER, USERNAME from the env given"""

    if 'REMOTE_USER' in env: #remote
        user = env['REMOTE_USER']
    elif 'USER' in env: #unixes
        user = env['USER']
    elif 'USERNAME' in env: #windows
        user = env['USERNAME']
    return user


def _get_reponame(repo, dest):
    """Get configured name of this repository"""
    for tmp in repo.configlist('autohook', 'repos'):
        if os.path.abspath(repo.config('autohook', "%s.path" % tmp)) == dest:
            return tmp
    return None

def _load_module(name, path):
    """Find and load module"""
    import imp
    mod = imp.find_module(name, path)
    globals()[name] = imp.load_module(name, *mod)

def _load_modules(repo):
    """Load modules configured in autohook.loadmodules"""
    for module in repo.configlist("autohook", "loadmodules"):
        print("Loading %s" % (module,))
        _load_module(module, repo.configlist("autohook", "loadpath"))

    
def hook(repo, node, pending, env):
    """Run hooks"""
    def debug(msg): 
        if repo.configbool('autohook', 'debug'): 
            print(msg + "\n")
    def info(msg):
        print(msg + "\n")
    def error(msg):
        print(msg + "\n")
        
    #Get the user
    user = _get_user(env)
    debug("User is %s" % (user,))
    
    #if superuser is set and matches, bypass hooks
    if user in repo.configlist('autohook', 'superuser'):
        info("User %s bypassing hooks" % (user,))
        return False
        
    #load configured modules
    _load_modules(repo)

    #Resolve path and see if we should handle this repo
    dest = os.path.abspath(pending)
    if not repo.configbool('autohook', 'selective'):
        repotests = []
    else:
        reponame = _get_reponame(repo, dest)
        if not reponame: 
            info("Not configured for repo at %s" % (dest,))
            return False
        debug("Repo name " + reponame)
        repotests = repo.configlist('autohook', '%s.tests' % (reponame,))

    #Get first and last revision
    start = repo[node].rev
    end = repo['tip'].rev

    debug("Looking at rev %s to %s" % (start, end))

    #Run tests, first global and then specific for this repo
    for test in (repo.configlist('autohook', 'tests') + repotests):
        debug("Running " + test)
        #Resolve nested names
        if "." in test:
            names = test.split(".")
            test_func = getattr(globals()[".".join(names[:-1])], names[-1])
        else:
            test_func = globals()[test]
        #run test
        if test_func(repo=repo, user=user, start=start, end=end):
            error("Test '%s' failed" % (test,))
            return True
    #Remember, False means no errors found
    return False


def main(env=os.environ):
    repo = hgapi.Repo(os.path.abspath(os.curdir))
    node = os.environ['HG_NODE']

    if 'HG_PENDING' in os.environ:
        pending = os.environ['HG_PENDING']
    elif repo.config('bundle','mainreporoot'):
        pending = repo.config('bundle','mainreporoot')
    else:
        pending = os.path.abspath(".")
    return int(hook(repo, node, pending, os.environ))
