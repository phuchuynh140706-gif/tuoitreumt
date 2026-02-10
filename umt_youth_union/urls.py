from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Password Reset (Đường dẫn mới)
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="umt_youth_union/auth/password_reset.html"), name="password_reset"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="umt_youth_union/auth/password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="umt_youth_union/auth/password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="umt_youth_union/auth/password_reset_done.html"), name="password_reset_complete"),

    # Main
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # Quản lý & Bổ nhiệm
    path('quan-ly-nhan-su/', views.quan_ly_nhan_su, name='quan_ly_nhan_su'),
    path('bo-nhiem/<int:pk>/', views.bo_nhiem_can_bo, name='bo_nhiem_can_bo'),
    path('export-excel/', views.export_excel_nhan_su, name='export_excel_nhan_su'),

    # Nghiệp vụ Hồ sơ
    path('chon-danh-hieu/', views.chon_danh_hieu, name='chon_danh_hieu'),
    path('nop-ho-so/<str:loai_danh_hieu>/', views.nop_ho_so_chi_tiet, name='nop_ho_so_chi_tiet'),
    path('danh-sach-ho-so/', views.danh_sach_ho_so, name='danh_sach_ho_so'),
    path('xet-duyet/<int:pk>/', views.chi_tiet_xet_duyet, name='chi_tiet_xet_duyet'),

    # Khác
    path('quy-dinh/', views.quy_dinh_view, name='quy_dinh'),
    path('huong-dan-cong-khai/', views.public_quy_dinh_view, name='public_quy_dinh'),
    path('vinh-danh/', views.vinh_danh_view, name='vinh_danh'),
    path('vinh-danh/<int:pk>/', views.chi_tiet_vinh_danh, name='chi_tiet_vinh_danh'),
]