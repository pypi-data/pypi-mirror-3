from django import forms


class SendGridEventForm(forms.Form):
	email = forms.EmailField()
	# event = JSONFormField()
	event = forms.CharField()
