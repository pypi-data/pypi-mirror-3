import functools
import inspect
from time import sleep

try:
    import transaction
    from tg.decorators import Decoration
    from tg import config, expose
    import sqlalchemy
except ImportError:
    raise Exception("Can't import standard TurboGears libraries.  Are you sure you're in the virtualenv?")

try:
    from tgext.ws import WebServicesRoot, WebServicesController, wsvalidate, wsexpose
    from tgext.ws.runtime import FunctionInfo
except ImportError:
    raise Exception("Can't import TGWebServices.  Install latest version from 'http://code.google.com/p/tgws/'")


#from . import helper
import helper

TableType = sqlalchemy.ext.declarative.DeclarativeMeta
ColumnType = sqlalchemy.orm.attributes.InstrumentedAttribute
RelationType = sqlalchemy.orm.properties.RelationshipProperty
PrimitiveType = sqlalchemy.orm.properties.ColumnProperty

mimetype_lookup = config.get('mimetype_lookup')
if mimetype_lookup == None:
    mimetype_lookup = {}
    
mimetype_lookup['.py'] = 'text/py'

config.mimetype_lookup = mimetype_lookup


                
class AutoAPIError(Exception):
    pass

class AutoAPI(object):
    """
    This class is used to decorate controller classes for those objects
    defined in the API.  It offers the client the ability to create and
    delete objects, as well as pull and post (ie. get and set) their 
    attributes.
    
    Usage::
    
    @
    
    """
    classes = {}
    exposed_tables = set()
    
    def __init__(decorator_obj, table):
        decorator_obj.table = table
        
        if not table in ExposeTable.classes.values():
            raise AutoAPIError("""You must decorate a table with ExposeTable before
                                applying AutoAPI(table) to a controller.""")
                                
        AutoAPI.exposed_tables.add(table)
        
        # Autogenerate API class for table
        
        class APITemplate(helper.APIClass):
            pass
        APITemplate.__name__ = table.__name__
            
        for name in dir(table):
            attr = getattr(table, name)
            if isinstance(attr, ColumnType):
                if isinstance(attr.property, RelationType):
                    if attr.property.target.name in ExposeTable.classes.keys():
                        APITemplate.__exposed_attrs__.append(name)
                        if attr.property.uselist:
                            setattr(APITemplate, name, ['%s' % attr.property.target.name])
                        else:
                            setattr(APITemplate, name, '%s' % attr.property.target.name)
                elif isinstance(attr.property, PrimitiveType):
                    columninfo = list(attr.property.columns)[0]
                    if len(columninfo.foreign_keys) == 0 and not columninfo.primary_key:
                        # Don't expose foreign keys or primary key.
                        APITemplate.__exposed_attrs__.append(name)
                        setattr(APITemplate, name, columninfo.type.python_type)
        
        decorator_obj.api_class = APITemplate
        
    
    def __call__(decorator_obj, cls):
        # Create API class
        table = decorator_obj.table
        cls.__exposed_table__ = table
        cls.api_class = decorator_obj.api_class
        
        if hasattr(cls, '__exposed_methods__'):
            exposed_methods = cls.__exposed_methods__
        else:
            exposed_methods = []
            
        cls.api_class.__exposed_methods__ = exposed_methods
        
        
        @Return(int)
        def create(self):
            new_obj = decorator_obj.table()
            DBSession = config.get('DBSession')
            DBSession.add(new_obj)
            transaction.commit()
            sleep(2)
            return new_obj.id
        cls.create = create
        
        @Params(int)
        @Return()
        @self_as_model(decorator_obj.table)
        def delete(self, id):
            obj = DBSession.query(decorator_obj.table).get(id)
            DBSession = config.get('DBSession')
            DBSession.delete(obj)
        cls.delete = delete
        
        
        for exposed_attr in decorator_obj.api_class.__exposed_attrs__:
            exposed_attr_type = getattr(decorator_obj.api_class, exposed_attr)
            if type(exposed_attr_type) == str:
                exposed_attr_type = ExposeTable.classes[exposed_attr_type]
            elif type(exposed_attr_type) == list:
                exposed_attr_type = [ ExposeTable.classes[exposed_attr_type[0]] ]
                
            class ExposedAttr(SubController):
                
                def __init__(self, exposed_attr):
                    SubController.__init__(self)
                    self.exposed_attr = exposed_attr
                    self.table = decorator_obj.table
                    self.__name__ = exposed_attr
                
                @Params(int, exposed_attr_type)
                def post(self, id, value):
                    DBSession = config.get('DBSession')
                    record = DBSession.query(self.table).get(id)
                    setattr(record, self.exposed_attr, value)
                
                @Params(int)
                @Return(exposed_attr_type)
                def pull(self, id):
                    DBSession = config.get('DBSession')
                    record = DBSession.query(self.table).get(id)
                    value = getattr(record, self.exposed_attr)
                    return value
                
            setattr(cls, exposed_attr, ExposedAttr(exposed_attr))
        
        AutoAPI.classes[table.__name__] = cls
        setattr(AutoAPI, table.__name__, cls)
        return cls

        
def FinaliseAPI(RootController):
    already_controlled_tables = AutoAPI.exposed_tables
    all_exposed_table = set(ExposeTable.classes.values())
    tables_needing_controllers = all_exposed_table.difference(already_controlled_tables)

    for table in tables_needing_controllers:
        @AutoAPI(table)
        class ControllerClassTemplate(Controller):
            pass
        ControllerClassTemplate.__name__ = table.__name__
        setattr(RootController, table.__name__, ControllerClassTemplate)
    api_file = '# Automatically generated TGInterface API file \n'
    api_file += 'import datetime'
    for controller in AutoAPI.classes.values():
        api_class = controller.api_class
        api_file += '\n\nclass %s:\n' % api_class.__name__
        api_file += '    __exposed_methods__ = %s\n' % `api_class.__exposed_methods__`
        api_file += '    __exposed_attrs__ = %s\n' % `api_class.__exposed_attrs__`
        for attr in api_class.__exposed_attrs__:
            value = getattr(api_class, attr)
            if value in helper._primitives:
                value = `value`.split("'")[1]
            elif type(value) == str:
                value = "'%s'" % value
            api_file += '    %s = %s\n' % (attr, value)
    
    AutoAPI.api_file = api_file
        
    @expose(content_type = 'text/py')
    def api(self):
        return AutoAPI.api_file
        
    RootController.api = api
        
        

LIST_OF_OBJECTS_FROM_MODEL = 0
OBJECT_FROM_MODEL = 1
PRIMITIVE = 2
NONE = 3

def discriminate(typ):
    """
    Determines to which group of types the given type belongs.
    """
    if typ in helper._primitives:
        # If it's a primitive type, just pass it along.
        return PRIMITIVE
    elif typ == None:
        return NONE
    elif type(typ) == list and typ[0] in ExposeTable.classes.values():
        # If it's a list of objects defined in model
        return LIST_OF_OBJECTS_FROM_MODEL
    elif typ in ExposeTable.classes.values():
        # If it's a single object defined in model
        return OBJECT_FROM_MODEL
        
    else:
        raise AutoAPIError('Type passed to decorator is not valid')

        
class InterfaceInfo:
    def __init__(self):
        self.self_as_model_obj = False
        self.self_table = None
        self.applied_decs = []
        
        
def get_interface_info(func):
    deco = Decoration.get_decoration(func)
    if not hasattr(deco, "_interface_info"):
        deco._interface_info = InterfaceInfo()
    return deco._interface_info
    
    
def get_func_info(func):
    deco = Decoration.get_decoration(func)
    if not hasattr(deco, "_ws_func_info"):
        params = inspect.getargspec(func).args
        param_defaults = inspect.getargspec(func).defaults
        deco._ws_func_info = FunctionInfo(params, param_defaults)
    return deco._ws_func_info

    
def transfer_info_from_to(frm, to):
    to_deco = Decoration.get_decoration(to)
    to_deco._ws_func_info = get_func_info(frm)
    to_deco._interface_info = get_interface_info(frm)
    
    
class self_as_model:
    def __init__(self, self_table = None):
        self.self_table = self_table
        
    def __call__(self, func):
        interface_info = get_interface_info(func)
        interface_info.self_as_model_obj = True
        interface_info.self_table = self.self_table
        interface_info.applied_decs.append('self_as_model')
        
        return func
           
           
class Params:
    def __init__(self, *param_types):
        self.param_types = [int] + list(param_types)
    
    def __call__(self, func):
        
        
        raw_param_types = []
        
        for param_type in self.param_types:
            type_description = discriminate(param_type)
            
            if type_description == LIST_OF_OBJECTS_FROM_MODEL:
                raw_param_types.append(helper.referenced_objs)
            
            elif type_description == OBJECT_FROM_MODEL:
                raw_param_types.append(helper.referenced_obj)
            
            elif type_description == PRIMITIVE:
                raw_param_types.append(param_type)
        
        
        func_info = get_func_info(func)
        func_info.params.insert(0, 'self_id')
        func_info.optional.insert(0, 'self_id')
        
        params_validator = wsvalidate(*raw_param_types)
        
    
        @functools.wraps(func)
        def wrappedFunc(*param_vals, **param_dict):
            DBSession = config.get('DBSession')
            
            interface_info = get_interface_info(func)
            
            param_vals = list(param_vals)
            # We'll put all the imported params into this dict
            imported_param_dict = {}
            imported_param_dict['self'] = param_vals.pop(0)
            
            # Put all param_vals into param_dict.
            param_dict.update( dict(zip(func_info.params, param_vals)) )
            
            """
            func_info.params = [a, b, c]
            self.param_types = [a_type, b_type, c_type]
            kw = b , I want b_type, so use param_types_dict['b']
            """
            param_types_dict = dict(zip(func_info.params, self.param_types))
            
            
            for param, param_val in param_dict.iteritems():
                param_type = param_types_dict[param]
                type_description = discriminate(param_type)
                
                if type_description == LIST_OF_OBJECTS_FROM_MODEL:
                    if param_val.obj_type == param_type[0].__name__:
                        imported_param_dict[param] = dereference_objs(param_val)
                    elif param_val.obj_type == None:
                        imported_param_dict[param] = []
                    else:
                        raise AutoAPIError('Object does not match type declared for this function')
                    
                elif type_description == OBJECT_FROM_MODEL:
                    if param_val.obj_type == param_type.__name__:
                        imported_param_dict[param] = dereference_objs(param_val)
                    elif param_val.obj_type == None:
                        imported_param_dict[param] = None
                    else:
                        raise AutoAPIError("'%s' object does not match '%s' type declared for this function"% (param_val.obj_type,param_type))
                    
                elif type_description == PRIMITIVE:
                    imported_param_dict[param] = param_val
                    
                
            
            if interface_info.self_as_model_obj:
                self_id = imported_param_dict['self_id']
                del imported_param_dict['self_id']
                
                if interface_info.self_table != None:
                    table = interface_info.self_table
                else:
                    table = imported_param_dict['self'].__class__.__exposed_table__
                    
                imported_param_dict['self'] = DBSession.query(table).get(self_id)
            elif 'self_id' in imported_param_dict:
                del imported_param_dict['self_id']
                
            
            return func(**imported_param_dict)
        
        transfer_info_from_to(func, wrappedFunc)
        
        validated_func = params_validator(wrappedFunc)
        interface_info = get_interface_info(func)
        interface_info.applied_decs.append('Params')
        
        return validated_func
        
        
class Return:
    def __init__(self, ret_type = None):
        self.ret_type = ret_type
        
    def __call__(self, func):
        
        type_description = discriminate(self.ret_type)
        
        if type_description == LIST_OF_OBJECTS_FROM_MODEL:
            ret_validator = wsexpose(helper.referenced_objs)
        
        elif type_description == OBJECT_FROM_MODEL:
            ret_validator = wsexpose(helper.referenced_obj)
        
        elif type_description == PRIMITIVE:
            ret_validator = wsexpose(self.ret_type)
            
        elif type_description == NONE:
            ret_validator = wsexpose()
            
        @functools.wraps(func)
        def wrappedFunc(*args, **kwargs):
            retval_type = discriminate(self.ret_type)
            
            retval = func(*args, **kwargs)
            
            if retval_type == LIST_OF_OBJECTS_FROM_MODEL:
                retval = helper.referenced_objs(retval)
                if retval.obj_type != self.ret_type[0].__name__ and retval.obj_type!=None:
                    raise AutoAPIError('Tried to return list of objects of wrong type')
            elif retval_type == OBJECT_FROM_MODEL:
                
                retval = helper.referenced_obj(retval)
                if retval.obj_type != self.ret_type.__name__ and retval.obj_type!=None:
                    raise AutoAPIError('Tried to return %s instead of %s' %(retval.obj_type, self.ret_type.__name__))
                
            return retval
        
        transfer_info_from_to(func, wrappedFunc)
        
        validated_func = ret_validator(wrappedFunc)
        interface_info = get_interface_info(func)
        interface_info.applied_decs.append('Return')
        
        return validated_func

        
class FixDecorators_metaclass(type):
    def __new__(self, cls, cls_parents, cls_dict):
        
        parent_methods = []
        for cls_parent in cls_parents:
            parent_methods.extend(dir(cls_parent))
        list_of_method_names = [ 
                            attr for attr in cls_dict.keys() 
                            if inspect.isfunction(cls_dict[attr]) 
                                and attr not in parent_methods
                            ]
        
        cls_dict['__exposed_methods__'] = []
        
        for method_name in list_of_method_names:
            method = cls_dict[method_name]
            applied_decs = get_interface_info(method).applied_decs
            
            if 'Params' not in applied_decs:
                cls_dict[method_name] = Params()(method)
            if 'Return' not in applied_decs and len(applied_decs)>0:
                cls_dict[method_name] = Return()(method)
                
            if len(applied_decs) > 0:
                cls_dict['__exposed_methods__'].append(method_name)
        
        return type.__new__(self, cls, cls_parents, cls_dict)
        
        
class Controller(WebServicesRoot):
    __metaclass__ = FixDecorators_metaclass
    
    
class SubController(WebServicesController):
    __metaclass__ = FixDecorators_metaclass

    
def dereference_objs(obj_refs):
    obj_type = obj_refs.obj_type
    if hasattr(obj_refs, 'obj_ids'):
        objs = []
        for obj_id in obj_refs.obj_ids.split(','):
            objs.append( dereference_obj(obj_type, int(obj_id)) )
        return objs
    elif hasattr(obj_refs, 'obj_id'):
        obj = dereference_obj(obj_type, obj_refs.obj_id)
        return obj

        
def dereference_obj(obj_type, obj_id):
    table = ExposeTable.classes[obj_type]
    DBSession = config.get('DBSession')
    return DBSession.query(table).get(obj_id)
    
    

class ExposeTable(object):
    classes = {}
    
    def __init__(self, read=None, write=None):
        # use TG user access decorators
        pass
    
    def __call__(self, cls):
        ExposeTable.classes[cls.__name__] = cls
        return cls



