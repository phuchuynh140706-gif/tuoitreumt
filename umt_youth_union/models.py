from django.db import models
from django.contrib.auth.models import User

# --- 1. MODEL CHI ĐOÀN ---
class ChiDoan(models.Model):
    ten_chi_doan = models.CharField(max_length=50, unique=True, verbose_name="Tên Chi Đoàn") 
    khoa = models.CharField(max_length=100, verbose_name="Khoa/Viện") 
    
    def __str__(self):
        return f"{self.ten_chi_doan} - {self.khoa}"
    
    class Meta:
        verbose_name_plural = "0. Danh sách Chi Đoàn"

# --- 2. MODEL SINH VIÊN ---
class SinhVien(models.Model):
    # Thêm db_index=True vào đây để tìm MSSV cực nhanh
    ma_sinh_vien = models.CharField(max_length=20, unique=True, db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Ảnh đại diện")
    
    # Thông tin cơ bản
    ma_sinh_vien = models.CharField(max_length=15, unique=True, verbose_name="MSSV")
    ho_ten = models.CharField(max_length=100, verbose_name="Họ và Tên")
    ngay_sinh = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    quoc_tich = models.CharField(max_length=50, default="Việt Nam", verbose_name="Quốc tịch")
    
    # Liên hệ
    email_sv = models.EmailField(max_length=100, verbose_name="Email Sinh viên")
    so_dien_thoai = models.CharField(max_length=15, null=True, blank=True, verbose_name="Số điện thoại")
    dia_chi_thuong_tru = models.TextField(null=True, blank=True, verbose_name="Nơi thường trú")
    dia_chi_tam_tru = models.TextField(null=True, blank=True, verbose_name="Nơi tạm trú")

    # Thông tin học tập
    truong = models.CharField(max_length=100, default="Đại học Quản lý và Công nghệ TP.HCM (UMT)", verbose_name="Trường")
    khoa_hoc = models.CharField(max_length=20, null=True, blank=True, verbose_name="Khóa học")
    chi_doan_gan_ket = models.ForeignKey(ChiDoan, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Chi Đoàn")
    
    # CHỨC VỤ - PHÂN QUYỀN DUYỆT
    CHUC_VU_CHOICES = (
        ('DOAN_VIEN', 'Đoàn viên (Nộp hồ sơ)'),
        ('UY_VIEN', 'Ủy viên (Duyệt Minh chứng)'),
        ('BI_THU_KHOA', 'Bí thư Khoa (Duyệt cấp 1)'),
        ('BI_THU_TRUONG', 'Bí thư Trường (Duyệt cuối)'),
    )
    chuc_vu = models.CharField(max_length=20, choices=CHUC_VU_CHOICES, default='DOAN_VIEN', verbose_name="Chức vụ Đoàn")

    def __str__(self):
        return f"{self.ho_ten} ({self.ma_sinh_vien})"

# --- 3. MODEL HỒ SƠ XÉT DUYỆT (NÂNG CẤP) ---
class HoSoXetDuyet(models.Model):
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE)
    nam_hoc = models.CharField(max_length=9, verbose_name="Năm học")
    
    LOAI_DANH_HIEU = (
        ('SV5T', 'Sinh viên 5 Tốt'),
        ('TNTT', 'Thanh niên Tiên tiến làm theo lời Bác'),
        ('CBTB', 'Cán bộ Đoàn Tiêu biểu'),
        ('KHAC', 'Thành tích khác'),
    )
    loai_danh_hieu = models.CharField(max_length=10, choices=LOAI_DANH_HIEU, default='SV5T', verbose_name="Loại danh hiệu")
    
    mo_ta_thanh_tich = models.TextField(verbose_name="Mô tả thành tích")
    
    # Nội dung bài viết vinh danh (sẽ được Ban truyền thông chỉnh sửa ở bước cuối)
    noi_dung_vinh_danh = models.TextField(null=True, blank=True, verbose_name="Bài viết Vinh danh")

    # QUY TRÌNH DUYỆT 3 BƯỚC
    TRANG_THAI_CHOICES = (
        ('CHO_MINH_CHUNG', 'Chờ Ủy viên duyệt MC'),
        ('CHO_KHOA', 'Chờ Khoa duyệt'),
        ('CHO_TRUONG', 'Chờ Trường duyệt'),
        ('DAT', 'Đã Duyệt (Vinh danh)'),
        ('TU_CHOI', 'Đã từ chối'),
    )
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='CHO_MINH_CHUNG')
    
    ngay_nop = models.DateField(auto_now_add=True)
    ly_do_tu_choi = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_loai_danh_hieu_display()} - {self.sinh_vien.ho_ten}"

# --- 4. MODEL MINH CHỨNG (CÓ CHECK HỢP LỆ) ---
class MinhChung(models.Model):
    ho_so = models.ForeignKey(HoSoXetDuyet, related_name='minh_chung_list', on_delete=models.CASCADE)
    hinh_anh = models.ImageField(upload_to='minh_chung/', verbose_name="Ảnh minh chứng")
    
    # Ủy viên sẽ tick vào đây nếu ảnh đúng
    is_valid = models.BooleanField(default=False, verbose_name="Hợp lệ")

    def __str__(self):
        return f"Minh chứng hồ sơ {self.ho_so.id}"

# --- 5. CÁC MODEL KHÁC ---
class VinhDanhCaNhan(models.Model):
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE)
    tieu_de = models.CharField(max_length=200)
    danh_hieu = models.CharField(max_length=50)
    hinh_anh_vinh_danh = models.ImageField(upload_to='vinh_danh/', null=True, blank=True)
    noi_dung_bai_viet = models.TextField()
    nam_dat = models.IntegerField()
    ngay_dang = models.DateField(auto_now_add=True)

class QuyDinhDieuLe(models.Model):
    ten_van_ban = models.CharField(max_length=255)
    loai_danh_hieu = models.CharField(max_length=100) 
    mo_ta = models.TextField(null=True, blank=True)
    file_pdf = models.FileField(upload_to='quyet_dinh/', null=True, blank=True) 
    ngay_ban_hanh = models.DateField()  
    # ... (Các model cũ giữ nguyên) ...

# --- 7. HỆ THỐNG THÔNG BÁO (NOTIFICATION) ---
class ThongBao(models.Model):
    nguoi_nhan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thong_bao')
    tieu_de = models.CharField(max_length=255)
    noi_dung = models.TextField()
    link_lien_ket = models.CharField(max_length=200, null=True, blank=True) # Bấm vào thông báo sẽ đi đến đâu
    da_xem = models.BooleanField(default=False)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tieu_de} - {self.nguoi_nhan.username}"
    # --- THÊM VÀO CUỐI FILE models.py ---

# Model lưu trữ thông báo (Cái chuông)
class ThongBao(models.Model):
    nguoi_nhan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thong_bao')
    tieu_de = models.CharField(max_length=255)
    noi_dung = models.TextField()
    link_lien_ket = models.CharField(max_length=200, null=True, blank=True) # Link khi bấm vào thông báo
    da_xem = models.BooleanField(default=False)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tieu_de} - {self.nguoi_nhan.username}"