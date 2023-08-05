from django.conf import settings
from django.http import HttpResponseRedirect
from mobi.useragents import search_strings

class MobileDetectionMiddleware(object):
    @staticmethod
    def process_request(request):
        """Adds a "mobile" attribute to the request which is True or False
           depending on whether the request should be considered to come from a
           small-screen device such as a phone or a PDA"""

        if request.META.has_key("HTTP_X_OPERAMINI_FEATURES"):
            #Then it's running opera mini. 'Nuff said.
            #Reference from:
            # http://dev.opera.com/articles/view/opera-mini-request-headers/
            request.mobile = True
            return None

        if request.META.has_key("HTTP_ACCEPT"):
            s = request.META["HTTP_ACCEPT"].lower()
            if 'application/vnd.wap.xhtml+xml' in s:
                # Then it's a wap browser
                request.mobile = True
                return None

        if request.META.has_key("HTTP_USER_AGENT"):
            # This takes the most processing. Surprisingly enough, when I
            # Experimented on my own machine, this was the most efficient
            # algorithm. Certainly more so than regexes.
            # Also, Caching didn't help much, with real-world caches.
            s = request.META["HTTP_USER_AGENT"].lower()
            for ua in search_strings:
                if ua in s:
                    request.mobile = True
                    return None

        #Otherwise it's not a mobile
        request.mobile = False
        return None

#===============================================================================
class MobileRedirectMiddleware(object):
    
    # Add MOBI_REDIRECT_URL to your settings.py file with a fully qualified 
    # url that you want to redirect mobile clients too.
    # i.e. http://example.mobi
    MOBI_REDIRECT_URL = getattr(settings, 'MOBI_REDIRECT_URL', None)

    #---------------------------------------------------------------------------
    def process_request(self, request):
        do_redirect = False

        user_agent = request.META.get('HTTP_USER_AGENT',None)

        # mobile browsers are the only people who send this.
        x_wap = request.META.get('HTTP_X_WAP_PROFILE',None)
        http_profile = request.META.get('HTTP_PROFILE',None)

        if x_wap or http_profile:
            do_redirect = True

        #look at the user agent if they don't have x_wap and http_profile
        if user_agent and not do_redirect:
            user_agent = user_agent.lower()
            is_mobile = [w for w in search_strings if w in user_agent]
            if is_mobile:
                do_redirect = True

        if do_redirect and MOBI_REDIRECT_URL:
             # tell adaptation services (transcoders and proxies) to not alter the content based on user agent as it's already being managed by this script
             # http://mobiforge.com/developing/story/setting-http-headers-advise-transcoding-proxies
             response = HttpResponseRedirect(MOBI_REDIRECT_URL)
             response['Cache-Control'] = 'no-transform'
             response['Vary'] = 'User-Agent, Accept'
             return response
        else:
            return None

