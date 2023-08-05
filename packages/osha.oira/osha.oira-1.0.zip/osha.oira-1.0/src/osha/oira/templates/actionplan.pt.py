registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _attrs_140793680 = _loads('(dp1\n.')
    _attrs_161507408 = _loads('(dp1\nVhref\np2\nV${webhelpers/session_overview_url}\np3\ns.')
    _attrs_140792464 = _loads('(dp1\n.')
    _attrs_140792400 = _loads('(dp1\nVhref\np2\nV${survey_url}/start\np3\ns.')
    _attrs_140794640 = _loads('(dp1\nVid\np2\nVstep-5\np3\ns.')
    _attrs_140795472 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
    _attrs_161507856 = _loads('(dp1\nVhref\np2\nV${webhelpers/country_url}/logout\np3\ns.')
    _attrs_161506448 = _loads('(dp1\n.')
    _attrs_140794192 = _loads('(dp1\n.')
    _attrs_140794960 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_140793488 = _loads('(dp1\nVclass\np2\nVcomplete\np3\nsVid\np4\nVstep-1\np5\ns.')
    _attrs_161509264 = _loads('(dp1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _attrs_140793744 = _loads('(dp1\nVid\np2\nVsteps\np3\ns.')
    _attrs_140794576 = _loads('(dp1\n.')
    _attrs_140793104 = _loads('(dp1\nVclass\np2\nVbuttonBar\np3\ns.')
    _attrs_140793616 = _loads('(dp1\nVclass\np2\nVcomplete\np3\nsVid\np4\nVstep-3\np5\ns.')
    _attrs_140795600 = _loads('(dp1\nVhref\np2\nV${view/next_url}\np3\nsVclass\np4\nVbutton-medium\np5\ns.')
    _attrs_140794832 = _loads('(dp1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_130619088 = _loads('(dp1\n.')
    _attrs_140795728 = _loads('(dp1\nVhref\np2\nV${survey_url}/identification\np3\ns.')
    _attrs_140795280 = _loads('(dp1\n.')
    _attrs_140793936 = _loads('(dp1\n.')
    _attrs_140793872 = _loads('(dp1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_140792592 = _loads('(dp1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _attrs_140792080 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_161508048 = _loads('(dp1\n.')
    _attrs_140794704 = _loads('(dp1\n.')
    _attrs_140792208 = _loads('(dp1\nVclass\np2\nVactionplan ${webhelpers/extra_css}\np3\ns.')
    _attrs_130621264 = _loads('(dp1\nVhref\np2\nV${survey_url}/actionplan\np3\ns.')
    _attrs_161505552 = _loads('(dp1\n.')
    _attrs_140792912 = _loads('(dp1\nVclass\np2\nVcomplete\np3\nsVid\np4\nVstep-2\np5\ns.')
    _attrs_140792272 = _loads('(dp1\nVhref\np2\nV${survey_url}/evaluation\np3\ns.')
    _attrs_161507536 = _loads('(dp1\nVhref\np2\nV${webhelpers/country_url}/account-settings\np3\ns.')
    _attrs_140793360 = _loads('(dp1\nVclass\np2\nVactive current\np3\nsVid\np4\nVstep-4\np5\ns.')
    _attrs_140794256 = _loads('(dp1\n.')
    _attrs_140793808 = _loads('(dp1\n.')
    _attrs_140794512 = _loads("(dp1\nVhref\np2\nV${python:webhelpers.survey_url(phase='report')}\np3\nsVclass\np4\nVbutton-medium\np5\ns.")
    _attrs_140794064 = _loads('(dp1\n.')
    _attrs_140792528 = _loads('(dp1\n.')
    _attrs_140795856 = _loads('(dp1\nVid\np2\nVnavigation\np3\ns.')
    _lookup_tile = _loads('cplonetheme.nuplone.tiles.tales\n_lookup_tile\np1\n.')
    _attrs_161505744 = _loads('(dp1\nVhref\np2\nV${webhelpers/help_url}#actionplan\np3\ns.')
    _attrs_130618512 = _loads('(dp1\nVhref\np2\nV${survey_url}/report\np3\ns.')
    _attrs_161509008 = _loads('(dp1\nVhref\np2\nV${webhelpers/survey_url}/status\np3\ns.')
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
        'nocall:request/client'
        client = _path(econtext['request'], econtext['request'], False, 'client')
        'nocall:context/@@webhelpers'
        webhelpers = _path(econtext['context'], econtext['request'], False, '@@webhelpers')
        attrs = _attrs_140795472
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml">\n  ')
        attrs = _attrs_140794192
        _write(u'<head>\n    ')
        attrs = _attrs_140794960
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
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, client=client, _out=_out, _write=_write)
        'webhelpers/macros/css'
        _write(u'\n    ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'css')
        u'{}'
        _tmp = {}
        'webhelpers/macros/css'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, client=client, _out=_out, _write=_write)
        _write(u'\n  </head>\n  ')
        attrs = _attrs_140792208
        'join(u\'actionplan \', value("_path(webhelpers, request, True, \'extra_css\')"))'
        _write(u'<body')
        _tmp1 = ('%s%s' % ('actionplan ', _path(webhelpers, econtext['request'], True, 'extra_css'), ))
        if (_tmp1 is _default):
            _tmp1 = u'actionplan ${webhelpers/extra_css}'
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
        attrs = _attrs_140792592
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
        'view/next_url'
        _write(u'</h1>\n    ')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'next_url')
        if _tmp1:
            pass
            _write(u'\n        ')
            attrs = _attrs_140793808
            u"%(translate)s('expl_actionplan_1', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<p>')
            _result = _translate('expl_actionplan_1', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'\n            After having identified the risks, you need to put an action plan in\n            place to manage the risks. To eliminate or reduce risks you need to\n            determine which preventive and protective measures are to be taken.\n        ')
            _write(u'</p>\n        ')
            attrs = _attrs_140794576
            u"%(translate)s('expl_actionplan_2', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<p>')
            _result = _translate('expl_actionplan_2', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'\n            Among the things to be considered for this step are:\n        ')
            _write(u'</p>\n        ')
            attrs = _attrs_140794256
            _write(u'<p>\n            ')
            attrs = _attrs_140794064
            _write(u'<ol>\n                ')
            attrs = _attrs_140793936
            u'{}'
            _write(u'<li>')
            _mapping_140793936 = {}
            u'True'
            _tmp1 = True
            if _tmp1:
                pass
                _tmp_out2 = _out
                _tmp_write2 = _write
                u'_init_stream()'
                (_out, _write, ) = _init_stream()
                attrs = _attrs_140794832
                _write(u'<ul>\n                        ')
                attrs = _attrs_140793680
                u"%(translate)s('expl_actionplan_4', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<li>')
                _result = _translate('expl_actionplan_4', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp2 = (_result is not _marker)
                if _tmp2:
                    pass
                    u'_result'
                    _tmp3 = _result
                    _write(_tmp3)
                else:
                    pass
                    _write(u'considering whether the task or job is necessary')
                _write(u'</li>\n                        ')
                attrs = _attrs_140792464
                u"%(translate)s('expl_actionplan_5', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<li>')
                _result = _translate('expl_actionplan_5', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp2 = (_result is not _marker)
                if _tmp2:
                    pass
                    u'_result'
                    _tmp3 = _result
                    _write(_tmp3)
                else:
                    pass
                    _write(u'removing the hazard')
                _write(u'</li>\n                        ')
                attrs = _attrs_140793872
                u'%(out)s.getvalue()'
                _write(u'<li>...</li>\n                    </ul>')
                _mapping_140793936['expl_actionplan_4_and_5'] = _out.getvalue()
                _write = _tmp_write2
                _out = _tmp_out2
            u"%(translate)s('expl_actionplan_3', domain=%(domain)s, mapping=_mapping_140793936, target_language=%(language)s, default=_marker)"
            _result = _translate('expl_actionplan_3', domain=_domain, mapping=_mapping_140793936, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                u"_mapping_140793936['expl_actionplan_4_and_5']"
                _write(u'\n                    Is a risk avoidable? Can it be removed entirely? For example, this could be achieved by:\n                    ')
                _tmp1 = _mapping_140793936['expl_actionplan_4_and_5']
                _write((_tmp1 + u'\n                '))
            _write(u'</li>\n                ')
            attrs = _attrs_140792528
            u"%(translate)s('expl_actionplan_6', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<li>')
            _result = _translate('expl_actionplan_6', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'\n                If certain risks are not avoidable, how can they be reduced to a level at which the health and safety of those exposed is not compromised?\n                ')
            _write(u'</li>\n            </ol>\n        </p>\n        ')
            attrs = _attrs_140792080
            u"%(translate)s('expl_actionplan_7', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<p>')
            _result = _translate('expl_actionplan_7', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'\n            Once you have decided how to eliminate or reduce a particular risk, then you describe the specific action(s) required to achieve this. You should also include details of the level of expertise and/or other requirements needed for those actions to be effective.\n        ')
            _write(u'</p>\n    ')
        u"not(_path(view, request, True, 'next_url'))"
        _write(u'\n    ')
        _tmp1 = not _path(econtext['view'], econtext['request'], True, 'next_url')
        if _tmp1:
            pass
            _write(u'\n        ')
            attrs = _attrs_140795280
            u"%(translate)s('expl_actionplan_empty', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<p>')
            _result = _translate('expl_actionplan_empty', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'\n            No risks were identified.  Please proceed directly to the report.\n        ')
            _write(u'</p>\n    ')
        _write(u'\n\n    ')
        attrs = _attrs_140793104
        'view/next_url'
        _write(u'<p class="buttonBar">\n      ')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'next_url')
        if _tmp1:
            pass
            attrs = _attrs_140795600
            'join(value("_path(view, request, True, \'next_url\')"),)'
            _write(u'<a class="button-medium"')
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'next_url')
            if (_tmp1 is _default):
                _tmp1 = u'${view/next_url}'
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
            u"%(translate)s('label_create_action_plan', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write('>')
            _result = _translate('label_create_action_plan', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Create action plan')
            _write(u'</a>')
        u"not(_path(view, request, True, 'next_url'))"
        _write(u'\n      ')
        _tmp1 = not _path(econtext['view'], econtext['request'], True, 'next_url')
        if _tmp1:
            pass
            attrs = _attrs_140794512
            'join(value("webhelpers.survey_url(phase=\'report\')"),)'
            _write(u'<a class="button-medium"')
            _tmp1 = _lookup_attr(webhelpers, 'survey_url')(phase='report')
            if (_tmp1 is _default):
                _tmp1 = u"${python:webhelpers.survey_url(phase='report')}"
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
            u"%(translate)s('label_jump_to_report', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write('>')
            _result = _translate('label_jump_to_report', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Go to report')
            _write(u'</a>')
        _write(u'\n    </p>\n\n    ')
        attrs = _attrs_140794704
        'webhelpers/survey_url'
        _write(u'<br />\n    ')
        survey_url = _path(webhelpers, econtext['request'], True, 'survey_url')
        attrs = _attrs_140793744
        _write(u'<ol id="steps">\n      ')
        attrs = _attrs_140793488
        _write(u'<li class="complete" id="step-1">\n        ')
        attrs = _attrs_140792400
        "join(value('_path(survey_url, request, True, )'), u'/start')"
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(survey_url, econtext['request'], True), '/start', ))
        if (_tmp1 is _default):
            _tmp1 = u'${survey_url}/start'
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
        attrs = _attrs_140792912
        _write(u'<li class="complete" id="step-2">\n        ')
        attrs = _attrs_140795728
        "join(value('_path(survey_url, request, True, )'), u'/identification')"
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(survey_url, econtext['request'], True), '/identification', ))
        if (_tmp1 is _default):
            _tmp1 = u'${survey_url}/identification'
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
        _write(u'\n          ')
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
        _write(u'\n        </a>\n      </li>\n      ')
        attrs = _attrs_140793616
        _write(u'<li class="complete" id="step-3">\n        ')
        attrs = _attrs_140792272
        "join(value('_path(survey_url, request, True, )'), u'/evaluation')"
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(survey_url, econtext['request'], True), '/evaluation', ))
        if (_tmp1 is _default):
            _tmp1 = u'${survey_url}/evaluation'
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
        _write(u'\n          ')
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
        _write(u'\n        </a>\n      </li>\n      ')
        attrs = _attrs_140793360
        _write(u'<li class="active current" id="step-4">\n        ')
        attrs = _attrs_130621264
        "join(value('_path(survey_url, request, True, )'), u'/actionplan')"
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(survey_url, econtext['request'], True), '/actionplan', ))
        if (_tmp1 is _default):
            _tmp1 = u'${survey_url}/actionplan'
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
        _write(u'\n          ')
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
        _write(u'\n        </a>\n      </li>\n      ')
        attrs = _attrs_140794640
        _write(u'<li id="step-5">\n        ')
        attrs = _attrs_130618512
        "join(value('_path(survey_url, request, True, )'), u'/report')"
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(survey_url, econtext['request'], True), '/report', ))
        if (_tmp1 is _default):
            _tmp1 = u'${survey_url}/report'
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
        _write(u'\n          ')
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
        _write(u'\n        </a>\n      </li>\n    </ol>\n    ')
        attrs = _attrs_140795856
        'webhelpers/macros/homelink'
        _write(u'<ul id="navigation">\n      ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'homelink')
        u'{}'
        _tmp = {}
        'webhelpers/macros/homelink'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, client=client, _out=_out, _write=_write)
        _write(u'\n      ')
        attrs = _attrs_130619088
        _write(u'<li>')
        attrs = _attrs_161507856
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
        attrs = _attrs_161508048
        _write(u'<li>')
        attrs = _attrs_161507408
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
        attrs = _attrs_161505552
        _write(u'<li>')
        attrs = _attrs_161505744
        'join(value("_path(webhelpers, request, True, \'help_url\')"), u\'#actionplan\')'
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(webhelpers, econtext['request'], True, 'help_url'), '#actionplan', ))
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/help_url}#actionplan'
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
        attrs = _attrs_161509264
        _write(u'<li>')
        attrs = _attrs_161509008
        'join(value("_path(webhelpers, request, True, \'survey_url\')"), u\'/status\')'
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(webhelpers, econtext['request'], True, 'survey_url'), '/status', ))
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/survey_url}/status'
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
        u"%(translate)s('navigation_status', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write('>')
        _result = _translate('navigation_status', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Status')
        _write(u'</a></li>\n      ')
        attrs = _attrs_161506448
        _write(u'<li>')
        attrs = _attrs_161507536
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
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, client=client, _out=_out, _write=_write)
        'webhelpers/macros/javascript'
        _write(u'\n    ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'javascript')
        u'{}'
        _tmp = {}
        'webhelpers/macros/javascript'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, client=client, _out=_out, _write=_write)
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

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/actionplan.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
