import tg
from tg.i18n import ugettext as _
from datetime import datetime
import pywapi
from tgext.datahelpers.caching import entitycached, CacheKey

def get_weather_language():
    langs = []

    try:
        browser_languages = tg.request.languages
    except:
        browser_languages = []

    for lang in browser_languages:
        try:
            lang = lang.split('-', 1)[0]
        except:
            pass
        langs.append(lang)

    langs.append(tg.config.get('lang', 'en'))
    return langs[0]

def get_weather_for_date(location, date):
    @entitycached('cache_key', expire=24*3600)
    def get_cached_weater(cache_key, location, date):
        weather = {}

        today_to_event = (date - datetime.now()).days
        if today_to_event >= -1:
            if today_to_event < 1:
                weather = pywapi.get_weather_from_google(location, hl=get_weather_language())
                weather = weather['current_conditions']
                if 'icon' in weather:
                    weather['icon'] = 'http://www.google.com' + weather['icon']
            elif today_to_event < 5:
                weather = pywapi.get_weather_from_google(location, hl=get_weather_language())
                weather = weather['forecasts'][today_to_event]
                if 'icon' in weather:
                    weather['icon'] = 'http://www.google.com' + weather['icon']

        if not weather:
            weather = {'icon':tg.url('/_pluggable/calendarevents/images/noweather.png'),
                       'temp_c':'', 'low':'', 'high':''}

        return weather

    try:
        return get_cached_weater(CacheKey('%s-%s' % (location, date)), location, date)
    except:
        return {'icon':tg.url('/_pluggable/calendarevents/images/noweather.png'),
                'temp_c':'', 'low':'', 'high':''}