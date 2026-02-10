from .models import ThongBao

def thong_bao_chung(request):
    """
    Hàm này giúp 'Cái chuông' hiển thị được ở tất cả các trang (Base.html)
    """
    if request.user.is_authenticated:
        # Lấy tối đa 10 thông báo mới nhất
        thong_baos = ThongBao.objects.filter(nguoi_nhan=request.user).order_by('-ngay_tao')[:10]
        # Đếm số lượng chưa đọc
        so_chua_xem = ThongBao.objects.filter(nguoi_nhan=request.user, da_xem=False).count()
        return {
            'chung_thong_bao_list': thong_baos,
            'chung_so_thong_bao': so_chua_xem
        }
    return {}