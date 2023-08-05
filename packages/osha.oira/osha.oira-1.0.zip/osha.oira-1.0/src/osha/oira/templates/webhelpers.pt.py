registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_225422480 = _loads('(dp1\nVhref\np2\nVclient/++resource++euphorie.media/favicon.png\np3\nsVrel\np4\nVicon\np5\nsVtype\np6\nVimage/png\np7\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_225422288 = _loads('(dp1\nVcontent\np2\nVtext/html; charset=utf-8\np3\nsVhttp-equiv\np4\nVContent-Type\np5\ns.')
    _attrs_225422352 = _loads('(dp1\nVcontent\np2\nVIE=edge\np3\nsVhttp-equiv\np4\nVX-UA-Compatible\np5\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_225422416 = _loads('(dp1\nVcontent\np2\nVwidth=device-width, initial-scale=1\np3\nsVname\np4\nVviewport\np5\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u"%(scope)s['%(out)s'], %(scope)s['%(write)s']"
        (_out, _write, ) = (econtext['_out'], econtext['_write'], )
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        _write(u'')
        attrs = _attrs_225422288
        _write(u'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n    ')
        attrs = _attrs_225422352
        _write(u'<meta http-equiv="X-UA-Compatible" content="IE=edge" />\n    ')
        attrs = _attrs_225422416
        _write(u'<meta name="viewport" content="width=device-width, initial-scale=1" />\n    ')
        attrs = _attrs_225422480
        _write(u'<link rel="icon" type="image/png" href="client/++resource++euphorie.media/favicon.png" />\n  \n\n  ')
        return
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/webhelpers.pt'
registry[('headers', False, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _attrs_225503504 = _loads('(dp1\nVmedia\np2\nVall\np3\nsVhref\np4\nVclient/++resource++osha.oira.stylesheets/lowercase_headers.css\np5\nsVrel\np6\nVstylesheet\np7\nsVtype\np8\nVtext/css\np9\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_225501840 = _loads('(dp1\nVmedia\np2\nVall\np3\nsVhref\np4\nV${base_url}/screen.css\np5\nsVrel\np6\nVstylesheet\np7\nsVtype\np8\nVtext/css\np9\ns.')
    _attrs_225502096 = _loads('(dp1\nVtitle\np2\nVebc\np3\nsVmedia\np4\nVonly screen and (min-width:768px)\np5\nsVhref\np6\nV${base_url}/screen-osha.css\np7\nsVrel\np8\nVstylesheet\np9\nsVtype\np10\nVtext/css\np11\ns.')
    _attrs_225503760 = _loads('(dp1\nVmedia\np2\nVall\np3\nsVtype\np4\nVtext/css\np5\ns.')
    _attrs_225502672 = _loads('(dp1\nVmedia\np2\nVall\np3\nsVhref\np4\nV${sector_url}/@@sector.css\np5\nsVrel\np6\nVstylesheet\np7\nsVtype\np8\nVtext/css\np9\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_225502928 = _loads('(dp1\nVtitle\np2\nVebc\np3\nsVmedia\np4\nVonly screen and (min-width:768px)\np5\nsVhref\np6\nV${base_url}/screen-osha.min.css\np7\nsVrel\np8\nVstylesheet\np9\nsVtype\np10\nVtext/css\np11\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_225502800 = _loads('(dp1\nVmedia\np2\nVall\np3\nsVhref\np4\nV${base_url}/screen.min.css\np5\nsVrel\np6\nVstylesheet\np7\nsVtype\np8\nVtext/css\np9\ns.')
    _attrs_225503440 = _loads('(dp1\nVmedia\np2\nVall\np3\nsVhref\np4\nV${oira_base_url}/main.css\np5\nsVrel\np6\nVstylesheet\np7\nsVtype\np8\nVtext/css\np9\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u"%(scope)s['%(out)s'], %(scope)s['%(write)s']"
        (_out, _write, ) = (econtext['_out'], econtext['_write'], )
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        'client/++resource++euphorie.style'
        base_url = _path(econtext['client'], econtext['request'], True, '++resource++euphorie.style')
        'client/++resource++osha.oira.stylesheets'
        oira_base_url = _path(econtext['client'], econtext['request'], True, '++resource++osha.oira.stylesheets')
        'webhelpers/on_mobile'
        on_mobile = _path(econtext['webhelpers'], econtext['request'], True, 'on_mobile')
        'webhelpers/debug_mode'
        _write(u'')
        _tmp1 = _path(econtext['webhelpers'], econtext['request'], True, 'debug_mode')
        if _tmp1:
            pass
            _write(u'')
            attrs = _attrs_225501840
            "join(value('_path(base_url, request, True, )'), u'/screen.css')"
            _write(u'<link rel="stylesheet" type="text/css" media="all"')
            _tmp1 = ('%s%s' % (_path(base_url, econtext['request'], True), '/screen.css', ))
            if (_tmp1 is _default):
                _tmp1 = u'${base_url}/screen.css'
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
            _write(u' />\n      ')
            attrs = _attrs_225502096
            "join(value('_path(base_url, request, True, )'), u'/screen-osha.css')"
            _write(u'<link rel="stylesheet" type="text/css" media="only screen and (min-width:768px)" title="ebc"')
            _tmp1 = ('%s%s' % (_path(base_url, econtext['request'], True), '/screen-osha.css', ))
            if (_tmp1 is _default):
                _tmp1 = u'${base_url}/screen-osha.css'
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
            u'base_url'
            _write(u' />\n      <!--[if lte IE 6]> <link rel="stylesheet" type="text/css" media="all" href="++resource++screen-ie6.css"/> <link rel="stylesheet" href="')
            _tmp1 = _path(base_url, econtext['request'], True)
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
            u'base_url'
            _write(u'/screen-osha.css" type="text/css" media="all" title="ebc" charset="utf-8" /><![endif]-->\n      <!--[if IE 7]> <link rel="stylesheet" type="text/css" media="all" href="')
            _tmp1 = _path(base_url, econtext['request'], True)
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
            u'base_url'
            _write(u'/screen-ie7.css"/> <link rel="stylesheet" href="')
            _tmp1 = _path(base_url, econtext['request'], True)
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
            u'base_url'
            _write(u'/screen-osha.css" type="text/css" media="all" title="ebc" charset="utf-8" /><![endif]-->\n      <!--[if IE 8]> <link rel="stylesheet" type="text/css" media="all" href="')
            _tmp1 = _path(base_url, econtext['request'], True)
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
            u'base_url'
            _write(u'/screen-ie8.css" /> <link rel="stylesheet" href="')
            _tmp1 = _path(base_url, econtext['request'], True)
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
            _write(u'/screen-osha.css" type="text/css" media="all" title="ebc" charset="utf-8" /><![endif]-->\n    ')
        u"not(_path(webhelpers, request, True, 'debug_mode'))"
        _write(u'\n    ')
        _tmp1 = not _path(econtext['webhelpers'], econtext['request'], True, 'debug_mode')
        if _tmp1:
            pass
            _write(u'\n      ')
            attrs = _attrs_225502800
            "join(value('_path(base_url, request, True, )'), u'/screen.min.css')"
            _write(u'<link rel="stylesheet" type="text/css" media="all"')
            _tmp1 = ('%s%s' % (_path(base_url, econtext['request'], True), '/screen.min.css', ))
            if (_tmp1 is _default):
                _tmp1 = u'${base_url}/screen.min.css'
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
            _write(u' />\n      ')
            attrs = _attrs_225502928
            "join(value('_path(base_url, request, True, )'), u'/screen-osha.min.css')"
            _write(u'<link rel="stylesheet" type="text/css" media="only screen and (min-width:768px)" title="ebc"')
            _tmp1 = ('%s%s' % (_path(base_url, econtext['request'], True), '/screen-osha.min.css', ))
            if (_tmp1 is _default):
                _tmp1 = u'${base_url}/screen-osha.min.css'
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
            u'base_url'
            _write(u' />\n      <!--[if lte IE 6]> <link rel="stylesheet" type="text/css" media="all" href="++resource++screen-ie6.css"/> <link rel="stylesheet" href="')
            _tmp1 = _path(base_url, econtext['request'], True)
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
            u'base_url'
            _write(u'/screen-osha.min.css" type="text/css" media="all" title="ebc" charset="utf-8" /><![endif]-->\n      <!--[if IE 7]> <link rel="stylesheet" type="text/css" media="all" href="')
            _tmp1 = _path(base_url, econtext['request'], True)
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
            u'base_url'
            _write(u'/screen-ie7.min.css"/> <link rel="stylesheet" href="')
            _tmp1 = _path(base_url, econtext['request'], True)
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
            u'base_url'
            _write(u'/screen-osha.min.css" type="text/css" media="all" title="ebc" charset="utf-8" /><![endif]-->\n      <!--[if IE 8]> <link rel="stylesheet" type="text/css" media="all" href="')
            _tmp1 = _path(base_url, econtext['request'], True)
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
            u'base_url'
            _write(u'/screen-ie8.min.css" /> <link rel="stylesheet" href="')
            _tmp1 = _path(base_url, econtext['request'], True)
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
            _write(u'/screen-osha.min.css" type="text/css" media="all" title="ebc" charset="utf-8" /><![endif]-->\n    ')
        'webhelpers/sector_url'
        _write(u'\n    ')
        sector_url = _path(econtext['webhelpers'], econtext['request'], True, 'sector_url')
        'sector_url and not on_mobile'
        _tmp1 = (sector_url and not on_mobile)
        if _tmp1:
            pass
            attrs = _attrs_225502672
            "join(value('_path(sector_url, request, True, )'), u'/@@sector.css')"
            _write(u'<link rel="stylesheet" type="text/css" media="all"')
            _tmp1 = ('%s%s' % (_path(sector_url, econtext['request'], True), '/@@sector.css', ))
            if (_tmp1 is _default):
                _tmp1 = u'${sector_url}/@@sector.css'
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
            _write(' />')
        _write(u'\n    ')
        attrs = _attrs_225503440
        "join(value('_path(oira_base_url, request, True, )'), u'/main.css')"
        _write(u'<link rel="stylesheet" type="text/css" media="all"')
        _tmp1 = ('%s%s' % (_path(oira_base_url, econtext['request'], True), '/main.css', ))
        if (_tmp1 is _default):
            _tmp1 = u'${oira_base_url}/main.css'
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
        'context/@@plone_portal_state'
        _write(u' />\n    ')
        portal_state = _path(econtext['context'], econtext['request'], True, '@@plone_portal_state')
        "portal_state.language() in ['el', 'el-cy', 'el-gr']"
        _tmp1 = (_lookup_attr(portal_state, 'language')() in ['el', 'el-cy', 'el-gr', ])
        if _tmp1:
            pass
            attrs = _attrs_225503504
            _write(u'<link rel="stylesheet" type="text/css" media="all" href="client/++resource++osha.oira.stylesheets/lowercase_headers.css" />')
        _write(u'\n    ')
        attrs = _attrs_225503760
        _write(u'<style type="text/css" media="all">\n        .report #appendix img {\n            margin-bottom: 0;\n        }\n        .appendix_oira_logo { \n            margin-right: 15px;\n            cursor: pointer;\n        }\n        .report .creative_commons_logo {\n            cursor: pointer;\n        }\n    </style>\n  \n\n  ')
        return
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/webhelpers.pt'
registry[('css', False, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_227832400 = _loads('(dp1\n.')
    _attrs_227835856 = _loads('(dp1\n.')
    _attrs_227835088 = _loads('(dp1\nVhref\np2\nV${webhelpers/client_url}\np3\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_227833872 = _loads('(dp1\nVhref\np2\nV${webhelpers/client_url}\np3\ns.')
    _attrs_227835472 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_227834704 = _loads('(dp1\nVid\np2\nVhome\np3\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u"%(scope)s['%(out)s'], %(scope)s['%(write)s']"
        (_out, _write, ) = (econtext['_out'], econtext['_write'], )
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        'webhelpers/logoMode'
        logo_mode = _path(econtext['webhelpers'], econtext['request'], True, 'logoMode')
        _write(u'')
        attrs = _attrs_227834704
        "logo_mode=='alien'"
        _write(u'<li id="home">\n      ')
        _tmp1 = (logo_mode == 'alien')
        if _tmp1:
            pass
            attrs = _attrs_227835088
            'join(value("_path(webhelpers, request, True, \'client_url\')"),)'
            _write(u'<a')
            _tmp1 = _path(econtext['webhelpers'], econtext['request'], True, 'client_url')
            if (_tmp1 is _default):
                _tmp1 = u'${webhelpers/client_url}'
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
            u'webhelpers/sector/title'
            _write('>')
            _tmp1 = _path(econtext['webhelpers'], econtext['request'], True, 'sector', 'title')
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
            _write(u'</a>')
        "logo_mode=='native'"
        _write(u'\n      ')
        _tmp1 = (logo_mode == 'native')
        if _tmp1:
            pass
            attrs = _attrs_227833872
            'join(value("_path(webhelpers, request, True, \'client_url\')"),)'
            _write(u'<a')
            _tmp1 = _path(econtext['webhelpers'], econtext['request'], True, 'client_url')
            if (_tmp1 is _default):
                _tmp1 = u'${webhelpers/client_url}'
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
            _write(u'>\n        ')
            attrs = _attrs_227832400
            u"%(translate)s('title_tool', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<strong>')
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
            _write(u'</strong>')
            attrs = _attrs_227835472
            u"%(translate)s('oira_name_line_1', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<br />\n        ')
            _result = _translate('oira_name_line_1', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Online interactive')
            attrs = _attrs_227835856
            u"%(translate)s('oira_name_line_2', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<br />\n        ')
            _result = _translate('oira_name_line_2', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Risk Assessment')
            _write(u'</a>')
        _write(u'\n    </li>\n  \n\n  ')
        return
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/webhelpers.pt'
registry[('homelink', False, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_225470992 = _loads('(dp1\nVhref\np2\nV${webhelpers/client_url}/disclaimer\np3\ns.')
    _attrs_225468944 = _loads('(dp1\nVhref\np2\nV${webhelpers/client_url}\np3\ns.')
    _attrs_225468560 = _loads('(dp1\nVsrc\np2\nV++resource++osha.oira.images/footer_logo.png\np3\nsVclass\np4\nVappendix_oira_logo\np5\ns.')
    _attrs_225470736 = _loads('(dp1\nVhref\np2\nV${webhelpers/client_url}/terms-and-conditions\np3\ns.')
    _attrs_225470416 = _loads('(dp1\nValt\np2\nVCC License\np3\nsVhref\np4\nVhttp://creativecommons.org/licenses/by-sa/2.5/\np5\ns.')
    _attrs_225470672 = _loads('(dp1\nVhref\np2\nV${page/url}\np3\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_225471056 = _loads('(dp1\nVhref\np2\nVhttp://www.gnu.org/licenses/gpl.html\np3\ns.')
    _attrs_225468496 = _loads('(dp1\nVid\np2\nVappendix\np3\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_225471312 = _loads('(dp1\nVhref\np2\nV${webhelpers/client_url}/about\np3\ns.')
    _attrs_225471248 = _loads('(dp1\nVsrc\np2\nV++resource++osha.oira.images/creative_commons.png\np3\nsVclass\np4\nVcreative_commons_logo\np5\ns.')
    _attrs_225470928 = _loads('(dp1\nVhref\np2\nVhttp://osha.europa.eu\np3\nsVtarget\np4\nV_new\np5\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u"%(scope)s['%(out)s'], %(scope)s['%(write)s']"
        (_out, _write, ) = (econtext['_out'], econtext['_write'], )
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        _tmp_domain0 = _domain
        u"'euphorie'"
        _domain = 'euphorie'
        _write(u'')
        attrs = _attrs_225468496
        _write(u'<p id="appendix">\n        ')
        attrs = _attrs_225468944
        'join(value("_path(webhelpers, request, True, \'client_url\')"),)'
        _write(u'<a')
        _tmp1 = _path(econtext['webhelpers'], econtext['request'], True, 'client_url')
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/client_url}'
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
        _write(u'>\n        ')
        attrs = _attrs_225468560
        'webhelpers/appendix'
        _write(u'<img class="appendix_oira_logo" src="++resource++osha.oira.images/footer_logo.png" />\n        </a>\n\n        ')
        _tmp1 = _path(econtext['webhelpers'], econtext['request'], True, 'appendix')
        page = None
        (_tmp1, _tmp2, ) = repeat.insert('page', _tmp1)
        for page in _tmp1:
            _tmp2 = (_tmp2 - 1)
            _write(u'\n            ')
            attrs = _attrs_225470672
            'join(value("_path(page, request, True, \'url\')"),)'
            _write(u'<a')
            _tmp3 = _path(page, econtext['request'], True, 'url')
            if (_tmp3 is _default):
                _tmp3 = u'${page/url}'
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
            u'page/title'
            _write('>')
            _tmp3 = _path(page, econtext['request'], True, 'title')
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
            _write(u'</a> |\n        ')
            if (_tmp2 == 0):
                break
            _write(' ')
        u'{}'
        _write(u'\n        ')
        _mapping_225469520 = {}
        u'True'
        _tmp1 = True
        if _tmp1:
            pass
            _tmp_out1 = _out
            _tmp_write1 = _write
            u'_init_stream()'
            (_out, _write, ) = _init_stream()
            attrs = _attrs_225470928
            u'%(out)s.getvalue()'
            _write(u'<a href="http://osha.europa.eu" target="_new">EU-OSHA</a>')
            _mapping_225469520['EU-OSHA'] = _out.getvalue()
            _write = _tmp_write1
            _out = _tmp_out1
        u"%(translate)s('appendix_produced_by', domain=%(domain)s, mapping=_mapping_225469520, target_language=%(language)s, default=_marker)"
        _result = _translate('appendix_produced_by', domain=_domain, mapping=_mapping_225469520, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            u"_mapping_225469520['EU-OSHA']"
            _write(u'\n        Produced by ')
            _tmp1 = _mapping_225469520['EU-OSHA']
            _write((_tmp1 + u'.'))
        _write(u' \n        |\n        ')
        attrs = _attrs_225471312
        'join(value("_path(webhelpers, request, True, \'client_url\')"), u\'/about\')'
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(econtext['webhelpers'], econtext['request'], True, 'client_url'), '/about', ))
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/client_url}/about'
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
        attrs = _attrs_225470736
        'join(value("_path(webhelpers, request, True, \'client_url\')"), u\'/terms-and-conditions\')'
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(econtext['webhelpers'], econtext['request'], True, 'client_url'), '/terms-and-conditions', ))
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/client_url}/terms-and-conditions'
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
        attrs = _attrs_225470992
        'join(value("_path(webhelpers, request, True, \'client_url\')"), u\'/disclaimer\')'
        _write(u'<a')
        _tmp1 = ('%s%s' % (_path(econtext['webhelpers'], econtext['request'], True, 'client_url'), '/disclaimer', ))
        if (_tmp1 is _default):
            _tmp1 = u'${webhelpers/client_url}/disclaimer'
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
        attrs = _attrs_225471056
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
        attrs = _attrs_225470416
        _write(u'<a href="http://creativecommons.org/licenses/by-sa/2.5/" alt="CC License">\n            ')
        attrs = _attrs_225471248
        _write(u'<img class="creative_commons_logo" src="++resource++osha.oira.images/creative_commons.png" />\n        </a>\n    </p>\n  \n\n  ')
        _domain = _tmp_domain0
        return
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/webhelpers.pt'
registry[('appendix', False, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
def bind():
    from cPickle import loads as _loads
    _attrs_227833104 = _loads('(dp1\nVsrc\np2\nV${client/++resource++euphorie.behaviour}/common.min.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_227832592 = _loads('(dp1\nVsrc\np2\nV${lib_url}/jquery.localscroll.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_223655120 = _loads('(dp1\nVsrc\np2\nV${lib_url}/jquery.bt.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_227834128 = _loads('(dp1\nVsrc\np2\nV${lib_url}/fancybox/jquery.mousewheel-3.0.2.pack.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_227832656 = _loads('(dp1\nVsrc\np2\nV${lib_url}/fancybox/jquery.fancybox-1.3.1.pack.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_223654096 = _loads('(dp1\nVsrc\np2\nV${lib_url}/jquery-ui-1.7.3.min.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_223657296 = _loads('(dp1\nVsrc\np2\nV${lib_url}/jquery.hoverIntent.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_227833936 = _loads('(dp1\nVsrc\np2\nV${lib_url}/jquery.scrollTo.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_144606288 = _loads('(dp1\nVsrc\np2\nV${lib_url}/jquery.numeric.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_227834832 = _loads('(dp1\nVsrc\np2\nV${client/++resource++euphorie.behaviour}/markup.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_144608720 = _loads('(dp1\nVsrc\np2\nV${lib_url}/jcarousellite_1.0.1.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_223657360 = _loads('(dp1\nVsrc\np2\nV${lib_url}/css_browser_selector.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_223657808 = _loads('(dp1\nVsrc\np2\nV${lib_url}/jquery-1.4.4.min.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u"%(scope)s['%(out)s'], %(scope)s['%(write)s']"
        (_out, _write, ) = (econtext['_out'], econtext['_write'], )
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        'client/++resource++euphorie.libraries'
        lib_url = _path(econtext['client'], econtext['request'], True, '++resource++euphorie.libraries')
        u'lib_url'
        _write(u'<!--[if lte IE 8]> <script type="text/javascript" src="')
        _tmp1 = _path(lib_url, econtext['request'], True)
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
        'webhelpers/debug_mode'
        _write(u'/excanvas.min.js"></script> <![endif]-->\n    ')
        _tmp1 = _path(econtext['webhelpers'], econtext['request'], True, 'debug_mode')
        if _tmp1:
            pass
            _write(u'\n        ')
            attrs = _attrs_223657808
            "join(value('_path(lib_url, request, True, )'), u'/jquery-1.4.4.min.js')"
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(lib_url, econtext['request'], True), '/jquery-1.4.4.min.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${lib_url}/jquery-1.4.4.min.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n        ')
            attrs = _attrs_223654096
            "join(value('_path(lib_url, request, True, )'), u'/jquery-ui-1.7.3.min.js')"
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(lib_url, econtext['request'], True), '/jquery-ui-1.7.3.min.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${lib_url}/jquery-ui-1.7.3.min.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n        ')
            attrs = _attrs_223657360
            "join(value('_path(lib_url, request, True, )'), u'/css_browser_selector.js')"
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(lib_url, econtext['request'], True), '/css_browser_selector.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${lib_url}/css_browser_selector.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n        ')
            attrs = _attrs_223657296
            "join(value('_path(lib_url, request, True, )'), u'/jquery.hoverIntent.js')"
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(lib_url, econtext['request'], True), '/jquery.hoverIntent.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${lib_url}/jquery.hoverIntent.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n        ')
            attrs = _attrs_223655120
            "join(value('_path(lib_url, request, True, )'), u'/jquery.bt.js')"
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(lib_url, econtext['request'], True), '/jquery.bt.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${lib_url}/jquery.bt.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n        ')
            attrs = _attrs_144608720
            "join(value('_path(lib_url, request, True, )'), u'/jcarousellite_1.0.1.js')"
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(lib_url, econtext['request'], True), '/jcarousellite_1.0.1.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${lib_url}/jcarousellite_1.0.1.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n        ')
            attrs = _attrs_144606288
            "join(value('_path(lib_url, request, True, )'), u'/jquery.numeric.js')"
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(lib_url, econtext['request'], True), '/jquery.numeric.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${lib_url}/jquery.numeric.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n        ')
            attrs = _attrs_227833936
            "join(value('_path(lib_url, request, True, )'), u'/jquery.scrollTo.js')"
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(lib_url, econtext['request'], True), '/jquery.scrollTo.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${lib_url}/jquery.scrollTo.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n        ')
            attrs = _attrs_227832592
            "join(value('_path(lib_url, request, True, )'), u'/jquery.localscroll.js')"
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(lib_url, econtext['request'], True), '/jquery.localscroll.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${lib_url}/jquery.localscroll.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n        ')
            attrs = _attrs_227832656
            "join(value('_path(lib_url, request, True, )'), u'/fancybox/jquery.fancybox-1.3.1.pack.js')"
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(lib_url, econtext['request'], True), '/fancybox/jquery.fancybox-1.3.1.pack.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${lib_url}/fancybox/jquery.fancybox-1.3.1.pack.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n        ')
            attrs = _attrs_227834128
            "join(value('_path(lib_url, request, True, )'), u'/fancybox/jquery.mousewheel-3.0.2.pack.js')"
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(lib_url, econtext['request'], True), '/fancybox/jquery.mousewheel-3.0.2.pack.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${lib_url}/fancybox/jquery.mousewheel-3.0.2.pack.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n        ')
            attrs = _attrs_227834832
            'join(value("_path(client, request, True, \'++resource++euphorie.behaviour\')"), u\'/markup.js\')'
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(econtext['client'], econtext['request'], True, '++resource++euphorie.behaviour'), '/markup.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${client/++resource++euphorie.behaviour}/markup.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n    ')
        u"not(_path(webhelpers, request, True, 'debug_mode'))"
        _write(u'\n    ')
        _tmp1 = not _path(econtext['webhelpers'], econtext['request'], True, 'debug_mode')
        if _tmp1:
            pass
            _write(u'\n      ')
            attrs = _attrs_227833104
            'join(value("_path(client, request, True, \'++resource++euphorie.behaviour\')"), u\'/common.min.js\')'
            _write(u'<script type="text/javascript"')
            _tmp1 = ('%s%s' % (_path(econtext['client'], econtext['request'], True, '++resource++euphorie.behaviour'), '/common.min.js', ))
            if (_tmp1 is _default):
                _tmp1 = u'${client/++resource++euphorie.behaviour}/common.min.js'
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
                _write(((' src="' + _tmp1) + '"'))
            _write(u'></script>\n    ')
        _write(u'\n\n  ')
        return
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/webhelpers.pt'
registry[('javascript', False, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_255284496 = _loads("(dp1\nVclass\np2\nV${item/class}\np3\nsVtitle\np4\nV${python:'%s. %s' % (item.number, item.title) if tree.leaf_module else None}\np5\ns.")
    _path_exists = _loads("ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveExistsTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n(dp5\nS'proxify'\np6\ncz3c.pt.expressions\nidentity\np7\nsb.")
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_255284880 = _loads('(dp1\nVclass\np2\nVcounter\np3\ns.')
    _attrs_255284624 = _loads('(dp1\nVhref\np2\nV${item/url}\np3\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_255284368 = _loads("(dp1\nVclass\np2\nV${python:'microns' if tree['leaf_module'] else None}\np3\ns.")
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u"%(scope)s['%(out)s'], %(scope)s['%(write)s']"
        (_out, _write, ) = (econtext['_out'], econtext['_write'], )
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        _write(u'')
        try:
            u'_path_exists(tree, request, True, )'
            _tmp1 = _path_exists(econtext['tree'], econtext['request'], True)
        except NameError, e:
            u'False'
            _tmp1 = False
        
        if _tmp1:
            pass
            attrs = _attrs_255284368
            'join(value("\'microns\' if tree[\'leaf_module\'] else None"),)'
            _write(u'<ol')
            _tmp1 = ('microns' if econtext['tree']['leaf_module'] else None)
            if (_tmp1 is _default):
                _tmp1 = u"${python:'microns' if tree['leaf_module'] else None}"
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
            'tree/children'
            _write(u'>\n      ')
            _tmp1 = _path(econtext['tree'], econtext['request'], True, 'children')
            item = None
            (_tmp1, _tmp2, ) = repeat.insert('item', _tmp1)
            for item in _tmp1:
                _tmp2 = (_tmp2 - 1)
                attrs = _attrs_255284496
                'join(value("\'%s. %s\' % (item.number, item.title) if tree.leaf_module else None"),)'
                _write(u'<li')
                _tmp3 = (('%s. %s' % (_lookup_attr(item, 'number'), _lookup_attr(item, 'title'), )) if _lookup_attr(econtext['tree'], 'leaf_module') else None)
                if (_tmp3 is _default):
                    _tmp3 = u"${python:'%s. %s' % (item.number, item.title) if tree.leaf_module else None}"
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
                    _write(((' title="' + _tmp3) + '"'))
                'join(value("_path(item, request, True, \'class\')"),)'
                _tmp3 = _path(item, econtext['request'], True, 'class')
                if (_tmp3 is _default):
                    _tmp3 = u'${item/class}'
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
                    _write(((' class="' + _tmp3) + '"'))
                'item/class'
                _write(u'>\n        ')
                item_class = _path(item, econtext['request'], True, 'class')
                attrs = _attrs_255284624
                "tree['leaf_module'] and not item_class"
                _tmp3 = (econtext['tree']['leaf_module'] and not item_class)
                if not _tmp3:
                    pass
                    'join(value("_path(item, request, True, \'url\')"),)'
                    _write(u'<a')
                    _tmp4 = _path(item, econtext['request'], True, 'url')
                    if (_tmp4 is _default):
                        _tmp4 = u'${item/url}'
                    if ((_tmp4 is not None) and (_tmp4 is not False)):
                        if (_tmp4.__class__ not in (str, unicode, int, float, )):
                            _tmp4 = unicode(_translate(_tmp4, domain=_domain, mapping=None, target_language=target_language, default=None))
                        else:
                            if not isinstance(_tmp4, unicode):
                                _tmp4 = unicode(str(_tmp4), 'UTF-8')
                        if ('&' in _tmp4):
                            if (';' in _tmp4):
                                _tmp4 = _re_amp.sub('&amp;', _tmp4)
                            else:
                                _tmp4 = _tmp4.replace('&', '&amp;')
                        if ('<' in _tmp4):
                            _tmp4 = _tmp4.replace('<', '&lt;')
                        if ('>' in _tmp4):
                            _tmp4 = _tmp4.replace('>', '&gt;')
                        if ('"' in _tmp4):
                            _tmp4 = _tmp4.replace('"', '&quot;')
                        _write(((' href="' + _tmp4) + '"'))
                    _write('>')
                "not tree['leaf_module']"
                _write(u'\n            ')
                _tmp4 = not econtext['tree']['leaf_module']
                if _tmp4:
                    pass
                    _write(u'')
                    attrs = _attrs_255284880
                    u'item/number'
                    _write(u'<strong class="counter">')
                    _tmp4 = _path(item, econtext['request'], True, 'number')
                    _tmp = _tmp4
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
                    u'item/title'
                    _write(u'</strong> ')
                    _tmp4 = _path(item, econtext['request'], True, 'title')
                    _tmp = _tmp4
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
                    _write(u'\n            ')
                _write(u'\n        ')
                if not _tmp3:
                    pass
                    _write(u'</a>')
                _write(u'\n        ')
                'item'
                tree = item
                "item['children']"
                _tmp3 = item['children']
                if _tmp3:
                    pass
                    'webhelpers/index/macros/survey_tree'
                    _write(u'\n          ')
                    _metal = _path(econtext['webhelpers'], econtext['request'], True, 'index', 'macros', 'survey_tree')
                    u'{}'
                    _tmp = {}
                    'webhelpers/index/macros/survey_tree'
                    _metal.render(_tmp, rcontext=rcontext, _domain=_domain, econtext=econtext, tree=tree, item=item, _out=_out, _write=_write)
                    _write(u'')
                _write(u'\n      ')
                _write(u'</li>')
                if (_tmp2 == 0):
                    break
                _write(' ')
            _write(u'\n    </ol>')
        _write(u'\n  \n\n  ')
        return
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/webhelpers.pt'
registry[('survey_tree', False, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_261238224 = _loads('(dp1\nVhref\np2\nV${large/url|nothing}\np3\nsVrel\np4\nVfancybox\np5\nsVtitle\np6\nV${risk/caption2|nothing}\np7\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_261263888 = _loads('(dp1\n.')
    _attrs_261238160 = _loads('(dp1\nVhref\np2\nV${large/url|nothing}\np3\nsVrel\np4\nVfancybox\np5\nsVtitle\np6\nV${risk/caption|nothing}\np7\ns.')
    _attrs_261264080 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_261238672 = _loads('(dp1\nVsrc\np2\nV${thumb/url}\np3\nsVheight\np4\nV${thumb/height}\np5\nsValt\np6\nV\nsVwith\np7\nV${thumb/width}\np8\nsVclass\np9\nVfloatBefore\np10\ns.')
    _attrs_261238416 = _loads('(dp1\nVsrc\np2\nV${thumb/url}\np3\nsVheight\np4\nV${thumb/height}\np5\nsValt\np6\nV\nsVwith\np7\nV${thumb/width}\np8\nsVclass\np9\nVfloatBefore\np10\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _attrs_261263696 = _loads('(dp1\n.')
    _attrs_261263952 = _loads('(dp1\nVclass\np2\nVnegation\np3\ns.')
    _attrs_261238544 = _loads('(dp1\nVsrc\np2\nV${thumb/url}\np3\nsVheight\np4\nV${thumb/height}\np5\nsValt\np6\nV\nsVwith\np7\nV${thumb/width}\np8\nsVclass\np9\nVfloatBefore\np10\ns.')
    _attrs_261238352 = _loads('(dp1\nVhref\np2\nV${large/url|nothing}\np3\nsVrel\np4\nVfancybox\np5\nsVtitle\np6\nV${risk/caption3|nothing}\np7\ns.')
    _attrs_261263568 = _loads('(dp1\n.')
    _attrs_261238480 = _loads('(dp1\nVhref\np2\nV${large/url|nothing}\np3\nsVrel\np4\nVfancybox\np5\nsVtitle\np6\nV${risk/caption4|nothing}\np7\ns.')
    _attrs_261237968 = _loads('(dp1\nVclass\np2\nVgallery\np3\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_261238288 = _loads('(dp1\nVsrc\np2\nV${thumb/url}\np3\nsVheight\np4\nV${thumb/height}\np5\nsValt\np6\nV\nsVwith\np7\nV${thumb/width}\np8\nsVclass\np9\nVfloatBefore\np10\ns.')
    _attrs_261264208 = _loads('(dp1\nVclass\np2\nVicon warning\np3\ns.')
    _attrs_261263504 = _loads('(dp1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u"%(scope)s['%(out)s'], %(scope)s['%(write)s']"
        (_out, _write, ) = (econtext['_out'], econtext['_write'], )
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        _tmp_domain0 = _domain
        u"'euphorie'"
        _domain = 'euphorie'
        'risk/@@images'
        _write(u'')
        images = _path(econtext['risk'], econtext['request'], True, '@@images')
        'risk.image is not None'
        _tmp1 = (_lookup_attr(econtext['risk'], 'image') is not None)
        if _tmp1:
            pass
            attrs = _attrs_261237968
            "images.scale('image', width=150, height=500, direction='thumbnail')"
            _write(u'<p class="gallery">\n      ')
            thumb = _lookup_attr(images, 'scale')('image', width=150, height=500, direction='thumbnail')
            "images.scale('image', width=590, height=1900, direction='thumbnail')"
            large = _lookup_attr(images, 'scale')('image', width=590, height=1900, direction='thumbnail')
            'thumb'
            _tmp1 = _path(thumb, econtext['request'], True)
            if _tmp1:
                pass
                attrs = _attrs_261238160
                'join(parts(value("_path(risk, request, True, \'caption\')"), value(\'None\')),)'
                _write(u'<a rel="fancybox"')
                try:
                    u'risk/caption'
                    _tmp3 = _path(econtext['risk'], econtext['request'], True, 'caption')
                except Exception, e:
                    u'nothing'
                    _tmp3 = None
                
                _tmp1 = _tmp3
                if (_tmp1 is _default):
                    _tmp1 = u'${risk/caption|nothing}'
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
                    _write(((' title="' + _tmp1) + '"'))
                'join(parts(value("_path(large, request, True, \'url\')"), value(\'None\')),)'
                try:
                    u'large/url'
                    _tmp3 = _path(large, econtext['request'], True, 'url')
                except Exception, e:
                    u'nothing'
                    _tmp3 = None
                
                _tmp1 = _tmp3
                if (_tmp1 is _default):
                    _tmp1 = u'${large/url|nothing}'
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
                _write('>')
                attrs = _attrs_261238288
                'join(value("_path(thumb, request, True, \'width\')"),)'
                _write(u'<img alt=""')
                _tmp1 = _path(thumb, econtext['request'], True, 'width')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/width}'
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
                    _write(((' with="' + _tmp1) + '"'))
                'join(value("_path(thumb, request, True, \'height\')"),)'
                _tmp1 = _path(thumb, econtext['request'], True, 'height')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/height}'
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
                    _write(((' height="' + _tmp1) + '"'))
                'join(value("_path(thumb, request, True, \'url\')"),)'
                _tmp1 = _path(thumb, econtext['request'], True, 'url')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/url}'
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
                    _write(((' src="' + _tmp1) + '"'))
                _write(u' class="floatBefore" />\n        </a>')
            _write(u'\n      ')
            "images.scale('image2', width=120, height=172, direction='thumbnail')"
            thumb = _lookup_attr(images, 'scale')('image2', width=120, height=172, direction='thumbnail')
            "images.scale('image2', width=590, height=1900, direction='thumbnail')"
            large = _lookup_attr(images, 'scale')('image2', width=590, height=1900, direction='thumbnail')
            'thumb'
            _tmp1 = _path(thumb, econtext['request'], True)
            if _tmp1:
                pass
                attrs = _attrs_261238224
                'join(parts(value("_path(risk, request, True, \'caption2\')"), value(\'None\')),)'
                _write(u'<a rel="fancybox"')
                try:
                    u'risk/caption2'
                    _tmp3 = _path(econtext['risk'], econtext['request'], True, 'caption2')
                except Exception, e:
                    u'nothing'
                    _tmp3 = None
                
                _tmp1 = _tmp3
                if (_tmp1 is _default):
                    _tmp1 = u'${risk/caption2|nothing}'
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
                    _write(((' title="' + _tmp1) + '"'))
                'join(parts(value("_path(large, request, True, \'url\')"), value(\'None\')),)'
                try:
                    u'large/url'
                    _tmp3 = _path(large, econtext['request'], True, 'url')
                except Exception, e:
                    u'nothing'
                    _tmp3 = None
                
                _tmp1 = _tmp3
                if (_tmp1 is _default):
                    _tmp1 = u'${large/url|nothing}'
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
                _write('>')
                attrs = _attrs_261238416
                'join(value("_path(thumb, request, True, \'width\')"),)'
                _write(u'<img alt=""')
                _tmp1 = _path(thumb, econtext['request'], True, 'width')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/width}'
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
                    _write(((' with="' + _tmp1) + '"'))
                'join(value("_path(thumb, request, True, \'height\')"),)'
                _tmp1 = _path(thumb, econtext['request'], True, 'height')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/height}'
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
                    _write(((' height="' + _tmp1) + '"'))
                'join(value("_path(thumb, request, True, \'url\')"),)'
                _tmp1 = _path(thumb, econtext['request'], True, 'url')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/url}'
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
                    _write(((' src="' + _tmp1) + '"'))
                _write(u' class="floatBefore" /></a>')
            _write(u'\n      ')
            "images.scale('image3', width=120, height=172, direction='thumbnail')"
            thumb = _lookup_attr(images, 'scale')('image3', width=120, height=172, direction='thumbnail')
            "images.scale('image3', width=590, height=1900, direction='thumbnail')"
            large = _lookup_attr(images, 'scale')('image3', width=590, height=1900, direction='thumbnail')
            'thumb'
            _tmp1 = _path(thumb, econtext['request'], True)
            if _tmp1:
                pass
                attrs = _attrs_261238352
                'join(parts(value("_path(risk, request, True, \'caption3\')"), value(\'None\')),)'
                _write(u'<a rel="fancybox"')
                try:
                    u'risk/caption3'
                    _tmp3 = _path(econtext['risk'], econtext['request'], True, 'caption3')
                except Exception, e:
                    u'nothing'
                    _tmp3 = None
                
                _tmp1 = _tmp3
                if (_tmp1 is _default):
                    _tmp1 = u'${risk/caption3|nothing}'
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
                    _write(((' title="' + _tmp1) + '"'))
                'join(parts(value("_path(large, request, True, \'url\')"), value(\'None\')),)'
                try:
                    u'large/url'
                    _tmp3 = _path(large, econtext['request'], True, 'url')
                except Exception, e:
                    u'nothing'
                    _tmp3 = None
                
                _tmp1 = _tmp3
                if (_tmp1 is _default):
                    _tmp1 = u'${large/url|nothing}'
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
                _write('>')
                attrs = _attrs_261238544
                'join(value("_path(thumb, request, True, \'width\')"),)'
                _write(u'<img alt=""')
                _tmp1 = _path(thumb, econtext['request'], True, 'width')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/width}'
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
                    _write(((' with="' + _tmp1) + '"'))
                'join(value("_path(thumb, request, True, \'height\')"),)'
                _tmp1 = _path(thumb, econtext['request'], True, 'height')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/height}'
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
                    _write(((' height="' + _tmp1) + '"'))
                'join(value("_path(thumb, request, True, \'url\')"),)'
                _tmp1 = _path(thumb, econtext['request'], True, 'url')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/url}'
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
                    _write(((' src="' + _tmp1) + '"'))
                _write(u' class="floatBefore" /></a>')
            _write(u'\n      ')
            "images.scale('image4', width=120, height=172, direction='thumbnail')"
            thumb = _lookup_attr(images, 'scale')('image4', width=120, height=172, direction='thumbnail')
            "images.scale('image4', width=590, height=1900, direction='thumbnail')"
            large = _lookup_attr(images, 'scale')('image4', width=590, height=1900, direction='thumbnail')
            'thumb'
            _tmp1 = _path(thumb, econtext['request'], True)
            if _tmp1:
                pass
                attrs = _attrs_261238480
                'join(parts(value("_path(risk, request, True, \'caption4\')"), value(\'None\')),)'
                _write(u'<a rel="fancybox"')
                try:
                    u'risk/caption4'
                    _tmp3 = _path(econtext['risk'], econtext['request'], True, 'caption4')
                except Exception, e:
                    u'nothing'
                    _tmp3 = None
                
                _tmp1 = _tmp3
                if (_tmp1 is _default):
                    _tmp1 = u'${risk/caption4|nothing}'
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
                    _write(((' title="' + _tmp1) + '"'))
                'join(parts(value("_path(large, request, True, \'url\')"), value(\'None\')),)'
                try:
                    u'large/url'
                    _tmp3 = _path(large, econtext['request'], True, 'url')
                except Exception, e:
                    u'nothing'
                    _tmp3 = None
                
                _tmp1 = _tmp3
                if (_tmp1 is _default):
                    _tmp1 = u'${large/url|nothing}'
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
                _write('>')
                attrs = _attrs_261238672
                'join(value("_path(thumb, request, True, \'width\')"),)'
                _write(u'<img alt=""')
                _tmp1 = _path(thumb, econtext['request'], True, 'width')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/width}'
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
                    _write(((' with="' + _tmp1) + '"'))
                'join(value("_path(thumb, request, True, \'height\')"),)'
                _tmp1 = _path(thumb, econtext['request'], True, 'height')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/height}'
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
                    _write(((' height="' + _tmp1) + '"'))
                'join(value("_path(thumb, request, True, \'url\')"),)'
                _tmp1 = _path(thumb, econtext['request'], True, 'url')
                if (_tmp1 is _default):
                    _tmp1 = u'${thumb/url}'
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
                    _write(((' src="' + _tmp1) + '"'))
                _write(u' class="floatBefore" /></a>')
            _write(u'\n    ')
            _write(u'</p>')
        _write(u'\n    ')
        'view/use_problem_description'
        use_problem_description = _path(econtext['view'], econtext['request'], True, 'use_problem_description')
        try:
            'show_statement'
            _tmp1 = _path(econtext['show_statement'], econtext['request'], True)
        except Exception, e:
            'nothing'
            _tmp1 = None
        
        if _tmp1:
            pass
            u"not(_path(view, request, True, 'risk_present'))"
            _write(u'\n      ')
            _tmp1 = not _path(econtext['view'], econtext['request'], True, 'risk_present')
            if _tmp1:
                pass
                u"''"
                _write(u'')
                _default.value = default = ''
                'risk/title'
                _content = _path(econtext['risk'], econtext['request'], True, 'title')
                attrs = _attrs_261263504
                u'_content'
                _write(u'<h2>')
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
                "risk.type=='top5'"
                _write(u'</h2>\n        ')
                _tmp1 = (_lookup_attr(econtext['risk'], 'type') == 'top5')
                if _tmp1:
                    pass
                    attrs = _attrs_261263568
                    u"%(translate)s('top5_risk_not_present', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write(u'<p>')
                    _result = _translate('top5_risk_not_present', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp1 = (_result is not _marker)
                    if _tmp1:
                        pass
                        u'_result'
                        _tmp2 = _result
                        _write(_tmp2)
                    else:
                        pass
                        _write(u'\n            This risk is not present in your organisation, but since the sector organisation considers this one of the priority risks it must be\n            included in this report.\n        ')
                    _write(u'</p>')
                _write(u'\n      ')
            'view/risk_present'
            _write(u'\n      ')
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'risk_present')
            if _tmp1:
                pass
                u"u'The fridges are checked daily.'"
                _write(u'\n        ')
                _default.value = default = u'The fridges are checked daily.'
                'use_problem_description'
                _tmp1 = _path(use_problem_description, econtext['request'], True)
                if _tmp1:
                    pass
                    'risk/problem_description'
                    _content = _path(econtext['risk'], econtext['request'], True, 'problem_description')
                    attrs = _attrs_261263696
                    u'_content'
                    _write(u'<h2>')
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
                    _write(u'</h2>')
                u'not(_path(use_problem_description, request, True, ))'
                _write(u'\n        ')
                _tmp1 = not _path(use_problem_description, econtext['request'], True)
                if _tmp1:
                    pass
                    u"u'The fridges are checked daily.'"
                    _write(u'\n          ')
                    _default.value = default = u'The fridges are checked daily.'
                    'risk/title'
                    _content = _path(econtext['risk'], econtext['request'], True, 'title')
                    attrs = _attrs_261263888
                    u'_content'
                    _write(u'<h2>')
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
                    _write(u'</h2>\n          ')
                    attrs = _attrs_261263952
                    _write(u'<p class="negation">\n            ')
                    attrs = _attrs_261264080
                    _write(u'<em>')
                    attrs = _attrs_261264208
                    u"%(translate)s('warn_risk_present', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write(u'<strong class="icon warning">\u26a0</strong>\n                ')
                    _result = _translate('warn_risk_present', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp1 = (_result is not _marker)
                    if _tmp1:
                        pass
                        u'_result'
                        _tmp2 = _result
                        _write(_tmp2)
                    else:
                        pass
                        _write(u' You responded negative to the above statement.')
                    _write(u'\n            </em>\n        </p>\n        ')
                _write(u'')
            _write(u'')
        _write(u'\n    ')
        u"u'\\n      The temperature in a fridge is critical to storing food. If the\\n      temperature is too high or fluctuates too much food can start\\n      rotting quickly.\\n    '"
        _default.value = default = u'\n      The temperature in a fridge is critical to storing food. If the\n      temperature is too high or fluctuates too much food can start\n      rotting quickly.\n    '
        'risk/description'
        _content = _path(econtext['risk'], econtext['request'], True, 'description')
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
        _write(u'\n  \n\n  ')
        _domain = _tmp_domain0
        return
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/webhelpers.pt'
registry[('risk_info', False, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_261237776 = _loads('(dp1\nVid\np2\nVoira_legal_show_anchor\np3\ns.')
    _attrs_261236624 = _loads('(dp1\nVstyle\np2\nVdisplay:none\np3\nsVid\np4\nVlegal_reference\np5\ns.')
    _attrs_261237712 = _loads('(dp1\nVclass\np2\nVoira_legal_header\np3\ns.')
    _attrs_261237840 = _loads('(dp1\nVid\np2\nVoira_legal_hide_anchor\np3\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_261236944 = _loads('(dp1\nVclear\np2\nVall\np3\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u"%(scope)s['%(out)s'], %(scope)s['%(write)s']"
        (_out, _write, ) = (econtext['_out'], econtext['_write'], )
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        _tmp_domain0 = _domain
        u"'euphorie'"
        _domain = 'euphorie'
        "request.get('show_legal') not in ['0', None]"
        _write(u'')
        legal_shown = (_lookup_attr(econtext['request'], 'get')('show_legal') not in ['0', None, ])
        "legal_shown and '0' or '1'"
        toggle_legal = ((legal_shown and '0') or '1')
        'risk/legal_reference'
        _tmp1 = _path(econtext['risk'], econtext['request'], True, 'legal_reference')
        if _tmp1:
            pass
            _write(u'')
            attrs = _attrs_261237712
            'oira_legal_header'
            _write(u'<h4')
            _tmp1 = 'oira_legal_header'
            if (_tmp1 is _default):
                _tmp1 = u'oira_legal_header'
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
            u"%(translate)s('header_legal_references', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write('>')
            _result = _translate('header_legal_references', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Legal and policy references')
            _write(u'</h4>\n        ')
            attrs = _attrs_261237776
            '${request/ACTUAL_URL}?show_legal=${toggle_legal}'
            _write(u'<a id="oira_legal_show_anchor"')
            _tmp1 = ('%s%s%s' % (_path(econtext['request'], econtext['request'], True, 'ACTUAL_URL'), '?show_legal=', _path(toggle_legal, econtext['request'], True), ))
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
            "not legal_shown and 'display: None'"
            _tmp1 = (not legal_shown and 'display: None')
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
                _write(((' style="' + _tmp1) + '"'))
            u"%(translate)s('action_hide', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write('>')
            _result = _translate('action_hide', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Hide')
            _write(u'</a>\n        ')
            attrs = _attrs_261237840
            '${request/ACTUAL_URL}?show_legal=${toggle_legal}'
            _write(u'<a id="oira_legal_hide_anchor"')
            _tmp1 = ('%s%s%s' % (_path(econtext['request'], econtext['request'], True, 'ACTUAL_URL'), '?show_legal=', _path(toggle_legal, econtext['request'], True), ))
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
            "legal_shown and 'display: None'"
            _tmp1 = (legal_shown and 'display: None')
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
                _write(((' style="' + _tmp1) + '"'))
            u"%(translate)s('action_show', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write('>')
            _result = _translate('action_show', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Show')
            _write(u'</a>\n        ')
            attrs = _attrs_261236944
            _write(u'<br clear="all" />\n        \n        ')
            attrs = _attrs_261236624
            "legal_shown and 'display:block' or 'display:none'"
            _write(u'<div id="legal_reference"')
            _tmp1 = ((legal_shown and 'display:block') or 'display:none')
            if (_tmp1 is _default):
                _tmp1 = u'display:none'
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
                _write(((' style="' + _tmp1) + '"'))
            u"u'\\n                    The requirements for fridges are defined in section 13.1 section a\\n                    of the health code.\\n            '"
            _write(u'>\n\n            ')
            _default.value = default = u'\n                    The requirements for fridges are defined in section 13.1 section a\n                    of the health code.\n            '
            'risk/legal_reference'
            _content = _path(econtext['risk'], econtext['request'], True, 'legal_reference')
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
            _write(u' \n        </div>\n    ')
        _write(u'')
        _write(u'\n\n')
        _domain = _tmp_domain0
        return
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/webhelpers.pt'
registry[('risk_legal_collapsible', False, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
def bind():
    from cPickle import loads as _loads
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_261691984 = _loads('(dp1\n.')
    _attrs_261691792 = _loads('(dp1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u"%(scope)s['%(out)s'], %(scope)s['%(write)s']"
        (_out, _write, ) = (econtext['_out'], econtext['_write'], )
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        _tmp_domain0 = _domain
        u"'euphorie'"
        _domain = 'euphorie'
        'risk/legal_reference'
        _write(u'')
        _tmp1 = _path(econtext['risk'], econtext['request'], True, 'legal_reference')
        if _tmp1:
            pass
            _write(u'')
            attrs = _attrs_261691792
            u"%(translate)s('header_legal_references', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h4>')
            _result = _translate('header_legal_references', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Legal and policy references')
            u"u'\\n        The requirements for fridges are defined in section 13.1 section a\\n        of the health code.\\n      '"
            _write(u'</h4>\n\n      ')
            _default.value = default = u'\n        The requirements for fridges are defined in section 13.1 section a\n        of the health code.\n      '
            'risk/legal_reference'
            _content = _path(econtext['risk'], econtext['request'], True, 'legal_reference')
            attrs = _attrs_261691984
            u'_content'
            _write(u'<p>')
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
            _write(u'</p> \n    ')
        _write(u'\n  \n  ')
        _domain = _tmp_domain0
        return
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/webhelpers.pt'
registry[('risk_legal', False, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
