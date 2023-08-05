registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_255692112 = _loads("(dp1\nVclass\np2\nV${python:'sortable' if can_edit and len(children)>1 else None}\np3\ns.")
    _attrs_255688784 = _loads('(dp1\n.')
    _attrs_245851216 = _loads('(dp1\nVsrc\np2\nV++resource++osha.oira.images/folder_icon.png\np3\ns.')
    _attrs_255688848 = _loads('(dp1\nVid\np2\nVchild-${child/id}\np3\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_255689488 = _loads('(dp1\n.')
    _attrs_255690448 = _loads('(dp1\n.')
    _attrs_255692304 = _loads('(dp1\n.')
    _attrs_255689360 = _loads('(dp1\nVhref\np2\nV${child/url}\np3\ns.')
    _attrs_255691024 = _loads('(dp1\n.')
    _attrs_255691472 = _loads('(dp1\n.')
    _attrs_255691792 = _loads('(dp1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_255689808 = _loads('(dp1\nVsrc\np2\nV++resource++osha.oira.images/question.png\np3\ns.')
    _attrs_255689616 = _loads('(dp1\n.')
    _attrs_255692752 = _loads('(dp1\n.')
    _lookup_tile = _loads('cplonetheme.nuplone.tiles.tales\n_lookup_tile\np1\n.')
    _attrs_255691600 = _loads('(dp1\n.')
    _attrs_255690960 = _loads('(dp1\nVclass\np2\nVgrid span-9\np3\ns.')
    _attrs_255692176 = _loads('(dp1\n.')
    _attrs_255689552 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_255691856 = _loads('(dp1\n.')
    _attrs_255692688 = _loads('(dp1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
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
        _write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        _tmp_domain0 = _domain
        u"'euphorie'"
        _domain = 'euphorie'
        'context/@@layout/macros/layout'
        _metal = _path(econtext['context'], econtext['request'], True, '@@layout', 'macros', 'layout')
        def _callback_title(econtext, _repeat, _out=_out, _write=_write, _domain=_domain, **_ignored):
            if _repeat:
                repeat.update(_repeat)
            u'view/group/title'
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'group', 'title')
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
                    _tmp = unicode(str(_tmp), 'UTF-8')
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
            _write('\n')
        def _callback_buttonbar(econtext, _repeat, _out=_out, _write=_write, _domain=_domain, **_ignored):
            if _repeat:
                repeat.update(_repeat)
            u"''"
            _default.value = default = ''
            'euphorie.addbar'
            _content = _lookup_tile(econtext['context'], econtext['request'], 'euphorie.addbar')
            u'_content'
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
                    _tmp = unicode(str(_tmp), 'UTF-8')
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
            _write('\n')
        def _callback_content(econtext, _repeat, _out=_out, _write=_write, _domain=_domain, **_ignored):
            if _repeat:
                repeat.update(_repeat)
            "tools.checkPermission('Modify portal content')"
            can_edit = _lookup_attr(econtext['tools'], 'checkPermission')('Modify portal content')
            _write(u'\n      ')
            attrs = _attrs_255692304
            u"%(translate)s('header_information', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h2>')
            _result = _translate('header_information', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Information')
            _write(u'</h2>\n\n      ')
            attrs = _attrs_255690960
            _write(u'<dl class="grid span-9">\n        ')
            attrs = _attrs_255691856
            u"%(translate)s('label_evaluation_phase', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<dt>')
            _result = _translate('label_evaluation_phase', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Evaluation phase')
            'context/evaluation_optional'
            _write(u'</dt>\n        ')
            _tmp1 = _path(econtext['context'], econtext['request'], True, 'evaluation_optional')
            if _tmp1:
                pass
                attrs = _attrs_255691792
                u"%(translate)s('optional', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<dd>')
                _result = _translate('optional', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Optional')
                _write(u'</dd>')
            u"not(_path(context, request, True, 'evaluation_optional'))"
            _write(u'\n        ')
            _tmp1 = not _path(econtext['context'], econtext['request'], True, 'evaluation_optional')
            if _tmp1:
                pass
                attrs = _attrs_255691024
                u"%(translate)s('mandatory', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<dd>')
                _result = _translate('mandatory', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Mandatory')
                _write(u'</dd>')
            _write(u'\n        ')
            attrs = _attrs_255692688
            u"%(translate)s('label_classification_code', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<dt>')
            _result = _translate('label_classification_code', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Classification code')
            'context/classification_code'
            _write(u'</dt>\n        ')
            _tmp1 = _path(econtext['context'], econtext['request'], True, 'classification_code')
            if _tmp1:
                pass
                attrs = _attrs_255691472
                u'context/classification_code'
                _write(u'<dd>')
                _tmp1 = _path(econtext['context'], econtext['request'], True, 'classification_code')
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
                        _tmp = unicode(str(_tmp), 'UTF-8')
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
                _write(u'</dd>')
            u"not(_path(context, request, True, 'classification_code'))"
            _write(u'\n        ')
            _tmp1 = not _path(econtext['context'], econtext['request'], True, 'classification_code')
            if _tmp1:
                pass
                attrs = _attrs_255689488
                _write(u'<dd>')
                attrs = _attrs_255689616
                u"%(translate)s('not_set', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<em>')
                _result = _translate('not_set', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Not set')
                _write(u'</em></dd>')
            _write(u'\n        ')
            attrs = _attrs_255689552
            u"%(translate)s('label_language', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<dt>')
            _result = _translate('label_language', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Language')
            'context/language'
            _write(u'</dt>\n        ')
            _tmp1 = _path(econtext['context'], econtext['request'], True, 'language')
            if _tmp1:
                pass
                attrs = _attrs_255688784
                u'tools.languageName(context.language, context.language)'
                _write(u'<dd>')
                _tmp1 = _lookup_attr(econtext['tools'], 'languageName')(_lookup_attr(econtext['context'], 'language'), _lookup_attr(econtext['context'], 'language'))
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
                        _tmp = unicode(str(_tmp), 'UTF-8')
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
                _write(u'</dd>')
            u"not(_path(context, request, True, 'language'))"
            _write(u'\n        ')
            _tmp1 = not _path(econtext['context'], econtext['request'], True, 'language')
            if _tmp1:
                pass
                attrs = _attrs_255690448
                _write(u'<dd>')
                attrs = _attrs_255691600
                u"%(translate)s('not_set', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<em>')
                _result = _translate('not_set', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Not set')
                _write(u'</em></dd>')
            'view/modules_and_profile_questions'
            _write(u'\n      </dl>\n\n    ')
            children = _path(econtext['view'], econtext['request'], True, 'modules_and_profile_questions')
            _write(u'\n      ')
            attrs = _attrs_255692176
            u"%(translate)s('header_modules_and_profile_questions', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h2>')
            _result = _translate('header_modules_and_profile_questions', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Modules and Profile Questions')
            u'not(children)'
            _write(u'</h2>\n\n      ')
            _tmp1 = not children
            if _tmp1:
                pass
                attrs = _attrs_255692752
                u"%(translate)s('no_modules', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<p>')
                _result = _translate('no_modules', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'This OiRA Tool has no modules.')
                _write(u'</p>')
            'children'
            _write(u'\n\n      ')
            _tmp1 = children
            if _tmp1:
                pass
                'children'
                _write(u'\n        ')
                _tmp1 = children
                if _tmp1:
                    pass
                    attrs = _attrs_255692112
                    'join(value("\'sortable\' if can_edit and len(children)>1 else None"),)'
                    _write(u'<ol')
                    _tmp1 = ('sortable' if (can_edit and (len(children) > 1)) else None)
                    if (_tmp1 is _default):
                        _tmp1 = u"${python:'sortable' if can_edit and len(children)>1 else None}"
                    if ((_tmp1 is not None) and (_tmp1 is not False)):
                        if (_tmp1.__class__ not in (str, unicode, int, float, )):
                            _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
                        else:
                            if not isinstance(_tmp1, unicode):
                                _tmp1 = unicode(str(_tmp1), 'UTF-8')
                        if ('&' in _tmp1):
                            if (';' in _tmp1):
                                _tmp1 = _re_amp.sub('&amp;', _tmp1)
                            else:
                                _tmp1 = _tmp1.replace('&', '&amp;')
                        if ('<' in _tmp1):
                            _tmp1 = _tmp1.replace('<', '&lt;')
                        if ('>' in _tmp1):
                            _tmp1 = _tmp1.replace('>', '&gt;')
                        if ('"' in _tmp1):
                            _tmp1 = _tmp1.replace('"', '&quot;')
                        _write(((' class="' + _tmp1) + '"'))
                    'children'
                    _write(u'>\n            ')
                    _tmp1 = _path(children, econtext['request'], True)
                    child = None
                    (_tmp1, _tmp2, ) = repeat.insert('child', _tmp1)
                    for child in _tmp1:
                        _tmp2 = (_tmp2 - 1)
                        attrs = _attrs_255688848
                        'join(u\'child-\', value("_path(child, request, True, \'id\')"))'
                        _write(u'<li')
                        _tmp3 = ('%s%s' % ('child-', _path(child, econtext['request'], True, 'id'), ))
                        if (_tmp3 is _default):
                            _tmp3 = u'child-${child/id}'
                        if ((_tmp3 is not None) and (_tmp3 is not False)):
                            if (_tmp3.__class__ not in (str, unicode, int, float, )):
                                _tmp3 = unicode(_translate(_tmp3, domain=_domain, mapping=None, target_language=target_language, default=None))
                            else:
                                if not isinstance(_tmp3, unicode):
                                    _tmp3 = unicode(str(_tmp3), 'UTF-8')
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
                            _write(((' id="' + _tmp3) + '"'))
                        u"not(_path(child, request, True, 'is_profile_question'))"
                        _write(u'>\n                ')
                        _tmp3 = not _path(child, econtext['request'], True, 'is_profile_question')
                        if _tmp3:
                            pass
                            attrs = _attrs_245851216
                            _write(u'<img src="++resource++osha.oira.images/folder_icon.png" />')
                        'child/is_profile_question'
                        _write(u'\n                ')
                        _tmp3 = _path(child, econtext['request'], True, 'is_profile_question')
                        if _tmp3:
                            pass
                            attrs = _attrs_255689808
                            _write(u'<img src="++resource++osha.oira.images/question.png" />')
                        _write(u'\n                ')
                        attrs = _attrs_255689360
                        'join(value("_path(child, request, True, \'url\')"),)'
                        _write(u'<a')
                        _tmp3 = _path(child, econtext['request'], True, 'url')
                        if (_tmp3 is _default):
                            _tmp3 = u'${child/url}'
                        if ((_tmp3 is not None) and (_tmp3 is not False)):
                            if (_tmp3.__class__ not in (str, unicode, int, float, )):
                                _tmp3 = unicode(_translate(_tmp3, domain=_domain, mapping=None, target_language=target_language, default=None))
                            else:
                                if not isinstance(_tmp3, unicode):
                                    _tmp3 = unicode(str(_tmp3), 'UTF-8')
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
                            _write(((' href="' + _tmp3) + '"'))
                        u'child/title'
                        _write('>')
                        _tmp3 = _path(child, econtext['request'], True, 'title')
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
                                _tmp = unicode(str(_tmp), 'UTF-8')
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
                        _write(u'</a>\n            </li>')
                        if (_tmp2 == 0):
                            break
                        _write(' ')
                    _write(u'\n        </ol>')
                _write(u'\n      ')
            _write(u'')
            _write('\n')
        u"{'content': _callback_content, 'buttonbar': _callback_buttonbar, 'title': _callback_title}"
        _tmp = {'content': _callback_content, 'buttonbar': _callback_buttonbar, 'title': _callback_title, }
        'context/@@layout/macros/layout'
        _metal.render(_tmp, _out=_out, _write=_write, _domain=_domain, econtext=econtext)
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/survey_view.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
