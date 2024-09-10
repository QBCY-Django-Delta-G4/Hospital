from django.http import HttpRequest
from django.shortcuts import render,redirect
from .forms import AvailableTimeForm



def Create_AvailableTime(request:HttpRequest):
    if request.method == "POST":
        form = AvailableTimeForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("/create_availableTime/")

    else:
        form = AvailableTimeForm()

    return render(request,"Create_AvailableTime.html",{"form":form})

