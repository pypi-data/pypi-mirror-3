_primitives = [int, float,  str, unicode, bool] 
_helpers = set(['APIClass', 'referenced_obj', 'referenced_objs', 'AddAttrList'])

class referenced_obj(object):
    
    obj_type = str
    obj_id = int
    
    def __init__(self, obj=None):
        if obj==None:
            self.obj_type = None
            self.obj_id = None
        else:
            #self.obj_type = `type(obj)`.split('.')[-1].split("'")[0]
            self.obj_type = obj.__class__.__name__
            self.obj_id = obj.id
    
        
class referenced_objs(object):
    obj_type = str
    obj_ids = str
    
    def __init__(self, objs=[]):
        if objs==None:
            objs=[]
        if len(objs)==0:
            self.obj_type = None
            self.obj_ids = None
        else:
            #self.obj_type = `type(objs[0])`.split('.')[-1].split("'")[0]
            self.obj_type = objs[0].__class__.__name__
            self.obj_ids = ','.join(str(obj.id) for obj in objs)


class AddAttrList(type):
    def __new__(self, cls, cls_parents, cls_dict):
        __exposed_attrs__ = [ attr for attr in cls_dict.keys() if not attr.startswith('_') ]
        cls_dict['__exposed_attrs__'] = __exposed_attrs__
        return type.__new__(self, cls, cls_parents, cls_dict)
        
class APIClass(object):
    __metaclass__ = AddAttrList
    def __init__(self, obj=None, id=None):
        if id:
            self.id = id
            # self.__not_yet_loaded = True
        elif obj:
            for attr in self.__exposed_attrs__:
                #if not attr.startswith('_') and not attr in self.__methods__:
                    
                attr_type = getattr(self, attr)
                
                if attr_type in _primitives:
                    attr_value = getattr(obj, attr)
                    setattr(self, attr, attr_value)
                
                elif attr_type == referenced_obj:
                    if hasattr(obj, attr):
                        obj_to_reference = getattr(obj, attr)
                    else:
                        obj_to_reference = None
                        
                    reference = referenced_obj( obj_to_reference )
                    setattr(self, attr, reference)
                
                elif attr_type == referenced_objs:
                    if hasattr(obj, attr):
                        objs_to_reference = getattr(obj, attr)
                    else:
                        objs_to_reference = []
                        
                    references = referenced_objs( objs_to_reference )
                    setattr(self, attr, references)
    

        