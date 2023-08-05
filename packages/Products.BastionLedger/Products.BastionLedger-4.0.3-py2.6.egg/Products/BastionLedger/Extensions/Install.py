#
#    Copyright (C) 2002-2011  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from Products.BastionLedger.config import *

def install(portal):                                       
    out = StringIO()

    setup_tool = getToolByName(portal, 'portal_setup')

    if getFSVersionTuple()[0]>=3:
        setup_tool.runAllImportStepsFromProfile(
                "profile-BastionLedger:default",
                purge_old=False)
    else:
        plone_base_profileid = "profile-CMFPlone:plone"
        setup_tool.setImportContext(plone_base_profileid)
        setup_tool.setImportContext("profile-BastionLedger:default")
        setup_tool.runAllImportSteps(purge_old=False)
        setup_tool.setImportContext(plone_base_profileid)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

def uninstall(portal, reinstall=False):
    out = StringIO()

    if not reinstall:
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile('profile-BastionLedger:default')

    print >> out, "Successfully uninstalled %s." % PROJECTNAME
    return out.getvalue()


#
# it's a pain when this module won't load - this immediately lets us know !!!

# but you might need /usr/lib/zope/lib/python in $PYTHONPATH
#
if __name__ == '__main__':
    print 'brilliant - it compiles ...'
