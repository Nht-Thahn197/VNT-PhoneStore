from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Q
from django.shortcuts import render, redirect

from .forms import RegisterForm


def _auth_gate_message(next_url: str | None) -> str | None:
    if not next_url:
        return None
    lowered = next_url.lower()
    if "cart" in lowered or "checkout" in lowered:
        return "Bạn chưa đăng nhập. Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng hoặc thanh toán."
    return None


def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")
    error = None
    identifier = ""

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")
        user = None

        if identifier:
            lookup_phone = identifier
            if "@" not in identifier:
                normalized = "".join(ch for ch in identifier if ch.isdigit() or ch == "+")
                if normalized:
                    lookup_phone = normalized
            user_model = get_user_model()
            candidate = user_model.objects.filter(
                Q(email__iexact=identifier) | Q(phone=lookup_phone) | Q(username__iexact=identifier)
            ).first()
            if candidate:
                user = authenticate(request, username=candidate.username, password=password)

        if user is None and identifier:
            user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url or "home")
        error = "Tên đăng nhập hoặc mật khẩu không đúng."

    context = {
        "next": next_url,
        "error": error,
        "identifier": identifier,
        "gate_message": _auth_gate_message(next_url),
    }
    return render(request, "accounts/login.html", context)


def register(request):
    next_url = request.GET.get("next") or request.POST.get("next")
    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect(next_url or "home")

    context = {
        "form": form,
        "next": next_url,
        "gate_message": _auth_gate_message(next_url),
    }
    return render(request, "accounts/register.html", context)


def logout_view(request):
    logout(request)
    return redirect("home")
