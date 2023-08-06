registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_230979920 = _loads('(dp1\nVclass\np2\nVerror\np3\ns.')
    _attrs_232368208 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
    _attrs_232754000 = _loads('(dp1\n.')
    _path_exists = _loads("ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveExistsTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n(dp5\nS'proxify'\np6\ncz3c.pt.expressions\nidentity\np7\nsb.")
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_230979728 = _loads('(dp1\nVname\np2\nVnext\np3\nsVvalue\np4\nVprevious\np5\nsVtype\np6\nVsubmit\np7\nsVclass\np8\nVprevious floatBefore back\np9\ns.')
    _attrs_230979408 = _loads('(dp1\nVclass\np2\nVbuttonBar\np3\ns.')
    _attrs_230981008 = _loads('(dp1\n.')
    _attrs_230979280 = _loads('(dp1\n.')
    _attrs_230981200 = _loads('(dp1\nVclass\np2\nVerror\np3\ns.')
    _attrs_230980496 = _loads('(dp1\nVname\np2\nVemail\np3\nsVvalue\np4\nV${request/email|nothing}\np5\nsVtype\np6\nVtext\np7\nsVclass\np8\nVautofocus\np9\ns.')
    _attrs_230980176 = _loads('(dp1\nVtype\np2\nVpassword\np3\nsVname\np4\nVpassword2:utf8:ustring\np5\ns.')
    _attrs_230979472 = _loads('(dp1\nVid\np2\nVnavigation\np3\ns.')
    _attrs_229744080 = _loads('(dp1\n.')
    _attrs_232753808 = _loads('(dp1\nVclass\np2\nVerror\np3\ns.')
    _attrs_230978768 = _loads('(dp1\nVtype\np2\nVpassword\np3\nsVname\np4\nVpassword1:utf8:ustring\np5\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_230977936 = _loads('(dp1\n.')
    _attrs_230979600 = _loads('(dp1\nVname\np2\nVnext\np3\nsVvalue\np4\nVnext\np5\nsVtype\np6\nVsubmit\np7\nsVclass\np8\nVnext floatAfter\np9\ns.')
    _attrs_229742544 = _loads('(dp1\n.')
    _lookup_tile = _loads('cplonetheme.nuplone.tiles.tales\n_lookup_tile\np1\n.')
    _attrs_229740688 = _loads('(dp1\n.')
    _attrs_230978512 = _loads('(dp1\n.')
    _attrs_232754320 = _loads('(dp1\nVaccept-charset\np2\nVUTF-8\np3\nsVaction\np4\nV${request/URL}\np5\nsVmethod\np6\nVpost\np7\nsVenctype\np8\nVmultipart/form-data\np9\ns.')
    _attrs_232754128 = _loads('(dp1\nVclass\np2\nVcountry ${country}\np3\nsVid\np4\nVcountry\np5\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_230978000 = _loads('(dp1\n.')
    _attrs_230981072 = _loads('(dp1\nVname\np2\nVcame_from\np3\nsVtype\np4\nVhidden\np5\nsVvalue\np6\nV${request/came_from}\np7\ns.')
    _attrs_230977744 = _loads('(dp1\nVclass\np2\nVconcise\np3\ns.')
    _attrs_230979088 = _loads('(dp1\nVhref\np2\nV${webhelpers/help_url}#authentication\np3\ns.')
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
        'nocall:request/client'
        client = _path(econtext['request'], econtext['request'], False, 'client')
        'nocall:context/@@webhelpers'
        webhelpers = _path(econtext['context'], econtext['request'], False, '@@webhelpers')
        attrs = _attrs_232368208
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml">\n  ')
        attrs = _attrs_229744080
        _write(u'<head>\n    ')
        attrs = _attrs_229740688
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
        attrs = _attrs_229742544
        _write(u'<body>\n    ')
        attrs = _attrs_232754000
        u"%(translate)s('header_register', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h1>')
        _result = _translate('header_register', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Register')
        'webhelpers/country'
        _write(u'</h1>\n\n    ')
        country = _path(webhelpers, econtext['request'], True, 'country')
        attrs = _attrs_232754128
        "join(u'country ', value('_path(country, request, True, )'))"
        _write(u'<p')
        _tmp1 = ('%s%s' % ('country ', _path(country, econtext['request'], True), ))
        if (_tmp1 is _default):
            _tmp1 = u'country ${country}'
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
        u'country'
        _write(u' id="country">')
        _tmp1 = _path(country, econtext['request'], True)
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
        _write(u'</p>\n    \n    ')
        try:
            'view/error'
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'error')
        except Exception, e:
            'nothing'
            _tmp1 = None
        
        if _tmp1:
            pass
            attrs = _attrs_232753808
            u'view/error'
            _write(u'<p class="error">')
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'error')
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
            _write(u'</p>')
        'view/errors'
        _write(u'\n\n    ')
        errors = _path(econtext['view'], econtext['request'], True, 'errors')
        attrs = _attrs_232754320
        'join(value("_path(request, request, True, \'URL\')"),)'
        _write(u'<form enctype="multipart/form-data" accept-charset="UTF-8" method="post"')
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
        try:
            'request/came_from'
            _tmp1 = _path(econtext['request'], econtext['request'], True, 'came_from')
        except Exception, e:
            'nothing'
            _tmp1 = None
        
        if _tmp1:
            pass
            attrs = _attrs_230981072
            'join(value("_path(request, request, True, \'came_from\')"),)'
            _write(u'<input type="hidden" name="came_from"')
            _tmp1 = _path(econtext['request'], econtext['request'], True, 'came_from')
            if (_tmp1 is _default):
                _tmp1 = u'${request/came_from}'
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
                _write(((' value="' + _tmp1) + '"'))
            _write(' />')
        _write(u'\n      ')
        attrs = _attrs_230978000
        u"%(translate)s('header_register', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h2>')
        _result = _translate('header_register', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Register')
        _write(u'</h2>\n      ')
        attrs = _attrs_230977744
        _write(u'<fieldset class="concise">\n        ')
        attrs = _attrs_230977936
        u"%(translate)s('label_email', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<label>')
        _result = _translate('label_email', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Email address')
        _write(u' ')
        attrs = _attrs_230980496
        'join(parts(value("_path(request, request, True, \'email\')"), value(\'None\')),)'
        _write(u'<input class="autofocus" type="text" name="email"')
        try:
            u'request/email'
            _tmp3 = _path(econtext['request'], econtext['request'], True, 'email')
        except Exception, e:
            u'nothing'
            _tmp3 = None
        
        _tmp1 = _tmp3
        if (_tmp1 is _default):
            _tmp1 = u'${request/email|nothing}'
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
            _write(((' value="' + _tmp1) + '"'))
        u"u'Invalid login name'"
        _write(u' />\n          ')
        _default.value = default = u'Invalid login name'
        try:
            u"_path_exists(errors, request, True, 'email')"
            _tmp1 = _path_exists(errors, econtext['request'], True, 'email')
        except NameError, e:
            u'False'
            _tmp1 = False
        
        if _tmp1:
            pass
            'errors/email'
            _content = _path(errors, econtext['request'], True, 'email')
            attrs = _attrs_230981200
            u'_content'
            _write(u'<em class="error">')
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
            _write(u'</em>')
        _write(u'</label>\n        ')
        attrs = _attrs_230981008
        u"%(translate)s('label_new_password', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<label>')
        _result = _translate('label_new_password', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Desired password')
        _write(u' ')
        attrs = _attrs_230978768
        u"u'Invalid password'"
        _write(u'<input type="password" name="password1:utf8:ustring" />\n          ')
        _default.value = default = u'Invalid password'
        try:
            u"_path_exists(errors, request, True, 'password')"
            _tmp1 = _path_exists(errors, econtext['request'], True, 'password')
        except NameError, e:
            u'False'
            _tmp1 = False
        
        if _tmp1:
            pass
            'errors/password'
            _content = _path(errors, econtext['request'], True, 'password')
            attrs = _attrs_230979920
            u'_content'
            _write(u'<em class="error">')
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
            _write(u'</em>')
        _write(u'</label>\n        ')
        attrs = _attrs_230978512
        u"%(translate)s('label_password_confirm', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<label>')
        _result = _translate('label_password_confirm', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Again password')
        _write(u' ')
        attrs = _attrs_230980176
        _write(u'<input type="password" name="password2:utf8:ustring" /> </label>\n      </fieldset>\n      ')
        attrs = _attrs_230979408
        _write(u'<p class="buttonBar">\n        ')
        attrs = _attrs_230979728
        u"%(translate)s('label_previous', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<button type="submit" name="next" value="previous" class="previous floatBefore back">')
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
        _write(u'</button>\n        ')
        attrs = _attrs_230979600
        u"%(translate)s('label_next', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<button type="submit" name="next" value="next" class="next floatAfter">')
        _result = _translate('label_next', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Next')
        _write(u'</button>\n      </p>\n    </form>\n\n    ')
        attrs = _attrs_230979472
        'webhelpers/macros/homelink'
        _write(u'<ul id="navigation">\n      ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'homelink')
        u'{}'
        _tmp = {}
        'webhelpers/macros/homelink'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, client=client, _out=_out, _write=_write)
        _write(u'\n      ')
        attrs = _attrs_230979280
        _write(u'<li>')
        attrs = _attrs_230979088
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

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/register.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
