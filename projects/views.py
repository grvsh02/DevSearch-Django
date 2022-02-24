from pydoc import describe
from .forms import RoomForm
from .models import Room, Topic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout

# rooms = [
#     {'id': 1, "name": "learn python here"},
#     {"id": 2, "name": "learn to create ui/ux design with me"},
#     {"id": 3, "name": "frontend developers unite!!"}
# ]


def loginPage(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user != None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'username or password doesnt exist')
    context = {}
    return render(request, 'projects/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def home(request):
    if request.GET.get('q'):
        q = request.GET.get('q')
    else:
        q = ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    room_count = rooms.count()
    topics = Topic.objects.all()
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'projects/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    # for i in rooms:
    #     if i["id"] == int(pk):
    #         room = i["name"]
    context = {"room": room}
    return render(request, 'projects/room.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    context = {'form': form}
    return render(request, 'projects/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    # if request.user != room.host:
    #     return

    context = {'form': form}
    return render(request, 'projects/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'projects/delete.html', {'obj': room})
