from Products.Five.browser import BrowserView
from zope.interface import implements, alsoProvides, noLongerProvides
from simplelayout.base.config import SLOT_INTERFACES_MAP, \
                                     COLUMN_INTERFACES_MAP

class SaveDragndropOrderView(BrowserView):

    def __call__(self, uids=[],slot='',column='',obj_uid=''):
        uids = uids.split(',')
        for i in range(len(uids)):
            uid = uids[i]
            uid = uid.replace('uid_','')
            obj = self.context.reference_catalog.lookupObject(uid)
            id = obj.id
            self.context.moveObject(id, i)
            obj.reindexObject(idxs=['getObjPositionInParent'])

        #set the new interfaces
        o_uid = obj_uid.replace('uid_','')
        o = self.context.reference_catalog.lookupObject(o_uid)

        iface_to_remove = []
        if SLOT_INTERFACES_MAP.has_key(slot):
            for i in SLOT_INTERFACES_MAP.values():
                if i.providedBy(o):
                    iface_to_remove.append(i) 
                    

            if SLOT_INTERFACES_MAP[slot] not in iface_to_remove:
                for iface in iface_to_remove:
                    noLongerProvides(o,iface)
                alsoProvides(o,SLOT_INTERFACES_MAP[slot])

    
        for col in column.split(' '):
            if col.find('column') != -1:
                new_col = col
        if COLUMN_INTERFACES_MAP.has_key(new_col):
            for i in COLUMN_INTERFACES_MAP.values():
                if i.providedBy(o): noLongerProvides(o,i)
            alsoProvides(o,COLUMN_INTERFACES_MAP[new_col])
        o.reindexObject(idxs=['object_provides'])
        
        return 'ok'
        
