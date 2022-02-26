from email import message
from http.client import HTTPResponse
from pydoc import describe
from .forms import RoomForm
from .models import Message, Room, Topic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout

# rooms = [
#     {'id': 1, "name": "learn python here"},
#     {"id": 2, "name": "learn to create ui/ux design with me"},
#     {"id": 3, "name": "frontend developers unite!!"}
# ]


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'projects/profile.html', context)


def loginPage(request):
    page = "login"
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
    context = {"page": page}
    return render(request, 'projects/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Please retry")
    return render(request, 'projects/login_register.html', {'form': form})


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

    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)).order_by('-created')

    topics = Topic.objects.all()
    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'projects/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {"room": room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'projects/room.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
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


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HTTPResponse('You are not allowed here !')

    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'projects/delete.html', {'obj': message})
