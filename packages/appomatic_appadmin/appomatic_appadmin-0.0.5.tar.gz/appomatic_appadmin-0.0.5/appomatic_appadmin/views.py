import django.shortcuts
import django.template
import settings
import appomatic_appadmin.utils.app
import appomatic_appadmin.utils.reload
import django.contrib.messages

def apps_by_source(apps):
    res = {}
    for app in apps:
        if app['SOURCE'] not in res:
            res[app['SOURCE']] = []
        res[app['SOURCE']].append(app)
    return res

def index(request):
    action = request.POST.get('action', '')

    if action == 'uninstall_selected':
        for name in appomatic_appadmin.utils.app.uninstall_pip_apps(
            *request.POST.getlist('_selected_action')):
            django.contrib.messages.add_message(request, django.contrib.messages.INFO, 'Successfully uninstalled %s' % (name,))
        appomatic_appadmin.utils.reload.reload(2)

    return django.shortcuts.render_to_response(
        'appomatic_appadmin/index.html',
        {"installed_apps": apps_by_source(settings.APPOMATIC_APPS),


         },
        context_instance=django.template.RequestContext(request))

def add(request):
    action = request.POST.get('action', '')
    query = request.GET.get('q', '')

    if action == 'install_selected':
        for name in appomatic_appadmin.utils.app.install_pip_apps(
            *request.POST.getlist('_selected_action')):
            django.contrib.messages.add_message(request, django.contrib.messages.INFO, 'Successfully installed %s' % (name,))
        appomatic_appadmin.utils.reload.reload(2)

    installed_app_names = [app['NAME'] for app in settings.APPOMATIC_APPS]
    found_apps = [app for app in appomatic_appadmin.utils.app.search_pip_apps(query)
                  if app['name'] not in installed_app_names]

    return django.shortcuts.render_to_response(
        'appomatic_appadmin/add.html',
        {"q": query, "found_apps": found_apps},
        context_instance=django.template.RequestContext(request))
