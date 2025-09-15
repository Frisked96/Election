from django.contrib import admin
from .models import User, Election, Candidate, Vote, CandidateField

class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name',)

class CandidateAdmin(admin.ModelAdmin):
    list_display = ('user', 'election', 'vote_count')
    search_fields = ('user__username', 'election__name')
    list_filter = ('election',)

admin.site.register(User)
admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Vote)
admin.site.register(CandidateField)