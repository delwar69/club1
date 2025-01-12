from django.shortcuts import render, redirect
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Notice, Member, GalleryImage, ClubMember
from .forms import ClubMemberForm
import os
from django.shortcuts import render
from reportlab.graphics import renderPDF
from django.conf import settings
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics  # Correct import for pdfmetrics
from reportlab.lib.units import inch, cm, mm
from reportlab.lib import colors
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import utils
from django.utils.timezone import now
#from reportlab.lib import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.platypus import Image
from reportlab.lib.pagesizes import A4

def home(request):
    notices = Notice.objects.all()
    members = Member.objects.all()
    gallery = GalleryImage.objects.all()
    return render(request, 'club/home.html', {'notices': notices, 'members': members, 'gallery': gallery})

# About Us Section Views
def about_club(request):
    return render(request, 'club/about_club.html')

def president(request):
    return render(request, 'club/president.html')

def secretary(request):
    return render(request, 'club/secretary.html')

def former_president(request):
    return render(request, 'club/former_president.html')

def former_secretary(request):
    return render(request, 'club/former_secretary.html')

def adhoc_committee(request):
    return render(request, 'club/adhoc_committee.html')

def all_members(request):
    return render(request, 'club/all_members.html')

# Service & Facilities Section Views
def celebration(request):
    return render(request, 'club/celebration.html')

def congratulations(request):
    return render(request, 'club/congratulations.html')

# Sports & Fitness Section Views
def badminton(request):
    return render(request, 'club/badminton.html')

def gym(request):
    return render(request, 'club/gym.html')

def table_tennis(request):
    return render(request, 'club/table_tennis.html')

def cards(request):
    return render(request, 'club/cards.html')

def squash(request):
    return render(request, 'club/squash.html')

# Contact Section Views
def contact(request):
    return render(request, 'club/contact.html')

# View to handle new member registration
def new_member_registration(request):
    if request.method == 'POST':
        form = ClubMemberForm(request.POST, request.FILES)
        if form.is_valid():
            club_member = form.save()
            pdf_response = generate_member_pdf(club_member)
            return pdf_response
        else:
            # Display the form with errors
            return render(request, 'club/new_member_registration.html', {'form': form})
    else:
        form = ClubMemberForm()
    return render(request, 'club/new_member_registration.html', {'form': form})

# Generate member PDF with provided details
def generate_member_pdf(club_member):
    # Register Bangla font
    bangla_font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Siyamrupali.ttf')
    
     # Check if the font file exists
    if not os.path.exists(bangla_font_path):
        raise FileNotFoundError(f"Font file not found: {bangla_font_path}")
    
     # Register font if the file exists
    pdfmetrics.registerFont(TTFont('Bangla', bangla_font_path))

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=registration_form_{club_member.id}.pdf'

    # Initialize canvas
    c = canvas.Canvas(response, pagesize=A4)
    top_margin = 800
    left_margin = 50
    right_margin = 550

    # Add BTV Club Logo 
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'btvclub_logo.png')
    logo_x, logo_y = left_margin + 6, top_margin - 35
    c.drawImage(logo_path, logo_x + 15, logo_y, width=25 * mm, height=28 * mm, preserveAspectRatio=True, anchor='c')

    # Titles
    c.setFont("Bangla", 14)
    c.setFillColor(colors.darkgreen)
    c.drawString(logo_x + 130, top_margin, "বাংলাদেশ টেলিভিশন অফিসার্স ক্লাব")
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawString(logo_x + 130, top_margin - 20, "Bangladesh Television Officers' Club")

    # Red Horizontal Line
    c.setStrokeColor(colors.red)
    c.setLineWidth(2)
    c.line(left_margin + 20, top_margin - 50, right_margin - 30, top_margin - 50)

    # Centered Membership Form Title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(300, top_margin - 75, "MEMBERSHIP FORM")

    # Profile Picture 
    profile_pic_width, profile_pic_height = 30 * mm, 35 * mm
    profile_x = right_margin - profile_pic_width + 12
    profile_y = top_margin - 100

    # Draw rectangle around the profile picture (0.5px black border)
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.3)
    c.rect(profile_x - 2, profile_y - 2, profile_pic_width + 4, profile_pic_height + 4)

    if club_member.profile_picture:
        c.drawImage(club_member.profile_picture.path, profile_x, profile_y, width=profile_pic_width, height=profile_pic_height)

    # Member Information
    details_x, details_y = left_margin, profile_y - 20
    line_height = 20
    c.setFont("Helvetica", 10)

    details = [
        ("Name", club_member.name),
        ("Designation", club_member.designation),
        ("Joining Date", club_member.joining_date),
        ("Department", club_member.department),
        ("Date of Birth", club_member.date_of_birth),
        ("Spouse Name", club_member.spouse_name),
        ("Religion", club_member.religion),
        ("Gender", club_member.gender),
        ("Permanent Address", club_member.permanent_address),
        ("Present Address", club_member.present_address),
        ("Email", club_member.email),
        ("Mobile", club_member.mobile),
        ("Phone (Office)", club_member.phone_office),
        ("Phone (Residence)", club_member.phone_residence),
        ("Blood Group", club_member.blood_group),
    ]

    for label, value in details:
        c.drawString(details_x, details_y, f"{label}:")
        c.drawString(details_x + 120, details_y, str(value))
        details_y -= line_height

    # Signatures and Date
    details_y -= 40
    if club_member.signature_image:
        c.drawImage(club_member.signature_image.path, details_x, details_y, width=100, height=40)
    c.drawString(details_x+15, details_y - 35, "Signature:")
    c.drawString(details_x + 400, details_y-10, f"{now().strftime('%Y-%m-%d')}")
    c.drawString(details_x + 412, details_y - 35, "Date")

    # Signature Section - Before QR Code
    details_y -= 120
    c.drawString(details_x, details_y, "Signature of Focal Point:")
    c.drawString(details_x + 200, details_y, "Signature of General Secretary:")
    c.drawString(details_x + 400, details_y, "Signature of President:")

    # QR Code - Smaller size, moved 10px leftward
    qr_data = f"ID: {club_member.id}, Name: {club_member.name}, Designation: {club_member.designation}, Department: {club_member.department}"
    qr_widget = QrCodeWidget(qr_data)
    qr_size = 40
    d = Drawing(qr_size, qr_size)
    d.add(qr_widget)
    renderPDF.draw(d, c, right_margin - 100, details_y - 110)

    # Membership ID - Moved downward 8px
    details_y -= 80
    c.drawString(details_x, details_y, f"Membership ID: {club_member.id}")

    # Footer Section - Moved downward 4px
    footer_y = details_y - 95
    c.setFillColor("#004d40")
    c.rect(0, footer_y - 40, A4[0], 40, fill=1)
    c.setFillColor(colors.white)
    c.drawCentredString(A4[0] / 2, footer_y - 20, "OFFICERS' CLUB, Bangladesh Television, Rampura, Dhaka-1219")

    # Finalize PDF
    c.showPage()
    c.save()

    return response