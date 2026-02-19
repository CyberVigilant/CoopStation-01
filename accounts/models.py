from django.conf import settings
from django.db import models
from django.utils import timezone


# -----------------------------
# Shared enums
# -----------------------------
class OpportunityStatus(models.TextChoices):
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"


class ReportType(models.TextChoices):
    BROKEN_LINK = "broken_link", "Broken link"
    WRONG_DEADLINE = "wrong_deadline", "Wrong deadline"
    WRONG_LOCATION = "wrong_location", "Wrong location"
    DUPLICATE = "duplicate", "Duplicate"
    SCAM = "scam", "Scam"
    OTHER = "other", "Other"


class ReportStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RESOLVED = "resolved", "Resolved"


class SubmitterType(models.TextChoices):
    STUDENT = "student", "Student"
    ADMIN = "admin", "Admin"
    AI = "ai", "AI"


class SubmissionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class ValidationResult(models.TextChoices):
    PENDING = "pending", "Pending"
    PASS = "pass", "Pass"
    FAIL = "fail", "Fail"


class ParsedState(models.TextChoices):
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"
    NOT_OPPORTUNITY = "not_opportunity", "Not opportunity"
    UNSURE = "unsure", "Unsure"


class ObsParsedStatus(models.TextChoices):
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"
    UNSURE = "unsure", "Unsure"
    ERROR = "error", "Error"


# -----------------------------
# Core profiles
# -----------------------------
class Student(models.Model):
    # IMPORTANT: Keep Student == Django User (1:1)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    full_name = models.CharField(max_length=150, blank=True)
    major = models.CharField(max_length=120, blank=True)

    # extra fields from your schema (does NOT replace Django user)
    phone_num = models.CharField(max_length=30, null=True, blank=True)
    linkedin_url = models.CharField(max_length=500, null=True, blank=True)

    @property
    def email(self) -> str:
        """Convenience accessor. Email is stored on the linked Django user."""
        return self.user.email

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # keep your current behavior
        return self.user.username


class Admin(models.Model):
    # Simple admin profile (you can later link this to AUTH_USER_MODEL if you want)
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


# -----------------------------
# Opportunities
# -----------------------------

class OppCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# High-level categories (majors) used for opportunities.
# Keep these broad (college-level) and avoid deep specializations.
DEFAULT_CATEGORIES = [
    "Computer Science & IT",
    "Cybersecurity",
    "Software Engineering",
    "Data & AI",
    "Information Systems",
    "Engineering",
    "Architecture & Planning",
    "Design (UI/UX & Graphic)",
    "Business & Management",
    "Finance",
    "Accounting",
    "Marketing",
    "Media & Communications",
    "Law",
    "Shariah & Islamic Studies",
    "Education",
    "Healthcare",
    "Pharmacy",
    "Agriculture & Environmental",
    "Arts & Humanities",
]


def seed_default_categories() -> None:
    """Create the default opportunity categories if they don't exist."""
    for name in DEFAULT_CATEGORIES:
        OppCategory.objects.get_or_create(name=name)


def get_default_category():
    """
    Returns the default category ID, creating it if it does not exist.
    We also seed the broad category list to keep the database consistent.
    """
    try:
        seed_default_categories()
        category, _ = OppCategory.objects.get_or_create(name="Computer Science & IT")
        return category.id
    except Exception:
        # Fallback for early migration/import edge cases
        category, _ = OppCategory.objects.get_or_create(name="General")
        return category.id


class Opportunity(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # Optional: rich HTML (store sanitized HTML from scraper later)
    description_html = models.TextField(null=True, blank=True)

    # Optional: plain text extracted from HTML (used for search + change tracking)
    description_text = models.TextField(null=True, blank=True)

    # Hash of description_text (e.g., sha256) to detect changes efficiently
    description_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    # When we last scraped/checked this opportunity
    last_checked_at = models.DateTimeField(null=True, blank=True)

    # Stored as: "Region,City" (example: "Riyadh,Riyadh")
    location = models.CharField(max_length=255, null=True, blank=True)

    deadline = models.DateField(null=True, blank=True)
    source_link = models.CharField(max_length=800, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=OpportunityStatus.choices,
        default=OpportunityStatus.OPEN,
    )

    avg_rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    major = models.CharField(max_length=150, null=True, blank=True)

    category = models.ForeignKey(
        OppCategory,
        on_delete=models.PROTECT,
        related_name="opportunities",
        default=get_default_category,
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def get_region_city(self):
        """Returns (region, city) parsed from `location` stored as 'Region,City'."""
        if not self.location:
            return (None, None)
        parts = [p.strip() for p in self.location.split(",", 1)]
        if len(parts) == 1:
            return (parts[0] or None, None)
        return (parts[0] or None, parts[1] or None)

    @property
    def region(self):
        return self.get_region_city()[0]

    @property
    def city(self):
        return self.get_region_city()[1]

    def __str__(self):
        return self.title


# Version history for Opportunity descriptions/content

class OpportunityVersion(models.Model):
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="versions",
    )

    fetched_at = models.DateTimeField(default=timezone.now)

    # Snapshot metadata (optional)
    source_link = models.CharField(max_length=800, null=True, blank=True)
    http_status = models.IntegerField(null=True, blank=True)

    # Snapshot content (optional)
    description_html = models.TextField(null=True, blank=True)
    description_text = models.TextField(null=True, blank=True)

    # Hash of description_text to detect changes
    content_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    # Whether this snapshot differs from the previous known state
    changed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.opportunity.title} @ {self.fetched_at:%Y-%m-%d %H:%M}"


# -----------------------------
# Student interactions
# -----------------------------
class Bookmark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="bookmarks")
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="bookmarked_by")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "opportunity"], name="uq_bookmark_student_opportunity")
        ]


class Rating(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="ratings")
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="ratings")

    learning_value = models.IntegerField(null=True, blank=True)
    work_env = models.IntegerField(null=True, blank=True)
    mentorship = models.IntegerField(null=True, blank=True)
    outcome = models.IntegerField(null=True, blank=True)

    overall = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "opportunity"], name="uq_rating_student_opportunity")
        ]


class Report(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="reports")
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="reports")

    report_type = models.CharField(max_length=30, choices=ReportType.choices)

    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
    )

    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)


# -----------------------------
# Submissions (student/admin/AI)
# -----------------------------
class Submission(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="submissions")

    submitted_at = models.DateTimeField(default=timezone.now)

    submitted_by_type = models.CharField(
        max_length=20,
        choices=SubmitterType.choices,
        null=True,
        blank=True,
        help_text="Auto-set based on submitted_by_student/submitted_by_admin",
    )

    # Keep your original schema idea (generic id), but also add optional FKs for clean Django usage
    submitted_by_student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions",
    )
    submitted_by_admin = models.ForeignKey(
        Admin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions",
    )

    def clean(self):
        """Ensure exactly one submitter FK is set (student OR admin)."""
        from django.core.exceptions import ValidationError

        student_set = self.submitted_by_student_id is not None
        admin_set = self.submitted_by_admin_id is not None

        if student_set and admin_set:
            raise ValidationError("Submission cannot be submitted by both student and admin.")
        if not student_set and not admin_set:
            raise ValidationError("Submission must have a submitter (student or admin).")

    def save(self, *args, **kwargs):
        # Auto-derive submitted_by_type from the FK that is set.
        if self.submitted_by_student_id is not None and self.submitted_by_admin_id is None:
            self.submitted_by_type = SubmitterType.STUDENT
        elif self.submitted_by_admin_id is not None and self.submitted_by_student_id is None:
            self.submitted_by_type = SubmitterType.ADMIN
        super().save(*args, **kwargs)

    link = models.CharField(max_length=800, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.PENDING,
    )

    decision_at = models.DateTimeField(null=True, blank=True)


class SubValidation(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="validations")

    admin = models.ForeignKey(
        Admin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validations",
    )

    validated_at = models.DateTimeField(default=timezone.now)
    note = models.TextField(null=True, blank=True)

    result = models.CharField(
        max_length=20,
        choices=ValidationResult.choices,
        default=ValidationResult.PENDING,
    )


# -----------------------------
# AI components
# -----------------------------
class AIDiscovery(models.Model):
    query = models.TextField(null=True, blank=True)
    fetch_url = models.TextField(null=True, blank=True)
    fetched_at = models.DateTimeField(null=True, blank=True)

    http_status = models.IntegerField(null=True, blank=True)

    parsed_status = models.CharField(
        max_length=30,
        choices=ParsedState.choices,
        null=True,
        blank=True,
    )

    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    evidence = models.TextField(null=True, blank=True)
    is_relevant = models.BooleanField(null=True, blank=True)

    created_submission = models.ForeignKey(
        Submission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_discoveries",
    )


class OpportunityObserverAI(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="ai_checks")

    fetch_url = models.TextField()
    checked_at = models.DateTimeField(default=timezone.now)

    http_status = models.IntegerField(null=True, blank=True)

    parsed_status = models.CharField(max_length=20, choices=ObsParsedStatus.choices)

    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    evidence = models.TextField(null=True, blank=True)

    change_detected = models.BooleanField(default=False)

    admin = models.ForeignKey(
        Admin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_reviews",
    )

    action_taken = models.CharField(max_length=50, null=True, blank=True)
    action_at = models.DateTimeField(null=True, blank=True)


# -----------------------------
# Leaderboard
# -----------------------------
class Leaderboard(models.Model):
    generated_at = models.DateTimeField(default=timezone.now)


class LeaderboardEntry(models.Model):
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name="entries")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="leaderboard_entries")

    rank = models.IntegerField()
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["leaderboard", "student"], name="uq_leaderboard_student"),
            models.UniqueConstraint(fields=["leaderboard", "rank"], name="uq_leaderboard_rank"),
        ]
