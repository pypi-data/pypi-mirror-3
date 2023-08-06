from collective.gsa.interfaces import IGSAFeedGenerator
from collective.gsa.utils import gsa_installed

def GSALogout(user, event):
    
    user.REQUEST.RESPONSE.expireCookie('GSACookie')


def GSAIndex(obj, event):
    if not gsa_installed():
        return
    processor = IGSAFeedGenerator(obj)
    processor.process(action="add")
    
def GSAUnindex(obj, event):
    if not gsa_installed():
        return
    request = obj.REQUEST
    # if it's delete confirmation check it's been submitted
    if 'delete_confirmation' in request['URL']:
        if not request.get('form.submitted'):
            return
    processor = IGSAFeedGenerator(obj)
    processor.process(action="delete")
