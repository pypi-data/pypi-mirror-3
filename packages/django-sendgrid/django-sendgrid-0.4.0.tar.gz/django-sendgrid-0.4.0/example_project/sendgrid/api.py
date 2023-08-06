"""
http://docs.sendgrid.com/documentation/api/web-api/
"""


url_generator = lambda spec: "/api/{method}.{action}.{format}".format(**spec)

MODULES = (
	"bounces",
	"blocks",
	"parse",
	"eventposturl",
	"filter",
	"invalidemails",
	"mail",
	"profile",
	"spamreports",
	"stats",
	"unsubscribes"
)

MODULE_METHODS = {
	"bounces": ("get", "delete"),
	"blocks": ("get", "delete"),
	"parse": ("get", "set", "edit", "delete"),
	"eventposturl": ("get", "set", "delete"),
	"filter": ("get", "activate", "deactivate", "setup", "getsettings"),
	"invalidemails": ("get", "delete"),
	"mail": ("send"),
	"profile": ("get", "set", "setUsername", "setPassword", "setEmail"),
	"spamreports": ("get", "delete"),
	"stats": ("get",),
	"unsubscribes": ("add", "get", "delete")
}


class SendGridAPIResponse(object):
	"""docstring for SendGridAPIResponse"""
	def __init__(self, status_code):
		super(SendGridAPIResponse, self).__init__()
		self.content = None
		
	def get_message(self):
		"""docstring for get_message"""
		return self.content["message"]
	message = property(get_message)
	
	def get_errors(self):
		"""docstring for get_errors"""
		return self.content["errors"]
	errors = property(get_errors)


class SendGridAPIRequest(object):
	"""docstring for SendGridAPIRequest"""
	def __init__(self, module, action, format):
		super(SendGridAPIRequest, self).__init__()
		self.module = module
		self.action = action
		self.format = format
		
	def make_request(self):
		"""docstring for make_request"""
		pass

class SendGridAPI(object):
	"""docstring for SendGridAPI"""
	def __init__(self, user, key):
		super(SendGridAPI, self).__init__()
		self.user = user
		self.key = key
		

if __name__ == "__main__":
	pass
