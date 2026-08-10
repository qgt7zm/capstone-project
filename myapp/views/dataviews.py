"""
Data views for myapp application.
"""
import json

from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect

from myapp.forms import UploadDataForm, DeleteDataForm
from myapp.models import model_classes


def data_export(request) -> HttpResponse:
    # Export data to JSON
    # Source: https://docs.djangoproject.com/en/5.1/topics/serialization/

    # Combine JSON arrays
    all_data = []
    for model_class in model_classes:
        model_data = model_class.objects.all().order_by("pk")
        # Exports to JSON array
        json_str = serializers.serialize("json", model_data)
        all_data += json.loads(json_str)

    return JsonResponse(all_data, safe=False)  # Need to export array


def data_upload(request) -> HttpResponse:
    if request.method == "POST":
        form = UploadDataForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Import data from JSON array
                file = form.cleaned_data.get("file")
                model_data = serializers.deserialize("json", file)

                # DANGER: Delete all data
                for model_class in model_classes:
                    model_class.objects.all().delete()

                for model_obj in model_data:
                    model_obj.object.save()
                    model_obj.save(save_m2m=True)
                messages.success(request, "Data uploaded successfully.")
            except serializers.base.DeserializationError:
                messages.error(request, "Please use the Django models .json format.")
        else:
            messages.error(request, "Please select a .json file.")

    return redirect("myapp:data")


def data_delete(request) -> HttpResponse:
    if request.method == "POST":
        form = DeleteDataForm(request.POST)
        if form.is_valid():
            # DANGER: Delete all data
            for model_class in model_classes:
                model_class.objects.all().delete()

            messages.success(request, "Data deleted successfully.")
        else:
            messages.error(request, "Please use the button to delete data.")

    return redirect("myapp:data")
