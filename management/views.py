from django.shortcuts import render,redirect
from .forms import PatientForm,AvailableTimeForm

# Create your views here.
def create_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            # return redirect('Done')
    else:
        form = PatientForm()
    return render(request, 'add_patient.html', {'form': form})



def Create_AvailableTime(request):
    if request.method == "POST":
        form = AvailableTimeForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("/create_availableTime/")

    else:
        form = AvailableTimeForm()

    return render(request,"Create_AvailableTime.html",{"form":form})


