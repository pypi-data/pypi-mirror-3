"""Authentication"""

def authenticate(user, secret):
    pass
    
def authorize(token, request):
    """Return true"""
    """token,user,date_created, date_start, date_end"""    
    
    pass
    
    
def disatch(request):
    token = request["token"]
    auth.authorize(request, token)


