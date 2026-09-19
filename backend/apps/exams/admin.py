from django.contrib import admin

from apps.exams.models import Ujian, UjianSoal


class UjianSoalInline(admin.TabularInline):
    model = UjianSoal
    extra = 0


@admin.register(Ujian)
class UjianAdmin(admin.ModelAdmin):
    list_display = ("nama_ujian", "jenis_ujian", "guru", "kelas", "jurusan", "token", "status", "hasil_published")
    list_filter = ("status", "jenis_ujian", "hasil_published")
    inlines = [UjianSoalInline]
