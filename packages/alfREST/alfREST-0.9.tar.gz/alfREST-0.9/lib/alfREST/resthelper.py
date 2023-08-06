# encoding: utf-8
# Copyright (c) 2011 AXIA Studio <info@axiastudio.it>
#
# This file may be used under the terms of the GNU General Public
# License versions 3.0 or later as published by the Free Software
# Foundation and appearing in the file LICENSE.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#

import httplib, urllib
import socket
from xml.dom.minidom import parseString, getDOMImplementation
import logging
from webscripts import *


ROLES = dict(
CONSUMER = "{http://www.alfresco.org/model/content/1.0}cmobject.Consumer",
EDITOR = "{http://www.alfresco.org/model/content/1.0}cmobject.Editor",
CONTRIBUTOR = "{http://www.alfresco.org/model/content/1.0}cmobject.Contributor",
COLLABORATOR = "{http://www.alfresco.org/model/content/1.0}cmobject.Collaborator",
COORDINATOR = "{http://www.alfresco.org/model/content/1.0}cmobject.Coordinator",
)


logger = logging.getLogger("alfrescohelper")
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(sh)


def parseComm(s):
    method, comm = s.split(" ")
    comm = comm.replace("{", "%(")
    comm = comm.replace("?}", ")s")
    comm = comm.replace("}", ")s")
    return method, comm


def formatComm(comm, pars):
    try:
        comm.index("?")
    except ValueError:
        return comm % pars
    noneKeys = [k for k in pars.keys() if pars[k] is None]
    for k in noneKeys:
        del pars[k]
    if len(pars)==0:
        return comm
    url, urlPars = comm.split("?")
    tkns = urlPars.split("&")
    outTkns = []
    for tkn in tkns:
        try:
            outTkns.append(tkn % pars)
        except KeyError:
            pass
    newComm = url + "?" + "&".join(outTkns)
    return newComm % pars


def pythonizeJson(json):
    json = json.replace("\r", "")
    json = json.replace("true", "True")
    json = json.replace("false", "False")
    json = json.replace("null", "None")
    return eval(json)


def restfuldoc(method):
    """
    Decore method's docstring with RESTful help
    """
    method.__doc__ = "\n"+globals()[method.__name__.upper()][0]
    return method


class RESTHelper(object):

    def __init__(self):
        self.ticket = None
        self.host = "127.0.0.1"
        self.port = "8080"
        #self.listAllRootGroups.__func__.__doc__ = 'ciao'

    @restfuldoc
    def login(self, username, password, host="127.0.0.1", port="8080"):

        self.host = host
        self.port = port
        getPars = {}
        postPars = dict(username=username, password=password)
        method, comm = parseComm(LOGIN[1])
        res = self.execute(method, comm, getPars, postPars, json=True)
        if res is not None:
            data = res.read()
            json = pythonizeJson(data)
            self.ticket = json["data"]["ticket"]
            logger.info("Alfresco login.")
            return True
        return False

    @restfuldoc
    def logout(self):

        getPars = dict(ticket=self.ticket)
        method, comm = parseComm(LOGOUT[1])
        res = self.execute(method, comm, getPars)
        if res is not None:
            logger.info("Alfresco logout.")
            return True
        return False

    @restfuldoc
    def listAllRootGroups(self, shortNameFilter=None, zone=None, maxItems=None, skipCount=None,
                                sortBy=None):

        method, comm = parseComm(LISTALLROOTGROUPS[1])
        getPars = dict(shortNameFilter = shortNameFilter,
                       zone = zone,
                       maxItems = maxItems,
                       skipCount = skipCount,
                       sortBy = sortBy)
        res = self.execute(method, comm, getPars)
        if res is not None:
            logger.info("List all root groups.")
            groups = pythonizeJson(res.read())["data"]
            return groups
        return False


    @restfuldoc
    def getACL(self, path):

        getPars = dict(path=path)
        method, comm = parseComm(GETACL[1])
        res = self.execute(method, comm, getPars)
        acl = {}
        if res is not None:
            logger.info("Get ACL for the path %s." % path)
            doc = parseString(res.read())
            #print doc.toxml()
            for child in doc.documentElement.childNodes:
                if child.nodeName == "cmis:permission":
                    principal = child.getElementsByTagName("cmis:principal")[0]
                    principiaId = principal.getElementsByTagName("cmis:principalId")[0].childNodes[0].wholeText
                    permissionNodes = child.getElementsByTagName("cmis:permission")
                    permissions = []
                    for permissionNode in permissionNodes:
                        permissions.append(permissionNode.childNodes[0].wholeText)
                    direct = child.getElementsByTagName("cmis:direct")[0].childNodes[0].wholeText
                    if principiaId not in acl.keys():
                        acl[principiaId] = []
                    acl[principiaId].append((permissions, direct=="true"))
        return acl


    @restfuldoc
    def applyACL(self, path, acl):

        impl = getDOMImplementation()
        namespace = "http://docs.oasis-open.org/ns/cmis/core/200908/"
        doc = impl.createDocument(namespace, "cmis:acl", None)
        doc.documentElement.setAttribute("xmlns:cmis", "http://docs.oasis-open.org/ns/cmis/core/200908/")
        for principiaIdText in acl.keys():
            for permissions, direct in acl[principiaIdText]:
                permissionElement = doc.createElement("cmis:permission")
                doc.documentElement.appendChild(permissionElement)
                principalElement = doc.createElement("cmis:principal")
                permissionElement.appendChild(principalElement)
                principalIdElement = doc.createElement("cmis:principalId")
                principalElement.appendChild(principalIdElement)
                principalIdElement.appendChild(doc.createTextNode(principiaIdText))
                for permission in permissions:
                    permissionSubElement = doc.createElement("cmis:permission")
                    permissionSubElement.appendChild(doc.createTextNode(permission))
                    permissionElement.appendChild(permissionSubElement)
                    directElement = doc.createElement("cmis:direct")
                    permissionElement.appendChild(directElement)
                    directElement.appendChild(doc.createTextNode(direct is True and 'true' or 'false'))

        getPars = dict(path=path)
        method, comm = parseComm(APPLYACL[1])

        res = self.execute(method, comm, getPars=getPars, postPars=doc.toxml(), cmisxml=True)
        if res is not None:
            logger.info("ACL applied to %s." % path)


    @restfuldoc
    def listChildAuthorities(self, shortName, authorityType='USER'):

        get_pars = dict(shortName=shortName, authorityType=authorityType)
        method, comm = parseComm(LISTCHILDAUTHORITIES[1])
        res = self.execute(method, comm, get_pars)
        if res is not None:
            logger.info('List child authorities (%s) for the group %s.' % (authorityType, shortName))
            users = pythonizeJson(res.read())['data']
            return users
        return False


    @restfuldoc
    def addPerson(self, userName, firstName, lastName, email, password=None):

        pars = dict(userName=userName, firstName=firstName, lastName=lastName, email=email)
        if password is not None:
            pars['password'] = password
        method, comm = parseComm(ADDPERSON[1])
        res = self.execute(method, comm, postPars=pars, json=True)
        if res is not None:
            logger.info('Person %s (%s %s) added.' % (userName, firstName, lastName))
            return True
        return False

    @restfuldoc
    def deletePerson(self, userName):

        getPars = dict(userName=userName)
        method, comm = parseComm(DELETEPERSON[1])
        res = self.execute(method, comm, getPars)
        if res is not None:
            logger.info('Person %s deleted.' % userName)
            return True
        return False


    @restfuldoc
    def addRootGroup(self, shortName, displayName=None):
        getPars = dict(shortName=shortName,)
        if displayName is not None:
            postPars = dict(displayName=displayName)
        else:
            postPars = {}
        method, comm = parseComm(ADDROOTGROUP[1])
        res = self.execute(method, comm, getPars, postPars, json=True)
        if res is not None:
            logger.info('Root group %s (%s) added' % (shortName, displayName))
            return True
        return False


    @restfuldoc
    def deleteRootGroup(self, shortName):

        get_pars = dict(shortName=shortName,)
        method, comm = parseComm(DELETEROOTGROUP[1])
        res = self.execute(method, comm, get_pars)
        if res is not None:
            logger.info('Root group %s deleted.' % shortName)
            return True
        return False


    @restfuldoc
    def addGroupOrUserToGroup(self, fullAuthorityName, shortName):

        getPars = dict(fullAuthorityName=fullAuthorityName, shortName=shortName)
        method, comm = parseComm(ADDGROUPORUSERTOGROUP[1])
        res = self.execute(method, comm, getPars)
        if res is not None:
            logger.info('Group or user %s inserted in group %s.' % (fullAuthorityName, shortName))
            return True
        return False


    @restfuldoc
    def removeAuthorityFromGroup(self, fullAuthorityName, shortGroupName):

        get_pars = dict(fullAuthorityName=fullAuthorityName, shortGroupName=shortGroupName)
        method, comm = parseComm(REMOVEAUTHORITYFROMGROUP[1])
        res = self.execute(method, comm, get_pars)
        if res is not None:
            logger.info('Authority %s removed from group %s.' % (fullAuthorityName, shortGroupName))
            return True
        return False


    def execute(self, method, comm, getPars={}, postPars={}, json=False, cmisxml=False):

        if "login" not in comm:
            logger.debug("%s %s" % (method, formatComm(comm, getPars)))
        http_conn = httplib.HTTPConnection(self.host, self.port, timeout=60)

        # if logged, append alf_ticket parameter
        if self.ticket is not None:
            try:
                comm.index("?")
                c = "&"
            except ValueError:
                c = "?"
            comm += "%salf_ticket=%s" % (c, self.ticket)

        if method in ("GET", "DELETE"):
            http_conn.request(method, formatComm(comm, getPars))

        elif method in ("POST", "PUT"):
            if json is True:
                headers = {"Content-type":"application/json", "Accept":"text/plain"}
                json = repr(postPars)
                http_conn.request(method, formatComm(comm, getPars), json, headers)
            elif cmisxml is True:
                headers = {"Content-type":"application/cmisacl+xml", "Accept":"text/plain"}
                cmisxml = postPars
                http_conn.request(method, formatComm(comm, getPars), cmisxml, headers)
            else:
                postPars = urllib.urlencode(postPars)
                http_conn.request(method, formatComm(comm, getPars), postPars)

        try:
            res = http_conn.getresponse()
        except socket.timeout:
            logger.error("Server timeout")
            return None
        if res.status/100 in (4, 5):
            logger.error(res.reason)
            msg = eval(res.read())["message"]
            logger.error(msg)
            return None
        return res

