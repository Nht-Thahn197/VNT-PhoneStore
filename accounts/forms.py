from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, label="Họ và tên")
    birth_date = forms.DateField(
        label="Ngày sinh",
        widget=forms.DateInput(attrs={"type": "date", "placeholder": "dd/mm/yyyy"}),
    )
    phone = forms.CharField(
        max_length=20,
        label="Số điện thoại",
        widget=forms.TextInput(attrs={"type": "tel"}),
    )
    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = get_user_model()
        fields = ("username", "full_name", "birth_date", "phone", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = False
        if "username" in self.fields:
            self.fields["username"].required = False
            self.fields["username"].widget = forms.HiddenInput()

        self.fields["email"].label = "Email"
        self.fields["password1"].label = "Mật khẩu"
        self.fields["password2"].label = "Nhập lại mật khẩu"

        self.fields["full_name"].widget.attrs.update({"placeholder": "Nhập họ và tên"})
        self.fields["birth_date"].widget.attrs.update({"placeholder": "dd/mm/yyyy"})
        self.fields["phone"].widget.attrs.update(
            {"placeholder": "Nhập số điện thoại", "autocomplete": "tel"}
        )
        self.fields["email"].widget.attrs.update(
            {"placeholder": "email@example.com", "autocomplete": "email"}
        )
        self.fields["password1"].widget.attrs.update(
            {"placeholder": "Tối thiểu 8 ký tự", "autocomplete": "new-password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Nhập lại mật khẩu", "autocomplete": "new-password"}
        )

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "")

    def clean_phone(self):
        phone_raw = (self.cleaned_data.get("phone") or "").strip()
        normalized = "".join(ch for ch in phone_raw if ch.isdigit() or ch == "+")
        phone = normalized or phone_raw
        if not phone:
            raise ValidationError("Vui lòng nhập số điện thoại.")
        user_model = get_user_model()
        if user_model.objects.filter(phone=phone).exists() or user_model.objects.filter(username=phone).exists():
            raise ValidationError("Số điện thoại đã được sử dụng.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        if phone:
            cleaned_data["username"] = phone
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = (self.cleaned_data.get("full_name") or "").strip()
        phone = self.cleaned_data.get("phone")
        email = self.cleaned_data.get("email") or ""
        birth_date = self.cleaned_data.get("birth_date")

        if full_name:
            parts = full_name.split()
            if len(parts) > 1:
                user.first_name = " ".join(parts[:-1])
                user.last_name = parts[-1]
            else:
                user.first_name = full_name

        user.username = phone
        user.phone = phone
        user.email = email
        user.birth_date = birth_date

        if commit:
            user.save()
        return user
