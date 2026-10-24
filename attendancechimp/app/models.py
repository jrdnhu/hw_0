"""
models.py — Data model for AttendanceChimp.

AttendanceChimp is an electronic class attendance tool.  Instructors create
courses and lectures; each lecture is assigned a random QR code.  Students
photograph the QR code and upload the image.  The system decodes the QR code,
matches it to a lecture, and records the attendance.

Entities
--------
- CourseProfile   : extends Django User → instructor-specific data
- StudentProfile  : extends Django User → student-specific data
- Course          : a course taught by one instructor
- Enrollment      : junction table linking students to courses
- Lecture         : a single class meeting (has a QR-code identifier)
- QRCodeUpload    : a student's uploaded QR-code photograph
"""

from django.db import models
from django.contrib.auth.models import User

import logging
import string
import random

logger = logging.getLogger(__name__) # set up tracking, auditing, and debugging
                                                               # allows using logger.warning(), logger.error(), 
                                                               # logger.info(), etc. Better than print() for debuggin... 


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------
class InstructorProfile(models.Model):
    """
    Represents an Instructor and connects them to Django. Referenced by courses. 
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class StudentProfile(models.Model):
    """
    Represents a Student and connects them to Django. Referenced by Enrollements and Qr Code Upload. 
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------
class Course(models.Model):
    """
    Represents a Course taught by a single Instructor. Stores course name, instructor, and meeting schedule. 
    """
    name = models.CharField()
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.PROTECT)
    meeting_schedule = models.CharField()


# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------
class Enrollment(models.Model):
    """
    Represents a student's enrollment in a course. 
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------
class Lecture(models.Model):
    """
    Represents one lecture of a course. Stores lecture time and date and unique qr_identifier
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField()
    qr_identifier = models.CharField(unique=True)


# ---------------------------------------------------------------------------
# QR Code Upload
# ---------------------------------------------------------------------------
class QRCodeUpload(models.Model):
    """
    Represents a qr code submitted by a student. 
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.FileField(upload_to="qrcodes/")

# ---------------------------------------------------------------------------
# Helper / API functions
# ---------------------------------------------------------------------------



