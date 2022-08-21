from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import User, Task
from django.views.decorators.csrf import csrf_exempt

def index(request):
    template = loader.get_template('tasks/index.html')
    context = {}
    return HttpResponse(template.render(context, request))

def register(request):
    template = loader.get_template('tasks/register.html')
    context = {}
    return HttpResponse(template.render(context, request))

def error(request):
    template = loader.get_template('tasks/error.html')
    context = {}
    return HttpResponse(template.render(context, request))

def tasks(request, username):
    user = User.objects.get(username=username)
    all_tasks = Task.objects.all().filter(task_user=user)
    done_tasks = all_tasks.filter(done=1)
    undone_tasks = all_tasks.filter(done=0)
    template = loader.get_template('tasks/tasks.html')
    context = { 'done_tasks' : done_tasks, 'username' : username, 'undone_tasks' : undone_tasks, }
    return HttpResponse(template.render(context, request))

def donetask(request):
    username = request.session['username']
    key = request.POST['task']
    task = Task.objects.get(task_number=key)
    task.done = 1
    task.save()
    return HttpResponseRedirect(reverse('tasks', args=(username,)))

@csrf_exempt
def addtask(request):
    task_text = request.POST['task']
    username = request.session['username']
    task_user = User.objects.get(username=username)
    number = int(Task.objects.all().count()) + 1
    try:
        task = Task(task_text=task_text, task_user=task_user, done=0, task_number=number)
        task.save()
        return HttpResponseRedirect(reverse('tasks', args=(username,)))
    except:
        return HttpResponseRedirect(reverse('error'))       

def adduser(request):
    username = request.POST['username']
    password = request.POST['password']
    password2 = request.POST['password2']
    if password != password2:
        return HttpResponseRedirect(reverse('error'))
    try:
        user = User(username=username, password=password)
        user.save()
        return HttpResponseRedirect(reverse('index'))
    except:
        return HttpResponseRedirect(reverse('error'))

def signin(request):
    username = request.POST['username']
    password = request.POST['password']
    try:
        query = 'SELECT * FROM tasks_user WHERE username = "%s"' % request.POST['username']
        user = User.objects.raw(query)[0]
        if password == user.password:
            request.session['username'] = username
            return HttpResponseRedirect(reverse('tasks', args=(username,)))
        return HttpResponseRedirect(reverse('error'))
    except:
        return HttpResponseRedirect(reverse('error'))

def signout(request):
    request.session.flush()
    template = loader.get_template('tasks/index.html')
    context = {}
    return HttpResponse(template.render(context, request))