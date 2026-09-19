from django.contrib import admin

from apps.master_data.models import MasterAdmin, MasterGuru, MasterJurusan, MasterKelas, MasterSiswa

admin.site.register(MasterKelas)
admin.site.register(MasterJurusan)
admin.site.register(MasterAdmin)
admin.site.register(MasterGuru)
admin.site.register(MasterSiswa)
