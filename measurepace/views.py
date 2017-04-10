from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader

import json
from performance_parameters_form import PerformanceParametersForm
from identify_project_form import IdentifyProjectForm
from peerpace import PeerPace

def index(request):
    return HttpResponse("Welcome to PeerPace, a tool that evaluates programmer productivity.")

def parameterize_performance_calculation(request):
    pp_form = PerformanceParametersForm()
    context = { 'performance_parameters_form': pp_form }
    return render(request, 'measurepace/parameterize-performance-calculation.html', context)

def identify_project(request):
    ip_form = IdentifyProjectForm(
    	impact_of_code_commits = request.GET.get('impact_of_code_commits'),
    	impact_of_line_changes = request.GET.get('impact_of_line_changes'),
    	impact_of_past_behavior = request.GET.get('impact_of_past_behavior'),
    )
    context = { 'identify_project_form': ip_form }
    return render(request, 'measurepace/identify-project.html', context)

def calculate_programmer_performance(request):
	peerpace = PeerPace()

	peerpace_json = peerpace.calculate_programmer_performance(
		request.GET.get('github_username'),
		request.GET.get('github_project_name'),
		request.GET.get('personal_access_token'),
		float(request.GET.get('impact_of_code_commits')),
		float(request.GET.get('impact_of_line_changes')),
		float(request.GET.get('impact_of_past_behavior'))
	)

	peerpace_info = json.loads(peerpace_json)
	return JsonResponse(peerpace_info)
