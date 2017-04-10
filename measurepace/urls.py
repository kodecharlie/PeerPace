from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^parameterize-performance-calculation/$', views.parameterize_performance_calculation, name='parameterize-performance-calculation'),
    url(r'^identify-project$', views.identify_project, name='identify-project'),
    url(r'^calculate-programmer-performance$', views.calculate_programmer_performance, name='calculate-programmer-performance'),
]
