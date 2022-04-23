from django.shortcuts import render, redirect
from django.http import HttpResponse
from .decorators import unauthenticated_user
from .decorators import unauthenticated_user, allowed_users, admin_only
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
from django.forms import  inlineformset_factory
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get("username")

                messages.success(request, 'Account was created for ' + username)
                return redirect("login")
    context = {'form':form}
    return render(request, "myfolder/register.html", context)
@allowed_users(allowed_roles=['customer'])
@login_required(login_url="login")
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status="Delivered").count()
    pending = orders.filter(status="Pending").count()


    context = {"orders":orders, "total_orders":total_orders,"delivered":delivered,"pending":pending}

    return render(request, "myfolder/user.html", context)
@unauthenticated_user
def loginPage(request):
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.info(request, "username OR password is incorrect")

        context = {}

        return render(request, "myfolder/login.html", context)

def logoutUser(request):
    logout(request)
    return redirect("login")
# Create your views here.
@login_required(login_url="login")
@admin_only
def home (request):
    # Pull from models/database, put the objects through a context for rendering later on the next line
    orders = Order.objects.all()
    customers = Customer.objects.all()
    total_customers = customers.count()
    order_count = Customer.objects.all()
    total_orders = orders.count()
    delivered = orders.filter(status="Delivered").count()
    pending = orders.filter(status="Pending").count()


    context = {"orders":orders, "customers":customers, "total_orders":total_orders, "delivered":delivered,"pending":pending}


    return render(request, "myfolder/dashboard.html", context)

@allowed_users(allowed_roles=['admin'])
@login_required(login_url="login")
def products (request):
    products = Product.objects.all()
    return render(request, "myfolder/products.html", {"products" :products})

@allowed_users(allowed_roles=['admin'])
@login_required(login_url="login")
def customer (request, pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    order_count = orders.count()
    context = {"customer":customer, "orders":orders, "order_count":order_count, "myFilter":myFilter}
    return render(request, "myfolder/customer.html",context)
def dashboard (request):
    return render(request, "myfolder/dashboard.html")

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):

    OrderFormSet = inlineformset_factory(Customer, Order, fields=("product", "status"), extra=10)
    # get customer from DB
    customer = Customer.objects.get(id=pk)

    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)

    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect("/")
        else:
            messages.info(request, "username OR password is incorrect")
            return render(request, "myfolder/login.html")

    context = {'formset':formset}
    return render(request, "myfolder/order_form.html", context)

@login_required(login_url="login")
@allowed_users(allowed_roles=['customer','admin'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {"form":form}
    return render(request, "myfolder/myfolder_settings.html", context)

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect("/")


    context = {"form": form}
    return render(request, "myfolder/order_form.html", context)
@login_required(login_url="login")
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect("/")
    context = {"item": order}
    return render(request, "myfolder/delete.html", context)