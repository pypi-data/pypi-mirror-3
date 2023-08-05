registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_257196432 = _loads('(dp1\n.')
    _attrs_257196752 = _loads('(dp1\n.')
    _attrs_257197136 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_257197584 = _loads('(dp1\nVhref\np2\nV${survey/url}\np3\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _attrs_257196560 = _loads('(dp1\nVclass\np2\nVsurveyVersions\np3\ns.')
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
        def _callback_content(econtext, _repeat, _out=_out, _write=_write, _domain=_domain, **_ignored):
            if _repeat:
                repeat.update(_repeat)
            _write(u'\n        ')
            attrs = _attrs_257196432
            u"%(translate)s('header_sector_tool_version_list', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h2>')
            _result = _translate('header_sector_tool_version_list', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'OiRA Tool versions')
            'view/surveys'
            _write(u'</h2>\n        ')
            surveys = _path(econtext['view'], econtext['request'], True, 'surveys')
            'surveys'
            _tmp1 = surveys
            if _tmp1:
                pass
                attrs = _attrs_257196560
                'surveys'
                _write(u'<ul class="surveyVersions">\n            ')
                _tmp1 = _path(surveys, econtext['request'], True)
                survey = None
                (_tmp1, _tmp2, ) = repeat.insert('survey', _tmp1)
                for survey in _tmp1:
                    _tmp2 = (_tmp2 - 1)
                    attrs = _attrs_257196752
                    _write(u'<li>\n                ')
                    attrs = _attrs_257197136
                    _write(u'<label>')
                    attrs = _attrs_257197584
                    'join(value("_path(survey, request, True, \'url\')"),)'
                    _write(u'<a')
                    _tmp3 = _path(survey, econtext['request'], True, 'url')
                    if (_tmp3 is _default):
                        _tmp3 = u'${survey/url}'
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
                    u'survey/title'
                    _write('>')
                    _tmp3 = _path(survey, econtext['request'], True, 'title')
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
                    _write(u'</a></label>\n            </li>')
                    if (_tmp2 == 0):
                        break
                    _write(' ')
                _write(u'\n        </ul>')
            _write(u'\n    ')
            _write('\n')
        u"{'content': _callback_content, 'title': _callback_title}"
        _tmp = {'content': _callback_content, 'title': _callback_title, }
        'context/@@layout/macros/layout'
        _metal.render(_tmp, _out=_out, _write=_write, _domain=_domain, econtext=econtext)
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/surveygroup_view.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
