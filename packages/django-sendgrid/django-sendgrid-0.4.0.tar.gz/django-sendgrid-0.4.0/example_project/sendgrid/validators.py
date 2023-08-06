# Generic Validators
# ------------------
validate_generic_get_date = lambda v: v == 1
validate_generic_get_days = lambda v: isinstance(v, int) and v > 0
validate_generic_get_limit = lambda v: isinstance(v, int)
validate_generic_get_offset = lambda v: isinstance(v, int)
validate_generic_get_type = lambda v: v in ("hard", "soft")

# Bounces Validators
# ------------------

validate_bounces_get_date = validate_generic_get_date
validate_bounces_get_days = validate_generic_get_days
validate_bounces_get_start_date = lambda v: False
validate_bounces_get_end_date = lambda v: False
validate_bounces_get_limit = validate_generic_get_limit
validate_bounces_get_offset = validate_generic_get_limit
validate_bounces_get_type = lambda v: v in ("hard", "soft")
validate_bounces_get_email = lambda v: False

validate_bounces_delete_start_date = lambda v: False
validate_bounces_delete_end_date = lambda v: False
validate_bounces_delete_type = lambda v: v in ("hard", "soft")
validate_bounces_delete_email = lambda v: False

# Blocks Validators
# -----------------

validate_blocks_get_date = validate_generic_get_date
validate_blocks_get_days = validate_generic_get_days
validate_blocks_get_start_date = lambda v: False
validate_blocks_get_end_date = lambda v: False

# Email Parse Validators
# ----------------------

# Event Notification URL Validators
# ---------------------------------

# Filters Validators
# ------------------

# Invalid Emails Validators
# -------------------------

validate_invalidemails_get_date = validate_generic_get_date
validate_invalidemails_get_days = validate_generic_get_days
validate_invalidemails_get_start_date = lambda v: False
validate_invalidemails_get_end_date = lambda v: False
validate_invalidemails_get_limit = validate_generic_get_limit
validate_invalidemails_get_offset = validate_generic_get_limit
validate_invalidemails_get_email = lambda v: False

validate_invalidemails_delete_start_date = lambda v: False
validate_invalidemails_delete_end_date = lambda v: False
validate_invalidemails_delete_email = lambda v: False


# Mail Validators
# ---------------

validate_mail_send_to = lambda v: False
validate_mail_send_toname = lambda v: False
validate_mail_send_xsmtpapi = lambda v: False
validate_mail_send_text = lambda v: False
validate_mail_send_html = lambda v: False
validate_mail_send_from = lambda v: False
validate_mail_send_bcc = lambda v: False
validate_mail_send_fromname = lambda v: False
validate_mail_send_replyto = lambda v: False
validate_mail_send_date = lambda v: False
validate_mail_send_files = lambda v: False
validate_mail_send_headers = lambda v: False


# Profile Validators
# ------------------

# Spam Reports Validators
# -----------------------

validate_spamreports_get_date = validate_generic_get_date
validate_spamreports_get_days = validate_generic_get_days
validate_spamreports_get_start_date = lambda v: False
validate_spamreports_get_end_date = lambda v: False
validate_spamreports_get_limit = validate_generic_get_limit
validate_spamreports_get_offset = validate_generic_get_limit
validate_spamreports_get_email = lambda v: False

# Stats Validators
# ----------------

validate_stats_get_start_date = lambda v: False # Says 'days' http://docs.sendgrid.com/documentation/api/web-api/webapistatistics/#get
validate_stats_get_end_date = lambda v: False
validate_stats_get_email = lambda v: False

# Unsubscribes Validators
# -----------------------

validate_unsubscribe_add_email = False

validate_unsubscribe_get_date = validate_generic_get_date
validate_unsubscribe_get_days = validate_generic_get_days
validate_unsubscribe_get_start_date = lambda v: False
validate_unsubscribe_get_end_date = lambda v: False
validate_unsubscribe_get_limit = validate_generic_get_limit
validate_unsubscribe_get_offset = validate_generic_get_limit
validate_unsubscribe_get_email = lambda v: False

validate_unsubscribe_delete_start_date = lambda v: False
validate_unsubscribe_delete_end_date = lambda v: False
validate_unsubscribe_delete_email = lambda v: False

# Helper Function
# ---------------

def validate_parameter(module, action, parameter, value):
	"""
	Validates the given value for a parameter.
	"""
	validatorName = "_".join(["validate", module, action, parameter])
	validator = getattr(globals, validatorName, None)
	if validator:
		parameterIsValid = validator(value)
	else:
		print "AHH", validatorName
		parameterIsValid = None
	return parameterIsValid

