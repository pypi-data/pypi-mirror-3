import datetime
import httplib
import time
import urllib
import urllib2


API_USER="mindsnacks"
API_KEY="Mind1806snacks"

TODAY = datetime.date.today()
TODAYS_DATE_ISO_FORMAT= TODAY.isoformat()
SEVEN_DAYS_AGO_ISO_FORMAT = TODAY - datetime.timedelta(days=7)


class SendGridAPI2(object):
	"""docstring for SendGridAPI2"""
	def __init__(self, arg):
		super(SendGridAPI2, self).__init__()
		self.arg = arg
		


class SendGridAPI(object):
	"""docstring for SendGridAPI"""
	def __init__(self, user, key):
		super(SendGridAPI, self).__init__()
		self.user = user
		self.key = key
		
	def request(self, module, action, format="json", **kwargs):
		"""docstring for request"""
		if format == "xml":
			raise NotImplementedError
		elif not format == "json":
			raise ValueError
			
		functionTemplate = "_{action}_{module}_{format}"
		requestor = getattr(self, functionTemplate.format(module=module, action=action, format=format))
		response = requestor(**kwargs)
		
		return response
		
	def _get_unsubscribes_json(self, date=None, days=None, start_date=None, end_date=None, limit=None, offset=None, email=None):
		"""
		Returns a list of unsubscribes with addresses and optionally with dates.

		https://sendgrid.com/api/unsubscribes.get.xml?api_user=yourusername&api_key=secureSecret&date=1

			@param: date
			@param: days
			@param: start_date
			@param: end_date
			@param: limit
			@param: offset
			@param: email
		"""
		ENDPOINT = "https://sendgrid.com/api/unsubscribes.get.json"
		parameters = {
			"api_user": self.user,
			"api_key": self.key,
			"date": date,
			"days": days,
			# "start_date": start_date,
			# "end_date": end_date,
			# "limit": limit,
			# "offset": offset,
			# "email": email,
		}
		data = urllib.urlencode(parameters)
		request = urllib2.Request(ENDPOINT, data)
		response = urllib2.urlopen(request)
		content = response.read()
		
		return content
		
	def _add_unsubscribes_json(self, email):
		"""
		Add email addresses to the Unsubscribe list.
		"""
		ENDPOINT = "https://sendgrid.com/api/unsubscribes.add.json"
		parameters = {
			"api_user": self.user,
			"api_key": self.key,
			"email": email,
		}
		data = urllib.urlencode(parameters)
		request = urllib2.Request(ENDPOINT, data)
		response = urllib2.urlopen(request)
		content = response.read()

		return content
		
	def _delete_unsubscribes_json(self, start_date, end_date, email):
		"""
		Delete an address from the Unsubscribe list. Please note that if no parameters are provided the ENTIRE list will be removed.
		"""
		ENDPOINT = "https://sendgrid.com/api/unsubscribes.delete.json"
		if not (start_date and end_date and email):
			raise Exception("You're about to delete the entire list!")
			
		parameters = {
			"api_user": self.user,
			"api_key": self.key,
			# "start_date": start_date,
			# "end_date": end_date,
			"email": email,
		}
		data = urllib.urlencode(parameters)
		request = urllib2.Request(ENDPOINT, data)
		response = urllib2.urlopen(request)
		content = response.read()

		return content

	def _get_stats_json(self, days=1, start_date=None, end_date=None, category=None):
		"""docstring for _get_stats"""
		ENDPOINT = "https://sendgrid.com/api/stats.get.json"
		if days:
			pass
			# assert not (start_date and end_date)
		elif start_date and end_date:
			assert not days
		else:
			raise AttributeError
			
		parameters = {
			"api_user": self.user,
			"api_key": self.key,
			"days": days,
			# "start_date": start_date,
			# "end_date": end_date,
			# "category": category,
		}
		data = urllib.urlencode(parameters)
		request = urllib2.Request(ENDPOINT, data)
		response = urllib2.urlopen(request)
		content = response.read()

		return content

	stats = property(_get_stats_json)
	unsubscribes = property(_get_unsubscribes_json)

class SendGridUserMixin:
	"""
	Adds SendGrid related convienence functions and properties to ``User`` objects.
	"""
	def is_unsubscribed(self):
		"""
		Returns True is the ``User``.``email`` belongs to the unsubscribe list.
		
		https://sendgrid.com/api/unsubscribes.get.xml?api_user=yourusername&api_key=secureSecret&date=1
		"""
		pass
		
	def delete_from_unsubscribe_list(self):
		"""
		Removes the ``User``.``email`` from the unsubscribe list.
		
		https://sendgrid.com/api/unsubscribes.delete.xml?api_user=yourusername&api_key=secureSecret&email=emailToDelete@domain.com
		
			@param: start_date
			@param: end_date
			@param: email
		"""
		pass


if __name__ == "__main__":
	api = SendGridAPI(API_USER, API_KEY)
	# resp = api.request("unsubscribes", "add", email="ASDFASDF@EXAMPLE.com")
	# resp = api.request("unsubscribes", "get", date=1, limit=1, offset=1, start_date="2012-01-01", end_date="2012-02-21")
	# assert "ASDFASDF@EXAMPLE.com" in api.unsubscribes
	# 
	# resp = api.request("unsubscribes", "delete", start_date="2012-01-01", end_date="2012-02-21", email="ASDFASDF@EXAMPLE.com")
	# resp = api.request("unsubscribes", "delete", start_date="2012-01-01", end_date="2012-02-21", email="ryan+test@mindsnacks.com")
	# resp = api.request("unsubscribes", "delete", start_date="2012-01-01", end_date="2012-02-21", email="ryan@mindsnacks.com")
	# resp = api.request("unsubscribes", "delete", start_date="2012-01-01", end_date="2012-02-21", email="ryan+erlgdp@mindsnacks.com")
	resp = api.request("unsubscribes", "delete", start_date="2012-01-01", end_date="2012-02-21", email="katarina+email@mindsnacks.com")
	# 
	resp = api.request("unsubscribes", "get", date=1, limit=1, offset=1, start_date="2012-01-01", end_date="2012-02-21")
	print resp

	resp = api.request("stats", "get", days=1, category="Purchase")
	resp = api.request("stats", "get", start_date=SEVEN_DAYS_AGO_ISO_FORMAT, end_date=TODAYS_DATE_ISO_FORMAT, category="Purchase")
	print api.stats
	print resp
