"""openid views

:organization: Logilab
:copyright: 2010-2011 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
from logilab.mtconverter import xml_escape
from logilab.common.decorators import clear_cache, monkeypatch

from openid.consumer import consumer
from openid.store import memstore
from openid.extensions import ax, pape, sreg

from cubicweb.vregistry import Registry
from cubicweb.utils import make_uid
from cubicweb.appobject import AppObject
from cubicweb.view import StartupView, View
from cubicweb.selectors import (match_form_params, anonymous_user, configuration_values,
                                match_kwargs, yes)

from cubicweb.web import Redirect, formfields as ff, formwidgets as fw, component, uicfg
from cubicweb.web.controller import Controller
from cubicweb.web.views import authentication, urlrewrite, forms
from cubicweb.web.views import basecomponents, basetemplates as templates

from cubes.openidrelay.utils import url_args

# web authentication info retriever ############################################

# a lot of vital information in openid/consummer/consummer.py

NEGOSTATE = {}
AX_REQUIRED =  (
    ('email', 'http://axschema.org/contact/email'),
    ('fullname', 'http://schema.openid.net/namePerson'),
    ('firstname', 'http://axschema.org/namePerson/first'),
    ('web', 'http://schema.openid.net/contact/web/default'),
    )

class OpenIDReqRewriter(urlrewrite.SimpleReqRewriter):
    rules = [
        ('/openid-confirm', dict(vid='openid-confirm'),)
        ]

#uicfg.autoform_field_kwargs.tag_attribute(('CWUser', 'openid'), 'main', 'hidden')
uicfg.primaryview_display_ctrl.tag_attribute(('CWUser', 'openid'), {'vid': 'attribute'})

def login_now(self, login, openid):
    req = self._cw
    clear_cache(req, 'get_authorization')
    req.form['__openidlogin'] = login
    req.form['__openid'] = openid
    if req.cnx:
        req.cnx.close()
    req.cnx = None
    try:
        self.appli.session_handler.set_session(req)
    except Redirect, r:
        pass
    assert req.user.login == login

class OpenIDConfirm(Controller):
    __regid__ = 'openid-confirm'
    __select__ = match_form_params('openid.assoc_handle')

    def _get_best_login(self, response):
        sreg_response = sreg.SRegResponse.fromSuccessResponse(response) or {}
        ax_response = ax.FetchResponse.fromSuccessResponse(response)
        if ax_response:
            for attr, schema in AX_REQUIRED:
                try:
                    return attr, ax_response.get(schema)
                except KeyError: # weird stuff
                    continue
        if sreg_response:
            return sreg_response.items()[0]

    def publish(self, rset=None):
        form = self._cw.form
        handle = form.get('openid.assoc_handle')
        if handle:
            state = NEGOSTATE.pop(handle, None)
            if state is None:
                self.warning('parameters already consummed or wrong for %s',
                             self.__regid__)
                raise Redirect(self._cw.build_url())
            negotiator, confirm_url = state
            response = negotiator.complete(form, confirm_url)
            _ = self._cw._
            if response.status == consumer.FAILURE:
                raise Redirect(self._cw.build_url(__message=_('openid login failure')))
            elif response.status == consumer.CANCEL:
                assert form.get('openid.mode') == 'cancel'
                raise Redirect(self._cw.build_url(__message=_('openid login cancelled')))
            elif response.status == consumer.SUCCESS:
                identity = form['openid.identity'].strip()
                users = self.appli.repo.find_users(('login',), openid=identity)
                assert len(users) < 2
                if users:
                    login_now(self, users[0][0], identity)
                    raise Redirect(self._cw.build_url())
                else:
                    loginfo = self._get_best_login(response)
                    token = make_uid()
                    self._cw.session.data[token] = (loginfo, identity)
                    raise Redirect(self._cw.build_url(vid='openid-createuser', __token=token))

class OpenIDCreateUserForm(forms.FieldsForm):
    __regid__ = action = 'openid-createuser'
    form_buttons = [fw.SubmitButton(label=_('create user')),
                    fw.ResetButton(label=_('cancel'))]

class OpenIDCreateUserController(Controller):
    __regid__ = 'openid-createuser'

    def publish(self, rset=None):
        token = self._cw.form.get('__token')
        if not token:
            raise Redirect(self._cw.build_url())
        loginfo_identity = self._cw.session.data[token]
        if not loginfo_identity:
            raise Redirect(self._cw.build_url())
        _loginfo, identity = loginfo_identity
        login = self._cw.form.get('identity').strip()
        # make a dumb un-guessable password
        password = make_uid()
        openid = identity.strip()
        self.appli.repo.register_user(login, password, openid=openid)
        login_now(self, login, openid)
        raise Redirect(self._cw.build_url('cwuser/%s?vid=edition' % login))


class OpenIDCreateUserFormView(View):
    __regid__ = 'openid-createuser'

    def call(self, **kwargs):
        token = self._cw.form.get('__token')
        if not token:
            raise Redirect(self._cw.build_url())
        loginfo_identity = self._cw.session.data[token]
        if not loginfo_identity:
            raise Redirect(self._cw.build_url())
        loginfo, _identity = loginfo_identity
        infoname, data = loginfo
        if not isinstance(data, basestring):
            data = data[0] if data else u''
        w = self.w; _ = self._cw._
        w(_('This is the first time you log in with this identity. '))
        w(_('Please confirm how you will be known to us.'))
        form = self._cw.vreg['forms'].select('openid-createuser', self._cw)
        form.add_hidden('__token', value=token)
        form.append_field(ff.StringField(name='identity', label=self._cw._('local identity'),
                                         max_length=254, value=data))
        form.render(w=w)

class yes_marker(object):
    def __bool__(self):
        return True

# Negotiation

class OpenIDRetrieverStart(authentication.WebAuthInfoRetreiver):
    """ openid authentication """
    __regid__ = 'openid-authenticate-start'
    order = 9

    def _build_url(self, vid='view', **kwargs):
        base_url = self._base_url()
        urlargs = '&'.join('%s=%s' % (k, v) for k, v in kwargs.items())
        if urlargs:
            return '%s%s?%s' % (base_url, vid, urlargs)
        return '%s%s' % (base_url, vid)

    def _base_url(self):
        # XXX self._cw is the registry !
        return self._cw.config['base-url']

    def request_has_auth_info(self, req):
        return '__openiduri' in req.form

    def revalidate_login(self, req):
        return yes_marker()

    def authentication_information(self, req):
        """retrieve authentication information from the given request, raise
        NoAuthInfo if expected information is not found
        return login crypted with secret shared key
        """
        self.info('openid web authenticator (%s) building auth info %s',
                  self.__class__.__name__, req.form)
        openiduri = req.form.get('__openiduri')
        if openiduri:
            session_dict = {}
            negotiator = consumer.Consumer(session_dict, memstore.MemoryStore())
            confirm_url = self._build_url('openid-confirm')
            try:
                auth_req = negotiator.begin(openiduri)
            except consumer.DiscoveryFailure, exc:
                self.error('discovery failure: %s', exc)
                raise Redirect(self._build_url(__message='discovery failure'))
            # we have to request a bit redundantly as openid providers
            # handle these things in a very ad-hockish way
            # just hope something comes out ...
            # hence sreg + ax
            sreg_request = sreg.SRegRequest(required=['email', 'nickname', 'fullname'])
            auth_req.addExtension(sreg_request)
            ax_request = ax.FetchRequest()
            for attr, schema in AX_REQUIRED:
                ax_request.add(
                    ax.AttrInfo(schema, alias=attr, required=True))
            auth_req.addExtension(ax_request)
            url = auth_req.redirectURL(realm=self._base_url(),
                                       return_to=confirm_url)
            args = url_args(url)
            if 'openid.assoc_handle' not in args:
                self.error('openid.assoc_handle was not found')
                raise authentication.NoAuthInfo
            handle = args['openid.assoc_handle']
            NEGOSTATE[handle] = (negotiator, confirm_url)
            raise Redirect(url)
        raise authentication.NoAuthInfo


class OpenIDRetrieverFinish(authentication.WebAuthInfoRetreiver):
    """ openid authentication """
    __regid__ = 'openid-authenticate-finish'
    order = OpenIDRetrieverStart.order - 1

    def request_has_auth_info(self, req):
        return '__openid' in req.form and '__openidlogin' in req.form

    def revalidate_login(self, req):
        return req.form.get('__openidlogin')

    def authentication_information(self, req):
        """retrieve authentication information from the given request, raise
        NoAuthInfo if expected information is not found
        return login crypted with secret shared key
        """
        self.info('openid web authenticator (%s) building auth info %s',
                  self.__class__.__name__, req.form)
        login = req.form.get('__openidlogin')
        openid = req.form.get('__openid')
        if login and openid:
            return login, {'openid': openid}
        raise authentication.NoAuthInfo

# Login links

class OpenIDLoginLink(basecomponents.HeaderComponent):
    __regid__ = 'openidlink'
    __select__ = (basecomponents.HeaderComponent.__select__ &
                  configuration_values('auth-mode', 'cookie') &
                  anonymous_user())
    context = _('header-right')
    onclick = "javascript: cw.htmlhelpers.popupLoginBox('%s', '%s');"

    def render(self, w):
        text = self._cw._('openid login')
        w(u"""<img src="%s" alt="%s" title="%s" onclick="%s"/>""" %
               (self._cw.uiprops['OPENID_SMALL_ICON'], text, text,
                self.onclick % ('openidlogbox', '__openiduri')))
        self._cw.view('openidlogform', rset=self.cw_rset, id='openidlogbox', w=w)

class OpenIdLogForm(forms.FieldsForm):
    __regid__ = domid = 'openidlogform'
    boxid = 'openidlogbox'
    onclick = "javascript: cw.htmlhelpers.popupLoginBox('%s', '%s');"

    __openiduri = ff.StringField('__openiduri', label=_('openiduri'),
                                widget=fw.TextInput({'class': 'data'}))
    form_buttons = [fw.SubmitButton(label=_('log in'),
                                    attrs={'class': 'loginButton'}),
                    fw.ResetButton(label=_('cancel'),
                                   attrs={'class': 'loginButton',
                                          'onclick': onclick % ('openidlogbox', '__openiduri')})]

    def form_action(self):
        if self.action is None:
            return templates.login_form_url(self._cw)
        return super(LogForm, self).form_action()


class Button(AppObject):
    # in cw ?
    __registry__ = 'buttons'
    __abstract__ =  True

class OpenIDButton(Button):
    __regid__ = 'openid_button'
    __abstract__ =  True
    onclick = 'javascript: cw.cubes.openidrelay.fillLogFormAndPost("%s", "%s", "%s");'

    def render(self, form, **kwargs):
        return fw.Button(label=self._cw._(self.label),
                         onclick=self.onclick % ('openidlogform', '__openiduri', self.url),
                         attrs={'class': 'loginButton'}).render(form)

# XXX

@monkeypatch(Registry)
def selectable(self, oid, *args, **kwargs):
    """return all appobjects having the given oid that are
    selectable against the given context, in score order
    """
    objects = []
    for appobject in self[oid]:
        score = appobject.__select__(appobject, *args, **kwargs)
        if score > 0:
            objects.append((score, appobject))
    return [obj(*args, **kwargs)
            for _score, obj in sorted(objects)]


# XXX jQuery.OpenID ?
class GmailButton(OpenIDButton):
    label = _('google')
    url = 'https://www.google.com/accounts/o8/id'

class YahooButton(OpenIDButton):
    label = _('yahoo')
    url = 'http://me.yahoo.com/'

class OpenIDLogFormView(View):
    __regid__ = 'openidlogform'
    __select__ = match_kwargs('id') &  configuration_values('auth-mode', 'cookie')
    help_msg = _("""
You can click on the Google or Yahoo buttons to sign-in with these identity providers,
or you just type your identity uri and click on the little login button.
""")

    title = _('log in using an openid account')

    def call(self, id):
        w = self.w
        self._cw.add_js('cubes.openidrelay.js')
        w(u'<div id="%s" class="popupLoginBox hidden">' % id)
        w(u'<div class="loginContent">\n')
        w(u'<p>%s</p>' % self._cw._(self.help_msg))
        form = self._cw.vreg['forms'].select('openidlogform', self._cw)
        morebuttons = self._cw.vreg['buttons'].selectable('openid_button', self._cw)
        # copy class buttons to form instance
        form.form_buttons = form.form_buttons[:]
        for button in morebuttons:
            form.form_buttons.insert(-1, button)
        form.render(w=w, table_class='', display_progress_div=False)
        self._cw.html_headers.add_onload('jQuery("#__openiduri:visible").focus()')
        w(u'</div></div>')
