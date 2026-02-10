from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import SinhVien

# --- FORM ĐĂNG KÝ TÀI KHOẢN ---
class DangKyForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Sinh viên (@st.umt.edu.vn)")
    last_name = forms.CharField(required=True, label="Họ và tên đệm")
    first_name = forms.CharField(required=True, label="Tên")

    class Meta:
        model = User
        fields = ('username', 'email', 'last_name', 'first_name')
        labels = {
            'username': 'Mã số sinh viên (MSSV)',
        }
        help_texts = {
            'username': '',
        }

# --- FORM HỒ SƠ CÁ NHÂN ---
class SinhVienProfileForm(forms.ModelForm):
    # Các trường hiển thị nhưng không cho sửa (readonly)
    ho_ten = forms.CharField(required=False, label="Họ và Tên", widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    ma_sinh_vien = forms.CharField(required=False, label="MSSV", widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    email_sv = forms.EmailField(required=False, label="Email Sinh viên", widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    
    class Meta:
        model = SinhVien
        # Loại bỏ các trường không cần user nhập
        exclude = ('user', 'chuc_vu', 'avatar') 
        
        # Giao diện đẹp cho các ô nhập liệu
        widgets = {
            'ngay_sinh': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dia_chi_thuong_tru': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'dia_chi_tam_tru': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'chi_doan_gan_ket': forms.Select(attrs={'class': 'form-control'}),
            'quoc_tich': forms.TextInput(attrs={'class': 'form-control'}),
            'so_dien_thoai': forms.TextInput(attrs={'class': 'form-control'}),
            'truong': forms.TextInput(attrs={'class': 'form-control'}),
            'khoa_hoc': forms.TextInput(attrs={'class': 'form-control'}),
            # Lưu ý: Đã xóa 'khoa_vien' vì trong model không có trường này
        }