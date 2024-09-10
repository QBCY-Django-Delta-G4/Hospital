from django.shortcuts import render
from .forms import PatientForm

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
