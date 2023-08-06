from collective.gsa.interfaces import IGSAFeedGenerator

def GSALogout(user, event):
    
    user.REQUEST.RESPONSE.expireCookie('GSACookie')


def GSAIndex(obj, event):
    processor = IGSAFeedGenerator(obj)
    processor.process(action="add")
    
def GSAUnindex(obj, event):
    request = obj.REQUEST
    # if it's delete confirmation check it's been submitted
    if 'delete_confirmation' in request['URL']:
        if not request.get('form.submitted'):
            return
    processor = IGSAFeedGenerator(obj)
    processor.process(action="delete")