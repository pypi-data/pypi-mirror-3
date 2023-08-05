from Acquisition import aq_parent
from Products.Archetypes.Field import FileField, TextField
from operator import eq
from prdg.plone.util.structure import objs_to_paths
from prdg.plone.util.users import get_password
from prdg.plone.util.utils import get_workflow_state, ofs_file_equal

def fail_unless_dict_and_obj_matches(self, d, obj):
    """
    Check if dict matches object.
    
    More specifically: iterate through all items in d and check if they 
    matches with attributes of obj. Special keys like _path, owner_userid,
    etc are tested too.
    """
    def fail_unless_equal(obj_value, eq_func=eq):
        self.failUnless(
            eq_func(value, obj_value),
            'field: %s. d = %s, obj = %s' % (name, value, obj_value)
        )
    
    d = dict(d) # Dont't modify the dict.        
    container = aq_parent(obj)
    
    # Required keys.
    (name, value) = ('container id', container.getId())
    fail_unless_equal(obj.getPhysicalPath()[-2])
    
    (name, value) = ('portal_type', d.pop('portal_type'))
    fail_unless_equal(obj.portal_type)
    
    (name, value) = ('id', d.pop('id'))
    fail_unless_equal(obj.getId())
        
    for (name, value) in d.iteritems():
        field = obj.getField(name)
        
        if name.startswith('ref:'):
            name = name.split(':')[1]
            value = set(value)
            field = obj.getField(name)
            
            referenced_objs = field.get(obj, aslist=True)
            referenced_paths = set(objs_to_paths(referenced_objs))
            fail_unless_equal(referenced_paths)                
        
        elif name == '_path':
            fail_unless_equal(obj.getPhysicalPath()[2:])
        
        elif name == 'owner_userid':
            fail_unless_equal(self.putils.getOwnerName(obj))
            
        elif name == 'workflow_dest_state':
            fail_unless_equal(get_workflow_state(obj))
        
        elif name == 'local_roles':
            obj_local_roles = getattr(obj, '__ac_local_roles__', {})
            local_roles = value            
            for (user_id, roles) in local_roles.iteritems():
                value = (user_id, roles)
                fail_unless_equal((user_id, obj_local_roles.get(user_id)))
                    
        elif isinstance(field, FileField) and (not isinstance(field, TextField)):
            fail_unless_equal(field.get(obj), ofs_file_equal)                
        
        else:
            fail_unless_equal(field.get(obj))

ROLES_TO_REMOVE = set(['Authenticated'])

def fail_unless_dict_and_member_matches(self, d, member):
    d = dict(d)    
    member_id = member.getId()
    
    self.failUnlessEqual(d.pop('id'), member_id)
    
    password = d.pop('password', None)
    real_password = get_password(self.portal, member_id)  
    self.failUnless(
        (real_password is None) or (password == real_password)         
    )
    
    roles = set(d.pop('roles')) - ROLES_TO_REMOVE
    real_roles = set(member.getRoles()) - ROLES_TO_REMOVE
    self.failUnlessEqual(roles, real_roles)
    
    for (k, v) in d.iteritems():
        self.failUnlessEqual(v, member.getProperty(k))
    
    
    