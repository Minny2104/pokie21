from django.shortcuts import render
from my_blog.models import *
from django.http import JsonResponse
from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.core.mail import send_mail
from my_blog.models import *
import json

# Create your views here.

def cart(request):
    return render(request, 'cart.html', context)

def checkout(request):
    return render(request, 'checkout.html', context)


def postlist(request):   
    if request.GET.get('search'):
        search = request.GET.get('search')
        posts = PostModel.objects.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )
    elif request.GET.get('category'):
        category = request.GET.get('category')
        posts = PostModel.objects.filter(category_id =category)
    else:
        posts = PostModel.objects.all().order_by('-create_date')
    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'postlist.html', {'posts':page_obj})

@permission_required('my_blog.add_postmodel', login_url='/login')
def postcreate(request):
    if request.method == 'GET':
        category = CategoryModel.objects.all()
        return render(request, 'postcreate.html',{'category':category})
    if request.method == 'POST':
        category = PostModel.objects.create(
            title = request.POST.get('title'),
            content = request.POST.get('content'),
            image = request.FILES.get('image'),
            price = request.POST.get('price'),
            author_id = request.user.id,
            category_id = request.POST.get('category')
        )
        messages.success(request, 'Post Created Success!')
        return redirect('postlist')
    
   
def postdetail(request, p_id):
    if request.method == "GET":
        post = PostModel.objects.get(id=p_id)
        cmt = Comment.objects.filter(post_id=p_id)
        return render(request, 'postdetail.html',{'post':post,'cmt':cmt})
    if request.method == "POST":
        if request.user.id == None:
            return redirect('/login')
        cmt = Comment.objects.create(
            content = request.POST.get('content'),
            post_id = p_id,
            author_id = request.user.id
        )
        return redirect(f'/blog/detail/{p_id}/#cmt')

@permission_required('my_blog.delete_postmodel', login_url='/login')
def postdelete(request, p_id):
    post = PostModel.objects.get(id=p_id)
    post.image.delete()
    post.delete()
    messages.success(request, 'Post Deleted Success!')
    return redirect('/blog/list/')

@permission_required('my_blog.change_postmodel', login_url='/login')
def postupdate(request, p_id):
    if request.method == 'GET':
        post = PostModel.objects.get(id=p_id)
        category = CategoryModel.objects.all()
        return render(request, 'postupdate.html',{'post':post, 'category': category})

    if request.method == 'POST':
        post = PostModel.objects.get(id=p_id)
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        if request.FILES.get('image'):
            post.image.delete()
            post.image = request.FILES.get('image')
        post.price = request.POST.get('price')
        post.category_id = request.POST.get('category')
        post.save()
        messages.success(request, 'Post Updated Success!')
        return redirect(f'/blog/detail/{p_id}')
    
def cmtdelete(request, p_id, c_id):
    cmt = Comment.objects.get(id=c_id)
    cmt.delete()
    return redirect(f'/blog/detail/{p_id}/#cmt')

def cmtupdate(request, p_id, c_id):
    if request.method == "GET":
        cmt = Comment.objects.get(id=c_id)
        return render(request, 'cmtupdate.html',{'cmt':cmt})
    if request.method == "POST":
        cmt = Comment.objects.get(id=c_id)
        cmt.content = request.POST.get('content')
        cmt.save()
        return redirect(f'/blog/detail/{p_id}/#cmt')

def myLogin(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(Q(email=username) | Q(username=username))
        except Exception:
            messages.error(request, 'Email or Password is incorrect !')
            return redirect('/login')
        else:
            if user.check_password(password):
                login(request, user)
                messages.success(request, 'Login Success!')
                return redirect('/blog/list')
            else:
                messages.error(request, 'Email or Password is incorrect !')
                return redirect('/login')
        
def mylogout(request):
    logout(request)
    messages.success(request, 'log out Successfully!')
    return redirect('/blog/list')

def myRegister(request):
    if request.method == "GET":
        return render(request,'register.html')
    if request.method == "POST":
        passwd1 = request.POST.get('password')
        passwd2 = request.POST.get('repassword')
        username = request.POST.get('username')
        email = request.POST.get('email')
        if passwd1 == passwd2:
            if User.objects.filter(username=username):
                messages.error(request,'Username already existed !')
                return redirect('/register')
            if User.objects.filter(email=email):
                messages.error(request, 'Email already exists !')
                return redirect('/register')
            user = User.objects.create(
                username = request.POST.get('username'),
                email = request.POST.get('email'),
                password = make_password(passwd1)
        )
            

            messages.success(request, 'Register Success!')    
            return redirect('/blog/list')
        else:
            messages.error(request, 'Password is not the same!')
            return redirect('/register')
    