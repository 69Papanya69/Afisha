# urls.py
from django.urls import path
from . import views
from .views import (
    PerformanceListView, PerformanceDetailView, PromotionListView, 
    LastPerformanceListView, update_review, delete_review,
    cart_list, cart_add, cart_update_quantity, cart_remove, cart_clear,
    order_list, order_detail, create_order, cancel_order, update_order_status,
    performance_schedules, FilteredPerformanceListView,
    CatalogCategoryListView, CatalogCategoryDetailView, CatalogFeaturedView,
    CatalogSearchView, CatalogStatsView
)

urlpatterns = [
    path('halls/', views.get_halls_by_theater, name='get_halls_by_theater'),
    path('performances/', PerformanceListView.as_view(), name='performance-list'),
    path('performances/filter/', FilteredPerformanceListView.as_view(), name='performance-filter'),
    path('performances/last/', LastPerformanceListView.as_view(), name='performance-last'),
    path('promotions/last/', PromotionListView.as_view(), name='promotion-last'),
    path('performances/<int:pk>/', PerformanceDetailView.as_view(), name='performance_detail'),
    path('performances/values/', views.get_performance_values, name='performance_values'),
    path('performances/values_list/', views.get_performance_values_list, name='performance_values_list'),
    path('performances/search/', views.search_performances, name='performance-search'),
    path('performances/<int:pk>/add_review/', views.add_review, name='add_review'),
    path('reviews/<int:pk>/update/', update_review, name='update_review'),
    path('reviews/<int:pk>/delete/', delete_review, name='delete_review'),
    path('reviews/<int:pk>/admin_delete/', views.admin_delete_review, name='admin_delete_review'),
    path('performances/<int:pk>/admin_delete/', views.admin_delete_performance, name='admin_delete_performance'),
    path('performances/<int:pk>/schedules/', performance_schedules, name='performance-schedules'),
    path('cart/', cart_list, name='cart-list'),
    path('cart/add/', cart_add, name='cart-add'),
    path('cart/update/<int:item_id>/', cart_update_quantity, name='cart-update-quantity'),
    path('cart/remove/<int:item_id>/', cart_remove, name='cart-remove'),
    path('cart/clear/', cart_clear, name='cart-clear'),
    path('orders/', order_list, name='order-list'),
    path('orders/<int:order_id>/', order_detail, name='order-detail'),
    path('orders/create/', create_order, name='order-create'),
    path('orders/<int:order_id>/cancel/', cancel_order, name='order-cancel'),
    path('orders/<int:order_id>/update-status/', update_order_status, name='order-update-status'),
    path('catalog/', CatalogFeaturedView.as_view(), name='catalog-featured'),
    path('catalog/categories/', CatalogCategoryListView.as_view(), name='catalog-categories'),
    path('catalog/categories/<int:pk>/', CatalogCategoryDetailView.as_view(), name='catalog-category-detail'),
    path('catalog/search/', CatalogSearchView.as_view(), name='catalog-search'),
    path('catalog/stats/', CatalogStatsView.as_view(), name='catalog-stats'),
]