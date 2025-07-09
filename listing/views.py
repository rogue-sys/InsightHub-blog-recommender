from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url="/login/")
def home(request):
    tags = Tag.objects.all()
    context = {'tags': tags}
    return render(request, 'home.html', context)

@login_required(login_url="/login/")
def api_blogs(request):
    blogs_objs = Blog.objects.all()

    price = request.GET.get('price')
    if price:
        blogs_objs = blogs_objs.filter(price__lte=price)

    tag_ids = request.GET.get('tags')
    if tag_ids:
        tag_ids = tag_ids.split(',')
        tag_list = []
        for tag_id in tag_ids:
            try:
                tag_list.append(int(tag_id))
            except Exception:
                pass
        blogs_objs = blogs_objs.filter(tags__in=tag_list).distinct()

    payload = []
    for blog_obj in blogs_objs:
        result = {
            'blog_name': blog_obj.blog_name,
            'blog_description': blog_obj.blog_description,
            'price': blog_obj.price,
        }
        payload.append(result)

    return JsonResponse(payload, safe=False)

def login_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_obj = User.objects.filter(username=username)
            if not user_obj.exists():
                messages.error(request, "Username not found")
                return redirect('/login/')
            user_obj = authenticate(username=username, password=password)
            if user_obj:
                login(request, user_obj)
                return redirect('/')
            messages.error(request, "Wrong Password")
            return redirect('/login/')
        except Exception:
            messages.error(request, "Something went wrong")
            return redirect('/register/')

    return render(request, "login.html")

def register_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_obj = User.objects.filter(username=username)
            if user_obj.exists():
                messages.error(request, "Username is taken")
                return redirect('/register/')
            user_obj = User.objects.create(username=username)
            user_obj.set_password(password)
            user_obj.save()
            messages.success(request, "Account created")
            return redirect('/login/')
        except Exception:
            messages.error(request, "Something went wrong")
            return redirect('/register/')

    return render(request, "register.html")
