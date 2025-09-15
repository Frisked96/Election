from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.ElectionListView.as_view(), name='election_list'),
    path('election/<int:pk>/', views.ElectionDetailView.as_view(), name='election_detail'),
    path('election/<int:pk>/results/', views.ElectionResultsView.as_view(), name='election_results'),

    # Admin URLs
    path('admin/elections/', views.AdminElectionListView.as_view(), name='admin_election_list'),
    path('admin/elections/create/', views.AdminElectionCreateView.as_view(), name='admin_election_create'),
    path('admin/elections/<int:pk>/edit/', views.AdminElectionUpdateView.as_view(), name='admin_election_edit'),
    path('admin/elections/<int:pk>/close/', views.AdminCloseElectionView.as_view(), name='admin_election_close'),
    path('admin/elections/<int:pk>/delete/', views.AdminElectionDeleteView.as_view(), name='admin_election_delete'),
    path('admin/elections/<int:pk>/candidates/', views.AdminManageCandidatesView.as_view(), name='admin_election_manage_candidates'),
    path('admin/candidates/<int:pk>/edit/', views.AdminCandidateUpdateView.as_view(), name='admin_candidate_edit'),
    path('admin/candidates/<int:pk>/delete/', views.AdminCandidateDeleteView.as_view(), name='admin_candidate_delete'),
    path('admin/candidates/<int:candidate_id>/fields/add/', views.AdminCandidateAddFieldView.as_view(), name='admin_candidate_add_field'),
]
