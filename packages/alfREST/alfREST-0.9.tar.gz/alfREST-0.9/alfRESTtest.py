#!/usr/bin/python

# test Alfresco

import sys
from alfREST import RESTHelper, ROLES

if len(sys.argv) != 6:
    print "Usage:\n"
    print "test.py username password host port path\n"
    print "es.\n"
    print "test.py admin alfresco 127.0.0.1 8080 /Sites/mysite/documentLibrary/test\n"
    exit(1)
    
_, login, password, host, port, path = sys.argv

# login
rh = RESTHelper()
rh.login(login, password, host, port)

# list of root groups
groups = rh.listAllRootGroups()
assert groups is not None

# add root group
rh.addRootGroup(u"GROUP_TEST")

# set ACL
acl = {}
acl[u'GROUP_TEST'] = [([u"{http://www.alfresco.org/model/content/1.0}cmobject.Consumer",], True),]
rh.applyACL(path, acl)

# add person
rh.addPerson("supermario", "mario", "super", "supermario@nintendo.com", "imsuper")

# add user to group
rh.addGroupOrUserToGroup(u"supermario", u"GROUP_TEST")

# list users in group
users = rh.listChildAuthorities(u"GROUP_TEST")
assert len(users) == 1
assert users[0]['fullName'] == "supermario"

# remove user from group
rh.removeAuthorityFromGroup(u"supermario", u"GROUP_TEST")

# list users in group
users = rh.listChildAuthorities(u"GROUP_TEST")
assert len(users) == 0

# delete person
rh.deletePerson("supermario")

# remove ACL
acl = {}
rh.applyACL(path, acl)

# delete root group
rh.deleteRootGroup(u"GROUP_TEST")

# logout
rh.logout()
