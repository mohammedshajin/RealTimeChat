from django.shortcuts import render

def home_screen_view(request, *args, **kwars):

    context = {}
    return render(request, "personal/home.html", context)
# Create your views here.
