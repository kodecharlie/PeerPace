from django import forms

class IdentifyProjectForm(forms.Form):
	# Solicit end-user input for these form fields.
	github_username = forms.CharField(max_length=64)
	github_project_name = forms.CharField(max_length=128)
	personal_access_token = forms.CharField(max_length=128)

	# These form fields are hidden and populated later through GET-request parameters.
	impact_of_code_commits = forms.FloatField(widget=forms.HiddenInput())
	impact_of_line_changes = forms.FloatField(widget=forms.HiddenInput())
	impact_of_past_behavior = forms.IntegerField(widget=forms.HiddenInput())

	def __init__(self, *args, **kwargs):
		arg_impact_of_code_commits = kwargs.pop('impact_of_code_commits')
		arg_impact_of_line_changes = kwargs.pop('impact_of_line_changes')
		arg_impact_of_past_behavior = kwargs.pop('impact_of_past_behavior')
		super(IdentifyProjectForm, self).__init__(*args, **kwargs)

		# Set initial values for some fields.
		self.fields['impact_of_code_commits'].initial = arg_impact_of_code_commits
		self.fields['impact_of_line_changes'].initial = arg_impact_of_line_changes
		self.fields['impact_of_past_behavior'].initial = arg_impact_of_past_behavior
