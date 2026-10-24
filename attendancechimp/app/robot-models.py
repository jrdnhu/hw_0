# LLM: ChatGPT

# Prompt:
# Generate a simple Django models.py for an app called AttendanceChimp. Emphasize attendance tracking and preventing cheating.
# Include these six models:
# - InstructorProfile: connected one-to-one to Django’s existing User accounts.
# - StudentProfile: connected one-to-one to Django’s existing User accounts.
# - Course table: table with at least name, instructor, meeting schedule.
# - Enrollment table: links students to courses (many-to-many).
# - Lecture table: linked to a course, has a date and a QR identifier.
# - QRCodeUpload: linked to a student and (optionally) a lecture.

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class InstructorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.user.username


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    student_id = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.user.username


class Course(models.Model):
    name = models.CharField(max_length=200)
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    meeting_schedule = models.CharField(max_length=200)

    students = models.ManyToManyField(
        StudentProfile,
        through="Enrollment",
        related_name="courses"
    )

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course"
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.course}"


class Lecture(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lectures"
    )
    date = models.DateField()

    # Unique QR identifier for each lecture
    qr_identifier = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    # QR codes expire to discourage sharing
    qr_expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.course.name} - {self.date}"


class QRCodeUpload(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="qr_uploads"
    )
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qr_uploads"
    )

    scanned_qr_identifier = models.UUIDField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(
        default=False,
        editable=False
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "lecture"],
                name="unique_student_lecture_attendance"
            )
        ]

    def clean(self):
        if self.lecture_id:
            # Student must be enrolled in the course
            if not Enrollment.objects.filter(
                student_id=self.student_id,
                course_id=self.lecture.course_id
            ).exists():
                raise ValidationError(
                    "Student is not enrolled in this course."
                )

            # Scanned QR must match the lecture
            if self.scanned_qr_identifier != self.lecture.qr_identifier:
                raise ValidationError("Invalid QR code.")

            # QR code must not be expired
            if timezone.now() > self.lecture.qr_expires_at:
                raise ValidationError("QR code has expired.")

    def save(self, *args, **kwargs):
        self.full_clean()
        self.is_verified = self.lecture_id is not None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.lecture}"
