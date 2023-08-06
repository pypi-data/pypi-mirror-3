#-*- coding: utf-8 -*-
from time import time
from warnings import warn
from cocktail.modeling import (
    getter,
    classgetter,
    empty_list,
    empty_dict,
    empty_set,
    OrderedSet
)
from cocktail.iteration import first
from cocktail.pkgutils import get_full_name
from cocktail.html.viewnames import get_view_full_name
from cocktail.html import renderers
from cocktail.html.rendering import (
    Rendering,
    generate_id,
    rendering_cache
)
from cocktail.html.documentmetadata import DocumentMetadata
from cocktail.html.resources import Resource
from cocktail.html.overlay import apply_overlays

default = object()


class Element(object):
    """Base class for all presentation components.
    
    An element provides an abstraction over a piece of HTML content. It can be
    modified programatically before it is rendered, which makes it possible to
    compound complex presentations out of simpler elements.
    
    Elements expose all the properties of an HTML tag, such as their tag name,
    attributes, CSS classes and inline styles.

    Elements can be nested inside each other, conforming a hierarchical
    structure represented in their `parent` and `children` properties. The
    `append`, `insert`, `place_before` and `place_after` methods provide
    several ways to grow this tree.

    Elements can be rendered as `stand alone fragments <render>` or embeded
    within a `full page structure <render_page>`.

    When being rendered in a full page, elements can take advantage of features
    such as `linked resources <resources>`, `meta declarations <meta>` and
    propagation of data to the client (`parameters <client_params>`,
    `variables <client_variables>`, `code snippets <client_code>` and
    `translations <client_translations>`).

    .. attribute:: tag

        The tag name assigned to the element. If set to None, the
        element's tag and attributes won't be rendered, only its content.

    .. attribute:: page_doctype

        Sets the doctype of the resulting document for a
        `full page rendering <render_page>` of the element.

    .. attribute:: page_title

        Sets the title of the resulting document for a
        `full page rendering <render_page>` of the element.

    .. attribute:: page_charset

        Sets the character set of the resulting document for a
        `full page rendering<render_page>` of the element.

    .. attribute:: page_content_type

        Sets the content type of the resulting document for
        a `full page rendering <render_page>` of the element.

    .. attribute:: page_base_href

        Sets the default base URL for any relative URLs inside the document.

    .. attribute:: styled_class
    
        Indicates if the element class should add its own name
        as a CSS class of its instances.
        
        For example, given the following python class hierarchy::
            
            class Box(Element):
                pass

            class FancyBox(Box):
                pass

        An instance of FancyBox will automatically have its 'class' HTML
        attribute set to "Box FancyBox".

        This property is *not inherited* between classes, each class must
        provide its own value for it. `Element` sets it to False, its
        subclasses set it to True by default.

    .. attribute:: visible
    
        Indicates if the element should be rendered (False) or hidden
        (True).

    .. attribute:: collapsible
    
        Elements marked as collapsible are automatically hidden
        if they don't have one or more children which should be rendered.

    .. attribute:: overlays_enabled
        
        Enables or disables `overlays <Overlay>` for the element.

    .. attribute:: client_model
        
        When set to a value other than None, the element won't
        be rendered normally. Instead, its HTML and javascript code will be
        serialized to a string and made available to the client side
        *cocktail.instantiate* method, using the given identifier.

    .. attribute:: data_display
    
        The `DataDisplay` used by the element for data binding purposes.
    
    .. attribute:: data
        The source of data used by the element for data binding purposes.

    .. attribute:: member
        
        The `~cocktail.schema.Member` used by the element for data binding
        purposes.

    .. attribute:: language
        
        The language used by the element for data binding purposes.
    """
    tag = "div"
    page_doctype = None
    page_title = None
    page_charset = None
    page_content_type = None
    page_base_href = None
    styled_class = False
    visible = True
    collapsible = False
    overlays_enabled = False
    client_model = None

    # Data binding
    data_display = None
    data = None
    member = None
    language = None
    
    def __init__(self,
        tag = default,
        class_name = None,
        children = None,
        **attributes):
 
        self.__parent = None
        self.__children = None

        if children:
            for child in children:
                self.append(child)
        
        if attributes:
            self.__attributes = dict(attributes)
        else:
            self.__attributes = None
    
        if self.class_css:
            self["class"] = self.class_css

        if class_name:
            self.add_class(class_name)

        self.__meta = None
        self.__resources = None
        self.__client_params = None
        self.__client_code = None
        self.__client_variables = None
        self.__client_translations = None
        self.__is_bound = False
        self.__is_ready = False
        self.__binding_handlers = None
        self.__ready_handlers = None
        self.__document_ready_callbacks = None

        if tag is not default:
            self.tag = tag
         
        if self.overlays_enabled:
            apply_overlays(self)

        self._build()

    class __metaclass__(type):

        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            cls._view_name = None
         
            if "overlays_enabled" not in members:
                cls.overlays_enabled = True

            # Aggregate CSS classes from base types
            cls._classes = list(cls.__mro__)[:-1]
            cls._classes.reverse()
            css_classes = []

            if "styled_class" not in members:
                cls.styled_class = True

            for c in cls._classes:
                if getattr(c, "styled_class", False):
                    css_classes.append(c.__name__)

            cls.class_css = css_classes and " ".join(css_classes) or None

    @classgetter
    def view_name(cls):
        if cls._view_name is None:
            cls._view_name = get_view_full_name(get_full_name(cls))
        return cls._view_name

    def __str__(self):

        if self.tag is None:
            return "html block"
        else:
            desc = "<" + self.tag
            
            id = self["id"]

            if id:
                desc += " id='%s'" % id

            css = self["class"]

            if css:
                desc += " class='%s'" % css

            desc += ">"
            return desc

    # Rendering
    #--------------------------------------------------------------------------

    def render_page(self,
        renderer = None,
        document_metadata = None,
        collect_metadata = True,
        cache = rendering_cache):
        """Renders the element as a full HTML page.

        This method creates a page structure for the element (using its
        `make_page` method) and outputs the resulting HTML code, including
        links to its resources and other metadata.

        :param renderer: The renderer that will generate the markup for the
            element.
        :type renderer: `Renderer`

        :param document_metadata: The set of resources and metadata for the
            rendered document: scripts, stylesheets, meta tags, client side
            state, etc.

            This parameter covers two use cases: it makes it possible to inject
            additional metadata into the rendered document, and it allows to
            inspect the produced metadata after rendering (the object will be
            modified by the rendering operation).
        :type document_metadata: `DocumentMetadata`

        :param collect_metadata: Determines if resources and meta data
            (scripts, stylesheets, meta tags, etc) defined by rendered elements
            should be evaluated and collected.
        :type collect_metadata: bool

        :param cache: A cache for rendered content and metadata. Will be used
            by those elements with `caching enabled <cached>`. Setting this
            parameter to None disables use of the cache for this rendering
            operation.
        :type cache: `~cocktail.cache.Cache`

        :return: The HTML code for the element, embeded within a full HTML
            page.
        :rtype: unicode
        """
        if renderer is None:
            renderer = renderers.default_renderer

        if document_metadata is None:
            document_metadata = DocumentMetadata()

        content = self.render(
            renderer = renderer,
            document_metadata = document_metadata,
            collect_metadata = collect_metadata,
            cache = cache
        )

        from cocktail.html.document import HTMLDocument
        document = HTMLDocument()
        document.content = content
        document.metadata = document_metadata
        document.rendering_options = {
            "renderer": renderer,
            "cache": cache
        }

        return document.render(
            renderer = renderer,
            collect_metadata = False,
            cache = None
        )

    def render(self,
        renderer = None,
        document_metadata = None,
        collect_metadata = True,
        cache = rendering_cache):
        """Renders the element as an HTML fragment.

        This method renders the HTML code for the element's tree. Note that the
        resources and meta data associated with the element will *not* be
        included in the produced markup; use `render_page` to render them
        within a full page structure.

        :param renderer: The renderer that will generate the markup for the
            element.
        :type renderer: `Renderer`

        :param document_metadata: The set of resources and metadata required by
            the rendered document: scripts, stylesheets, meta tags, client side
            state, etc.
            
            This parameter covers two use cases: it makes it possible to inject
            additional metadata into rendering results, and it allows to
            inspect the produced metadata after rendering (the object will be
            modified by the rendering operation).
        :type document_metadata: `DocumentMetadata`

        :param collect_metadata: Determines if resources and meta data
            (scripts, stylesheets, meta tags, etc) defined by rendered elements
            should be evaluated and collected.
        :type collect_metadata: bool

        :param cache: A cache for rendered content and metadata. Will be used
            by those elements with `caching enabled <cached>`. Setting this
            parameter to None disables use of the cache for this rendering
            operation.
        :type cache: `~cocktail.cache.Cache`

        :return: The HTML code for the element.
        :rtype: unicode
        """
        if renderer is None:
            renderer = renderers.default_renderer

        rendering = Rendering(
            renderer = renderer,
            document_metadata = document_metadata,
            collect_metadata = collect_metadata,
            cache = cache        
        )
        rendering.render_element(self)
        return rendering.markup()                

    def _render(self, rendering):
        """Readies the element and writes its HTML code to the given stream.

        This is an internal method; applications should invoke `render_page`
        or `render`, which in turn will call this method.
        
        The default implementation delegates the production of its HTML code to
        the given renderer object. Overriding this behavior will seldom be 
        necessary. The `Content` class is one of the rare cases. Another case
        were it may make sense is to optimize expensive rendering operations,
        bypassing the `Element` class to produce opaque HTML blobs for nested
        content.

        :param rendering: The rendering buffer where the element should be
            written.
        :type renderer: `Rendering`
        """
        rendering.renderer.write_element(self, rendering)

    def _build(self):
        """Initializes the object.
        
        This method is used by subclasses of `Element` to initialize their
        instances. It is recommended to use this method instead of overriding
        the class constructor, which can be tricky.
        """

    def bind(self):
        """Updates the element's state before it is rendered.
        
        This method gives the element a chance to initialize its state before
        its HTML code is written. 
        
        `bind` serves a similar purpose to `ready`, which is executed right 
        after. By convention, `bind` code should only perform 'shallow' updates
        of the element's state: modifying its content should be done at the
        `ready` stage. This separation makes it possible to implement effective
        caching: `bind` will always be called before rendering, while `ready`
        won't be when rendering an element from cached content.

        The method will first invoke the element's `_binding` method, and then
        any function scheduled with `when_binding`.

        It is safe to call this method more than once, but any invocation after
        the first will produce no effect.
        """
        if not self.__is_bound:
            self._binding()

            if self.__binding_handlers:
                for handler in self.__binding_handlers:
                    handler()

            self.__is_bound = True

    def when_binding(self, handler):
        """Call the given function when the element reaches the `bind` stage.

        See `bind` and `ready` for more details on late initialization.

        :param handler: The function that will be invoked. It should
            not receive any parameter.
        :type handler: callable
        """
        if self.__binding_handlers is None:
            self.__binding_handlers = [handler]
        else:
            self.__binding_handlers.append(handler)

    def _binding(self):
        """A method invoked when the element reaches the `bind` stage.
        
        This is a placeholder method, to implement late initialization for the
        element. It's an alternative to `when_binding`, and can be more
        convenient when defining initialization logic at the class level.
        Implementors should always call the overriden method from their bases.

        See `bind` and `ready` for more details on late initialization.
        """

    def ready(self):
        """Readies the element before it is rendered.

        This method gives the element a chance to initialize itself and its
        content before its HTML code is written. This can be useful to delay
        filling certain parts of an element until the very last moment. Data
        driven controls are a very common use case for this mechanism (ie.
        don't create a table's rows until the table is about to be rendered,
        allowing the data source to change in the mean time).

        This method serves a similar purpose to `bind`, which is always
        executed before `ready`. While `bind` is expected to perform shallow,
        relatively unexpensive updates of the element, `ready` is allowed to
        modify its content and perform heavy weight initialization duty.

        Note that the rendering cache takes advantage of this convention, by
        skipping the `ready` stage when rendering an element from cached
        content.
        
        The method will first invoke `bind`, then the element's `_ready`
        method, and then any function scheduled with `when_ready`.

        It is safe to call this method more than once, but any invocation after
        the first will produce no effect. Likewise, the implicit call to `bind`
        won't produce any effect if it had been executed already.
        """
        if not self.__is_ready:
            
            self.bind()
                        
            self._ready()
            
            if self.__ready_handlers:
                for handler in self.__ready_handlers:
                    handler()

            if self.__client_params or self.__client_code:
                self.require_id()

            if self.member: 
                self.add_class(self.member.__class__.__name__)

            self.__is_ready = True

    def when_ready(self, handler):
        """Call the given function when the element reaches the `ready` stage.
        
        See `bind` and `ready` for more details on late initialization.

        :param handler: The function that will be invoked. It should
            not receive any parameter.
        :type handler: callable
        """
        if self.__ready_handlers is None:
            self.__ready_handlers = [handler]
        else:
            self.__ready_handlers.append(handler)

    def _ready(self):
        """A method invoked when the element reaches the `ready` stage.
        
        This is a placeholder method, to implement late initialization for the
        element. It's an alternative to `when_ready`, and can be more
        convenient when defining initialization logic at the class level.
        Implementors should always call the overriden method from their bases.

        See `bind` and `ready` for more details on late initialization.
        """

    # Cached content
    #--------------------------------------------------------------------------
    cached = False
    cache_expiration = None

    def get_cache_key(self):
        raise KeyError("%s doesn't define a cache key" % self)

    def get_cache_invalidation(self):
        return None

    # Attributes
    #--------------------------------------------------------------------------
    
    @getter
    def attributes(self):
        """A dictionary containing the HTML attributes defined by the element.

        Attributes can be set to any value that can be transformed into
        unicode. Attributes set to None will not be rendered.        
        """
        if self.__attributes is None:
            return empty_dict
        else:
            return self.__attributes

    def __getitem__(self, key):
        """Gets the value of an HTML attribute, using the indexing operator.

        :param key: The name of the attribute to retrieve.
        :type key: str

        :return: The value for the requested attribute, or None if it's not
            defined by the element.
        """
        if self.__attributes is None:
            return None
        else:
            return self.__attributes.get(key)

    def __setitem__(self, key, value):
        """Sets the value of an HTML attribute, using the indexing operator.

        :param key: The name of the attribute to set.
        :type key: str

        :param value: The value to assign to the attribute.
        """
        if self.__attributes is None:
            if value is not None:
                self.__attributes = {key: value}
        else:
            if value is None:
                self.__attributes.pop(key, None)
            else:
                self.__attributes[key] = value

    def __delitem__(self, key):
        """Removes an attribute from the element, using the 'del' operator.

        Deleting an undefined attribute is allowed, and will produce no effect.        
        """
        if self.__attributes is not None:
            self.__attributes.pop(key, None)

    def require_id(self):
        """Makes sure the element has an 'id' HTML attribute.

        If the element already has an id, the method does nothing. If it
        doesn't, it will generate a unique identifier for the element, and
        assign it to its 'id' HTML attribute.
        
        This method can be useful to identify the element uniquely at the
        client side (ie. to pass parameters for javascript scripts, set up the
        'for' attribute of a <label> tag, etc).

        Generated identifiers are guaranteed to be unique throughout a
        rendering operation (that is, within the span of a call to the
        `render` or `render_page` methods). Calling `require_id` from two
        separate (not nested) rendering invocations will generate duplicate
        identifiers.
        
        Identifier generation is only enabled during rendering operations.
        Calling this method outside a rendering method will raise an
        `IdGenerationError` exception.

        :return: The id attribute assigned to the element.
        :rtype: str

        :raise: Raises `IdGenerationError` if the method is called outside the
            scope of a call to `render` or `render_page`.
        """
        id = self["id"]

        if not id:
            id = generate_id()
            self["id"] = id

        return id

    # Visibility
    #--------------------------------------------------------------------------
    
    @getter
    def rendered(self):
        """Indicates if the element should be rendered.

        An element will be rendered or ignored depending on its `visible` and
        `collapsible` attributes.
        """
        return self.visible \
            and (not self.collapsible or self.has_rendered_children())
        
    @getter
    def substantial(self):
        """Indicates if the element has enough weight to influence the
        visibility of a `collapsible` element.

        Collapsible elements are only rendered if they have one or more
        children that are deemed to be substantial. By default, an element is
        considered substantial if it is rendered. Some subclasses may alter
        this behavior: notably, `Content` considers an element consisting
        fully of whitespace to be insubstantial.
        """
        return self.rendered

    def has_rendered_children(self):
        """Indicates if any of the element's children should be rendered.

        :return: True if the element has one or more children which should be
            rendered, False if it has no children or all of its children should
            not be rendered.
        :rtype: bool
        """
        if self.__children:
            for child in self.__children:
                if child.substantial:                
                    return True

        return False

    # Tree
    #--------------------------------------------------------------------------

    @getter
    def parent(self):
        """The `element <Element>` that the element is attached to.

        Elements arrange themselves in a tree (by using `append`, `insert`,
        `place_before` or `place_after`. This property gives access to the
        element that acts as a container for the element.
        """
        return self.__parent

    @getter
    def children(self):
        """The list of child `elements <Element>` attached to the element.

        Elements arrange themselves in a tree (by using `append`, `insert`,
        `place_before` or `place_after`. This property gives access to the
        child elements that hang directly from the element.
        """
        if self.__children is None:
            return empty_list
        else:
            return self.__children
    
    def append(self, child):
        """Attach another element as the last child of the element.

        If the element to attach is a string, it will be wrapped using a new
        `Content` instance.

        If the element to attach already had a parent, it will be
        `released <release>` before being relocated within the element.

        :param child: The attached element.
        :type child: `Element` or basestring
        """
        if not isinstance(child, Element):
            child = Content(unicode(child))
        else:
            child.release()

        if self.__children is None:
            self.__children = [child]
        else:
            self.__children.append(child)
        
        child.__parent = self

    def insert(self, index, child):
        """Attach a child element at the specified position.

        If the element to attach is a string, it will be wrapped using a new
        `Content` instance.

        If the element to attach already had a parent, it will be
        `released <release>` before being relocated within the element.

        :param index: The ordinal position of the new child among its siblings.
            Accepts negative indices.
        :type index: int
        
        :param child: The attached element.
        :type child: `Element` or basestring
        """        
        if not isinstance(child, Element):
            child = Content(unicode(child))
        else:
            child.release()

        if self.__children is None:
            self.__children = []

        self.__children.insert(index, child)
        child.__parent = self

    def place_before(self, sibling):
        """Positions the element just before another element.

        If the element already had a parent, it will be `released <release>`
        before being relocated.

        :param sibling: The element that indicates the point in the element
            tree where the element should be placed.
        :type sibling: `Element`

        :raise: Raises `ElementTreeError` if the given element has no parent.
        """
        if sibling.__parent is None:
            raise ElementTreeError()

        self.release()

        sibling.__parent.__children.insert(
            sibling.__parent.__children.index(sibling),
            self
        )

        self.__parent = sibling.__parent

    def place_after(self, sibling):
        """Positions the element just after another element.

        If the element already had a parent, it will be `released <release>`
        before being relocated.

        :param sibling: The element that indicates the point in the element
            tree where the element should be placed.
        :type sibling: `Element`

        :raise: Raises `ElementTreeError` if the given element has no parent.
        """
        if sibling.__parent is None:
            raise ElementTreeError()

        self.release()

        sibling.__parent.__children.insert(
            sibling.__parent.__children.index(sibling) + 1,
            self
        )

        self.__parent = sibling.__parent

    def wrap(self, wrapped_element):
        """Positions the element before the given element, and relocates said
        element inside it.

        :param wrapped_element: The element that should be wrapped.
        :type wrapped_element: `Element`

        :raise: Raises `ElementTreeError` if the element to wrap has no parent.
        """
        self.place_before(wrapped_element)
        self.append(wrapped_element)

    def empty(self):
        """Removes all children from the element."""
        if self.__children is not None:
            for child in self.__children:
                child.__parent = None

            self.__children = None

    def release(self):
        """Removes the element from its parent.

        It is safe to call this method on an element with no parent.
        """
        if self.__parent is not None:
            self.__parent.__children.remove(self)
            self.__parent = None

    def replace(self, target):
        """Puts the element in place of the indicated element.
        
        :param target: The element that indicates the point in the element
            tree where the element should be placed.
        :type target: `Element`

        :raise: Raises `ElementTreeError` if the given element has no parent.
        """
        if target.__parent is None:
            raise ElementTreeError()

        self.release()        
        pos = target.__parent.__children.index(target)
        target.__parent.__children[pos] = self
        target.__parent = None

    def replace_with(self, replacement):
        """Replaces the element with another element.
        
        :param replacement: The element that will be put in the position
            currently occupied by the element.            
        :type replacement: `Element`

        :raise: Raises `ElementTreeError` if the element that is being replaced
            has no parent.
        """
        if not isinstance(replacement, Element):
            replacement = Content(unicode(replacement))

        replacement.replace(self)

    def reverse(self):
        """Reverses the order of the element's children."""
        if self.__children:
            self.__children.reverse()

    # CSS classes
    #--------------------------------------------------------------------------

    @getter
    def classes(self):
        """The list of CSS classes assigned to the element."""        
        css_class = self["class"]

        if css_class is None:
            return empty_list
        else:
            return css_class.split()

    def add_class(self, name):
        """Adds a CSS class to the element.

        This method makes it convenient to set the element's 'class' HTML
        attribute incrementally. Classes will be rendered in the same order
        they are assigned. Assigning the same class twice to an element will
        produce no effect.

        :param name: The name of the class to assign to the element.
        :type name: str
        """
        css_class = self["class"]

        if css_class is None:
            self["class"] = name
        else:
            if name not in css_class.split():
                self["class"] = css_class + " " + name

    def remove_class(self, name):
        """Removes a CSS class from the element.

        Just as `add_class`, this is a convenience method to manipulate the
        element's 'class' HTML attribute. It is safe to remove an undefined
        class from the element.

        :param name: The CSS class to remove.
        :type name: str
        """
        css_class = self["class"]
        
        if css_class is not None:
            classes = css_class.split()
            try:
                css_class = classes.remove(name)
            except ValueError:
                pass
            else:
                if classes:
                    self["class"] = " ".join(classes)
                else:
                    del self["class"]

    # Inline CSS styles
    #--------------------------------------------------------------------------
    
    @getter
    def style(self):
        """A dictionary containing the inline CSS declarations for the element.
        """
        style = self["style"]

        if style is None:
            return empty_dict
        else:
            style_dict = {}

            for declaration in style.split(";"):
                prop, value = declaration.split(":")
                style_dict[prop.strip()] = value.strip()

            return style_dict

    def get_style(self, property):
        """Retrieves the value of an inline CSS property.
        
        :param property: The style property to retrieve (ie. font-weight,
            color, etc).
        :type property: str

        :return: The value for the property, or None if it's undefined.
        """
        return self.style.get(property)

    def set_style(self, property, value):
        """Sets the value of an inline CSS property.

        Setting a property to None removes its declaration from the element.

        :param property: The property to retrieve the value for.
        :type property: str

        :param value: The value to assign to the property. Can be any object
            that can be serialized to a string.
        """
        style = self.style

        if style:
            if value is None:
                style.pop(property, None)
            else:
                style[property] = value

            if style:
                self["style"] = \
                    "; ".join("%s: %s" % decl for decl in style.iteritems())
            else:
                del self["style"]
        else:
            self["style"] = "%s: %s" % (property, value)

    # Resources
    #--------------------------------------------------------------------------
    
    @getter
    def resources(self):
        """The list of `resources <Resource>` (scripts, stylesheets, etc)
        linked to the element.
        
        Linked resources will be rendered along the element when a
        `full page rendering <render_page>` is requested.
        """
        if self.__resources is None:
            return empty_list
        else:
            return self.__resources

    def add_resource(self, resource, mime_type = None, ie_condition = None):
        """Links a `resource <resources>` to the element.

        Resources are `indexed by their URI<resource_uris>`, allowing only one
        instance of each URI per element. That means that linking the same
        script or stylesheet twice will produce no effect.
        
        :param resource: A resource object, or a resource URI. URI strings will
            be wrapped using a new resource object of the appropiate type.
        :type resource: `Resource` or basestring

        :param mime_type: Specifies an explicit MIME type for the resource.
            Its main purpose is to manually identify the type of URIs where
            that can't be accomplished by looking at their file extension.
        :type mime_type: str

        :param ie_condition: Indicates that the linked resource should be
            wrapped in an Internet Explorer `conditional comment 
            <http://msdn.microsoft.com/en-us/library/ms537512(VS.85).aspx>`
            with the specified expression.
        :type ie_condition: str
        """
        # Normalize the resource
        if isinstance(resource, basestring):
            uri = resource
            resource = Resource.from_uri(uri, mime_type, ie_condition)
        else:
            if mime_type or ie_condition:
                raise ValueError(
                    "Element.add_resource() should receive a reference to a "
                    "Resource object or values for creating a new Resource "
                    "instance; mixing the two is not allowed."
                )

            uri = resource.uri
            
            if uri is None:
                raise ValueError("Can't add a resource without a defined URI.")

        if self.__resources is None:
            self.__resources = OrderedSet()

        self.__resources.append(resource)

    def remove_resource(self, resource):
        """Unlinks a `resource <resources>` from the element.

        :param resource: A resource object, or a resource URI.
        :type resource: `Resource` or basestring

        :raise: Raises `ValueError` if the indicated resource is not linked by
            the element.
        """
        if isinstance(resource, basestring):
            removed_uri = resource
            resource = first(self.__resources, uri = removed_uri)

            if resource is None:
                raise ValueError("Error removing '%s' from %s: "
                    "the element doesn't have a resource with that URI")
            else:
                self.__resources.remove(resource)
        else:
            self.__resources.remove(resource)

    # Meta attributes
    #--------------------------------------------------------------------------
    
    @getter
    def meta(self):
        """A dictionary containing the meta declarations for the element.

        Meta declarations will be rendered as <meta> tags when performing a
        `full page rendering <render_page>`. 
        """
        if self.__meta is None:
            return empty_dict
        else:
            return self.__meta

    def get_meta(self, key):
        """Gets the value of the given `meta declaration <meta>`.

        :param key: The name of the meta tag to retrieve the value for.
        :type key: str

        :return: The value for the indicated declaration, or None if it's not
            defined by the element.
        """
        if self.__meta is None:
            return None
        else:
            return self.__meta.get(key)

    def set_meta(self, key, value):
        """Assigns a `meta declaration <meta>` to the element.

        :param key: The name of the meta tag to set the value for.
        :type key: str

        :param value: The value to assign to the meta tag.
        """
        if self.__meta is None:
            if value is not None:
                self.__meta = {key: value}
        else:
            if value is None:
                self.__meta.pop(key, None)
            else:
                self.__meta[key] = value

    # Document ready callback functions
    #--------------------------------------------------------------------------
    def when_document_ready(self, callback):
        if self.__document_ready_callbacks is None:
            self.__document_ready_callbacks = [callback]
        else:
            self.__document_ready_callbacks.append(callback)

    @getter
    def document_ready_callbacks(self):
        if self.__document_ready_callbacks is None:
            return empty_list
        else:
            return self.__document_ready_callbacks

    def add_head_element(self, element):
        """Specifies that the given element should be rendered within the
        <head> tag when the element takes part in a
        `full page rendering <render_page>`.

        :param element: The element to add to the page's head.
        :type element: `Element`
        """
        warn(
            "Element.add_head_element() is deprecated, use the more general "
            "Element.when_document_ready method instead, which can be used to "
            "achieve the same effect",
            DeprecationWarning,
            stacklevel = 2
        )
        @self.when_document_ready
        def add_head_element(document):
            document.head.append(element)

    def add_body_end_element(self, element):
        """Specifies that the given element should be rendered just before the
        closure of the <body> tag when the element takes part in a 
        `full page rendering <render_page>`
        """
        warn(
            "Element.add_body_end_element() is deprecated, use the more "
            "general Element.when_document_ready method instead, which can "
            "be used to achieve the same effect",
            DeprecationWarning,
            stacklevel = 2
        )
        @self.when_document_ready
        def add_body_end_element(document):
            document.body.append(element)

    # Client side element parameters
    #--------------------------------------------------------------------------
    
    @getter
    def client_params(self):
        """A dictionary with the client side parameters for the element.
    
        Each parameter in this dictionary will be relayed client side as an
        attribute of the element's DOM element, using a JSON encoder.

        Client side parameters will only be rendered if a
        `full page rendering <render_page>` is requested.
        """
        if self.__client_params is None:
            return empty_dict
        else:
            return self.__client_params
    
    def get_client_param(self, key):
        """Gets the value of the indicated
        `client side parameter <client_params>`.
        
        :param key: The parameter to retrieve.
        :type key: str

        :return: The value for the indicated parameter.

        :raise: Raises `KeyError` if the element doesn't define the indicated
            parameter.
        """
        if self.__client_params is None:
            raise KeyError("Trying to read an undefined "
                "client param '%s' on %s" % (key, self))
        else:
            return self.__client_params[key]

    def set_client_param(self, key, value):
        """Sets the value of the indicated
        `client side parameter <client_params>`.

        :param key: The parameter to set.
        :type key: str

        :param value: The value for the parameter. Can be any object that can
            be exported as JSON.
        """
        if self.__client_params is None:
            self.__client_params = {key: value}
        else:
            self.__client_params[key] = value

    def remove_client_param(self, key):
        """Deletes a `client side parameter <client_params>` from the element.

        :param key: The parameter to delete.
        :type key: str

        :raise: Raises `KeyError` if the element doesn't define the indicated
            parameter.
        """
        if self.__client_params is None:
            raise KeyError("Trying to remove an undefined "
                "client param '%s' on %s" % (key, self))
        else:
            del self.__client_params[key]
    
    # Client side element initialization code
    #--------------------------------------------------------------------------
    
    @getter
    def client_code(self):
        """A dictionary containing the snippets of javascript code attached to
        the element.

        Code attached using this mechanism will be executed as soon as the DOM
        tree is ready and its `parameters <client_params>` from the server have
        been assigned.

        Attached code will only be rendered if a
        `full page rendering <render_page>` is requested.
        """
        if self.__client_code is None:
            return empty_list
        else:
            return self.__client_code
    
    def add_client_code(self, snippet):
        """Attaches a `snippet of javascript code <client_code>` to the
        element.

        :param snippet: The snippet of code to attach to the element.
        :type snippet: str
        """
        if self.__client_code is None:
            self.__client_code = [snippet]
        else:
            self.__client_code.append(snippet)

    # Client side variables
    #--------------------------------------------------------------------------

    @getter
    def client_variables(self):
        """A dictionary containing the client side variables declared by the
        element.
    
        Each parameter in this dictionary will be relayed client side as a
        global javascript variable, using a JSON encoder. Note that different
        elements can define the same variable, overriding its value.

        Client side variables will only be rendered if a
        `full page rendering <render_page>` is requested.
        """
        if self.__client_variables is None:
            return empty_dict
        else:
            return self.__client_variables
    
    def get_client_variable(self, key):
        """Gets the value of the indicated
        `client side variable <client_variables>`.

        :param key: The name of the variable to obtain retrieve.
        :type key: str

        :return: The value for the specified variable.
        :rtype: object

        :raise: Raises `KeyError` if an undefined variable is requested.
        """
        if self.__client_variables is None:
            raise KeyError("Trying to read an undefined "
                "client variable '%s' on %s" % (key, self))
        else:
            return self.__client_variables[key]

    def set_client_variable(self, key, value):
        """Sets the value of the indicated
        `client side variable <client_variables>`.

        :param key: The name of the variable to set.
        :type key: str

        :param value: The value to set the variable to. Can be any object that
            can be serialized as JSON.
        """
        if self.__client_variables is None:
            self.__client_variables = {key: value}
        else:
            self.__client_variables[key] = value

    def remove_client_variable(self, key):
        """Deletes a `client side variable <client_variables>` from the
        element.

        :param key: The name of the variable to delete.
        :type: key str

        :raise: Raises `KeyError` if trying to delete an undefined variable.
        """
        if self.__client_variables is None:
            raise KeyError("Trying to remove an undefined "
                "client variable '%s' on %s" % (key, self))
        else:
            del self.__client_variables[key]

    # Client side translations
    #--------------------------------------------------------------------------
    
    @getter
    def client_translations(self):
        """A set of translation keys to relay client side.

        Translation keys included in this collection will be made available
        client side, using the *cocktail.translate* method.

        Translation keys will only be rendered if a
        `full page rendering <render_page>` is requested.
        """
        if self.__client_translations is None:
            return empty_set
        else:
            return self.__client_translations
    
    def add_client_translation(self, key):
        """Makes the given translation key available client side.

        The key will be added to the set of
        `translation keys <client_translations>` that the element requires at
        the client side. It is safe to call this method twice for the same key.

        :param key: The translation key to make available.
        """
        if self.__client_translations is None:
            self.__client_translations = set()
        self.__client_translations.add(key)
        

class Content(Element):
    """A piece of arbitrary HTML content.

    When rendered, instances of this class ignore their tag, attributes and
    children, using their `value` attribute as their HTML representation.
    They can still link to resources or client side assets.

    .. attribute:: value
    
        The HTML code for the element. Can be anything that can be represented
        as an unicode string.
    """
    styled_class = False
    value = None
    overlays_enabled = False

    def __init__(self, value = None, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self.value = value
 
    @getter
    def rendered(self):
        return self.visible
    
    @getter
    def substantial(self):
        return (
            self.visible
            and self.value is not None
            and unicode(self.value).strip()
        )

    def _render(self, rendering):
        if self.value is not None:
            rendering.write(unicode(self.value))


class TranslatedValue(Content):
    styled_class = False
    overlays_enabled = False

    def _render(self, rendering):
        if self.member is not None:
            rendering.write(
                self.member.translate_value(self.value)
            )


class PlaceHolder(Content):
    """A blob of content that produces its value just before it's rendered.
    
    .. attribute:: expression
        
        A callable that produces the content for the placeholder.    
    """
    def __init__(self, expression):
        Content.__init__(self)
        self.expression = expression

    def _ready(self):
        self.value = self.expression()


class ElementTreeError(Exception):
    """An exception raised when violating the integrity of an `Element` tree.
    """

