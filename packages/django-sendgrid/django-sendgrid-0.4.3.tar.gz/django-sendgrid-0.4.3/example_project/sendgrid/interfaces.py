INTERFACES = {
	"bounces": {
		"get": {
			"required": [],
			"optional": [
				"date",
				"days",
				"start_date",
				"end_date",
				"limit",
				"offset",
				"type",
				"email"
			]
		},
		"delete": {
			"required": [],
			"optional": [
				"start_date",
				"end_date",
				"type",
				"email"
			]
		},
		# Not listed in SendGrid documentation
		"count": {
			"required": [],
			"optional": [
				"start_date",
				"end_date",
				"type"
			]
		}
	},
	"blocks": {
		"get": {
			"required": [],
			"optional": [
				"date",
				"days",
				"start_date",
				"end_date"
			]
		},
		"delete": {
			"required": [
				"email"
			],
			"optional": []
		}
	},
	# Missing from SendGrid documentation
	"parse": {
		"get": {
			"required": [],
			"optional": []
		},
		"set": {
			"required": [],
			"optional": []
		},
		"edit": {
			"required": [],
			"optional": []
		},
		"delete": {
			"required": [],
			"optional": []
		}
	},
	"eventposturl": {
		"get": {}, # Missing from SendGrid documentation
		"set": {
			"required": [
				"url"
			],
			"optional": []
		},
		"delete": {} # Missing from SendGrid documentation
	},
	"filter": {
		"get": {}, # Missing from SendGrid documentation
		"activate": {}, # Missing from SendGrid documentation
		"deactivate": {}, # Missing from SendGrid documentation
		"setup": {}, # Missing from SendGrid documentation
		"getsettings": {} # Missing from SendGrid documentation
	},
	"invalidemails": {
		"get": {
			"required": [],
			"optional": [
				"date",
				"days",
				"start_date",
				"end_date",
				"limit",
				"offset",
				"email"
			]
		},
		"delete": {
			"required": [],
			"optional": [
				"start_date",
				"end_date",
				"email"
			]
		},
		# Missing from SendGrid documentation
		"count": {
			"required": [],
			"optional": [
				"start_date",
				"end_date"
			]
		}
	},
	"mail": {
		"send": {
			"required": [
				"to",
				"subject",
				"text", # text and/or html
				"html", # text and/or html
				"from"
			],
			"optional": [
				"toname",
				"x-smtpapi",
				"bcc",
				"fromname",
				"replyto",
				"date",
				"files",
				"headers"
			]
		}
	},
	"profile": {
		"get": {},
		"set": {
			"required": [],
			"optional": [
				"first_name",
				"last_name",
				"address",
				"city",
				"state",
				"country",
				"zip",
				"phone",
				"website"
			]
		},
		"setUsername": {},
		"setPassword": {},
		"setEmail": {}
	},
	"spamreports": {
		"get": {},
		"delete": {}
	},
	"stats": {
		"get": {}
	},
	"unsubscribes": {
		"add": {
			"required": [
				"email"
			],
			"optional": []
		},
		"get": {
			"required": [],
			"optional": [
				"date",
				"days",
				"start_date",
				"end_date",
				"limit",
				"offset",
				"email"
			]
		},
		"delete": {
			"required": [],
			"optional": [
				"start_date",
				"end_date",
				"email"
			]
		}
	}
}
