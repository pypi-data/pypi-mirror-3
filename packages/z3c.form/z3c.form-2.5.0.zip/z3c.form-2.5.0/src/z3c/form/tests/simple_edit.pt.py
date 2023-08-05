registry = dict(version='8.3.2.1')
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_39532336 = _loads('(dp1\nVclass\np2\nVaction\np3\ns.')
    _attrs_39464048 = _loads('(dp1\nVaction\np2\nV.\ns.')
    _attrs_39532400 = _loads('(dp1\nVfor\np2\nV\ns.')
    _attrs_39532048 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
    _attrs_39532240 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_39463984 = _loads('(dp1\n.')
    _attrs_39532304 = _loads('(dp1\nVclass\np2\nVrow\np3\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_39532176 = _loads('(dp1\n.')
    _attrs_39532368 = _loads('(dp1\n.')
    _attrs_39464304 = _loads('(dp1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _path = _loads("ccopy_reg\n_reconstructor\np1\n(cz3c.pt.expressions\nZopeTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n(dp5\nS'proxify'\np6\ncz3c.pt.expressions\nidentity\np7\nsb.")
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u'_init_stream()'
        (_out, _write, ) = _init_stream()
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        _write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
        attrs = _attrs_39532048
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml">       \n  ')
        attrs = _attrs_39532176
        u"''"
        _write(u'<body>\n    ')
        _default.value = default = ''
        u'view/status'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'status')
        if _tmp1:
            pass
            u'view/status'
            _content = _path(econtext['view'], econtext['request'], True, 'status')
            attrs = _attrs_39532240
            u'_content'
            _write(u'<i>')
            _tmp1 = _content
            _tmp = _tmp1
            if (_tmp.__class__ not in (str, unicode, int, float, )):
                try:
                    _tmp = _tmp.__html__
                except:
                    _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
                else:
                    _tmp = _tmp()
                    _write(_tmp)
                    _tmp = None
            if (_tmp is not None):
                if not isinstance(_tmp, unicode):
                    _tmp = str(_tmp)
                if ('&' in _tmp):
                    if (';' in _tmp):
                        _tmp = _re_amp.sub('&amp;', _tmp)
                    else:
                        _tmp = _tmp.replace('&', '&amp;')
                if ('<' in _tmp):
                    _tmp = _tmp.replace('<', '&lt;')
                if ('>' in _tmp):
                    _tmp = _tmp.replace('>', '&gt;')
                _write(_tmp)
            _write(u'</i>')
        u'view/widgets/errors'
        _write(u'\n    ')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'widgets', 'errors')
        if _tmp1:
            pass
            attrs = _attrs_39464304
            u'view/widgets/errors'
            _write(u'<ul>\n      ')
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'widgets', 'errors')
            error = None
            (_tmp1, _tmp2, ) = repeat.insert('error', _tmp1)
            for error in _tmp1:
                _tmp2 = (_tmp2 - 1)
                attrs = _attrs_39463984
                u'error/widget'
                _write(u'<li>\n        ')
                _tmp3 = _path(error, econtext['request'], True, 'widget')
                if _tmp3:
                    pass
                    u"''"
                    _write(u'')
                    _default.value = default = ''
                    u'error/widget/label'
                    _content = _path(error, econtext['request'], True, 'widget', 'label')
                    u'_content'
                    _tmp3 = _content
                    _tmp = _tmp3
                    if (_tmp.__class__ not in (str, unicode, int, float, )):
                        try:
                            _tmp = _tmp.__html__
                        except:
                            _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
                        else:
                            _tmp = _tmp()
                            _write(_tmp)
                            _tmp = None
                    if (_tmp is not None):
                        if not isinstance(_tmp, unicode):
                            _tmp = str(_tmp)
                        if ('&' in _tmp):
                            if (';' in _tmp):
                                _tmp = _re_amp.sub('&amp;', _tmp)
                            else:
                                _tmp = _tmp.replace('&', '&amp;')
                        if ('<' in _tmp):
                            _tmp = _tmp.replace('<', '&lt;')
                        if ('>' in _tmp):
                            _tmp = _tmp.replace('>', '&gt;')
                        _write(_tmp)
                    _write(u':')
                u"''"
                _write(u'\n        ')
                _default.value = default = ''
                u'error/render'
                _content = _path(error, econtext['request'], True, 'render')
                u'_content'
                _tmp3 = _content
                _tmp = _tmp3
                if (_tmp.__class__ not in (str, unicode, int, float, )):
                    try:
                        _tmp = _tmp.__html__
                    except:
                        _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
                    else:
                        _tmp = _tmp()
                        _write(_tmp)
                        _tmp = None
                if (_tmp is not None):
                    if not isinstance(_tmp, unicode):
                        _tmp = str(_tmp)
                    _write(_tmp)
                _write(u'\n      </li>')
                if (_tmp2 == 0):
                    break
                _write(' ')
            _write(u'\n    </ul>')
        _write(u'\n    ')
        attrs = _attrs_39464048
        u'view/widgets/values'
        _write(u'<form action=".">\n      ')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'widgets', 'values')
        widget = None
        (_tmp1, _tmp2, ) = repeat.insert('widget', _tmp1)
        for widget in _tmp1:
            _tmp2 = (_tmp2 - 1)
            attrs = _attrs_39532304
            u"''"
            _write(u'<div class="row">\n        ')
            _default.value = default = ''
            u'widget/error'
            _tmp3 = _path(widget, econtext['request'], True, 'error')
            if _tmp3:
                pass
                u'widget/error/render'
                _content = _path(widget, econtext['request'], True, 'error', 'render')
                attrs = _attrs_39532368
                u'_content'
                _write(u'<b>')
                _tmp3 = _content
                _tmp = _tmp3
                if (_tmp.__class__ not in (str, unicode, int, float, )):
                    try:
                        _tmp = _tmp.__html__
                    except:
                        _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
                    else:
                        _tmp = _tmp()
                        _write(_tmp)
                        _tmp = None
                if (_tmp is not None):
                    if not isinstance(_tmp, unicode):
                        _tmp = str(_tmp)
                    _write(_tmp)
                _write(u'</b>')
            u"''"
            _default.value = default = ''
            u'widget/label'
            _content = _path(widget, econtext['request'], True, 'label')
            attrs = _attrs_39532400
            u'widget/id'
            _write(u'<label')
            _tmp3 = _path(widget, econtext['request'], True, 'id')
            if (_tmp3 is _default):
                _tmp3 = u''
            if ((_tmp3 is not None) and (_tmp3 is not False)):
                if (_tmp3.__class__ not in (str, unicode, int, float, )):
                    _tmp3 = unicode(_translate(_tmp3, domain=_domain, mapping=None, target_language=target_language, default=None))
                else:
                    if not isinstance(_tmp3, unicode):
                        _tmp3 = str(_tmp3)
                if ('&' in _tmp3):
                    if (';' in _tmp3):
                        _tmp3 = _re_amp.sub('&amp;', _tmp3)
                    else:
                        _tmp3 = _tmp3.replace('&', '&amp;')
                if ('<' in _tmp3):
                    _tmp3 = _tmp3.replace('<', '&lt;')
                if ('>' in _tmp3):
                    _tmp3 = _tmp3.replace('>', '&gt;')
                if ('"' in _tmp3):
                    _tmp3 = _tmp3.replace('"', '&quot;')
                _write(((' for="' + _tmp3) + '"'))
            u'_content'
            _write('>')
            _tmp3 = _content
            _tmp = _tmp3
            if (_tmp.__class__ not in (str, unicode, int, float, )):
                try:
                    _tmp = _tmp.__html__
                except:
                    _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
                else:
                    _tmp = _tmp()
                    _write(_tmp)
                    _tmp = None
            if (_tmp is not None):
                if not isinstance(_tmp, unicode):
                    _tmp = str(_tmp)
                if ('&' in _tmp):
                    if (';' in _tmp):
                        _tmp = _re_amp.sub('&amp;', _tmp)
                    else:
                        _tmp = _tmp.replace('&', '&amp;')
                if ('<' in _tmp):
                    _tmp = _tmp.replace('<', '&lt;')
                if ('>' in _tmp):
                    _tmp = _tmp.replace('>', '&gt;')
                _write(_tmp)
            u"''"
            _write(u'</label>\n        ')
            _default.value = default = ''
            u'widget/render'
            _content = _path(widget, econtext['request'], True, 'render')
            u'_content'
            _tmp3 = _content
            _tmp = _tmp3
            if (_tmp.__class__ not in (str, unicode, int, float, )):
                try:
                    _tmp = _tmp.__html__
                except:
                    _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
                else:
                    _tmp = _tmp()
                    _write(_tmp)
                    _tmp = None
            if (_tmp is not None):
                if not isinstance(_tmp, unicode):
                    _tmp = str(_tmp)
                _write(_tmp)
            _write(u'</div>')
            if (_tmp2 == 0):
                break
            _write(' ')
        u'view/actions/values'
        _write(u'\n      ')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'actions', 'values')
        action = None
        (_tmp1, _tmp2, ) = repeat.insert('action', _tmp1)
        for action in _tmp1:
            _tmp2 = (_tmp2 - 1)
            attrs = _attrs_39532336
            u"''"
            _write(u'<div class="action">\n        ')
            _default.value = default = ''
            u'action/render'
            _content = _path(action, econtext['request'], True, 'render')
            u'_content'
            _tmp3 = _content
            _tmp = _tmp3
            if (_tmp.__class__ not in (str, unicode, int, float, )):
                try:
                    _tmp = _tmp.__html__
                except:
                    _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
                else:
                    _tmp = _tmp()
                    _write(_tmp)
                    _tmp = None
            if (_tmp is not None):
                if not isinstance(_tmp, unicode):
                    _tmp = str(_tmp)
                _write(_tmp)
            _write(u'</div>')
            if (_tmp2 == 0):
                break
            _write(' ')
        _write(u'\n    </form>\n  </body>\n</html>')
        return _out.getvalue()
    return render

__filename__ = 'd:\\eggdev\\source\\z3c\\z3c.form\\trunk\\src\\z3c\\form\\tests\\simple_edit.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
