registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _attrs_203946960 = _loads('(dp1\nVclass\np2\nVbuttonBar\np3\ns.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_203947472 = _loads('(dp1\nVsrc\np2\nV${thumb/url}\np3\nsVheight\np4\nV${thumb/height}\np5\nsVwidth\np6\nV${thumb/width}\np7\nsValt\np8\nV\nsVclass\np9\nVfloatBefore\np10\ns.')
    _attrs_203947216 = _loads('(dp1\nVhref\np2\nV${survey_url}/start\np3\ns.')
    _attrs_203945424 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_204014352 = _loads('(dp1\n.')
    _attrs_204014416 = _loads('(dp1\nVhref\np2\nV${webhelpers/session_overview_url}\np3\ns.')
    _attrs_203946000 = _loads('(dp1\nVclass\np2\nVcomplete\np3\nsVid\np4\nVstep-3\np5\ns.')
    _attrs_204014544 = _loads('(dp1\nVhref\np2\nV${webhelpers/help_url}#actionplan\np3\ns.')
    _attrs_203947856 = _loads('(dp1\nVid\np2\nVsteps\np3\ns.')
    _attrs_204013904 = _loads('(dp1\nVhref\np2\nV${survey_url}/report\np3\ns.')
    _attrs_204014224 = _loads('(dp1\n.')
    _attrs_203945360 = _loads('(dp1\nVhref\np2\nV${view/next_url}\np3\nsVclass\np4\nVbutton-medium floatAfter\np5\ns.')
    _attrs_204014672 = _loads('(dp1\nVhref\np2\nV${webhelpers/survey_url}/status\np3\ns.')
    _attrs_203972304 = _loads('(dp1\nVid\np2\nVstep-5\np3\ns.')
    _attrs_203947536 = _loads('(dp1\n.')
    _attrs_204014480 = _loads('(dp1\n.')
    _attrs_204014800 = _loads('(dp1\nVhref\np2\nV${webhelpers/country_url}/account-settings\np3\ns.')
    _attrs_203944848 = _loads('(dp1\nVclass\np2\nVactionplan ${webhelpers/extra_css}\np3\ns.')
    _attrs_203972048 = _loads('(dp1\nVclass\np2\nVactive current\np3\nsVid\np4\nVstep-4\np5\ns.')
    _attrs_204014160 = _loads('(dp1\n.')
    _attrs_204014288 = _loads('(dp1\nVhref\np2\nV${webhelpers/country_url}/logout\np3\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_203945872 = _loads('(dp1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _attrs_203946704 = _loads('(dp1\nVhref\np2\nV${large/url|nothing}\np3\nsVrel\np4\nVfancybox\np5\nsVtitle\np6\nV${module/caption|nothing}\np7\ns.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _attrs_203945040 = _loads('(dp1\n.')
    _attrs_203971984 = _loads('(dp1\nVhref\np2\nV${survey_url}/identification\np3\ns.')
    _attrs_203946128 = _loads('(dp1\nVclass\np2\nVcomplete\np3\nsVid\np4\nVstep-1\np5\ns.')
    _attrs_203946064 = _loads('(dp1\nVclass\np2\nVcomplete\np3\nsVid\np4\nVstep-2\np5\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_203944528 = _loads('(dp1\nVhref\np2\nV${view/previous_url}\np3\nsVclass\np4\nVbutton-medium floatBefore back\np5\ns.')
    _attrs_204014608 = _loads('(dp1\n.')
    _lookup_tile = _loads('cplonetheme.nuplone.tiles.tales\n_lookup_tile\np1\n.')
    _attrs_203946192 = _loads('(dp1\nVid\np2\nVnavigation\np3\ns.')
    _attrs_203947408 = _loads('(dp1\nVclass\np2\nVgallery\np3\ns.')
    _attrs_203972240 = _loads('(dp1\nVhref\np2\nV${survey_url}/evaluation\np3\ns.')
    _attrs_203972496 = _loads('(dp1\nVhref\np2\nV${survey_url}/actionplan\np3\ns.')
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
        attrs = _attrs_203945424
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml">\n  ')
        attrs = _attrs_203945872
        _write(u'<head>\n    ')
        attrs = _attrs_203945040
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
        'nocall:view/module'
        _write(u'\n  </head>\n  ')
        module = _path(econtext['view'], econtext['request'], False, 'module')
        attrs = _attrs_203944848
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
        attrs = _attrs_203947536
        u'view/title'
        _write(u'<h1>')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'title')
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
        'module/@@images'
        _write(u'</h1>\n\n    ')
        images = _path(module, econtext['request'], True, '@@images')
        'module.image is not None'
        _tmp1 = (_lookup_attr(module, 'image') is not None)
        if _tmp1:
            pass
            attrs = _attrs_203947408
            "images.scale('image', width=150, height=500, direction='thumbnail')"
            _write(u'<p class="gallery">\n        ')
            thumb = _lookup_attr(images, 'scale')('image', width=150, height=500, direction='thumbnail')
            'thumb'
            _tmp1 = _path(thumb, econtext['request'], True)
            if _tmp1:
                pass
                "images.getImageSize('image') > (150*1.5, 500)"
                _write(u'')
                has_larger_version = (_lookup_attr(images, 'getImageSize')('image') > ((150 * 1.5), 500, ))
                "has_larger_version and images.scale('image', width=590, height=1900, direction='thumbnail')"
                large = (has_larger_version and _lookup_attr(images, 'scale')('image', width=590, height=1900, direction='thumbnail'))
                attrs = _attrs_203946704
                u'not(_path(has_larger_version, request, True, ))'
                _tmp1 = not _path(has_larger_version, econtext['request'], True)
                if not _tmp1:
                    pass
                    'join(parts(value("_path(module, request, True, \'caption\')"), value(\'None\')),)'
                    _write(u'<a rel="fancybox"')
                    try:
                        u'module/caption'
                        _tmp4 = _path(module, econtext['request'], True, 'caption')
                    except Exception, e:
                        u'nothing'
                        _tmp4 = None
                    
                    _tmp2 = _tmp4
                    if (_tmp2 is _default):
                        _tmp2 = u'${module/caption|nothing}'
                    if ((_tmp2 is not None) and (_tmp2 is not False)):
                        if (_tmp2.__class__ not in (str, unicode, int, float, )):
                            _tmp2 = unicode(_translate(_tmp2, domain=_domain, mapping=None, target_language=target_language, default=None))
                        else:
                            if not isinstance(_tmp2, unicode):
                                _tmp2 = unicode(str(_tmp2), 'UTF-8')
                        if ('&' in _tmp2):
                            if (';' in _tmp2):
                                _tmp2 = _re_amp.sub('&amp;', _tmp2)
                            else:
                                _tmp2 = _tmp2.replace('&', '&amp;')
                        if ('<' in _tmp2):
                            _tmp2 = _tmp2.replace('<', '&lt;')
                        if ('>' in _tmp2):
                            _tmp2 = _tmp2.replace('>', '&gt;')
                        if ('"' in _tmp2):
                            _tmp2 = _tmp2.replace('"', '&quot;')
                        _write(((' title="' + _tmp2) + '"'))
                    'join(parts(value("_path(large, request, True, \'url\')"), value(\'None\')),)'
                    try:
                        u'large/url'
                        _tmp4 = _path(large, econtext['request'], True, 'url')
                    except Exception, e:
                        u'nothing'
                        _tmp4 = None
                    
                    _tmp2 = _tmp4
                    if (_tmp2 is _default):
                        _tmp2 = u'${large/url|nothing}'
                    if ((_tmp2 is not None) and (_tmp2 is not False)):
                        if (_tmp2.__class__ not in (str, unicode, int, float, )):
                            _tmp2 = unicode(_translate(_tmp2, domain=_domain, mapping=None, target_language=target_language, default=None))
                        else:
                            if not isinstance(_tmp2, unicode):
                                _tmp2 = unicode(str(_tmp2), 'UTF-8')
                        if ('&' in _tmp2):
                            if (';' in _tmp2):
                                _tmp2 = _re_amp.sub('&amp;', _tmp2)
                            else:
                                _tmp2 = _tmp2.replace('&', '&amp;')
                        if ('<' in _tmp2):
                            _tmp2 = _tmp2.replace('<', '&lt;')
                        if ('>' in _tmp2):
                            _tmp2 = _tmp2.replace('>', '&gt;')
                        if ('"' in _tmp2):
                            _tmp2 = _tmp2.replace('"', '&quot;')
                        _write(((' href="' + _tmp2) + '"'))
                    _write('>')
                _write(u'\n            ')
                attrs = _attrs_203947472
                'join(value("_path(thumb, request, True, \'url\')"),)'
                _write(u'<img alt="" class="floatBefore"')
                _tmp2 = _path(thumb, econtext['request'], True, 'url')
                if (_tmp2 is _default):
                    _tmp2 = u'${thumb/url}'
                if ((_tmp2 is not None) and (_tmp2 is not False)):
                    if (_tmp2.__class__ not in (str, unicode, int, float, )):
                        _tmp2 = unicode(_translate(_tmp2, domain=_domain, mapping=None, target_language=target_language, default=None))
                    else:
                        if not isinstance(_tmp2, unicode):
                            _tmp2 = unicode(str(_tmp2), 'UTF-8')
                    if ('&' in _tmp2):
                        if (';' in _tmp2):
                            _tmp2 = _re_amp.sub('&amp;', _tmp2)
                        else:
                            _tmp2 = _tmp2.replace('&', '&amp;')
                    if ('<' in _tmp2):
                        _tmp2 = _tmp2.replace('<', '&lt;')
                    if ('>' in _tmp2):
                        _tmp2 = _tmp2.replace('>', '&gt;')
                    if ('"' in _tmp2):
                        _tmp2 = _tmp2.replace('"', '&quot;')
                    _write(((' src="' + _tmp2) + '"'))
                'join(value("_path(thumb, request, True, \'width\')"),)'
                _tmp2 = _path(thumb, econtext['request'], True, 'width')
                if (_tmp2 is _default):
                    _tmp2 = u'${thumb/width}'
                if ((_tmp2 is not None) and (_tmp2 is not False)):
                    if (_tmp2.__class__ not in (str, unicode, int, float, )):
                        _tmp2 = unicode(_translate(_tmp2, domain=_domain, mapping=None, target_language=target_language, default=None))
                    else:
                        if not isinstance(_tmp2, unicode):
                            _tmp2 = unicode(str(_tmp2), 'UTF-8')
                    if ('&' in _tmp2):
                        if (';' in _tmp2):
                            _tmp2 = _re_amp.sub('&amp;', _tmp2)
                        else:
                            _tmp2 = _tmp2.replace('&', '&amp;')
                    if ('<' in _tmp2):
                        _tmp2 = _tmp2.replace('<', '&lt;')
                    if ('>' in _tmp2):
                        _tmp2 = _tmp2.replace('>', '&gt;')
                    if ('"' in _tmp2):
                        _tmp2 = _tmp2.replace('"', '&quot;')
                    _write(((' width="' + _tmp2) + '"'))
                'join(value("_path(thumb, request, True, \'height\')"),)'
                _tmp2 = _path(thumb, econtext['request'], True, 'height')
                if (_tmp2 is _default):
                    _tmp2 = u'${thumb/height}'
                if ((_tmp2 is not None) and (_tmp2 is not False)):
                    if (_tmp2.__class__ not in (str, unicode, int, float, )):
                        _tmp2 = unicode(_translate(_tmp2, domain=_domain, mapping=None, target_language=target_language, default=None))
                    else:
                        if not isinstance(_tmp2, unicode):
                            _tmp2 = unicode(str(_tmp2), 'UTF-8')
                    if ('&' in _tmp2):
                        if (';' in _tmp2):
                            _tmp2 = _re_amp.sub('&amp;', _tmp2)
                        else:
                            _tmp2 = _tmp2.replace('&', '&amp;')
                    if ('<' in _tmp2):
                        _tmp2 = _tmp2.replace('<', '&lt;')
                    if ('>' in _tmp2):
                        _tmp2 = _tmp2.replace('>', '&gt;')
                    if ('"' in _tmp2):
                        _tmp2 = _tmp2.replace('"', '&quot;')
                    _write(((' height="' + _tmp2) + '"'))
                _write(u' />\n            ')
                if not _tmp1:
                    pass
                    _write(u'</a>')
                _write(u'\n        ')
            _write(u'\n    ')
            _write(u'</p>')
        _write(u'\n\n    ')
        u"u'\\n      This is a description of the module.\\n\\n      Nam eget tincidunt arcu. Suspendisse potenti. Nulla gravida rutrum\\n      turpis, nec aliquam turpis hendrerit eget. In viverra velit at erat\\n      commodo sed pellentesque sem fringilla. Vivamus mattis convallis tellus a\\n      malesuada. Vivamus luctus nunc eu sapien viverra vel semper nibh auctor.\\n      Pellentesque habitant morbi tristique senectus et netus et malesuada\\n      fames ac turpis egestas. Quisque arcu diam, lobortis a dapibus non,\\n      vulputate sit amet justo. Cum sociis natoque penatibus et magnis dis\\n      parturient montes, nascetur ridiculus mus. Nunc pellentesque nibh sed\\n      orci tempor viverra.  Nullam ullamcorper sollicitudin erat nec egestas.\\n      Phasellus pulvinar elementum elit, sit amet malesuada magna tincidunt\\n      ut.'"
        _default.value = default = u'\n      This is a description of the module.\n\n      Nam eget tincidunt arcu. Suspendisse potenti. Nulla gravida rutrum\n      turpis, nec aliquam turpis hendrerit eget. In viverra velit at erat\n      commodo sed pellentesque sem fringilla. Vivamus mattis convallis tellus a\n      malesuada. Vivamus luctus nunc eu sapien viverra vel semper nibh auctor.\n      Pellentesque habitant morbi tristique senectus et netus et malesuada\n      fames ac turpis egestas. Quisque arcu diam, lobortis a dapibus non,\n      vulputate sit amet justo. Cum sociis natoque penatibus et magnis dis\n      parturient montes, nascetur ridiculus mus. Nunc pellentesque nibh sed\n      orci tempor viverra.  Nullam ullamcorper sollicitudin erat nec egestas.\n      Phasellus pulvinar elementum elit, sit amet malesuada magna tincidunt\n      ut.'
        'module/description'
        _content = _path(module, econtext['request'], True, 'description')
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
        u"u'\\n      This module has a solution direction. This is it.\\n    '"
        _write(u'\n\n    ')
        _default.value = default = u'\n      This module has a solution direction. This is it.\n    '
        'view/use_solution_direction'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'use_solution_direction')
        if _tmp1:
            pass
            'module/solution_direction'
            _content = _path(module, econtext['request'], True, 'solution_direction')
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
        _write(u'\n    ')
        attrs = _attrs_203946960
        _write(u'<p class="buttonBar">\n      ')
        attrs = _attrs_203944528
        'join(value("_path(view, request, True, \'previous_url\')"),)'
        _write(u'<a class="button-medium floatBefore back"')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'previous_url')
        if (_tmp1 is _default):
            _tmp1 = u'${view/previous_url}'
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
        _write('>')
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
        _write(u'</a>\n      ')
        attrs = _attrs_203945360
        'join(value("_path(view, request, True, \'next_url\')"),)'
        _write(u'<a class="button-medium floatAfter"')
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
        u"%(translate)s('label_next', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write('>')
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
        'webhelpers/survey_url'
        _write(u'</a>\n    </p>\n    <!--[if lte IE 7]> <br/> <![endif]-->\n    ')
        survey_url = _path(webhelpers, econtext['request'], True, 'survey_url')
        attrs = _attrs_203947856
        _write(u'<ol id="steps">\n      ')
        attrs = _attrs_203946128
        _write(u'<li class="complete" id="step-1">\n        ')
        attrs = _attrs_203947216
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
        attrs = _attrs_203946064
        _write(u'<li class="complete" id="step-2">\n        ')
        attrs = _attrs_203971984
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
        attrs = _attrs_203946000
        _write(u'<li class="complete" id="step-3">\n        ')
        attrs = _attrs_203972240
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
        attrs = _attrs_203972048
        _write(u'<li class="active current" id="step-4">\n        ')
        attrs = _attrs_203972496
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
        'view/tree'
        _write(u'\n        </a>\n        ')
        tree = _path(econtext['view'], econtext['request'], True, 'tree')
        'webhelpers/index/macros/survey_tree'
        _write(u'\n          ')
        _metal = _path(webhelpers, econtext['request'], True, 'index', 'macros', 'survey_tree')
        u'{}'
        _tmp = {}
        'webhelpers/index/macros/survey_tree'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, tree=tree, module=module, client=client, survey_url=survey_url, _out=_out, _write=_write)
        _write(u'\n      ')
        _write(u'</li>\n      ')
        attrs = _attrs_203972304
        _write(u'<li id="step-5">\n        ')
        attrs = _attrs_204013904
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
        _write(u'\n        </a>\n      </li>\n    </ol>\n\n    ')
        attrs = _attrs_203946192
        'webhelpers/macros/homelink'
        _write(u'<ul id="navigation">\n      ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'homelink')
        u'{}'
        _tmp = {}
        'webhelpers/macros/homelink'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, module=module, client=client, _out=_out, _write=_write)
        _write(u'\n      ')
        attrs = _attrs_204014160
        _write(u'<li>')
        attrs = _attrs_204014288
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
        attrs = _attrs_204014224
        _write(u'<li>')
        attrs = _attrs_204014416
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
        attrs = _attrs_204014352
        _write(u'<li>')
        attrs = _attrs_204014544
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
        attrs = _attrs_204014480
        _write(u'<li>')
        attrs = _attrs_204014672
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
        attrs = _attrs_204014608
        _write(u'<li>')
        attrs = _attrs_204014800
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
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, module=module, client=client, _out=_out, _write=_write)
        'webhelpers/macros/javascript'
        _write(u'\n    ')
        _metal = _path(webhelpers, econtext['request'], True, 'macros', 'javascript')
        u'{}'
        _tmp = {}
        'webhelpers/macros/javascript'
        _metal.render(_tmp, _domain=_domain, econtext=econtext, webhelpers=webhelpers, module=module, client=client, _out=_out, _write=_write)
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
        _write(u'\n  </body>\n')
        _write(u'</html>')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/home/jc/dev/euphorie/src/osha.oira/src/osha/oira/templates/module_actionplan.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
