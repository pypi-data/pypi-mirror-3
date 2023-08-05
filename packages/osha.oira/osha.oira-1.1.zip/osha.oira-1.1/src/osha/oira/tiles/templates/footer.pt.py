registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_235891856 = _loads('(dp1\nVsrc\np2\nV++resource++osha.oira.images/footer_logo.png\np3\nsVstyle\np4\nVmargin-right: 15px\np5\ns.')
    _attrs_235892048 = _loads('(dp1\nVhref\np2\nVhttp://osha.europa.eu\np3\nsVtarget\np4\nV_new\np5\ns.')
    _attrs_235891408 = _loads('(dp1\nVclear\np2\nVall\np3\ns.')
    _attrs_235891984 = _loads('(dp1\n.')
    _attrs_235892432 = _loads('(dp1\nVsrc\np2\nV++resource++osha.oira.images/creative_commons.png\np3\nsVstyle\np4\nVmargin-right: 15px; cursor: pointer;\np5\ns.')
    _attrs_235892112 = _loads('(dp1\n.')
    _attrs_235892176 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_235891600 = _loads('(dp1\nVstyle\np2\nVpadding-bottom: 20px; padding-left: 220px; padding-top: 10em;\np3\nsVid\np4\nVnuplone_appendix\np5\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_235891472 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
    _attrs_235892304 = _loads('(dp1\nValt\np2\nVCC License\np3\nsVhref\np4\nVhttp://creativecommons.org/licenses/by-sa/2.5/\np5\ns.')
    _attrs_235892240 = _loads('(dp1\nVhref\np2\nVhttp://www.gnu.org/licenses/gpl.html\np3\ns.')
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
        attrs = _attrs_235891408
        _write(u'<br clear="all" />')
        _tmp_domain0 = _domain
        u"'euphorie'"
        _domain = 'euphorie'
        attrs = _attrs_235891472
        'here/@@plone_portal_state/language'
        _write(u'<span xmlns="http://www.w3.org/1999/xhtml">\n\n    ')
        lang = _path(econtext['here'], econtext['request'], True, '@@plone_portal_state', 'language')
        attrs = _attrs_235891600
        _write(u'<p id="nuplone_appendix" style="padding-bottom: 20px; padding-left: 220px; padding-top: 10em;">\n\n        ')
        attrs = _attrs_235891856
        u'{}'
        _write(u'<img style="margin-right: 15px" src="++resource++osha.oira.images/footer_logo.png" />\n\n        ')
        _mapping_235891920 = {}
        u'True'
        _tmp1 = True
        if _tmp1:
            pass
            _tmp_out1 = _out
            _tmp_write1 = _write
            u'_init_stream()'
            (_out, _write, ) = _init_stream()
            attrs = _attrs_235892048
            u'%(out)s.getvalue()'
            _write(u'<a href="http://osha.europa.eu" target="_new">EU-OSHA</a>')
            _mapping_235891920['EU-OSHA'] = _out.getvalue()
            _write = _tmp_write1
            _out = _tmp_out1
        u"%(translate)s('appendix_produced_by', domain=%(domain)s, mapping=_mapping_235891920, target_language=%(language)s, default=_marker)"
        _result = _translate('appendix_produced_by', domain=_domain, mapping=_mapping_235891920, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            u"_mapping_235891920['EU-OSHA']"
            _write(u'\n            Produced by ')
            _tmp1 = _mapping_235891920['EU-OSHA']
            _write((_tmp1 + u'.'))
        _write(u'\n        |\n        ')
        attrs = _attrs_235891984
        'http://client.oiraproject.eu/about?set_language=$lang'
        _write(u'<a')
        _tmp1 = ('%s%s' % ('http://client.oiraproject.eu/about?set_language=', _path(lang, econtext['request'], True), ))
        if (_tmp1 is _default):
            _tmp1 = None
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
        u"%(translate)s('appendix_about', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write('>')
        _result = _translate('appendix_about', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'About')
        _write(u'</a>\n        |\n        ')
        attrs = _attrs_235892112
        'http://devbox:4080/Plone2/client/terms-and-conditions?set_language=$lang'
        _write(u'<a')
        _tmp1 = ('%s%s' % ('http://devbox:4080/Plone2/client/terms-and-conditions?set_language=', _path(lang, econtext['request'], True), ))
        if (_tmp1 is _default):
            _tmp1 = None
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
        u"%(translate)s('appendix_privacy', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write('>')
        _result = _translate('appendix_privacy', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Privacy')
        _write(u'</a>\n        |\n        ')
        attrs = _attrs_235892176
        'http://client.oiraproject.eu/disclaimer?set_language=$lang'
        _write(u'<a')
        _tmp1 = ('%s%s' % ('http://client.oiraproject.eu/disclaimer?set_language=', _path(lang, econtext['request'], True), ))
        if (_tmp1 is _default):
            _tmp1 = None
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
        u"%(translate)s('appendix_disclaimer', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write('>')
        _result = _translate('appendix_disclaimer', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Disclaimer')
        _write(u'</a>\n        |\n        ')
        attrs = _attrs_235892240
        u"%(translate)s('appendix_gpl_license', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<a href="http://www.gnu.org/licenses/gpl.html">')
        _result = _translate('appendix_gpl_license', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'GPL License')
        _write(u'</a>\n        |\n        ')
        attrs = _attrs_235892304
        _write(u'<a href="http://creativecommons.org/licenses/by-sa/2.5/" alt="CC License">\n            ')
        attrs = _attrs_235892432
        _write(u'<img style="margin-right: 15px; cursor: pointer;" src="++resource++osha.oira.images/creative_commons.png" />\n        </a>\n    </p>\n')
        _write(u'</span>')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/tiles/templates/footer.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
