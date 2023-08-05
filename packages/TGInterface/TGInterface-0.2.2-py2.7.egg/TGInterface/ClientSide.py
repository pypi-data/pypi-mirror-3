import urllib2
from json import dumps, loads
import threading
from copy import copy
import time

#from . import helper
import helper

HEADERS = {
            'Content-type':"application/json", 
            'Accept':"application/json", 
            }
DB={}

MULTITHREADED = True


BASE_URL = None
API = None

def loadAPI(api, url):
    global API
    API = api
    global BASE_URL
    BASE_URL = url
    CompleteTheModel()

class WebServiceError(Exception):
    pass

    
class AutoAPIError(Exception):
    pass

    
class WebRequestInfo(object):
    """
    This stores information on the request.  It's used in 
    NewClass.__onRemoteResponse__ to work out what the request was for (eg. 
    for getting the value of an attribute, or for running a server-side 
    function, etc.).  The instantiation of NewClass to invoke is
    ``handler``
    
    @param handler Instantiation of NewClass to call on completion
    @param attr Either the variable or the function to be called server-side
    @param operation If ``attr`` is a variable, this is either 'post' or 'pull'
    """
    def __init__(self, attr, operation):
        self.attr = attr
        self.operation = operation
        

class WebServiceProxy(object):
    """
    This does the actual sending of data along the inter-tubes.
    Instantiating gives an object that is ready to access the specified
    server-side function.  It can then be called as a function, and 
    arguments passed to it are passed to the server-side function.
    
    Usage
    
    ::
    
	web_function = WebServiceProxy(
					'Object',
					'Attribute', 
					'pull',
					handler
					)
	web_function(data_to_send)
    
    """
    def __init__(self, obj_name, attr, operation=None, handler=None):
        self.url = '/'.join(bit for bit in [BASE_URL, obj_name, attr, operation] if bit!=None)
        self.request_info = WebRequestInfo(attr, operation)
        self.handler = handler
        
    def __call__(self, *params, **kwargs):
        """
        Calls the server-side function, passing it ``params`` and ``kwargs``.
        """
        # Briefly check that ``params`` and ``kwargs`` are sane
        if isinstance(params, tuple):
            params = list(params)
        if kwargs:
            if params:
                if not isinstance(params, dict):
                    raise WebServiceError("Cannot mix positional and keyword arguments")
                params.update(kwargs)
            else:
                params = kwargs
        
        # Encode the data in JSON
        params_data = dumps(params)
        
        self.timestamp = time.time()
        
        if MULTITHREADED:
            t = threading.Thread(target=self.send, args=[params_data])
            t.start()
        else:
            self.send(params_data)
        
    def send(self, params_data):
        timestamp = self.timestamp
        
        # Create request
        request_obj = urllib2.Request(self.url, params_data, HEADERS)
        response_obj = urllib2.urlopen(request_obj)
        
        # Perform request
        response_data = loads(response_obj.read())
        
        # Close request
        response_obj.close()
        
        """
        If ``self()`` was called after this thread started, it will have 
        changed ``self.timestamp``.  In this case, I should ignore my response
        and let the newer thread carry on and use its response.
        """
        if self.timestamp != timestamp:
            print '%f : I took too long and will die quietly' %timestamp
            return
        
        # Process response
        if 'result' in response_data and self.handler != None:
            self.handler.__onRemoteResponse__(
                                    self.request_info, 
                                    response_data['result'] 
                                    )
        else:
            error = dict(
                code=response_data['faultcode'],
                message=response_data['faultstring'],
                )
            raise WebServiceError(
                            "Server returned an error, but no handler was set. %s"
                            % `response_data`
                            )
            if self.handler != None:
                self.handler.__onRemoteError__(self.request_info, error)
            else:
                raise WebServiceError(
                            "Server returned an error, but no handler was set."
                            % response_data
                            )
            
        

# Not that either works in Pyjamas, but I think I prefer class decorators to metaclasses:
"""
eg. for attr == Name:
    Attr setter is ``self.__set_Name``, which:
        1. Saves the old value (in ``self.__old_Name``) in case of post-error,
        2. Saves the new value (in ``self.__Name``)
        3. Posts the new value (by calling ``self.__post_Name``)
        NB. self.__old_Name and self.__Name are either primitive types or referenced_obj(s) dicts
            (ie. these hidden values are the types defined in the ``api``)
        TODO?: after setting value, check through DB for any objects where self is an attribute,
            then run ``obj.onSelfChange`` if it exists.
    Attr getter is ``self.__get_Name``:
        ``referenced_obj(s)`` are translated into local types (and are instantiated if not in DB),
        Then all primitive types are ``magicked`` to have a Name.update() method.
    
    ``self.oldName`` is a read-only property who's getter is ``self.__get_old_Name``:
        It reads ``self.__old_Name``, and if it's a referenced_obj(s) then it's dereferenced.
        
    On receiving an error, we call ``self.__post_NameError`` which rolls back the change.
    Pulling data from server is handled by ``self.update('Name')``, 
        which calls self.__pull_Name.
    
    When the data arrives, if it's different to the self.__Name then call self.onNameChange
"""



class AutoAPI(object):
    """
    This class is used to decorate the client-side classes to give it the 
    attributes and methods defined in the API, and allows a similar level of 
    access as if you were coding on the server.  The main difference to 
    consider is that it takes time for packets to reach the server, so 
    instead the ClientClass should be written in an asynchronous manner. Eg
    
    ::
    
	@AutoAPI(api.Cheese)
	class Cheese(GUI):
		def _onAvailabilityChange_(self):
		if self.Availability == False:
			self.setlabel('Fresh out of %s, squire.' %self.Name)
	
	@AutoAPI(api.Shop)
	class Shop(GUI):
		def _onCheesesChange_(self):
		old_cheeses = set(self.__old__['Cheese'])
		current_cheeses = set(self.Cheeses)
		new_cheeses = old_cheeses.difference(new_cheeses)
		
		for each cheese in new_cheeses:
			cheese.Availability = False
	
	camembert = Cheese(Name=camembert)
	cheddar = Cheese(Name=cheddar)
	my_shop = Shop(Cheeses=[cheddar])
	camembert.Shop = my_shop
	
    At this point, ``my_shop.Cheeses`` is just ``[cheddar]``
    Once camembert posts its ``Shop`` and receives confirmation that the
    server successfully updated the DB, ``my_shop`` will automatically update 
    its ``Cheeses`` attribute to ``[cheddar, camembert]``.
    As such, it is pointless to do anything to ``my_shop.Cheeses`` here.  
    Anything you want to do with it should be put in
    ``my_shop._onCheesesChange_``.
    
    Current attribute values (for objects, their references)
    are stored in ``self.__hidden__``.  The old value is
    stored in ``self.__old__``.
    
    When a new class is decorated, the NewClass is stored in the 
    ``AutoAPI.classes`` dict, and can also be found (for exaple, if 
    decorating ``Obj``) at AutoAPI.Obj
    """
    
    classes = {}
    
    def __init__(self, api_class, autoload=False):
        """
        @param api_class This is the relevant class in the api.
        @param autoload This defines whether an object of the decorated class
                        should automatically pull all attributes on instantiation.
        """
        self.api_class = api_class
        self.autoload = autoload
        
    def __call__(self, cls):
        NewClass = CreateNewClass(ClientClass=cls, APIClass=self.api_class, autoload=self.autoload)
            
        # Give the class its attributes as defined in the API
        for attr in self.api_class.__exposed_attrs__:
            # Set the attributes as properties of NewClass
            setter = setAttrTemplate(self.api_class, attr)
            getter = getAttrTemplate(self.api_class, attr)
            setattr(NewClass, attr, property(getter, setter))
            
            # Set the value of each attribute to the correct version of ``None``
            attr_type = getattr(self.api_class, attr)
            attr_type_group = discriminate(attr_type)
            if attr_type_group == LIST_OF_OBJECTS_FROM_MODEL:
                NewClass.__hidden__[attr] = reference_objs([])
                NewClass.__old__[attr] = reference_objs([])
            elif attr_type_group == OBJECT_FROM_MODEL:
                NewClass.__hidden__[attr] = reference_objs(None)
                NewClass.__old__[attr] = reference_objs(None)
            else:
                NewClass.__hidden__[attr] = None
                NewClass.__old__[attr] = None
                
        # Give the class its methods as defined in the API
        methods =  [ "delete" ]
        if hasattr(self.api_class, "__exposed_methods__"):
            methods.extend(self.api_class.__exposed_methods__)
        for method in methods:
            setattr(NewClass, method, methodTemplate(method).get_func())
        
        
        
        # Update AutoAPI.classes:
        AutoAPI.classes[self.api_class.__name__] = NewClass
        setattr(AutoAPI, self.api_class.__name__, NewClass)
        DB[self.api_class.__name__] = {}
                    
        return NewClass

        
def CreateNewClass(ClientClass, APIClass, autoload):
    """
    Creates the NewClass based on the supplied ``ClientClass``.
    
    @param ClientClass This is the client-side class to add the API magic to.
    @param APIClass This is the API class which defines the attributes to add.
    @param autoload This sets whether, on instantiation, an object pulls all of its attributes.
    """
    class NewClass(ClientClass):
        
        __api__ = APIClass
        __autoload__ = autoload
        __attrs_to_post_onCreate__ = set()
        __attrs_to_pull_onCreate__ = set()
        __funcs_to_run_onCreate__ = {}
        __name__ = ClientClass.__name__
        __client_cls__ = ClientClass
        __hidden__ = {}
        __old__ = {}
        __attrs_to_copy__ = ['__hidden__', '__old__']
        
        def __init__(self, *args, **kwargs):
            for attr_to_copy in self.__class__.__attrs_to_copy__:
                """
                ``__hidden__`` and ``__old__`` contain (at the moment) default
                values for the attributes defined in the API.  To avoid
                writing to NewClass.__hidden__, we create a copy in self.
                """
                value_to_copy = getattr(self.__class__, attr_to_copy)
                setattr(self, attr_to_copy, copy(value_to_copy) )
            
            """
            Passing ``id`` implies loading an object from the server DB 
            instead of creating a new one.  Typically this functionality
            is only used within the interface model.
            """
            if kwargs.has_key('id'):
                self.id = kwargs['id']
                DB[self.__api__.__name__][self.id] = self
                del kwargs['id']
            else:
                """
                If no ``id`` is passed, we create a new object.
                Setting ``self.id = None`` stops this object from being 
                referenced by another object, for example::
                
                ni = CommonPhrases('Ni')
                knight = Knight()
                knight.common_phrases = ni
                
                The last line will wait (ie. hang) for ``ni`` to be created on 
                the server and for ``ni.id`` to be set before 
                ``knight.common_phrases`` is set and flow continues.
                """
                self.id = None
                self.__create__()
                
            """
            ``autoload`` can also be passed as a keyword on instantiation
            of the class to define whether the object should pull all of its
            attributes.
            """
            if kwargs.has_key('autoload'):
                self.__autoload__ = kwargs['autoload']
                del kwargs['autoload']
            if self.__autoload__:
                self._update_()
            
            """
            Now we look for any attributes from the API in ``kwargs``,
            and set them accordingly (note that since self.arg is a 
            property, there's more to it than it seems.  Check 
            :class:`~interface.client.setAttrTemplate` for details.
            """
            client_kwargs = {}
            for arg, value in kwargs.iteritems():
                if arg in self.__api__.__exposed_attrs__:
                    setattr(self, arg, value)
                else:
                    client_kwargs[arg] = value
                    
            """
            All other kwargs are passed on to ``ClientClass.__init__``,
            if it exists.
            """
            if hasattr(self.__client_cls__, '__init__'):
                self.__client_cls__.__init__(self, *args, **client_kwargs)
                
        def __repr__(self):
            if hasattr(self.__client_cls__, '__repr__'):
                return self.__client_cls__.__repr__(self)
            elif self.id!=None:
                return '%s object with id=%d' %(self.__api__.__name__, self.id)
            else:
                return '%s object without id' %self.__api__.__name__
            
        def __create__(self):
            """
            All methods set above have to wait until the object's ``id`` is set.
            Since ``__create__`` is what creates ``id``, the same rules can't
            apply here.  As such the ``__create__`` function needs to bypass 
            that check and go straight to the WebServiceProxy.
            """
            WebServiceProxy(self.__api__.__name__, 'create', handler=self)()
                    
        def _createResponse_(self, id):
            """
            When ``self.__create__`` comes back with an ``id``, we need to go
            through the lists of attributes and functions that were waiting
            for creation.
            """
            
            """
            Setting ``self.id`` un-hangs threads caught referencing ``self``.
            """
            self.id = id
            
            """
            We now register ``self`` with the client-side ``DB`` dict.
            """
            DB[self.__api__.__name__][self.id] = self
            
            """
            If ``self.attribute`` was set while ``self.id == None``, it was
            added to ``self.__attrs_to_post_onCreate__``.  Now we can post
            the new values.
            """
            for attr in self.__attrs_to_post_onCreate__:
                attr_type = getattr(self.__api__, attr)
                attr_type_group = discriminate(attr_type)
                
                value = getattr(self, attr)
                if attr_type_group in [OBJECT_FROM_MODEL, LIST_OF_OBJECTS_FROM_MODEL]:
                    # If value is object (eg. Atoms(), Projects()), then convert to dict.
                    value = reference_objs(value)
                self.__post__(attr, value)
                
            """
            If ``self._update_('attribute')`` was called while 
            ``self.id == None``, we can update the attribute now.
            """
            for attr in self.__attrs_to_pull_onCreate__:
                if attr not in self.__attrs_to_post_onCreate__:
                    self.__pull__(attr)
            
            """
            If ``self.server_method()`` was called while ``self.id == None``,
            we can now make the remote call.  When it comes back, 
            ``self.__server_methodResponse__`` will be called if it exists.
            """
            for func_name, (args, kwargs) in self.__funcs_to_run_onCreate__.iteritems():
                func = getattr(self, func_name)
                func(*args, **kwargs)
            
            """
            If ``ClientClass._onCreate_`` exists, call it.
            """
            if hasattr(self.__client_cls__, '_onCreate_'):
                self.__client_cls__._onCreate_()
                
        
        def _deleteResponse_(self):
            """
            If ``self.delete`` was called and the server acknowledged it,
            call ``ClientClass._onDelete_()`` if it exists.
            """
            if hasattr(self.__client_cls__, '_onDelete_'):
                self.__client_cls__._onDelete_()
        
        
        def _update_(self, *attrs_to_update):
            """
            This is a friendly interface to ``self.__pull__``.
            Pass it some attributes and it will pull them.
            Pass it nothing and it will update all attributes.
            
            @param *attrs_to_update This is a series of attributes 
                                    (eg. ``"Name"``) to pull.
            """
            if len(attrs_to_update)==0:
                attrs_to_update = self.__api__.__exposed_attrs__
            for attr in attrs_to_update:
                self.__pull__(attr)
                
        def __pull__(self, attr):
            """
            This pulls the value of ``attr`` for this object from the server's
            DB (ie. the object in the server's DB where ""id == self.id"".
            If ``self.id`` doesn't exist yet, put this request in a queue for
            when it does exist.
            """
            if self.id != None:
                WebServiceProxy(self.__api__.__name__, attr, operation='pull', handler=self)(id=self.id)
            else:
                self.__attrs_to_pull_onCreate__.add(attr)
            
        def __post__(self, attr, value):
            """
            This posts (sets) the value of ``attr`` for this object on the 
            server's DB (ie. the object in the server's DB where 
            ""id == self.id"".
            If ``self.id`` doesn't exist yet, put this request in a queue for
            when it does exist.
            """
            if self.id != None:
                WebServiceProxy(self.__api__.__name__, attr, operation='post', handler=self)(id=self.id, value=value)
            else:
                self.__attrs_to_post_onCreate__.add(attr)
            
        def __onRemoteResponse__(self,request_info, response):
            """
            This is called whenever the server has finished a request.
            There are three types of request:
            * Pull an attribute
            * Post an attribute
            * Call a server-side function
            """
            attr = request_info.attr
            operation = request_info.operation
            
            if attr in self.__api__.__exposed_attrs__ and operation=='pull':
                expected_attr_type = getattr(self.__api__, attr)
                expected_attr_type_group = discriminate(expected_attr_type)
                new_value = response
                current_value = self.__hidden__[attr]
                
                """
                If ``attr`` is an object or list of objects defined in the API
                then new_value is a dict that refers to those object(s).
                Dereferencing means turning that reference into a local object.
                """
                if expected_attr_type_group in [OBJECT_FROM_MODEL, LIST_OF_OBJECTS_FROM_MODEL]:
                    new_obj = dereference_objs(new_value)
                elif expected_attr_type_group == PRIMITIVE:
                    new_value = expected_attr_type(new_value)
                
                # If The attribute has changed:
                if new_value!=current_value:
                    if type(new_value) == dict:
                        if expected_attr_type_group==OBJECT_FROM_MODEL\
                            and new_value['obj_type'] in [expected_attr_type, None]:
                            pass
                        elif expected_attr_type_group==LIST_OF_OBJECTS_FROM_MODEL\
                            and new_value['obj_type'] in [expected_attr_type[0], None]:
                            pass
                    elif type(new_value) in [expected_attr_type, type(None)]:
                        pass
                    elif type(new_value)==str and expected_attr_type==unicode:
                        new_value = unicode(new_value)
                    else:
                        """
                        If none of the above conditions are met, something 
                        went wrong.
                        """
                        raise Warning('Wrong data %s of type %s stored in property %s which expects %s' %(`new_value`, `type(new_value)`,`attr`, `expected_attr_type`) )
                    
                    
                    self.__hidden__[attr] = new_value
                    self.__old__[attr] = current_value
                    
                    # Now call the appropriate _onAttributeChange_ method
                    self.__onAttrChange__(attr)
                    
                    """
                    If I've been told by the server that 
                    ``cheddar.Shop`` has changed from old_shop to new_shop, 
                    I'll need to update old_shop.Cheeses and new_shop.Cheeses
                    """
                    self.__process_dependencies__(attr)
            
            elif attr in self.__api__.__exposed_attrs__ and operation=='post':
                """
                If I've just set ``cheddar.Shop = my_shop`` and the server
                successfully committed the change to its DB, I'll need to
                update old_shop.Cheeses and new_shop.Cheeses
                """
                self.__process_dependencies__(attr)
            
            elif attr not in self.__api__.__exposed_attrs__:
                """
                If the server completed a method defined in the API, here we
                run the ``self._functionResponse_`` method and pass it any
                data that the server returned.  Of course if it's a reference
                to an object, it is first dereferenced into a local object.
                """
                if hasattr(self, '_%sResponse_' %attr):
                    if response==None:
                        getattr(self, '_%sResponse_' %attr)()
                    elif type(response) == dict:
                        getattr(self, '_%sResponse_' %attr)(dereference_objs(response))
                    else:
                        getattr(self, '_%sResponse_' %attr)(response)
        
        def __onRemoteError__(self,request_info, error):
            """
            If the web call failed, either call the ``self._functionError_``
            method if it exists, or just raise an Exception.
            """
            if hasattr(self, '_%sError_' %request_info.attr):
                getattr(self, '_%sError_' %request_info.attr)(request_info, error)
            else:
                raise WebServiceError('Remote call failed, and no callback function defined: Error=%s' %`error`)
        
        def __onAttrChange__(self, attr):
            """
            This is called when an attribute is changed (either locally
            or on the server).  If changing cheese, it calls 
            ``self._onCheeseChange_``.
            """
            if hasattr(self, "_on%sChange_" %attr):
                changeHandler = getattr(self, "_on%sChange_" %attr)
                changeHandler()
            
        def __process_dependencies__(self, attr):
            """
            If the given ``attr`` is defined in the APIClass as an object
            or list of objects, this finds the old and new objects and
            passes them to ``self.__update_relevant_attrs__``.
            """
            attr_type = getattr(self.__api__, attr)
            attr_type_group = discriminate(attr_type)
            old_value = self.__old__[attr]
            new_value = self.__hidden__[attr]
            
            
            # If it was an object that just changed, I need to ...
            if attr_type_group == OBJECT_FROM_MODEL:
                old_obj = dereference_objs(old_value)
                new_obj = dereference_objs(new_value)
                if old_obj:
                    # ... tell the old_obj I've changed
                    old_obj = dereference_objs( old_value )
                    old_obj.__update_relevant_attrs__(self)
                if new_obj:
                    # ... and tell the new_obj that I've changed
                    new_obj = dereference_objs( new_value )
                    new_obj.__update_relevant_attrs__(self)
            
            # If it was a list of objects that changed, I ...
            if attr_type_group == LIST_OF_OBJECTS_FROM_MODEL:
                changed_objs = set(dereference_objs(new_value)).symmetric_difference(set(dereference_objs(old_value)))
                for changed_obj in changed_objs:
                    # ... tell the changed_obj I've changed
                    changed_obj.__update_relevant_attrs__(self)
        
        def __update_relevant_attrs__(self, changed_obj):
            """
            This guesses relationships on the server's DB (be they one-to-one,
            one-to-many, or many-to-many), and attempts to update any related
            object attributes.  For example if I change ``cheese.Shop`` from
            ``old_shop`` to ``new_shop``, this checks the Shop APIClass for
            any attributes who's type is "Cheese".  It finds the attribute
            ``Cheeses``, so tells ``old_shop.Cheeses`` and ``new_shop.Cheeses``
            to update themselves.
            This is called when the server is given new data or new data is
            pulled, but only when it is new data.  This avoids infinite 
            recursion.
            Any more complicated relationships should update themselves in
            ``self._onAttributeChange_`` methods.  For example if ``Shop``
            has an attribute ``NumberOfCheesesAvailable``, changing 
            ``my_shop.Cheeses`` would not automatically update it here.
            Instead, consider::
            
            
            @AutoAPI(api.Shop)
            class Shop:
                def _onCheesesChange_(self):
                    self.update('NumberOfCheesesAvailable')
            
            
            """
            
            changed_obj_classname = changed_obj.__api__.__name__
            relevant_attrs = []
            for exposed_attr in self.__api__.__exposed_attrs__:
                exposed_attr_type = getattr(self.__api__, exposed_attr)
                exposed_attr_type_group = discriminate(exposed_attr_type)
                if exposed_attr_type_group == LIST_OF_OBJECTS_FROM_MODEL and exposed_attr_type[0] == changed_obj_classname:
                    relevant_attrs.append(exposed_attr)
                elif exposed_attr_type_group == OBJECT_FROM_MODEL and exposed_attr_type == changed_obj_classname:
                    relevant_attrs.append(exposed_attr)
            #pdb.set_trace()
            #print "I am %s and I'm updating %s" %(`self`, `relevant_attrs`)
            self._update_(*relevant_attrs)
    return NewClass
        
        
def CompleteTheModel():
    """
    This creates a class for all objects defined in the API that haven't been
    defined in the client code.
    """
    already_defined_api_classnames = set(AutoAPI.classes.keys())
    all_api_classnames = set([api_classname for api_classname in dir(API) if type(getattr(API, api_classname))==helper.AddAttrList])

    all_api_classnames_except_helpers = all_api_classnames.difference( helper._helpers )

    undefined_api_classnames = all_api_classnames_except_helpers.difference( already_defined_api_classnames )


    for classname in undefined_api_classnames:
        api_class = getattr(API, classname)
        @AutoAPI(api_class)
        class ModelTemplate(object):
            pass
        ModelTemplate.__name__ = classname



def reference_objs(objs):
    """
    This turns local object(s) into a reference, which is a dict containing
    the object(s) id(s) and type.  This is what's saved in the ``__old__`` and
    ``__hidden__`` dicts in the classes decorated with AutoAPI, and it's what
    is passed between the client and server.
    If the client code tries to reference an object that hasn't been created
    on the server yet, it is here that the code hangs.
    """
    if objs == None:
        return dict(obj_id=None, obj_type=None)
    elif objs == []:
        return dict(obj_ids=None, obj_type=None)
    elif type(objs) == list:
        obj_ids = []
        for obj in objs:
            while( obj.id == None ):
                pass
            obj_ids.append( obj.id )
                
        obj_ids = ','.join(str(obj_id) for obj_id in obj_ids)
        return dict(obj_ids=obj_ids, obj_type=objs[0].__api__.__name__)
    else:
        while( objs.id == None ):
            pass
        return dict(obj_id=objs.id, obj_type=objs.__api__.__name__)
    
    
def dereference_objs(obj_refs):
    """
    This turns a reference into a local object (or list thereof).
    It does the opposite of :class:`~reference_objs`
    """
    obj_type = obj_refs['obj_type']
    if 'obj_ids' in obj_refs:
        if obj_type == None:
            return []
        objs = []
        for obj_id in obj_refs['obj_ids'].split(','):
            objs.append( dereference_obj(obj_type, int(obj_id)) )
        return objs
    elif 'obj_id' in obj_refs:
        if obj_type == None:
            return None
        obj = dereference_obj(obj_type, obj_refs['obj_id'])
        return obj

def dereference_obj(obj_type, obj_id):
    """
    This is called by ``dereference_objs`` to get a single local object.
    If it doesn't exist, this creates it.
    """
    if not obj_id in DB[ obj_type ].keys():
        obj_class = AutoAPI.classes[obj_type]
        obj = obj_class( id=obj_id )
    else:
        obj = DB[ obj_type ][ obj_id ]
        
    return obj


class setAttrTemplate:
    """
    This class gives the setter for attributes in classes decorated with 
    AutoAPI.
    """
    def __init__(self, api_class, attr):
        self.attr = attr
        self.attr_type = getattr(api_class, attr)
        self.attr_type_group = discriminate(self.attr_type)
        
    def __call__(self, api_obj, value):
        """
        This is the actual setter function for the attribute.
        """
        old_value = api_obj.__hidden__[self.attr]
        
        if self.attr_type_group in [OBJECT_FROM_MODEL, LIST_OF_OBJECTS_FROM_MODEL]:
            # If value is a local object, create a reference to it.
            value = reference_objs(value)
        elif self.attr_type_group == PRIMITIVE:
            value = self.attr_type(value)
        
        if value!=old_value:
            """
            If this attribute has changed:
            Firstly, update the attribute's hidden values (``__hidden__`` and 
            ``__old__``)
            """
            api_obj.__old__[self.attr] = old_value
            api_obj.__hidden__[self.attr] = value
            
            """
            Secondly, post the new value to the server
            """
            api_obj.__post__(self.attr, value)
            
            """
            Finally, call the relevant change handler.
            """
            api_obj.__onAttrChange__(self.attr)
            
                
            
            
                

class getAttrTemplate:
    """
    This class gives the getter for attributes in classes decorated with 
    AutoAPI.
    """
    def __init__(self, api_class, attr):
        self.attr = attr
        self.attr_type = getattr(api_class, attr)
        self.attr_type_group = discriminate(self.attr_type) 
        
    def __call__(self, api_obj):
        """
        This is the actual getter function for the attribute.
        """
        value = api_obj.__hidden__[self.attr]
        
        if self.attr_type_group in [OBJECT_FROM_MODEL, LIST_OF_OBJECTS_FROM_MODEL] and value!=None:
            """
            If this attribute should give an object or list thereof, then 
            ``value`` is a reference to it.  Dereferencing gives those local
            objects.
            """
            value = dereference_objs(value)
        return value

class methodTemplate:
    """
    This is the template for creating server-side functions locally.
    """
    def __init__(self, method):
        self.method = method
        self.web_function = None
        
    def get_func(self):
        """
        This returns the actual function that can be called inside the
        object of a class decorated by AutoAPI.  It's made a little messy
        since we need the same :class:`~WebServiceProxy` object to be called
        for subsequent calls to ``func``.  This prevents
        :class:`~WebServiceProxy` from getting confused with overlapping
        requests.
        """
        def func(api_obj, *args, **kwargs):
            if self.web_function == None:
                self.web_function = WebServiceProxy(api_obj.__api__.__name__, self.method, handler=api_obj)
            if api_obj.id != None:
                self.web_function(self_id = api_obj.id, *args, **kwargs)
            else:
                api_obj.__funcs_to_run_onCreate__[self.method] = (args, kwargs)
        return func

LIST_OF_OBJECTS_FROM_MODEL = 0
OBJECT_FROM_MODEL = 1
PRIMITIVE = 2
NONE = 3

def discriminate(typ):
    """
    Determines to which group of types the given type belongs.
    """
    if typ in helper._primitives:
        # If it's a primitive type
        return PRIMITIVE
    elif typ == None:
        # It would be odd if this is the case
        return NONE
    elif type(typ) == list and hasattr(API, typ[0]):
        # If it's a list of objects defined in model
        return LIST_OF_OBJECTS_FROM_MODEL
    elif hasattr(API, typ):
        # If it's a single object defined in model
        return OBJECT_FROM_MODEL
        
    else:
        raise AutoAPIError('Type passed to decorator is not valid')

        
#CompleteTheModel()