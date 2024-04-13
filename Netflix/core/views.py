from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import auth
from core.models import Movie, MovieList
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import re


# Create your views here.
@login_required(login_url="login")
def index(request):
    movies = None
    movies = Movie.objects.all().order_by("title")
    featured_movie = None
    if movies:
        featured_movie = movies[len(movies) - 1]

    context = {
        "movies": movies,
        "featured_movie": featured_movie,
    }
    return render(request, "index.html", context)


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, "Credentials Invalid")
            return redirect("login")

    return render(request, "login.html")


def signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email alredy exist.")
                return redirect("signup")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username taken.")
                return redirect("signup")
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect("/")
        else:
            messages.info(request, "Password not matching.")
            return redirect("signup")

    else:
        return render(request, "signup.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    return redirect("login")


@login_required(login_url="login")
def movie(request, pk=None):
    movie_uuid = pk
    movie_details = Movie.objects.get(uu_id=movie_uuid)

    context = {"movie_details": movie_details}

    return render(request, "movie.html", context)


@login_required(login_url="login")
def genre(request, pk=None):
    movie_genre = pk
    movies = Movie.objects.filter(genre=movie_genre)

    context = {
        'movies': movies,
        'movie_genre': movie_genre,
    }
    return render(request, 'genre.html', context)


@login_required(login_url="login")
def my_list(request):
    movie_list = MovieList.objects.filter(owner_user=request.user)
    user_movie_list = []

    for movie in movie_list:
        user_movie_list.append(movie.movie)

    context = {"movies": user_movie_list}
    return render(request, "my_list.html", context)


@login_required(login_url="login")
def add_to_list(request):
    if request.method == "POST":
        movie_url_id = request.POST.get("movie_id")
        uuid_patterns = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        match = re.search(uuid_patterns, movie_url_id)
        movie_id = match.group() if match else None

        movie = get_object_or_404(Movie, uu_id=movie_id)
        movie_list, created = MovieList.objects.get_or_create(
            owner_user=request.user, movie=movie
        )

        if created:
            respose_data = {"status": "success", "message": "Movie added."}
        else:
            respose_data = {"status": "info", "message": "Movie already in list."}

        return JsonResponse(respose_data)
    else:
        return JsonResponse(
            {"status": "error", "message": "Invalid request"}, status=400
        )


@login_required(login_url='login')
def search(request):
    if request.method == 'POST':
        search_term = request.POST['search_term']
        movies = Movie.objects.filter(title__icontains=search_term)

        context = {
            'movies': movies,
            'search_term': search_term,
        }
        return render(request, 'search.html', context)
    else:
        return redirect('/')