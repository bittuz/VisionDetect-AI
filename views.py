from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from ultralytics import YOLO
import os, uuid, subprocess

# Load YOLOv8 model
model = YOLO(r"objectdetection/Model/best.pt")

def index(request):
    # Handle contact form submission
    if request.method == "POST" and request.POST.get("form_type") == "contact":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message_text = request.POST.get("message")

        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_text}"

        send_mail(
            subject=f"Contact Form Submission from {name}",
            message=full_message,
            from_email=email,
            recipient_list=["bittu.john08@gmail.com"],
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect("index")

    return render(request, "index.html")


def analyze(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)

        # Output directory
        processed_dir = os.path.join(settings.MEDIA_ROOT, "processed")
        os.makedirs(processed_dir, exist_ok=True)

        unique_run = f"run_{uuid.uuid4().hex[:8]}"
        output_folder = os.path.join(processed_dir, unique_run)
        os.makedirs(output_folder, exist_ok=True)

        # Run YOLO
        model.predict(
            source=file_path,
            save=True,
            project=processed_dir,
            name=unique_run,
            exist_ok=True
        )

        # Find YOLO output video
        yolo_output_path = None
        for f in os.listdir(output_folder):
            if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                yolo_output_path = os.path.join(output_folder, f)
                break

        if not yolo_output_path:
            return render(request, "result.html", {"error": "No processed video found."})

        # Re-encode to browser-friendly MP4
        output_name = f"{uuid.uuid4()}.mp4"
        final_output_path = os.path.join(processed_dir, output_name)
        subprocess.run([
            "ffmpeg", "-y", "-i", yolo_output_path,
            "-vcodec", "libx264", "-acodec", "aac",
            final_output_path
        ])

        # Redirect to result page
        return redirect('result', video_name=output_name)

    return redirect('index')


def result(request, video_name):
    video_url = f"{settings.MEDIA_URL}processed/{video_name}"
    return render(request, "result.html", {"video_url": video_url})
