registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _attrs_218634512 = _loads('(dp1\n.')
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_218634192 = _loads('(dp1\n.')
    _attrs_218634576 = _loads('(dp1\n.')
    _attrs_218634256 = _loads('(dp1\n.')
    _attrs_218634384 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_218634704 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_218634768 = _loads('(dp1\n.')
    _attrs_218634448 = _loads('(dp1\n.')
    _attrs_218634320 = _loads('(dp1\n.')
    _attrs_218634640 = _loads('(dp1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
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
        _tmp_domain0 = _domain
        u"'euphorie'"
        _domain = 'euphorie'
        _write(u'\n\n')
        _tmp_domain0 = _domain
        _tmp_domain0 = _domain
        u"'euphorie'"
        _domain = 'euphorie'
        _write(u'')
        attrs = _attrs_218634192
        u"%(translate)s('header_risk_aware', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h2>')
        _result = _translate('header_risk_aware', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Are you aware of all the risks?')
        _write(u'</h2>\n    ')
        attrs = _attrs_218634256
        u"u'Including the risks to your employees and your equipment?  What if there is an accident with one of the machines? What if an employee is exposed to hazardous substances? A risk assessment helps you to define these risks and tackle them head on. A risk assessment mainly consists of two parts: a '"
        _write(u'<p>')
        _msgid = u'Including the risks to your employees and your equipment?  What if there is an accident with one of the machines? What if an employee is exposed to hazardous substances? A risk assessment helps you to define these risks and tackle them head on. A risk assessment mainly consists of two parts: a '
        u"%(translate)s('intro_risk_aware', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _result = _translate('intro_risk_aware', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Including the risks to your employees and your equipment?  What if there is an accident with one of the machines? What if an employee is exposed to hazardous substances? A risk assessment helps you to define these risks and tackle them head on. A risk assessment mainly consists of two parts: a ')
            attrs = _attrs_218634384
            _write(u'<em>list</em> with all the risks in your company and an ')
            attrs = _attrs_218634448
            _write(u'<em>action plan</em> with details of how to deal with these risks. These two components allow you to limit the risks to your employees and your company, and therefore the financial risk.')
        _write(u'</p>\n\n    ')
        attrs = _attrs_218634320
        u"%(translate)s('header_not_complicated', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h2>')
        _result = _translate('header_not_complicated', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'The assessment is not complicated')
        _write(u'</h2>\n    ')
        attrs = _attrs_218634512
        u"%(translate)s('intro_not_complicated', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('intro_not_complicated', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Complicated? Not really. It just takes a bit of time. However, the RA is important. So important that it is a legal requirement. This is for good reason. If risks are not assessed or properly dealt with, a suitable risk management process cannot be started and appropriate preventive measures are unlikely to be found or put in place.')
        _write(u'</p>\n\n    ')
        attrs = _attrs_218634576
        u"%(translate)s('header_consultation_of_workers', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h2>')
        _result = _translate('header_consultation_of_workers', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Consultation and participation of workers')
        _write(u'</h2>\n    ')
        attrs = _attrs_218634640
        u"%(translate)s('intro_consultation_of_workers', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('intro_consultation_of_workers', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u"Workers or workers' representatives with specific responsibility for the safety and health of workers shall take part in a balanced way or shall be consulted in advance and in good time by the employer with regard to risk assessment")
        _write(u'</p>\n\n    ')
        attrs = _attrs_218634704
        u"%(translate)s('header_oira_tool', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h2>')
        _result = _translate('header_oira_tool', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'The OiRA tool')
        _write(u'</h2>\n    ')
        attrs = _attrs_218634768
        u"%(translate)s('intro_oira_tool', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('intro_oira_tool', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'This risk assessment tool is mainly intended for micro (less than 10 workers) and small (less than 50 workers) enterprises/organisations.')
        _write(u'</p>\n\n\t')
        _domain = _tmp_domain0
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/default_introduction.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_233774224 = _loads('(dp1\n.')
    _attrs_233774160 = _loads('(dp1\n.')
    _attrs_233774416 = _loads('(dp1\n.')
    _attrs_233774672 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_233762448 = _loads('(dp1\n.')
    _attrs_233774480 = _loads('(dp1\n.')
    _attrs_233774352 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_233774544 = _loads('(dp1\n.')
    _attrs_233774288 = _loads('(dp1\n.')
    _attrs_233774608 = _loads('(dp1\n.')
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
        _tmp_domain0 = _domain
        u"'euphorie'"
        _domain = 'euphorie'
        _write(u'')
        attrs = _attrs_233762448
        u"%(translate)s('header_risk_aware', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h2>')
        _result = _translate('header_risk_aware', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Are you aware of all the risks?')
        _write(u'</h2>\n    ')
        attrs = _attrs_233774160
        u"u'Including the risks to your employees and your equipment?  What if there is an accident with one of the machines? What if an employee is exposed to hazardous substances? A risk assessment helps you to define these risks and tackle them head on. A risk assessment mainly consists of two parts: a '"
        _write(u'<p>')
        _msgid = u'Including the risks to your employees and your equipment?  What if there is an accident with one of the machines? What if an employee is exposed to hazardous substances? A risk assessment helps you to define these risks and tackle them head on. A risk assessment mainly consists of two parts: a '
        u"%(translate)s('intro_risk_aware', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _result = _translate('intro_risk_aware', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Including the risks to your employees and your equipment?  What if there is an accident with one of the machines? What if an employee is exposed to hazardous substances? A risk assessment helps you to define these risks and tackle them head on. A risk assessment mainly consists of two parts: a ')
            attrs = _attrs_233774288
            _write(u'<em>list</em> with all the risks in your company and an ')
            attrs = _attrs_233774352
            _write(u'<em>action plan</em> with details of how to deal with these risks. These two components allow you to limit the risks to your employees and your company, and therefore the financial risk.')
        _write(u'</p>\n\n    ')
        attrs = _attrs_233774224
        u"%(translate)s('header_not_complicated', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h2>')
        _result = _translate('header_not_complicated', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'The assessment is not complicated')
        _write(u'</h2>\n    ')
        attrs = _attrs_233774416
        u"%(translate)s('intro_not_complicated', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('intro_not_complicated', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Complicated? Not really. It just takes a bit of time. However, the RA is important. So important that it is a legal requirement. This is for good reason. If risks are not assessed or properly dealt with, a suitable risk management process cannot be started and appropriate preventive measures are unlikely to be found or put in place.')
        _write(u'</p>\n\n    ')
        attrs = _attrs_233774480
        u"%(translate)s('header_consultation_of_workers', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h2>')
        _result = _translate('header_consultation_of_workers', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Consultation and participation of workers')
        _write(u'</h2>\n    ')
        attrs = _attrs_233774544
        u"%(translate)s('intro_consultation_of_workers', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('intro_consultation_of_workers', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u"Workers or workers' representatives with specific responsibility for the safety and health of workers shall take part in a balanced way or shall be consulted in advance and in good time by the employer with regard to risk assessment")
        _write(u'</p>\n\n    ')
        attrs = _attrs_233774608
        u"%(translate)s('header_oira_tool', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h2>')
        _result = _translate('header_oira_tool', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'The OiRA tool')
        _write(u'</h2>\n    ')
        attrs = _attrs_233774672
        u"%(translate)s('intro_oira_tool', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<p>')
        _result = _translate('intro_oira_tool', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'This risk assessment tool is mainly intended for micro (less than 10 workers) and small (less than 50 workers) enterprises/organisations.')
        _write(u'</p>\n\n\t  \n')
        _domain = _tmp_domain0
        return
    return render

__filename__ = '/home/jc/dev/oira/src/osha.oira/src/osha/oira/templates/default_introduction.pt'
registry[('default_introduction', False, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
