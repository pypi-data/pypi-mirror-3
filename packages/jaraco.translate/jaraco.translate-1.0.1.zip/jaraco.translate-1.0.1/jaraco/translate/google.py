
import json
import urllib
import urllib2

def translate(text, target_lang='en', source_lang=None):
	"""
	Use the Google v2 API to translate the text. You had better have set
	the API key on this function before calling it.
	"""
	url_base = 'https://www.googleapis.com/language/translate/v2'
	params = dict(
		key = translate.API_key,
		q = text,
		target = target_lang,
	)
	if source_lang:
		params['source'] = source_lang
	u = urllib2.urlopen(url_base + '?' + urllib.urlencode(params))
	data = u.read()
	return json.loads(data)['data']['translations'][0]['translatedText']
