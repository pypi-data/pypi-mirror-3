from __future__ import absolute_import

from collections import defaultdict

from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.test import TestCase

from .mail import get_sendgrid_connection
from .mail import send_sendgrid_mail
from .message import SendGridEmailMessage
from .message import SendGridEmailMultiAlternatives
from .signals import sendgrid_email_sent
from .utils import filterutils
from .utils import in_test_environment


TEST_SENDER_EMAIL = "ryan@example.com"
TEST_RECIPIENTS = ["ryan@example.com"]

validate_filter_setting_value = filterutils.validate_filter_setting_value
validate_filter_specification = filterutils.validate_filter_specification
update_filters = filterutils.update_filters


class SendGridEmailTest(TestCase):
	"""docstring for SendGridEmailTest"""
	def test_email_has_unique_id(self):
		"""
		Tests the existence of the ``SendGridEmailMessage._message_id`` attribute.
		"""
		email = SendGridEmailMessage()
		self.assertTrue(email._message_id)
		
	def test_email_sends_unique_id(self):
		"""
		Tests sending a ``SendGridEmailMessage`` adds a ``message_id`` to the unique args.
		"""
		email = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		email.send()
		self.assertTrue(email.sendgrid_headers.data["unique_args"]["message_id"])
		
	def test_unique_args_persist(self):
		"""
		Tests that unique args are not lost due to sending adding the ``message_id`` arg.
		"""
		email = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		uniqueArgs = {
			"unique_arg_1": 1,
			"unique_arg_2": 2,
			"unique_arg_3": 3,
		}
		email.sendgrid_headers.setUniqueArgs(uniqueArgs)
		email.send()

		for k, v in uniqueArgs.iteritems():
			self.assertEqual(v, email.sendgrid_headers.data["unique_args"][k])

		self.assertTrue(email.sendgrid_headers.data["unique_args"]["message_id"])

	def test_email_sent_signal_has_message(self):
		"""
		Tests the existence of the ``message`` keywork arg from the ``sendgrid_email_sent`` signal.
		"""
		@receiver(sendgrid_email_sent)
		def receive_sendgrid_email_sent(*args, **kwargs):
			"""
			Receives sendgrid_email_sent signals.
			"""
			self.assertTrue("response" in kwargs)
			self.assertTrue("message" in kwargs)
			
		email = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		response = email.send()


class SendGridInTestEnvTest(TestCase):
	def test_in_test_environment(self):
		"""
		Tests that the test environment is detected.
		"""
		self.assertEqual(in_test_environment(), True)


class SendWithSendGridEmailMessageTest(TestCase):
	def setUp(self):
		"""
		Sets up the tests.
		"""
		self.signalsReceived = defaultdict(list)
		
	def test_send_email_sends_signal(self):
		"""
		Tests that sending a ``SendGridEmailMessage`` sends a ``sendgrid_email_sent`` signal.
		"""
		@receiver(sendgrid_email_sent)
		def receive_sendgrid_email_sent(*args, **kwargs):
			"""
			Receives sendgrid_email_sent signals.
			"""
			self.signalsReceived["sendgrid_email_sent"].append(1)
			return True
			
		email = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		email.send()
		
		numEmailSentSignalsRecieved = sum(self.signalsReceived["sendgrid_email_sent"])
		self.assertEqual(numEmailSentSignalsRecieved, 1)
		
	def test_send_with_send_mail(self):
		"""
		Tests sending an email with the ``send_email_with_sendgrid`` helper.
		"""
		send_sendgrid_mail(
			subject="Your new account!",
			message="Thanks for signing up.",
			from_email='welcome@example.com',
			recipient_list=['ryan@example.com'],
		)


class SendWithEmailMessageTest(TestCase):
	"""docstring for SendWithEmailMessageTest"""
	def setUp(self):
		"""
		Sets up the tests.
		"""
		self.connection = get_sendgrid_connection()
		
	def test_send_with_email_message(self):
		"""
		Tests sending an ``EmailMessage`` with the ``SendGridEmailBackend``.
		"""
		email = EmailMessage(
			subject="Your new account!",
			body="Thanks for signing up.",
			from_email='welcome@example.com',
			to=['ryan@example.com'],
			connection=self.connection,
		)
		email.send()


class SendWithSendGridEmailMultiAlternativesTest(TestCase):
	def setUp(self):
		self.signalsReceived = defaultdict(list)
		
	def test_send_multipart_email(self):
		"""
		Tests sending multipart emails.
		"""
		subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
		text_content = 'This is an important message.'
		html_content = '<p>This is an <strong>important</strong> message.</p>'
		msg = SendGridEmailMultiAlternatives(subject, text_content, from_email, [to])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
		
	def test_send_multipart_email_sends_signal(self):
		@receiver(sendgrid_email_sent)
		def receive_sendgrid_email_sent(*args, **kwargs):
			"""
			Receives sendgrid_email_sent signals.
			"""
			self.signalsReceived["sendgrid_email_sent"].append(1)
			return True
			
		email = SendGridEmailMultiAlternatives(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		email.send()
		
		numEmailSentSignalsRecieved = sum(self.signalsReceived["sendgrid_email_sent"])
		self.assertEqual(numEmailSentSignalsRecieved, 1)


class FilterUtilsTests(TestCase):
	"""docstring for FilterUtilsTests"""
	def setUp(self):
		"""
		Set up the tests.
		"""
		pass
		
	def test_validate_filter_spec(self):
		"""
		Tests validation of a filter specification.
		"""
		filterSpec = {
			"subscriptiontrack": {
				"enable": 1,
			},
			"opentrack": {
				"enable": 0,
			},
		}
		self.assertEqual(validate_filter_specification(filterSpec), True)
		
	def test_subscriptiontrack_enable_parameter(self):
		"""
		Tests the ``subscriptiontrack`` filter's ``enable`` paramter.
		"""
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", 0), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", 1), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", 0.0), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", 1.0), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", "0"), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", "1"), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", "0.0"), False)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", "1.0"), False)
		
	def test_opentrack_enable_parameter(self):
		"""
		Tests the ``opentrack`` filter's ``enable`` paramter.
		"""
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", 0), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", 1), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", 0.0), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", 1.0), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", "0"), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", "1"), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", "0.0"), False)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", "1.0"), False)


class UpdateFiltersTests(TestCase):
	"""docstring for SendWithFiltersTests"""
	def setUp(self):
		"""docstring for setUp"""
		self.email = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		
	def test_update_filters(self):
		"""
		Tests SendGrid filter functionality.
		"""
		filterSpec = {
			"subscriptiontrack": {
				"enable": 1,
			},
			"opentrack": {
				"enable": 0,
			},
		}
		update_filters(self.email, filterSpec)
		self.email.send()
