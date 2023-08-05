registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _attrs_310455056 = _loads('(dp1\nVclass\np2\nVintroduction\np3\ns.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_310453904 = _loads("(dp1\nVclass\np2\nV${python:'sortable' if can_edit and len(view.modules)>1 else None}\np3\ns.")
    _attrs_310452368 = _loads('(dp1\nVid\np2\nVchild-${risk/id}\np3\ns.')
    _attrs_304034704 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_310452432 = _loads('(dp1\nVid\np2\nVchild-${module/id}\np3\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_310454800 = _loads('(dp1\n.')
    _lookup_tile = _loads('cplonetheme.nuplone.tiles.tales\n_lookup_tile\np1\n.')
    _attrs_310454480 = _loads('(dp1\n.')
    _attrs_310456272 = _loads('(dp1\n.')
    _attrs_310455760 = _loads('(dp1\n.')
    _attrs_310452688 = _loads('(dp1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_310455696 = _loads('(dp1\n.')
    _attrs_310456016 = _loads("(dp1\nVclass\np2\nV${python:'sortable' if can_edit and len(view.risks)>1 else None}\np3\ns.")
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
            u'context/title'
            _tmp1 = _path(econtext['context'], econtext['request'], True, 'title')
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
            attrs = _attrs_310455056
            u"u'Van belang is dat de spuitlans de juiste lengte heeft om rechtopstaand te werken. Een gebogen spuitlans geeft een hogere polsbelasting en wordt daarom afgeraden.'"
            _write(u'<div class="introduction">\n        ')
            _default.value = default = u'Van belang is dat de spuitlans de juiste lengte heeft om rechtopstaand te werken. Een gebogen spuitlans geeft een hogere polsbelasting en wordt daarom afgeraden.'
            'context/description'
            _content = _path(econtext['context'], econtext['request'], True, 'description')
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
                _write(_tmp)
            _write(u'\n      </div>\n\n      ')
            attrs = _attrs_310454480
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
            "context.type=='optional'"
            _write(u'</h2>\n      ')
            _tmp1 = (_lookup_attr(econtext['context'], 'type') == 'optional')
            if _tmp1:
                pass
                attrs = _attrs_310456272
                u"%(translate)s('profilequestion_type_optional', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<p>')
                _result = _translate('profilequestion_type_optional', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'This is an optional profile item.')
                _write(u'</p>')
            "context.type=='repeat'"
            _write(u'\n      ')
            _tmp1 = (_lookup_attr(econtext['context'], 'type') == 'repeat')
            if _tmp1:
                pass
                attrs = _attrs_310455696
                u"%(translate)s('profilequestion_type_repeat', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<p>')
                _result = _translate('profilequestion_type_repeat', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'This is a repeatable profile item.')
                _write(u'</p>')
            'view.modules'
            _write(u'\n\n      ')
            _tmp1 = _lookup_attr(econtext['view'], 'modules')
            if _tmp1:
                pass
                _write(u'\n        ')
                attrs = _attrs_310454800
                u"%(translate)s('header_modules', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<h2>')
                _result = _translate('header_modules', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Modules')
                'view.modules'
                _write(u'</h2>\n        ')
                _tmp1 = _lookup_attr(econtext['view'], 'modules')
                if _tmp1:
                    pass
                    attrs = _attrs_310453904
                    'join(value("\'sortable\' if can_edit and len(view.modules)>1 else None"),)'
                    _write(u'<ol')
                    _tmp1 = ('sortable' if (can_edit and (len(_lookup_attr(econtext['view'], 'modules')) > 1)) else None)
                    if (_tmp1 is _default):
                        _tmp1 = u"${python:'sortable' if can_edit and len(view.modules)>1 else None}"
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
                    'view/modules'
                    _write(u'>\n          ')
                    _tmp1 = _path(econtext['view'], econtext['request'], True, 'modules')
                    module = None
                    (_tmp1, _tmp2, ) = repeat.insert('module', _tmp1)
                    for module in _tmp1:
                        _tmp2 = (_tmp2 - 1)
                        attrs = _attrs_310452432
                        'join(u\'child-\', value("_path(module, request, True, \'id\')"))'
                        _write(u'<li')
                        _tmp3 = ('%s%s' % ('child-', _path(module, econtext['request'], True, 'id'), ))
                        if (_tmp3 is _default):
                            _tmp3 = u'child-${module/id}'
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
                        u"u'Module title'"
                        _write('>')
                        _default.value = default = u'Module title'
                        'module/title'
                        _content = _path(module, econtext['request'], True, 'title')
                        attrs = _attrs_310452688
                        'module/url'
                        _write(u'<a')
                        _tmp3 = _path(module, econtext['request'], True, 'url')
                        if (_tmp3 is _default):
                            _tmp3 = None
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
                        _write(u'</a></li>')
                        if (_tmp2 == 0):
                            break
                        _write(' ')
                    _write(u'\n        </ol>')
                _write(u'\n      ')
            'view.risks'
            _write(u'\n\n      ')
            _tmp1 = _lookup_attr(econtext['view'], 'risks')
            if _tmp1:
                pass
                _write(u'\n        ')
                attrs = _attrs_310455760
                u"%(translate)s('header_risks', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<h2>')
                _result = _translate('header_risks', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Risks')
                'view.risks'
                _write(u'</h2>\n        ')
                _tmp1 = _lookup_attr(econtext['view'], 'risks')
                if _tmp1:
                    pass
                    attrs = _attrs_310456016
                    'join(value("\'sortable\' if can_edit and len(view.risks)>1 else None"),)'
                    _write(u'<ol')
                    _tmp1 = ('sortable' if (can_edit and (len(_lookup_attr(econtext['view'], 'risks')) > 1)) else None)
                    if (_tmp1 is _default):
                        _tmp1 = u"${python:'sortable' if can_edit and len(view.risks)>1 else None}"
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
                    'view/risks'
                    _write(u'>\n          ')
                    _tmp1 = _path(econtext['view'], econtext['request'], True, 'risks')
                    risk = None
                    (_tmp1, _tmp2, ) = repeat.insert('risk', _tmp1)
                    for risk in _tmp1:
                        _tmp2 = (_tmp2 - 1)
                        attrs = _attrs_310452368
                        'join(u\'child-\', value("_path(risk, request, True, \'id\')"))'
                        _write(u'<li')
                        _tmp3 = ('%s%s' % ('child-', _path(risk, econtext['request'], True, 'id'), ))
                        if (_tmp3 is _default):
                            _tmp3 = u'child-${risk/id}'
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
                        u"u'Risk title'"
                        _write('>')
                        _default.value = default = u'Risk title'
                        'risk/title'
                        _content = _path(risk, econtext['request'], True, 'title')
                        attrs = _attrs_304034704
                        'risk/url'
                        _write(u'<a')
                        _tmp3 = _path(risk, econtext['request'], True, 'url')
                        if (_tmp3 is _default):
                            _tmp3 = None
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
                        _write(u'</a></li>')
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

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/profilequestion_view.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
