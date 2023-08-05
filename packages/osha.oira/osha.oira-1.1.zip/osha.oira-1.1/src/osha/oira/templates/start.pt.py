registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_182781840 = _loads('(dp1\nVid\np2\nVsteps\np3\ns.')
    _attrs_164013200 = _loads('(dp1\nVid\np2\nVstep-4\np3\ns.')
    _lookup_tile = _loads('cplonetheme.nuplone.tiles.tales\n_lookup_tile\np1\n.')
    _attrs_181753744 = _loads('(dp1\nVid\np2\nVstep-2\np3\ns.')
    _attrs_186318672 = _loads('(dp1\nVhref\np2\nV${webhelpers/country_url}/account-settings\np3\ns.')
    _attrs_182782672 = _loads('(dp1\nVaction\np2\nV${request/URL}\np3\nsVmethod\np4\nVpost\np5\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_182783952 = _loads('(dp1\n.')
    _attrs_182872080 = _loads('(dp1\n.')
    _attrs_164014416 = _loads('(dp1\nVid\np2\nVstep-5\np3\ns.')
    _attrs_182872464 = _loads('(dp1\n.')
    _attrs_186317520 = _loads('(dp1\n.')
    _attrs_181730128 = _loads('(dp1\nVclass\np2\nVbuttonBar\np3\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_186317648 = _loads('(dp1\nVhref\np2\nV${webhelpers/country_url}/logout\np3\ns.')
    _attrs_186317904 = _loads('(dp1\nVhref\np2\nV${webhelpers/session_overview_url}\np3\ns.')
    _attrs_182873744 = _loads('(dp1\nVclass\np2\nVstart ${webhelpers/extra_css}\np3\ns.')
    _attrs_181754960 = _loads('(dp1\nVhref\np2\nV${context/absolute_url}/start\np3\ns.')
    _attrs_186317968 = _loads('(dp1\n.')
    _attrs_181730320 = _loads('(dp1\nVtype\np2\nVsubmit\np3\nsVclass\np4\nVfloatAfter\np5\ns.')
    _attrs_186317584 = _loads('(dp1\n.')
    _attrs_181731280 = _loads('(dp1\nVid\np2\nVnavigation\np3\ns.')
    _attrs_181731216 = _loads('(dp1\nVhref\np2\nV${webhelpers/session_overview_url}\np3\nsVclass\np4\nVfloatBefore button-medium back\np5\ns.')
    _attrs_186317712 = _loads('(dp1\n.')
    _attrs_181752976 = _loads('(dp1\nVclass\np2\nVactive current\np3\nsVid\np4\nVstep-1\np5\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_182873680 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
    _attrs_181754256 = _loads('(dp1\nVid\np2\nVstep-3\np3\ns.')
    _attrs_186318032 = _loads('(dp1\nVhref\np2\nV${webhelpers/help_url}#preparation\np3\ns.')
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
        u'_default'
        default = _default
        'nocall:request/client'
        client = _path(econtext['request'], econtext['request'], False, 'client')
        'nocall:context/@@webhelpers'
        webhelpers = _path(econtext['context'], econtext['request'], False, '@@webhelpers')
        'nocall:context/@@default_introduction'
        default_introduction = _path(econtext['context'], econtext['request'], False, '@@default_introduction')
        attrs = _attrs_182873680
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml">\n')
        attrs = _attrs_182872080
        _write(u'<head>\n    ')
        attrs = _attrs_182872464
        u"%(translate)s('title_tool', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<title>')
        _result = _translate('title_tool', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'OiRA - Online interactive Risk Assessment')
        'webhelpers/macros/headers'
        _write(u'</title>\n    ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'headers')
        u'{}'
        _tmp = {}
        'webhelpers/macros/headers'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, default_introduction=default_introduction, client=client, _out=_out, _write=_write)
        'webhelpers/macros/css'
        _write(u'\n    ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'css')
        u'{}'
        _tmp = {}
        'webhelpers/macros/css'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, default_introduction=default_introduction, client=client, _out=_out, _write=_write)
        _write(u'\n</head>\n')
        attrs = _attrs_182873744
        'join(u\'start \', value("_path(webhelpers, request, True, \'extra_css\')"))'
        _write(u'<body')
        _tmp1 = ('%s%s' % ('start ', _path(webhelpers, econtext['request'], True, 'extra_css'), ))
        if (_tmp1 is _default):
            _tmp1 = u'start ${webhelpers/extra_css}'
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
        _write(u'>\n    ')
        attrs = _attrs_182783952
        u'context/title'
        _write(u'<h1>')
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
        u"not(_path(view, request, True, 'has_introduction'))"
        _write(u'</h1>\n    ')
        _tmp1 = not _path(econtext['view'], econtext['request'], True, 'has_introduction')
        if _tmp1:
            pass
            'default_introduction/macros/default_introduction'
            _write(u'\n        ')
            _metal = _path(default_introduction, econtext['request'], True, 'macros', 'default_introduction')
            u'{}'
            _tmp = {}
            'default_introduction/macros/default_introduction'
            _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, default_introduction=default_introduction, client=client, _out=_out, _write=_write)
            _write(u'')
        u"u'\\n      Introduction text for this sector.\\n    '"
        _write(u'\n    ')
        _default.value = default = u'\n      Introduction text for this sector.\n    '
        'view/has_introduction'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'has_introduction')
        if _tmp1:
            pass
            'context/introduction'
            _content = _path(econtext['context'], econtext['request'], True, 'introduction')
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
        _write(u'\n\n    ')
        attrs = _attrs_182782672
        'join(value("_path(request, request, True, \'URL\')"),)'
        _write(u'<form method="post"')
        _tmp1 = _path(econtext['request'], econtext['request'], True, 'URL')
        if (_tmp1 is _default):
            _tmp1 = u'${request/URL}'
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
            _write(((' action="' + _tmp1) + '"'))
        _write(u'>\n      ')
        attrs = _attrs_181730128
        _write(u'<p class="buttonBar">\n        ')
        attrs = _attrs_181731216
        'join(value("_path(webhelpers, request, True, \'session_overview_url\')"),)'
        _write(u'<a')
        _tmp1 = _path(webhelpers, econtext['request'], True, 'session_overview_url')
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/session_overview_url}'
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
            _write(((' href="' + _tmp1) + '"'))
        u"%(translate)s('label_previous', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u' class="floatBefore button-medium back">')
        _result = _translate('label_previous', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Previous')
        _write(u'</a>\n        ')
        attrs = _attrs_181730320
        u"%(translate)s('label_start_survey', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<button class="floatAfter" type="submit">')
        _result = _translate('label_start_survey', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Start')
        _write(u'</button>\n      </p>\n    </form>\n    ')
        attrs = _attrs_182781840
        _write(u'<ol id="steps">\n      ')
        attrs = _attrs_181752976
        _write(u'<li class="active current" id="step-1">\n        ')
        attrs = _attrs_181754960
        'join(value("_path(context, request, True, \'absolute_url\')"), u\'/start\')'
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(econtext['context'], econtext['request'], True, 'absolute_url'), '/start', ))
        if (_tmp1 is _default):
            _tmp1 = u'${context/absolute_url}/start'
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
            _write(((' href="' + _tmp1) + '"'))
        u"not(_path(webhelpers, request, True, 'is_iphone'))"
        _write(u'>\n          ')
        _tmp1 = not _path(webhelpers, econtext['request'], True, 'is_iphone')
        if _tmp1:
            pass
            u"%(translate)s('label_preparation', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _result = _translate('label_preparation', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Preparation')
        'webhelpers/is_iphone'
        _write(u'\n          ')
        _tmp1 = _path(webhelpers, econtext['request'], True, 'is_iphone')
        if _tmp1:
            pass
            u"%(translate)s('iphone_label_preparation', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _result = _translate('iphone_label_preparation', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Preparation')
        _write(u'\n        </a>\n      </li>\n      ')
        attrs = _attrs_181753744
        u"not(_path(webhelpers, request, True, 'is_iphone'))"
        _write(u'<li id="step-2">\n        ')
        _tmp1 = not _path(webhelpers, econtext['request'], True, 'is_iphone')
        if _tmp1:
            pass
            u"%(translate)s('label_identification', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _result = _translate('label_identification', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Identification')
        'webhelpers/is_iphone'
        _write(u'\n        ')
        _tmp1 = _path(webhelpers, econtext['request'], True, 'is_iphone')
        if _tmp1:
            pass
            u"%(translate)s('iphone_label_identification', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _result = _translate('iphone_label_identification', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Identification')
        _write(u'\n      </li>\n      ')
        attrs = _attrs_181754256
        u"not(_path(webhelpers, request, True, 'is_iphone'))"
        _write(u'<li id="step-3">\n        ')
        _tmp1 = not _path(webhelpers, econtext['request'], True, 'is_iphone')
        if _tmp1:
            pass
            u"%(translate)s('label_evaluation', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _result = _translate('label_evaluation', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Evaluation')
        'webhelpers/is_iphone'
        _write(u'\n        ')
        _tmp1 = _path(webhelpers, econtext['request'], True, 'is_iphone')
        if _tmp1:
            pass
            u"%(translate)s('iphone_label_evaluation', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _result = _translate('iphone_label_evaluation', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Evaluation')
        _write(u'\n      </li>\n      ')
        attrs = _attrs_164013200
        u"not(_path(webhelpers, request, True, 'is_iphone'))"
        _write(u'<li id="step-4">\n        ')
        _tmp1 = not _path(webhelpers, econtext['request'], True, 'is_iphone')
        if _tmp1:
            pass
            u"%(translate)s('label_action_plan', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _result = _translate('label_action_plan', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Action Plan')
        'webhelpers/is_iphone'
        _write(u'\n        ')
        _tmp1 = _path(webhelpers, econtext['request'], True, 'is_iphone')
        if _tmp1:
            pass
            u"%(translate)s('iphone_label_action_plan', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _result = _translate('iphone_label_action_plan', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Action Plan')
        _write(u'\n      </li>\n      ')
        attrs = _attrs_164014416
        u"not(_path(webhelpers, request, True, 'is_iphone'))"
        _write(u'<li id="step-5">\n        ')
        _tmp1 = not _path(webhelpers, econtext['request'], True, 'is_iphone')
        if _tmp1:
            pass
            u"%(translate)s('label_report', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _result = _translate('label_report', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Report')
        'webhelpers/is_iphone'
        _write(u'\n        ')
        _tmp1 = _path(webhelpers, econtext['request'], True, 'is_iphone')
        if _tmp1:
            pass
            u"%(translate)s('iphone_report', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _result = _translate('iphone_report', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Report')
        _write(u'\n      </li>\n    </ol>\n\n    ')
        attrs = _attrs_181731280
        'webhelpers/macros/homelink'
        _write(u'<ul id="navigation">\n      ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'homelink')
        u'{}'
        _tmp = {}
        'webhelpers/macros/homelink'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, default_introduction=default_introduction, client=client, _out=_out, _write=_write)
        _write(u'\n      ')
        attrs = _attrs_186317520
        _write(u'<li>')
        attrs = _attrs_186317648
        'join(value("_path(webhelpers, request, True, \'country_url\')"), u\'/logout\')'
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(webhelpers, econtext['request'], True, 'country_url'), '/logout', ))
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/country_url}/logout'
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
            _write(((' href="' + _tmp1) + '"'))
        u"%(translate)s('navigation_logout', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write('>')
        _result = _translate('navigation_logout', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Logout')
        _write(u'</a></li>\n      ')
        attrs = _attrs_186317584
        _write(u'<li>')
        attrs = _attrs_186317904
        'join(value("_path(webhelpers, request, True, \'session_overview_url\')"),)'
        _write(u'<a')
        _tmp1 = _path(webhelpers, econtext['request'], True, 'session_overview_url')
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/session_overview_url}'
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
            _write(((' href="' + _tmp1) + '"'))
        u"%(translate)s('navigation_surveys', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write('>')
        _result = _translate('navigation_surveys', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Sessions')
        _write(u'</a></li>\n      ')
        attrs = _attrs_186317712
        _write(u'<li>')
        attrs = _attrs_186318032
        'join(value("_path(webhelpers, request, True, \'help_url\')"), u\'#preparation\')'
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(webhelpers, econtext['request'], True, 'help_url'), '#preparation', ))
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/help_url}#preparation'
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
            _write(((' href="' + _tmp1) + '"'))
        u"%(translate)s('navigation_help', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write('>')
        _result = _translate('navigation_help', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Help')
        _write(u'</a></li>\n      ')
        attrs = _attrs_186317968
        _write(u'<li>')
        attrs = _attrs_186318672
        'join(value("_path(webhelpers, request, True, \'country_url\')"), u\'/account-settings\')'
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(webhelpers, econtext['request'], True, 'country_url'), '/account-settings', ))
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/country_url}/account-settings'
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
            _write(((' href="' + _tmp1) + '"'))
        u"%(translate)s('navigation_settings', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write('>')
        _result = _translate('navigation_settings', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Settings')
        'webhelpers/macros/appendix'
        _write(u'</a></li>\n    </ul>\n    ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'appendix')
        u'{}'
        _tmp = {}
        'webhelpers/macros/appendix'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, default_introduction=default_introduction, client=client, _out=_out, _write=_write)
        'webhelpers/macros/javascript'
        _write(u'\n    ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'javascript')
        u'{}'
        _tmp = {}
        'webhelpers/macros/javascript'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, default_introduction=default_introduction, client=client, _out=_out, _write=_write)
        u"''"
        _write(u'\n    ')
        _default.value = default = ''
        'client-analytics'
        _content = _lookup_tile(econtext['context'], econtext['request'], 'client-analytics')
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
        _write(u'\n  </body>\n</html>')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/start.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
