"""
A template tag that creates menu items that introspect the view 
they point to, only displaying those that the currently logged
in user can access. It also marks the currently selected item as
'active' with a css class.

Usage:

    {% menu_item "url:view_name" "Menu Title" %}

If you prefix view_name with url, as shown, then it will use reverse()
to find the view.  Otherwise, it assumes you have entered the actual
url.

A third, optional argument is a list of css classes that should be
applied to this menu item.

Note: If you have urls like /foo/bar/baz/, and your menu is /foo/bar/,
then this matches the url, and the menu item /foo/bar/ would be selected.
This would mean you can't use {% menu_item '/' 'Home' %}, so I have a
couple of special cases:
    
* the url '/' is handled specially, only an exact match will cause
  it to be marked as active.
* the text 'Menu Title' is compared in a case insensitive fashion
  to the string 'home': if it matches exactly, then it requires an
  exact url match (not just a matching prefix) to be marked as
  active.
    
The logic for determining permission to access a view is pretty simple:
look for any decorators on that view that take a first argument called
`user` or `u`, and call them with the current request.user object. If
any fail, then this user may not access that view.
"""

from django import template
from django.conf import settings
from django.core.urlresolvers import Resolver404

register = template.Library()
from django.core.urlresolvers import reverse, resolve

def get_callable_cells(function):
    """
    Iterate through all of the decorators on this function,
    and put those that might be callable onto our callable stack.
    
    Note that we will also include the function itself, as that
    is callable.
    
    This is probably the funkiest introspection code I've ever written in python.
    """
    callables = []
    if not hasattr(function, 'func_closure'):
        if hasattr(function, 'view_func'):
            return get_callable_cells(function.view_func)
    if not function.func_closure:
        return [function]
    for closure in function.func_closure:
        if hasattr(closure.cell_contents, '__call__'):
            # Class-based view does not have a .func_closure attribute.
            # Instead, we want to look for decorators on the dispatch method.
            # We can also look for decorators on a "get" method, if one exists.
            if hasattr(closure.cell_contents, 'dispatch'):
                callables.extend(get_callable_cells(closure.cell_contents.dispatch.__func__))
                if hasattr(closure.cell_contents, 'get'):
                    callables.extend(get_callable_cells(closure.cell_contents.get.__func__))
            elif hasattr(closure.cell_contents, 'func_closure') and closure.cell_contents.func_closure:
                callables.extend(get_callable_cells(closure.cell_contents))
            else:
                callables.append(closure.cell_contents)
    return callables

def get_tests(function):
    """
    Get a list of callable cells attached to this function that have the first
    parameter named "u" or "user".
    """
    return [
        x for x in get_callable_cells(function)
        if x.func_code.co_varnames[0] in ["user", "u"]
    ]

class MenuItem(template.Node):
    """
    The template node for generating a menu item.
    """
    def __init__(self, template_file, url, text, classes=None):
        """
        template_file : the name of the template that should be used for each
                        menu item. defaults to 'menu/item.html', but you can
                        override this in a new instance of this tag.
        url:            the url or url:view_name that this menu_item should point to.
        text:           the text that this menu_item will display
        classes:        Any CSS classes that should be applied to the item.
        """
        super(MenuItem, self).__init__()
        self.template_file = template_file or 'menu/item.html'
        url = url.strip('\'"')
        if url.startswith('url:'):
            self.url = reverse(url[4:], args=[])
        else:
            self.url = url
            
        self.text = text.strip('\'"')
        self.classes = classes or ""
        self.nodelist = False
        
    def render(self, context):
        """
        At render time, we need to access the context, to get some data that
        is required.
        
        Basically, we need `request` to be in the context, so we can access
        the logged in user.
        """
        if self not in context.render_context:
            context.render_context[self] = {
                'url': self.url,
                'text': self.text,
                'classes': self.classes
            }
        
        local = dict(context.render_context[self])
        
        if 'request' not in context:
            if settings.DEBUG:
                raise template.TemplateSyntaxError("menu_item tag requires 'request' in context")
            return ''
        
        request = context['request']
        
        # To find our current url, look in order at these.
        if 'page_url' in context:
            page_url = context['page_url']
        elif 'flatpage' in context:
            page_url = context['flatpage'].url
        else:
            page_url = request.path
        
        user = request.user
        
        # This is a fairly nasty hack to get around how I have my mod_python (!!!)
        # setup: which sets the SCRIPT_NAME.
        local['url'] = local['url'].replace(request.META.get('SCRIPT_NAME',''), '')
        
        # See if that url is for a valid view.
        try:
            view = resolve(local['url']).func
        except Resolver404:
            if settings.DEBUG:
                raise
            return ''
        
        # See if the user passes all tests.
        # Note that any type of Exception will result in a failure.
        try:
            can_view = all([test(user) for test in get_tests(view)])
        except Exception:
            if settings.DEBUG:
                raise
            return ''
        
        # If the user can't access the view, this token collapses to an empty string.
        if not can_view:
            return ''
        
        # Now import and render the template.
        file_name = self.template_file
        
        # Cache the nodelist within this template file.
        if not self.nodelist:
            from django.template.loader import get_template, select_template
            if isinstance(file_name, template.Template):
                t = file_name
            elif not isinstance(file_name, basestring) and is_iterable(file_name):
                t = select_template(file_name)
            else:
                t = get_template(file_name)
            self.nodelist = t.nodelist
        
        # Special-case: when the menu-item's url is '/' or text is 'home', then we don't mark
        # it as active unless it's a complete match.
        if page_url.startswith(local['url']):
            if (local['url'] != '/' and local['text'].lower() != 'home') or page_url == local['url']:
                local['classes'] += " active"
        
        new_context = template.context.Context(local)
        return self.nodelist.render(new_context)
        
    
def tested_menu_item(_parser, token):
    """
    The actual template tag.
    """
    error_message = "'menu_item' tag requires at least 2, at most 3 arguments"
    
    try:
        parts = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(error_message)
    
    if not (3 <= len(parts) <= 4):
        raise template.TemplateSyntaxError(error_message)
    
    # parts[0] is the name of the tag.
    return MenuItem('menu/item.html', *parts[1:])

register.tag('menu_item', tested_menu_item)