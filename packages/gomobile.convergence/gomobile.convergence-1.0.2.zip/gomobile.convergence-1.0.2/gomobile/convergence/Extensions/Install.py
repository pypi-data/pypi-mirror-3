"""


    Old-fashioned uninstall script.
    
"""


from StringIO import StringIO

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.setuphandlers import clean_up_content_annotations

def uninstall(portal, reinstall=False):

    output = StringIO()
    if not reinstall:

        # Clean up generic multichannel per document settings
        try:
            report = clean_up_content_annotations(portal, ["multichannel"])
        except Exception, e:
            print >> str(e), output

        print >> output, report
        #print report        
            
        # Clean up per-document convergence field overrrides
        try:
            report = clean_up_content_annotations(portal, ["mobile_override_values"])
        except Exception, e:
            print >> str(e), output

        #print report
    
        print >> output, report    
        print >> output, "Ran all uninstall steps."
        
        return output.getvalue()
