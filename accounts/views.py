from django.core.paginator import Paginator
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.db import models
from django.db.models import Q
from .forms import SignupForm, LoginForm
from .models import Student, Opportunity, OppCategory
from urllib.parse import urlencode

def hello(request):
    # Show homepage for everyone (logged in or not)
    return render(request, "pages/homepage.html")

def register_view(request):
    signup_form = SignupForm()
    login_form = LoginForm()
    active_tab = "signup"

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "signup":
            active_tab = "signup"
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                # Ensure the Student profile exists (so we can show name/major in the navbar)
                Student.objects.get_or_create(
                    user=user,
                    defaults={
                        "full_name": getattr(user, "username", ""),
                        "major": "",
                    },
                )
                auth_login(request, user)
                return redirect("opportunities")  # change to your page name
            else:
                messages.error(request, "Please fix the signup errors.")

        elif form_type == "login":
            active_tab = "login"
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = login_form.cleaned_data["user"]
                auth_login(request, user)
                return redirect("opportunities")
            else:
                messages.error(request, "Please fix the login errors.")

    return render(
        request,
        "pages/register.html",
        {
            "signup_form": signup_form,
            "login_form": login_form,
            "active_tab": active_tab,
        },
    )


def about_us(request):
    return render(request, 'pages/about-us.html')
def contact_us(request):
    return render(request, "pages/contact-us.html")

def terms_of_service(request):
    return render(request, "pages/terms-of-service.html")

def bookmarks(request):
    return render(request, "pages/bookmarks.html")

def profile(request):
    return render(request, "pages/profile.html")

def leaderboard(request):
    return render(request, "pages/leaderboard.html")
def privacy_policy(request):
    return render(request, "pages/privacy-policy.html")

from django.contrib.auth.decorators import login_required


@login_required
def opportunities(request):
    student_profile = Student.objects.filter(user=request.user).first()

    # -----------------------------
    # Base queryset (apply filters)
    # -----------------------------
    qs = Opportunity.objects.all().order_by("-created_at", "-id")

    # -----------------------------
    # Category filter (Major) - MULTI SELECT + COUNTS
    # -----------------------------
    raw_category_ids = request.GET.getlist("category")
    selected_category_ids: list[int] = []
    for x in raw_category_ids:
        try:
            selected_category_ids.append(int(x))
        except (TypeError, ValueError):
            continue
    selected_category_ids = sorted(set(selected_category_ids))

    categories = OppCategory.objects.all().order_by("name")

    # Counts should reflect current filters EXCEPT major itself
    qs_for_major_counts = qs

    # Apply selected majors to list queryset
    if selected_category_ids:
        qs = qs.filter(category_id__in=selected_category_ids)

    # Major counts
    major_counts = dict(
        qs_for_major_counts.values("category_id")
        .annotate(c=models.Count("id"))
        .values_list("category_id", "c")
    )

    def build_toggle_major_url(cat_id: int) -> str:
        params = request.GET.copy()
        params.pop("page", None)

        current = set(selected_category_ids)
        if cat_id in current:
            current.remove(cat_id)
        else:
            current.add(cat_id)

        params.setlist("category", [str(i) for i in sorted(current)])
        qs_str = params.urlencode()
        return f"{reverse('opportunities')}{('?' + qs_str) if qs_str else ''}"

    def build_clear_majors_url() -> str:
        params = request.GET.copy()
        params.pop("page", None)
        params.pop("category", None)
        qs_str = params.urlencode()
        return f"{reverse('opportunities')}{('?' + qs_str) if qs_str else ''}"

    categories_ui = []
    for c in categories:
        categories_ui.append({
            "id": c.id,
            "name": c.name,
            "count": int(major_counts.get(c.id, 0) or 0),
            "selected": c.id in selected_category_ids,
            "toggle_url": build_toggle_major_url(c.id),
        })

    # For button label (only when exactly 1 selected)
    selected_category = None
    if len(selected_category_ids) == 1:
        selected_category = OppCategory.objects.filter(id=selected_category_ids[0]).first()

    # Backward-compat: some templates still expect `category_id` (single value).
    # Keep it only when exactly 1 major is selected.
    category_id = str(selected_category_ids[0]) if len(selected_category_ids) == 1 else None

    # Nice-to-have for UI labels
    selected_category_names = [c["name"] for c in categories_ui if c.get("selected")]

    # -----------------------------
    # Location filter (Region/City)
    # -----------------------------
    REGIONS_AND_CITIES = {
        "Riyadh": ["Riyadh", "Al Kharj", "Al Majma’ah", "Al Quway’iyah"],
        "Makkah": ["Jeddah", "Makkah", "Taif", "Rabigh"],
        "Eastern Province": ["Dammam", "Khobar", "Dhahran", "Jubail"],
        "Madinah": ["Madinah", "Yanbu", "Al Ula", "Badr"],
        "Qassim": ["Buraidah", "Unaizah", "Al Rass", "Bukayriyah"],
        "Asir": ["Abha", "Khamis Mushait", "Mahayel", "Bisha"],
        "Tabuk": ["Tabuk", "Duba", "Umluj", "Tayma"],
        "Hail": ["Hail", "Baqaa", "Ash Shinan", "Ghazalah"],
        "Jazan": ["Jazan", "Sabya", "Abu Arish", "Al Ardah"],
        "Najran": ["Najran", "Sharurah", "Hubuna"],
        "Al Bahah": ["Al Bahah", "Baljurashi", "Al Mandaq"],
        "Al Jawf": ["Sakaka", "Dumat Al Jandal", "Qurayyat"],
        "Northern Borders": ["Arar", "Rafha", "Turaif"],
    }

    selected_region = (request.GET.get("region") or "").strip() or None
    selected_city = (request.GET.get("city") or "").strip() or None

    # Validate selections
    if selected_region and selected_region not in REGIONS_AND_CITIES:
        selected_region = None
        selected_city = None
    if selected_region and selected_city and selected_city not in REGIONS_AND_CITIES.get(selected_region, []):
        selected_city = None

    # Counts should reflect current filters EXCEPT location (so users can see what exists before clicking)
    base_for_counts = qs

    # Apply location filters to the actual list queryset
    if selected_region and selected_city:
        # Handle both "Region,City" and "Region, City"
        qs = qs.filter(
            Q(location__iexact=f"{selected_region},{selected_city}")
            | Q(location__iexact=f"{selected_region}, {selected_city}")
        )
    elif selected_region:
        # Region only
        qs = qs.filter(Q(location__startswith=f"{selected_region},") | Q(location__startswith=f"{selected_region}, "))

    # Build region -> city -> count from the DB (best effort by parsing Opportunity.location)
    counts: dict[str, dict[str, int]] = {r: {c: 0 for c in cities} for r, cities in REGIONS_AND_CITIES.items()}
    for loc in base_for_counts.values_list("location", flat=True):
        if not loc:
            continue
        parts = [p.strip() for p in str(loc).split(",", 1)]
        if len(parts) != 2:
            continue
        r, c = parts[0], parts[1]
        if r in counts and c in counts[r]:
            counts[r][c] += 1

    # Prepare menu data for the template
    location_menu = {
        r: [{"city": c, "count": counts[r][c]} for c in REGIONS_AND_CITIES[r]]
        for r in REGIONS_AND_CITIES
    }

    # -----------------------------
    # Pagination
    # -----------------------------
    paginator = Paginator(qs, 5)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)

    # Ellipsis page range
    current = page_obj.number
    last = paginator.num_pages
    window = 2

    pages = []
    for p in range(1, last + 1):
        if p == 1 or p == last or (current - window <= p <= current + window):
            pages.append(p)

    page_range = []
    prev = None
    for p in pages:
        if prev is not None and p - prev > 1:
            page_range.append(None)
        page_range.append(p)
        prev = p

    # -----------------------------
    # Keep filters in pagination links
    # -----------------------------
    # Keep everything except page
    params = request.GET.copy()
    params.pop("page", None)
    qs_str = params.urlencode()
    extra_qs = ("&" + qs_str) if qs_str else ""

    # URL that clears ALL filters
    clear_all_url = reverse("opportunities")

    # URL that clears ONLY majors (keeps other filters like location)
    clear_majors_url = build_clear_majors_url()

    # URL that clears ONLY location (keeps other filters like majors)
    params_clear_loc = request.GET.copy()
    params_clear_loc.pop("page", None)
    params_clear_loc.pop("region", None)
    params_clear_loc.pop("city", None)
    clear_loc_qs = params_clear_loc.urlencode()
    clear_location_url = f"{reverse('opportunities')}{('?' + clear_loc_qs) if clear_loc_qs else ''}"

    # Querystring containing ONLY selected majors (used by JS when building location links)
    majors_params = [("category", str(cid)) for cid in selected_category_ids]
    majors_qs = urlencode(majors_params)

    return render(
        request,
        "pages/opportunities.html",
        {
            "student_profile": student_profile,
            "opportunities": page_obj.object_list,
            "page_obj": page_obj,
            "page_range": page_range,

            # Majors (multi-select)
            "categories": categories,  # raw queryset (optional, if template still uses it)
            "categories_ui": categories_ui,
            "selected_category": selected_category,
            "selected_category_ids": selected_category_ids,
            "category_id": category_id,
            "selected_category_names": selected_category_names,
            "selected_category_count": len(selected_category_ids),
            "clear_majors_url": clear_majors_url,
            "clear_location_url": clear_location_url,
            "majors_qs": majors_qs,

            # Location menu
            "location_menu": location_menu,
            "selected_region": selected_region,
            "selected_city": selected_city,

            # Pagination querystring
            "extra_qs": extra_qs,

            # Clear everything
            "clear_all_url": clear_all_url,
        },
    )
