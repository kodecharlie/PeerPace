from django import forms

# We dynamically populate these hidden fields on the browser side.
class PerformanceParametersForm(forms.Form):
	impact_of_code_commits = forms.FloatField(widget=forms.HiddenInput())
	impact_of_line_changes = forms.FloatField(widget=forms.HiddenInput())
	impact_of_past_behavior = forms.IntegerField(widget=forms.HiddenInput())
