import auth
from entity import *
from gui import *

### Match categories with API paths
categories = {
    'domains': '/domain',
    'bills'  : '/me/bill',
    'stats'  : '/hosting/web',
    'me'     : '/me'
}
    

class GUI_ovh(GUI):
    def __init__(self, *args, **kwargs):
        GUI.__init__(self, *args, **kwargs)
        
        self.build_menu(categories.keys())
        self.build_content_frames()

        ### Grant access to users' account
        api = auth.get_api(self)
        
        ### Retrieve OVH objects and apply content to application's frames
        for cat, path in categories.items():
            objects = Nodes(api, path)
            setattr(self, cat, objects)
            self.content_frames[cat].add_entries(objects)

        ### Show 'Domains' on top
        self.content_frames['domains'].show()

