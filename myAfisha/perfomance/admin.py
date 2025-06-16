from django.contrib import admin
from django import forms
from django.urls import path
from django.http import JsonResponse, FileResponse
from .models import Performance, PerformanceCategory, PerformanceSchedule, Promotion, Review, Like, CartItem, Order, OrderItem
from main.models import Hall, Theater
import io
from reportlab.pdfgen import canvas


@admin.register(PerformanceCategory)
class PerformanceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_performances_count')
    search_fields = ('name',)
    
    def get_performances_count(self, obj):
        return obj.performances.count()
    get_performances_count.short_description = 'Количество спектаклей'


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_duration', 'created_at', 'get_schedule_count', 'file')
    list_filter = ('category', 'created_at')
    search_fields = ('name__icontains', 'category__name__icontains', 'description__icontains')
    date_hierarchy = 'created_at'
    readonly_fields = ('get_schedule_count',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'category', 'duration_time')
        }),
        ('Медиа', {
            'fields': ('image', 'file', 'related_link')
        }),
        ('Дополнительно', {
            'fields': ('created_at', 'get_schedule_count')
        }),
    )
    actions = ['generate_pdf', 'generate_catalog_pdf']

    def get_duration(self, obj):
        if not obj.duration_time:
            return "Не указана"
        
        total_seconds = obj.duration_time.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        if hours > 0:
            return f"{hours} ч {minutes} мин"
        return f"{minutes} мин"
    get_duration.short_description = 'Продолжительность'
    
    def get_schedule_count(self, obj):
        return obj.schedule.count()
    get_schedule_count.short_description = 'Количество сеансов'

    def generate_pdf(self, request, queryset):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)

        y = 800  # Начальная позиция для текста
        for performance in queryset:
            p.drawString(100, y, f"Название: {performance.name}")
            p.drawString(100, y - 20, f"Категория: {performance.category}")
            p.drawString(100, y - 40, f"Дата создания: {performance.created_at}")
            y -= 80  # Переместиться на следующую позицию

        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='спектакли.pdf')
    generate_pdf.short_description = "Сгенерировать PDF для выбранных спектаклей"
    
    def generate_catalog_pdf(self, request, queryset):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        
        # Заголовок
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 800, "Каталог спектаклей")
        p.setFont("Helvetica", 12)
        
        y = 750  # Начальная позиция для текста
        
        # Группируем спектакли по категориям
        categories = {}
        for performance in queryset:
            category_name = performance.category.name if performance.category else "Без категории"
            if category_name not in categories:
                categories[category_name] = []
            categories[category_name].append(performance)
        
        # Выводим спектакли по категориям
        for category_name, performances in categories.items():
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, category_name)
            y -= 30
            
            p.setFont("Helvetica", 12)


class PerformanceScheduleForm(forms.ModelForm):
    class Meta:
        model = PerformanceSchedule
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        hall = cleaned_data.get('hall')
        theater = cleaned_data.get('theater')

        if hall and theater and hall.theater != theater:
            self.add_error('hall', 'Этот зал не принадлежит выбранному театру.')

        return cleaned_data

@admin.register(PerformanceSchedule)
class PerformanceScheduleAdmin(admin.ModelAdmin):
    form = PerformanceScheduleForm
    list_display = ('performance', 'theater', 'hall', 'date_time', 'available_seats')
    list_filter = ('performance', 'theater', 'date_time')
    date_hierarchy = 'date_time'

    class Media:
        js = ('admin/js/filter_halls_by_theater.js',)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percentage', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('title',)
    date_hierarchy = 'start_date'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'performance', 'created_at')
    list_filter = ('performance', 'created_at')
    search_fields = ('user__username', 'performance__name')
    date_hierarchy = 'created_at'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'review', 'created_at')
    list_filter = ('user', 'review')
    date_hierarchy = 'created_at'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_performance', 'get_theater', 'get_hall', 'quantity', 'added_at')
    list_filter = ('added_at', 'user')
    search_fields = ('user__username', 'performance_schedule__performance__name')
    
    def get_performance(self, obj):
        return obj.performance_schedule.performance.name
    get_performance.short_description = 'Спектакль'
    
    def get_theater(self, obj):
        return obj.performance_schedule.theater.name if obj.performance_schedule.theater else '-'
    get_theater.short_description = 'Театр'
    
    def get_hall(self, obj):
        return obj.performance_schedule.hall.number_hall if obj.performance_schedule.hall else '-'
    get_hall.short_description = 'Зал'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('performance_schedule', 'quantity', 'price_per_unit')
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'customer_name', 'get_status_display', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'customer_name', 'customer_email')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'status', 'total_amount', 'created_at', 'updated_at')
        }),
        ('Информация о заказчике', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Оплата', {
            'fields': ('payment_method', 'payment_id')
        }),
    )
    
    actions = ['generate_order_pdf', 'mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']
    
    def get_status_display(self, obj):
        return dict(OrderStatus.choices)[obj.status]
    get_status_display.short_description = 'Статус'
    
    def generate_order_pdf(self, request, queryset):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        
        y = 800
        for order in queryset:
            # Заголовок заказа
            p.drawString(100, y, f"Заказ #{order.id}")
            p.drawString(100, y - 20, f"Покупатель: {order.customer_name}")
            p.drawString(100, y - 40, f"Email: {order.customer_email}")
            p.drawString(100, y - 60, f"Статус: {dict(OrderStatus.choices)[order.status]}")
            p.drawString(100, y - 80, f"Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}")
            
            y -= 120
            
            # Элементы заказа
            p.drawString(100, y, "Спектакли:")
            y -= 20
            
            for item in order.items.all():
                p.drawString(120, y, f"- {item.performance_schedule.performance.name}")
                p.drawString(120, y - 20, f"  Дата: {item.performance_schedule.date_time.strftime('%d.%m.%Y %H:%M')}")
                p.drawString(120, y - 40, f"  Кол-во: {item.quantity} x {item.price_per_unit} руб.")
                p.drawString(120, y - 60, f"  Итого: {item.subtotal} руб.")
                
                y -= 100
            
            p.drawString(100, y, f"Общая сумма: {order.total_amount} руб.")
            y -= 120
        
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='orders.pdf')
    generate_order_pdf.short_description = "Сгенерировать PDF для выбранных заказов"
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status=OrderStatus.CONFIRMED)
        self.message_user(request, f"{updated} заказов отмечены как подтвержденные.")
    mark_as_confirmed.short_description = "Отметить как подтвержденные"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status=OrderStatus.COMPLETED)
        self.message_user(request, f"{updated} заказов отмечены как выполненные.")
    mark_as_completed.short_description = "Отметить как выполненные"
    
    def mark_as_cancelled(self, request, queryset):
        for order in queryset:
            if order.status != OrderStatus.CANCELLED:
                # Возвращаем места в расписание при отмене
                for item in order.items.all():
                    item.performance_schedule.release_seats(item.quantity)
                order.status = OrderStatus.CANCELLED
                order.save()
        
        self.message_user(request, f"{queryset.count()} заказов отмечены как отмененные.")
    mark_as_cancelled.short_description = "Отметить как отмененные"
    
    def save_model(self, request, obj, form, change):
        # Если изменился статус с отмененного на другой, резервируем места
        if change and 'status' in form.changed_data:
            old_order = Order.objects.get(pk=obj.pk)
            if old_order.status == OrderStatus.CANCELLED and obj.status != OrderStatus.CANCELLED:
                # Резервируем места
                for item in obj.items.all():
                    if not item.performance_schedule.reserve_seats(item.quantity):
                        # Если недостаточно мест, оставляем заказ отмененным
                        self.message_user(
                            request, 
                            f"Недостаточно мест для '{item.performance_schedule.performance.name}'. "
                            f"Доступно: {item.performance_schedule.available_seats}, "
                            f"требуется: {item.quantity}",
                            level='ERROR'
                        )
                        obj.status = OrderStatus.CANCELLED
                        break
            # Если изменился статус с другого на отмененный, возвращаем места
            elif old_order.status != OrderStatus.CANCELLED and obj.status == OrderStatus.CANCELLED:
                for item in obj.items.all():
                    item.performance_schedule.release_seats(item.quantity)
        
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'get_performance', 'quantity', 'price_per_unit', 'get_subtotal')
    list_filter = ('order',)
    search_fields = ('order__id', 'performance_schedule__performance__name')
    readonly_fields = ('order', 'performance_schedule', 'quantity', 'price_per_unit')
    
    def get_performance(self, obj):
        return obj.performance_schedule.performance.name
    get_performance.short_description = 'Спектакль'
    
    def get_subtotal(self, obj):
        return obj.subtotal
    get_subtotal.short_description = 'Итого'
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
