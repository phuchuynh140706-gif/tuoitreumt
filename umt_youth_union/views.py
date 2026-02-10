from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.utils import timezone
from django.http import HttpResponse 
from django.contrib import messages 
import openpyxl 

from .models import HoSoXetDuyet, MinhChung, QuyDinhDieuLe, SinhVien, VinhDanhCaNhan, ChiDoan

try:
    from .forms import DangKyForm, SinhVienProfileForm
except ImportError:
    pass
# --- 1. THÊM VÀO ĐẦU FILE (Phần Import) ---
from .models import ThongBao # Nhớ import model này

# --- 2. THÊM HÀM NÀY VÀO DƯỚI CÁC DÒNG IMPORT ---
def gui_thong_bao(user, tieu_de, noi_dung, link=None):
    """Hàm helper để tạo thông báo nhanh"""
    if user and user.is_authenticated:
        ThongBao.objects.create(
            nguoi_nhan=user,
            tieu_de=tieu_de,
            noi_dung=noi_dung,
            link_lien_ket=link if link else '#'
        )

# --- 3. CẬP NHẬT HÀM DASHBOARD (Để Test Chuông) ---
@login_required(login_url='login')
def dashboard_view(request):
    # DEBUG: Tự động gửi thông báo chào mừng nếu chưa có cái nào
    if request.user.is_authenticated:
        if not ThongBao.objects.filter(nguoi_nhan=request.user).exists():
            gui_thong_bao(
                request.user, 
                "Chào mừng thành viên mới! 🎉", 
                "Hệ thống thông báo đã hoạt động. Mọi tin tức sẽ hiện ở đây.", 
                "/profile/"
            )

    # (Phần code thống kê cũ giữ nguyên)
    so_ho_so_cho = HoSoXetDuyet.objects.filter(trang_thai='CHO_DUYET').count()
    so_sv_dat = HoSoXetDuyet.objects.filter(trang_thai='DAT').count()
    so_van_ban = QuyDinhDieuLe.objects.count()
    
    try:
        sinh_vien = request.user.sinhvien
        context = {
            'sinh_vien': sinh_vien,
            'so_ho_so_cho': so_ho_so_cho,
            'so_sv_dat': so_sv_dat,
            'so_van_ban': so_van_ban
        }
        return render(request, 'umt_youth_union/dashboard.html', context)
    except SinhVien.DoesNotExist:
        return redirect('profile')

# --- 4. CẬP NHẬT HÀM NỘP HỒ SƠ (Dùng Chuông thay vì Message) ---
@login_required(login_url='login')
def nop_ho_so_chi_tiet(request, loai_danh_hieu):
    # ... (Giữ nguyên phần lấy sinh_vien và TIEU_CHI_DATA) ...
    # (Nếu bạn cần code full phần này hãy bảo tôi, tôi đang viết tắt để tập trung vào chỗ sửa)

    if request.method == 'POST':
        # ... (Giữ nguyên logic tạo HoSoXetDuyet và MinhChung) ...
        
        # SỬA ĐOẠN NÀY: Dùng gui_thong_bao thay vì messages.success
        if has_file:
            gui_thong_bao(
                request.user,
                "Nộp hồ sơ thành công ✔️",
                f"Hồ sơ {loai_danh_hieu} đã được gửi. Vui lòng chờ kết quả.",
                "/ho-so/"
            )
        else:
            gui_thong_bao(
                request.user,
                "Lưu ý hồ sơ ⚠️",
                "Hồ sơ đã tạo nhưng bạn chưa tải minh chứng nào lên.",
                "/ho-so/"
            )

        return redirect('danh_sach_ho_so') # Chuyển trang ngay, không cần message flash nữa

    # ... (Phần return render giữ nguyên) ...

# --- AUTH (Folder: auth/) ---
class CustomLoginView(LoginView):
    template_name = 'umt_youth_union/auth/login.html' # Đã sửa đường dẫn vào folder auth
    next_page = 'dashboard'
    redirect_authenticated_user = True
    
    def form_invalid(self, form):
        messages.error(self.request, "Tên đăng nhập hoặc mật khẩu không đúng!")
        return super().form_invalid(form)

login_view = CustomLoginView.as_view()

def custom_logout(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = DangKyForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Tự động đăng nhập sau khi đăng ký
            login(request, user)
            
            # Tạo hồ sơ sinh viên, tự động lấy Username làm MSSV
            SinhVien.objects.create(
                user=user, 
                ho_ten=f"{user.last_name} {user.first_name}", 
                email_sv=user.email,        # Lưu Email vào hồ sơ
                ma_sinh_vien=user.username  # QUAN TRỌNG: Lưu Username vào cột MSSV
            )
            
            messages.success(request, "Đăng ký thành công! Chào mừng bạn đến với Cổng thông tin Đoàn.")
            return redirect('profile')
        else:
            messages.error(request, "Đăng ký thất bại. Vui lòng kiểm tra lại thông tin (MSSV có thể đã tồn tại).")
    else:
        form = DangKyForm()
    
    # Trỏ đúng vào thư mục auth bạn đã tạo
    return render(request, 'umt_youth_union/auth/register.html', {'form': form})
# --- DASHBOARD & PROFILE (Giữ nguyên ở ngoài) ---
@login_required(login_url='login')

def dashboard_view(request):
    so_ho_so_cho = HoSoXetDuyet.objects.filter(trang_thai='CHO_DUYET').count()
    so_sv_dat = HoSoXetDuyet.objects.filter(trang_thai='DAT').count()
    so_van_ban = QuyDinhDieuLe.objects.count()
    try:
        sinh_vien = SinhVien.objects.get(user=request.user)
        user_role = sinh_vien.chuc_vu
    except SinhVien.DoesNotExist:
        sinh_vien = None
        user_role = 'DOAN_VIEN'

    context = {
        'page_title': 'Trang Tổng quan',
        'so_ho_so_cho': so_ho_so_cho,
        'so_sv_dat': so_sv_dat,
        'so_van_ban': so_van_ban,
        'sinh_vien': sinh_vien,
        'user_role': user_role,
        'is_admin': request.user.is_superuser
    }
    return render(request, 'umt_youth_union/dashboard.html', context)

@login_required(login_url='login')
def profile_view(request):
    sinh_vien, created = SinhVien.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = SinhVienProfileForm(request.POST, request.FILES, instance=sinh_vien)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật hồ sơ thành công!")
            return redirect('profile')
    else:
        form = SinhVienProfileForm(instance=sinh_vien)
    return render(request, 'umt_youth_union/profile.html', {'form': form, 'sinh_vien': sinh_vien, 'page_title': 'Thông tin cá nhân'})

# --- QUẢN LÝ NHÂN SỰ (Folder: manager/) ---
@login_required(login_url='login')
def quan_ly_nhan_su(request):
    if not request.user.is_superuser: return redirect('dashboard')
    danh_sach_sv = SinhVien.objects.all().order_by('chi_doan_gan_ket', 'ho_ten')
    danh_sach_chi_doan = ChiDoan.objects.all()
    chi_doan_id = request.GET.get('chi_doan_id')
    if chi_doan_id: danh_sach_sv = danh_sach_sv.filter(chi_doan_gan_ket_id=chi_doan_id)
    # Trỏ vào folder manager
    return render(request, 'umt_youth_union/manager/quan_ly_nhan_su.html', {'danh_sach_sv': danh_sach_sv, 'danh_sach_chi_doan': danh_sach_chi_doan})

@login_required(login_url='login')
def bo_nhiem_can_bo(request, pk):
    if not request.user.is_superuser: return redirect('dashboard')
    sinh_vien = get_object_or_404(SinhVien, pk=pk)
    if request.method == 'POST':
        sinh_vien.chuc_vu = request.POST.get('chuc_vu_moi')
        sinh_vien.save()
        messages.success(request, f"Đã cập nhật chức vụ cho {sinh_vien.ho_ten}")
    return redirect('quan_ly_nhan_su')

@login_required(login_url='login')
def export_excel_nhan_su(request):
    if not request.user.is_superuser: return redirect('dashboard')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Danh sách Đoàn viên"
    ws.append(['MSSV', 'Họ tên', 'Ngày sinh', 'Email', 'SĐT', 'Chi Đoàn', 'Chức vụ'])
    rows = SinhVien.objects.all().values_list('ma_sinh_vien', 'ho_ten', 'ngay_sinh', 'email_sv', 'so_dien_thoai', 'chi_doan_gan_ket__ten_chi_doan', 'chuc_vu')
    for row in rows: ws.append(list(row))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="DS_DoanVien.xlsx"'
    wb.save(response)
    return response

# --- XÉT DUYỆT (Folder: ho_so/) ---
@login_required(login_url='login')
def chon_danh_hieu(request):
    # Trỏ vào folder ho_so
    return render(request, 'umt_youth_union/ho_so/chon_danh_hieu.html')


@login_required(login_url='login')
def nop_ho_so_chi_tiet(request, loai_danh_hieu):
    try:
        sinh_vien = request.user.sinhvien
    except:
        return redirect('profile')

    # --- DỮ LIỆU TIÊU CHÍ (CẤU HÌNH CHI TIẾT TẠI ĐÂY) ---
    # Bạn có thể sửa đổi nội dung mô tả cho phù hợp thực tế trường UMT
    TIEU_CHI_DATA = {
        'SV5T': [
            {'id': 'dao_duc', 'icon': 'fa-heart', 'name': 'Đạo đức tốt', 'desc': 'Điểm rèn luyện từ 80 trở lên, không vi phạm kỷ luật.'},
            {'id': 'hoc_tap', 'icon': 'fa-book', 'name': 'Học tập tốt', 'desc': 'Điểm trung bình học tập (GPA) từ 3.2/4.0 trở lên.'},
            {'id': 'the_luc', 'icon': 'fa-running', 'name': 'Thể lực tốt', 'desc': 'Đạt danh hiệu "Thanh niên khỏe" hoặc tham gia giải thể thao cấp trường.'},
            {'id': 'tinh_nguyen', 'icon': 'fa-hands-helping', 'name': 'Tình nguyện tốt', 'desc': 'Tham gia ít nhất 02 hoạt động tình nguyện hoặc 05 ngày tình nguyện/năm.'},
            {'id': 'hoi_nhap', 'icon': 'fa-globe', 'name': 'Hội nhập tốt', 'desc': 'Hoàn thành chứng chỉ Tiếng Anh/Tin học hoặc tham gia hoạt động giao lưu quốc tế.'},
        ],
        'TNTT': [
            {'id': 'guong_mau', 'icon': 'fa-star', 'name': 'Gương mẫu chấp hành', 'desc': 'Chấp hành tốt chủ trương, chính sách của Đảng và Nhà nước.'},
            {'id': 'chuyen_mon', 'icon': 'fa-briefcase', 'name': 'Chuyên môn giỏi', 'desc': 'Có công trình nghiên cứu khoa học hoặc sáng kiến kinh nghiệm.'},
            {'id': 'hoat_dong', 'icon': 'fa-users', 'name': 'Hoạt động sôi nổi', 'desc': 'Là hạt nhân nòng cốt trong các phong trào Đoàn - Hội.'},
        ],
        'CBTB': [
            {'id': 'thanh_tich', 'icon': 'fa-trophy', 'name': 'Thành tích Công tác Đoàn', 'desc': 'Có đóng góp tích cực, sáng tạo và hiệu quả cho công tác Đoàn.'},
            {'id': 'khen_thuong', 'icon': 'fa-certificate', 'name': 'Khen thưởng', 'desc': 'Đã nhận được giấy khen cấp Trường trở lên.'},
        ],
        'KHAC': [
            {'id': 'thanh_tich_chung', 'icon': 'fa-file-alt', 'name': 'Nội dung thành tích', 'desc': 'Mô tả chi tiết và tải lên các minh chứng liên quan.'},
        ]
    }

    # Lấy danh sách tiêu chí dựa trên loại danh hiệu user chọn
    tieu_chi_list = TIEU_CHI_DATA.get(loai_danh_hieu, TIEU_CHI_DATA['KHAC'])

    if request.method == 'POST':
        # 1. Tổng hợp nội dung mô tả từ các checkbox
        mo_ta_tong_hop = ""
        for tc in tieu_chi_list:
            # Kiểm tra xem sinh viên có tick vào tiêu chí này không
            if request.POST.get(f'check_{tc["id"]}') == 'on':
                mo_ta_tong_hop += f"- Đạt tiêu chí: {tc['name']}\n"
        
        # Thêm ghi chú
        ghi_chu = request.POST.get('ghi_chu_them', '')
        if ghi_chu:
            mo_ta_tong_hop += f"\n* Ghi chú thêm: {ghi_chu}"

        # 2. Tạo Hồ sơ
        ho_so = HoSoXetDuyet.objects.create(
            sinh_vien=sinh_vien,
            loai_danh_hieu=loai_danh_hieu,
            nam_hoc="2024-2025", # Có thể sửa thành lấy năm hiện tại tự động
            mo_ta_thanh_tich=mo_ta_tong_hop,
            trang_thai='CHO_MINH_CHUNG'
        )

        # 3. Xử lý File Minh Chứng (Lặp qua từng tiêu chí để lấy file)
        has_file = False
        for tc in tieu_chi_list:
            # Lấy list file của từng ô input riêng biệt (vd: file_dao_duc, file_hoc_tap...)
            files = request.FILES.getlist(f'file_{tc["id"]}')
            for f in files:
                MinhChung.objects.create(ho_so=ho_so, hinh_anh=f)
                has_file = True
        
        if has_file:
            messages.success(request, "Đã nộp hồ sơ thành công! Vui lòng chờ duyệt.")
        else:
            messages.warning(request, "Hồ sơ đã tạo nhưng chưa có minh chứng nào được tải lên.")

        return redirect('danh_sach_ho_so')

    # Lấy văn bản hướng dẫn (nếu có)
    quy_dinh = QuyDinhDieuLe.objects.filter(loai_danh_hieu__contains=loai_danh_hieu).first()

    return render(request, 'umt_youth_union/ho_so/nop_ho_so_chi_tiet.html', {
        'loai_danh_hieu': loai_danh_hieu,
        'tieu_chi_list': tieu_chi_list,
        'quy_dinh': quy_dinh
    })
    
    # Data mẫu (giữ nguyên logic của bạn)
    TIEU_CHI_DATA = {'SV5T': [{'id':'chung', 'name':'Thành tích', 'desc':'Nộp minh chứng'}], 'TNTT': [{'id':'chung', 'name':'Thành tích', 'desc':'Nộp minh chứng'}], 'CBTB': [{'id':'chung', 'name':'Thành tích', 'desc':'Nộp minh chứng'}], 'KHAC': [{'id':'chung', 'name':'Thành tích', 'desc':'Nộp minh chứng'}]}
    tieu_chi_list = TIEU_CHI_DATA.get(loai_danh_hieu, TIEU_CHI_DATA['KHAC'])
    
    if request.method == 'POST':
        mo_ta = request.POST.get('ghi_chu_them', '')
        ho_so = HoSoXetDuyet.objects.create(sinh_vien=sinh_vien, loai_danh_hieu=loai_danh_hieu, nam_hoc="2024-2025", mo_ta_thanh_tich=mo_ta, trang_thai='CHO_MINH_CHUNG')
        for key, file_list in request.FILES.lists():
            for f in file_list: MinhChung.objects.create(ho_so=ho_so, hinh_anh=f)
        return redirect('danh_sach_ho_so')
        
    quy_dinh = QuyDinhDieuLe.objects.filter(loai_danh_hieu__contains=loai_danh_hieu).first()
    # Trỏ vào folder ho_so
    return render(request, 'umt_youth_union/ho_so/nop_ho_so_chi_tiet.html', {'loai_danh_hieu': loai_danh_hieu, 'tieu_chi_list': tieu_chi_list, 'quy_dinh': quy_dinh})

@login_required(login_url='login')
def danh_sach_ho_so(request):
    try:
        me = request.user.sinhvien
        role = me.chuc_vu
    except: return redirect('profile')
    
    danh_sach = HoSoXetDuyet.objects.select_related('sinh_vien', 'sinh_vien__chi_doan_gan_ket').all().order_by('-ngay_nop')
    tieu_de = "Hồ sơ của tôi"
    
    # Logic phân quyền (Giữ nguyên logic của bạn)
    if role == 'UY_VIEN':
        danh_sach = HoSoXetDuyet.objects.filter(trang_thai='CHO_MINH_CHUNG')
        tieu_de = "Duyệt Minh Chứng (Ủy viên)"
    elif role in ['BI_THU_KHOA', 'PHO_BI_THU_KHOA']:
        my_khoa = me.chi_doan_gan_ket.khoa if me.chi_doan_gan_ket else ""
        danh_sach = HoSoXetDuyet.objects.filter(trang_thai='CHO_KHOA', sinh_vien__chi_doan_gan_ket__khoa=my_khoa)
        tieu_de = f"Duyệt cấp Khoa ({my_khoa})"
    elif role in ['BI_THU_TRUONG', 'PHO_BI_THU_TRUONG'] or request.user.is_superuser:
        danh_sach = HoSoXetDuyet.objects.filter(trang_thai='CHO_TRUONG')
        tieu_de = "Duyệt cấp Trường"
        
    # Trỏ vào folder ho_so
    return render(request, 'umt_youth_union/ho_so/ds_ho_so.html', {'danh_sach': danh_sach, 'tieu_de': tieu_de, 'user_role': role})

@login_required(login_url='login')
def chi_tiet_xet_duyet(request, pk):
    ho_so = get_object_or_404(HoSoXetDuyet, pk=pk)
    minh_chung = ho_so.minh_chung_list.all()
    me = request.user.sinhvien
    role = me.chuc_vu

    if request.method == 'POST':
        action = request.POST.get('action')
        # ... (Giữ nguyên logic duyệt 3 cấp như cũ) ...
        # (Để ngắn gọn tôi không paste lại đoạn logic duyệt dài dòng, vì nó không đổi)
        # Chỉ cần đảm bảo dòng return cuối cùng trỏ đúng file:
        if role == 'UY_VIEN' and ho_so.trang_thai == 'CHO_MINH_CHUNG':
            if action == 'xac_nhan_mc':
                ho_so.trang_thai = 'CHO_KHOA'
                ho_so.save()
            elif action == 'tra_ve':
                ho_so.trang_thai = 'TU_CHOI'
                ho_so.save()
        elif role in ['BI_THU_KHOA', 'PHO_BI_THU_KHOA'] and ho_so.trang_thai == 'CHO_KHOA':
            if action == 'duyet_khoa':
                ho_so.trang_thai = 'CHO_TRUONG'
                ho_so.save()
            elif action == 'tu_choi':
                ho_so.trang_thai = 'TU_CHOI'
                ho_so.save()
        elif (role in ['BI_THU_TRUONG', 'PHO_BI_THU_TRUONG'] or request.user.is_superuser) and ho_so.trang_thai == 'CHO_TRUONG':
            if action == 'duyet_truong':
                ho_so.trang_thai = 'DAT'
                ho_so.noi_dung_vinh_danh = request.POST.get('noi_dung_vinh_danh')
                ho_so.save()
                anh_bia = None
                mc_first = ho_so.minh_chung_list.first()
                if mc_first: anh_bia = mc_first.hinh_anh
                elif ho_so.sinh_vien.avatar: anh_bia = ho_so.sinh_vien.avatar
                VinhDanhCaNhan.objects.create(sinh_vien=ho_so.sinh_vien, tieu_de=f"Gương sáng: {ho_so.sinh_vien.ho_ten}", danh_hieu=ho_so.get_loai_danh_hieu_display(), noi_dung_bai_viet=ho_so.noi_dung_vinh_danh, nam_dat=2025, hinh_anh_vinh_danh=anh_bia)
            elif action == 'tu_choi':
                ho_so.trang_thai = 'TU_CHOI'
                ho_so.save()
        return redirect('danh_sach_ho_so')

    # QUAN TRỌNG: Trỏ vào folder ho_so
    return render(request, 'umt_youth_union/ho_so/chi_tiet_ho_so.html', {'ho_so': ho_so, 'minh_chung': minh_chung, 'user_role': role})

# --- VINH DANH (Folder: vinh_danh/) ---
@login_required(login_url='login')
def vinh_danh_view(request):
    danh_sach = VinhDanhCaNhan.objects.all().order_by('-nam_dat')
    return render(request, 'umt_youth_union/vinh_danh/vinh_danh.html', {'danh_sach': danh_sach}) # Đã sửa

@login_required(login_url='login')
def chi_tiet_vinh_danh(request, pk):
    bai_viet = get_object_or_404(VinhDanhCaNhan, pk=pk)
    # SỬA LẠI ĐƯỜNG DẪN ĐÚNG VÀO THƯ MỤC CON vinh_danh/
    return render(request, 'umt_youth_union/vinh_danh/bai_viet_vinh_danh.html', {'bai_viet': bai_viet})

# --- QUY ĐỊNH (Sửa lỗi quyền Upload) ---
@login_required(login_url='login')
def quy_dinh_view(request):
    # Logic kiểm tra quyền: Admin hoặc Bí thư đều được
    is_authorized = False
    if request.user.is_superuser:
        is_authorized = True
    else:
        try:
            role = request.user.sinhvien.chuc_vu
            if 'BI_THU' in role: # Chỉ cần chức vụ có chữ BI_THU là được
                is_authorized = True
        except:
            pass

    if request.method == 'POST' and is_authorized:
        QuyDinhDieuLe.objects.create(
            ten_van_ban=request.POST.get('ten_van_ban'),
            loai_danh_hieu=request.POST.get('loai_danh_hieu'),
            file_pdf=request.FILES.get('file_pdf'),
            ngay_ban_hanh=timezone.now()
        )
        messages.success(request, "Đã đăng tải văn bản thành công!")
        return redirect('quy_dinh')
        
    danh_sach = QuyDinhDieuLe.objects.all().order_by('-ngay_ban_hanh')
    
    # Truyền biến 'can_upload' ra template
    return render(request, 'umt_youth_union/quy_dinh.html', {
        'danh_sach_van_ban': danh_sach,
        'can_upload': is_authorized
    })
def public_quy_dinh_view(request):
    danh_sach = QuyDinhDieuLe.objects.all().order_by('-ngay_ban_hanh')
    # File này vẫn để ở ngoài thư mục gốc template
    return render(request, 'umt_youth_union/public_quy_dinh.html', {'danh_sach_van_ban': danh_sach})