# coding=utf-8

import OvhApi as ovh

### Application's credentials
AK = 'W9MZLywjTDlSno1d'
AS = 'JNCa8QCbPJpQ8XErtGbHj5VaBB06oJ1i'
### User's credentials bind Api object with user's account
CK = ''

def save_CK():
    print 'Saving consumer key %s...' % CK
    if CK is None or not isinstance(CK, basestring) or CK is '':
        raise Exception("Invalid consumer key (CK).")
    with open('ck.key', "w") as f:
        #print '[' + CK + ']'
        f.write(CK)

def load_CK():
    print 'Loading consumer key...'
    try:
        with open('ck.key', "rU") as f:
            global CK
            CK = f.readline().rstrip()
            #print '[' + CK + ']'
    except IOError:
        print 'No user key found. If you are logging for the first time, you must grant access to your OVH account now.' 

def request_CK(api, gui):
    global CK
    response = api.requestCredential([{ 'method': 'GET', 'path': '/*' }])
    CK = response['consumerKey']
    if gui is None:
        print 'Please sign in to OVH. Simply follow the link:'
        print response['validationUrl']
        raw_input("\nLogged in? Ok, press any key to continue...")
    else:
        gui.login.set_login_button(response['validationUrl'])
        gui.login.show()
        gui.wait_for_click()    # User clicks 'Go online'
        if gui.login.step.get() == 'quit':
            quit()
        ### Web browser opens for login. When back to GUI... 
        gui.wait_for_click()    # User clicks 'Continue'
        if gui.login.step.get() == 'quit':
            quit()
    save_CK()
    api = ovh.Api(ovh.OVH_API_EU, AK, AS, CK)
    return api

def access_granted(api):
    ### Check everything's ok
    response = api.get('/me')
    if u'You must login first' in response.values():
        return False
    if 'errorCode' in response.keys():
        print 'Your consumer key (CK) may have expired.'
        return False
    return True

def get_api(gui=None):
    print 'Granting access to OVH...'
    ### Load previous CK or request for one if any 
    load_CK()
    api = ovh.Api(ovh.OVH_API_EU, AK, AS, CK)
    while not access_granted(api):
        api = request_CK(api, gui)
    print 'Access ready.'
    return api

