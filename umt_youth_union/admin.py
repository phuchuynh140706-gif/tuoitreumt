from django.contrib import admin
from .models import SinhVien, HoSoXetDuyet, MinhChung, VinhDanhCaNhan, QuyDinhDieuLe, ChiDoan

# --- Cấu hình hiển thị danh sách Minh Chứng trong trang Hồ sơ ---
class MinhChungInline(admin.TabularInline):
    model = MinhChung
    extra = 1

class HoSoXetDuyetAdmin(admin.ModelAdmin):
    inlines = [MinhChungInline] # Cho phép xem ảnh minh chứng ngay trong hồ sơ
    list_display = ('sinh_vien', 'loai_danh_hieu', 'nam_hoc', 'trang_thai')
    list_filter = ('loai_danh_hieu', 'trang_thai', 'nam_hoc')

# --- Đăng ký các Model ---
admin.site.register(SinhVien)
admin.site.register(HoSoXetDuyet, HoSoXetDuyetAdmin) # Đăng ký kèm cấu hình Inline
admin.site.register(VinhDanhCaNhan)
admin.site.register(QuyDinhDieuLe)
admin.site.register(ChiDoan)

# Tùy chỉnh tiêu đề trang Admin
admin.site.site_header = "HỆ THỐNG QUẢN TRỊ ĐOÀN VỤ"
admin.site.site_title = "UMT Youth Union Admin"