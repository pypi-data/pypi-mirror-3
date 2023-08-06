registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_205337232 = _loads('(dp1\n.')
    _attrs_205337424 = _loads('(dp1\n.')
    _attrs_205337168 = _loads('(dp1\n.')
    _attrs_205336784 = _loads('(dp1\n.')
    _attrs_205337936 = _loads('(dp1\nVhref\np2\nV${webhelpers/help_url}#authentication\np3\ns.')
    _attrs_205337616 = _loads('(dp1\nVid\np2\nVnavigation\np3\ns.')
    _attrs_205337808 = _loads('(dp1\n.')
    _attrs_205337488 = _loads('(dp1\n.')
    _attrs_205337360 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_205336912 = _loads('(dp1\n.')
    _lookup_tile = _loads('cplonetheme.nuplone.tiles.tales\n_lookup_tile\np1\n.')
    _attrs_205336656 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
    _attrs_205337296 = _loads('(dp1\n.')
    _attrs_205337552 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _attrs_205336848 = _loads('(dp1\n.')
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
        attrs = _attrs_205336656
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml">\n  ')
        attrs = _attrs_205336784
        _write(u'<head>\n    ')
        attrs = _attrs_205336912
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
        attrs = _attrs_205336848
        _write(u'<body>\n    ')
        attrs = _attrs_205337168
        u"%(translate)s('header_disclaimer', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h1>')
        _result = _translate('header_disclaimer', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Disclaimer of Liability')
        _write(u'</h1>\n\n    ')
        attrs = _attrs_205337232
        u"%(translate)s('disclaimer_other_websites', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('disclaimer_other_websites', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'\n        This tool contains links to other websites which are not are not under the\n        control of the European Agency for Safety and Health and the organisations\n        involved. The Agency and the organisations involved accept no liability in\n        respect of the content of these websites.\xa0\n    ')
        _write(u'</p>\n\n    ')
        attrs = _attrs_205337296
        u"%(translate)s('disclaimer_tool_information', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('disclaimer_tool_information', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'\n        The European Agency for Safety and Health at Work and the organisations\n        involved will not be liable for any false, inaccurate, inappropriate or\n        incomplete information stored in the OiRA tool or any other damages as a result\n        of using the software.\n    ')
        _write(u'</p>\n\n    ')
        attrs = _attrs_205337360
        u"%(translate)s('disclaimer_risk_coverage', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('disclaimer_risk_coverage', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'\n        Moreover, an OiRA tool is not intended to cover all the risks of every\n        workplace but to help you put the risk assessment process into practice. For\n        the OiRA tool to be fully effective it needs to be adapted to the context of\n        your particular enterprise - some items might need to be added others omitted\n        if they are not relevant. \n    ')
        _write(u'</p>\n\n    ')
        attrs = _attrs_205337424
        u"%(translate)s('disclaimer_interactions', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('disclaimer_interactions', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'\n        For practical and analytical reasons, the tool presents problems/hazards\n        separately, but in workplaces they may be intertwined. Therefore interactions\n        between the different problems or risk factors identified must be taken into\n        account. \n    ')
        _write(u'</p>\n\n    ')
        attrs = _attrs_205337488
        u"%(translate)s('disclaimer_coverage_liability', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('disclaimer_coverage_liability', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'\n        Therefore, EU-OSHA does not accept any liability for damages and claims in case\n        a tool does not cover all risks of a given sector.\n    ')
        _write(u'</p>\n\n    ')
        attrs = _attrs_205337552
        u"%(translate)s('disclaimer_printed_assesment', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('disclaimer_printed_assesment', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'\n        Moreover, the Agency and the organisations involved in the production of the\n        OiRA tool do not accept any liability for damages and claims arising out of the\n        use or inability to use the tool and the data stored therein. Similarly,\n        EU-OSHA does not accept any liability in case of unavailability of the function\n        of the OiRA tools to print the report, recording the risk assessment\n        automatically generated by the tool. Therefore, the employer has to make sure,\n        at any time, to be in possession of a printed, accurate and up-dated risk\n        assessment. \n    ')
        _write(u'</p>\n\n\n    ')
        attrs = _attrs_205337616
        'webhelpers/macros/homelink'
        _write(u'<ul id="navigation">\n      ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'homelink')
        u'{}'
        _tmp = {}
        'webhelpers/macros/homelink'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, client=client, _out=_out, _write=_write)
        _write(u'\n      ')
        attrs = _attrs_205337808
        _write(u'<li>')
        attrs = _attrs_205337936
        'join(value("_path(webhelpers, request, True, \'help_url\')"), u\'#authentication\')'
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(webhelpers, econtext['request'], True, 'help_url'), '#authentication', ))
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/help_url}#authentication'
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

__filename__ = '/home/jc/dev/euphorie/src/osha.oira/src/osha/oira/templates/disclaimer.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
