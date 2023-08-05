# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1326343307.95461
_template_filename='/mnt/md0/MyWork/MyProjects/PyCK/pyck/forms/templates/form_as_p.mako'
_template_uri='form_as_p.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='ascii'
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        errors_position = context.get('errors_position', UNDEFINED)
        labels_position = context.get('labels_position', UNDEFINED)
        form = context.get('form', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        if form._use_csrf_protection:
            # SOURCE LINE 2
            __M_writer(u'<input type="hidden" name="csrf_token" value="')
            __M_writer(unicode(form._csrf_token))
            __M_writer(u'" />\n')
            pass
        # SOURCE LINE 4
        if '_csrf' in form.errors:
            # SOURCE LINE 5
            __M_writer(u'<div class="errors">')
            __M_writer(unicode(form.errors['_csrf'][0]))
            __M_writer(u'</div><br />\n')
            pass
        # SOURCE LINE 7
        for field in form:
            # SOURCE LINE 8

            field_errors = ''
            if field.errors:
                field_errors = '<span class="errors">'
                for e in field.errors:
                    field_errors += e + ', '
                
                field_errors = field_errors[:-2] + '</span>'
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['field_errors','e'] if __M_key in __M_locals_builtin_stored]))
            # SOURCE LINE 16
            __M_writer(u'\n<p>\n')
            # SOURCE LINE 18
            if 'top' == labels_position:
                # SOURCE LINE 19
                __M_writer(u'<label for="')
                __M_writer(unicode(field.name))
                __M_writer(u'">')
                __M_writer(unicode(field.label))
                __M_writer(u'</label><br /> ')
                pass
            # SOURCE LINE 22
            if field_errors and 'top'==errors_position:
                # SOURCE LINE 23
                __M_writer(unicode(field_errors))
                __M_writer(u'<br /> ')
                pass
            # SOURCE LINE 26
            if 'left' == labels_position:
                # SOURCE LINE 27
                __M_writer(u'<label for="')
                __M_writer(unicode(field.name))
                __M_writer(u'">')
                __M_writer(unicode(field.label))
                __M_writer(u'</label> ')
                pass
            # SOURCE LINE 30
            if field_errors and 'left'==errors_position:
                # SOURCE LINE 31
                __M_writer(unicode(field_errors))
                __M_writer(u' ')
                pass
            # SOURCE LINE 34
            __M_writer(unicode(field))
            __M_writer(u' ')
            # SOURCE LINE 35
            if 'bottom' == labels_position:
                # SOURCE LINE 36
                __M_writer(u'<label for="')
                __M_writer(unicode(field.name))
                __M_writer(u'">')
                __M_writer(unicode(field.label))
                __M_writer(u'</label> ')
                pass
            # SOURCE LINE 39
            if field_errors and 'bottom'==errors_position:
                # SOURCE LINE 40
                __M_writer(u'<br />')
                __M_writer(unicode(field_errors))
                __M_writer(u' ')
                pass
            # SOURCE LINE 43
            if 'right' == labels_position:
                # SOURCE LINE 44
                __M_writer(u'<label for="')
                __M_writer(unicode(field.name))
                __M_writer(u'">')
                __M_writer(unicode(field.label))
                __M_writer(u'</label> ')
                pass
            # SOURCE LINE 47
            if field_errors and 'right'==errors_position:
                # SOURCE LINE 48
                __M_writer(unicode(field_errors))
                __M_writer(u' ')
                pass
            # SOURCE LINE 50
            __M_writer(u'</p>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


