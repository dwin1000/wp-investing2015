import mechanize
import cookielib

def set_logger(level):
    import logging
    import logging.config
    #global logger

    debugLevel = "logging." + level

    """
    logger = logging.getLogger(__name__)
    logger.setLevel(debugLevel)

    ch = logging.StreamHandler()
    ch.setLevel(debugLevel)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
        %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    """
    LOGGING = {
        'version': 1,
        #'disable_existing_loggers': False,  # this fixes the problem

        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            }
        },
        'handlers': {
            'default': {
                'level': logging.DEBUG,
                'class':'logging.StreamHandler',
                'formatter': 'standard'
            }
        },
        'loggers': {
            'root': {
                'handlers': ['default'],
                'level': logging.DEBUG,
                'propagate': True
                }
        }
    }

    return LOGGING
    #logging.config.dictConfig(LOGGING)



def login_gf(url, user, passwd):
    #logger = logging.getLogger()
    ###logger.debug("Url: %s    user: %s  " % (url, user))
    print "Here"
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    #br.set_all_readonly(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; \
        en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        # [('User-agent', 'Firefox')]

    print "Url: %s" % url
    br.open(url)
    br.follow_link(text_regex=r'LOG IN', nr=0)
    ###logger.info(br.title())
    br.select_form(nr=0)
    br.form["username"] = user
    br.form["password"] = passwd
    try:
        br.submit()
        ####logger.info(br.title())

        #return br
    except Exception, e:
        sys.exit("failed: %d  %s " % (e.code, e.msg))

    return br

def setUp_WPauth():
    import wpAuth

    #url = "https://www.gurufocus.com"
    gfStuff =wpAuth.gfInfo()
    url = gfStuff.Url
    gfUser = gfStuff.email
    gfPass = gfStuff.passwd

    return (gfUser, gfPass, url)




