from cgi import escape

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import safe_unicode
from plone.app.layout.viewlets.common import ViewletBase

from Acquisition import aq_inner
from zope.component import getMultiAdapter, getUtility

from xhostplus.social.interfaces.configuration import ISocialConfiguration
from xhostplus.social import socialMessageFactory as _

class OpenGraph(ViewletBase):

    def update(self):
        super(OpenGraph, self).update()

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
                                        name=u'plone_portal_state')
        context_state = getMultiAdapter((context, self.request),
                                         name=u'plone_context_state')
        portal = portal_state.portal()

        bprops = portal.restrictedTraverse('base_properties', None)
        if bprops is not None:
            logoName = bprops.logoName
        else:
            logoName = 'logo.jpg'

        try:
            self.og_page_title = escape(safe_unicode(context_state.object_title()))
        except:pass

        try:
            self.og_portal_title = escape(safe_unicode(portal.Title()))
        except:pass

        try:
            self.og_portal_description = escape(safe_unicode(portal.Description()))
        except:pass

        try:
            self.og_image = portal.restrictedTraverse(logoName).absolute_url()
        except:pass

        try:
            self.og_url = escape(safe_unicode(context.absolute_url()))
        except:pass

    def socialButtonsEnabled(self):
        try:
            return self.context.Schema()['socialButtons'].get(self.context)
        except:
            return False


class Buttons(ViewletBase):

    def update(self):
        super(Buttons, self).update()
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')

        self.language = portal_state.language().split('-')[0].split('_')[0]

    def socialButtonsEnabled(self):
        try:
            return self.context.Schema()['socialButtons'].get(self.context)
        except:
            return False

    def twoClickEnabled(self):
        try:
            settings = getUtility(ISocialConfiguration)
            return settings.two_click_buttons
        except:
            return False

    def two_click_import_script(self):
        language = self.language
        facebook_language = self.get_facebook_langcode()

        code = """
        (function($) {
            $(document).ready(function() {
              if($('#socialshareprivacy').length > 0){
                 $('#socialshareprivacy').socialSharePrivacy({
                    'services' : {
                        'facebook' : {
                            'dummy_img'         : portal_url + '/++resource++xhostplus.social.images/%(facebook_dummy_image)s',
                            'txt_info'          : '%(facebook_info_text)s',
                            'txt_fb_off'        : '%(facebook_disconnected)s',
                            'txt_fb_on'         : '%(facebook_connected)s',
                            'language'          : '%(facebook_language)s',
                        },
                        'twitter' : {
                            'dummy_img'         : portal_url + '/++resource++xhostplus.social.images/%(twitter_dummy_image)s',
                            'txt_info'          : '%(twitter_info_text)s',
                            'txt_twitter_off'   : '%(twitter_disconnected)s',
                            'txt_twitter_on'    : '%(twitter_connected)s',
                            'language'          : '%(language)s'
                        },
                        'gplus' : {
                            'dummy_img'         : portal_url + '/++resource++xhostplus.social.images/%(googleplus_dummy_image)s',
                            'txt_info'          : '%(googleplus_info_text)s',
                            'txt_gplus_off'     : '%(googleplus_disconnected)s',
                            'txt_gplus_on'      : '%(googleplus_connected)s',
                            'language'          : '%(language)s'
                        },
                        'linkedin' : {
                            'dummy_img'         : portal_url + '/++resource++xhostplus.social.images/%(linkedin_dummy_image)s',
                            'txt_info'          : '%(linkedin_info_text)s',
                            'txt_linkedin_off'  : '%(linkedin_disconnected)s',
                            'txt_linkedin_on'   : '%(linkedin_connected)s',
                            'language'          : '%(language)s'
                        }
                    },
                    'txt_help'          : '%(txt_help)s',
                    'settings_perma'    : '%(settings_perma)s'
                 });
              }
            });
        })(jQuery);
        """ % {
            'facebook_info_text' : self.context.translate(_(u'2 clicks for your privacy: Only if you click here the button will get active and you can send your recommendation to Facebook. An active button will send data do a third-party &ndash; more information on <em>i</em>.')),
            'facebook_disconnected' : self.context.translate(_(u'not connected to Facebook')),
            'facebook_connected' : self.context.translate(_(u'connected to Facebook')),
            'twitter_info_text' : self.context.translate(_(u'2 clicks for your privacy: Only if you click here the button will get active and you can send your recommendation to Twitter. An active button will send data do a third-party &ndash; more information on <em>i</em>.')),
            'twitter_disconnected' : self.context.translate(_(u'not connected to Twitter')),
            'twitter_connected' : self.context.translate(_(u'connected to Twitter')),
            'googleplus_info_text' : self.context.translate(_(u'2 clicks for your privacy: Only if you click here the button will get active and you can send your recommendation to Google+. An active button will send data do a third-party &ndash; more information on <em>i</em>.')),
            'googleplus_disconnected' : self.context.translate(_(u'not connected to Google+')),
            'googleplus_connected' : self.context.translate(_(u'connected to Google+')),
            'linkedin_info_text' : self.context.translate(_(u'2 clicks for your privacy: Only if you click here the button will get active and you can send your recommendation to LinkedIn. An active button will send data do a third-party &ndash; more information on <em>i</em>.')),
            'linkedin_disconnected' : self.context.translate(_(u'not connected to LinkedIn')),
            'linkedin_connected' : self.context.translate(_(u'connected to LinkedIn')),
            'language' : language,
            'facebook_language' : facebook_language,
            'facebook_dummy_image' : self.context.translate(_(u'dummy_facebook_en.png')),
            'twitter_dummy_image' : self.context.translate(_(u'dummy_twitter_en.png')),
            'googleplus_dummy_image' : self.context.translate(_(u'dummy_googleplus_en.png')),
            'linkedin_dummy_image' : self.context.translate(_(u'dummy_linkedin_en.png')),
            'txt_help' : self.context.translate(_(u'Only if you activate the buttons, data will get sent to Facebook, Twitter, Google or LinkedIn. This data might get stored in the USA. Get more information by clicking on <em>i</em>.')),
            'settings_perma' : self.context.translate(_(u'Activate buttons permanently:')),
        }
        return code

    def import_script(self):
        code = ""
        scripts = [
            self.get_facebook_script_url(),
            self.get_googleplus_script_url(),
            self.get_twitter_script_url(),
            self.get_linkedin_script_url(),
        ]

        for script in scripts:
            code += "xhostplus_social_inject_js(\"%(url)s\", \"%(inner_code)s\");\n" % {
                'url' : script[0],
                'inner_code' : script[1],
            }

        return """
        (function() {
            %s
        })();
        """ % code

    def get_facebook_langcode(self):
        defaut_language = 'en_GB'
        languages = {
            'de' : 'de_DE',
            'en' : 'en_GB',
            'nl' : 'nl_NL',
            'fr' : 'fr_FR',
            'it' : 'it_IT',
            'jp' : 'ja_JP',
            'ja' : 'ja_JP',
            'ru' : 'ru_RU',
        }

        return languages.get(self.language, defaut_language)

    def get_facebook_script_url(self):
        language = self.get_facebook_langcode()
        return (("http://connect.facebook.net/%s/all.js#xfbml=1" % language), '')

    def get_googleplus_script_url(self):
        language = self.language.split('-')[0].split('_')[0]
        return ("https://apis.google.com/js/plusone.js", ("{lang: '%s'}" % language))

    def get_twitter_script_url(self):
        return ('http://platform.twitter.com/widgets.js', '')

    def get_linkedin_script_url(self):
        return ('http://platform.linkedin.com/in.js', '')
