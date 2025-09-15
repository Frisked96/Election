from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import ElectionForm, CandidateForm, CandidateFieldForm
from .models import Election, Candidate, Vote, CandidateField, User


class IsAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'


class UserLoginView(LoginView):
    template_name = 'polls/login.html'

    def get_success_url(self):
        if self.request.user.role == 'admin':
            return reverse_lazy('admin_election_list')
        return reverse_lazy('election_list')


def logout_view(request):
    logout(request)
    return redirect('login')


class ElectionListView(LoginRequiredMixin, ListView):
    model = Election
    template_name = 'polls/election_list.html'
    context_object_name = 'elections'


class ElectionDetailView(LoginRequiredMixin, DetailView):
    model = Election
    template_name = 'polls/election_detail.html'
    context_object_name = 'election'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Prevent admins from voting
            if self.request.user.role == 'admin':
                context['user_is_admin'] = True
            # Prevent candidates from voting in their own election
            if self.object.candidates.filter(user=self.request.user).exists():
                context['user_is_candidate'] = True
            # Check if the user has already voted
            if Vote.objects.filter(user=self.request.user, election=self.object).exists():
                context['user_has_voted'] = True
        # Check if the election is closed
        if self.object.is_closed:
            context['election_is_closed'] = True
        return context

    def post(self, request, *args, **kwargs):
        election = self.get_object()

        # Prevent admins from voting
        if request.user.role == 'admin':
            return HttpResponseForbidden("Admins are not allowed to vote.")

        # Prevent candidates from voting in their own election
        if election.candidates.filter(user=request.user).exists():
            return HttpResponseForbidden("You cannot vote in an election you are a candidate in.")

        # Prevent users from voting twice
        if Vote.objects.filter(user=request.user, election=election).exists():
            return HttpResponseForbidden("You have already voted in this election.")

        candidate_id = request.POST.get('candidate')
        if candidate_id:
            new_candidate = get_object_or_404(Candidate, pk=candidate_id)
            with transaction.atomic():
                # New vote
                Candidate.objects.filter(pk=new_candidate.pk).update(vote_count=F('vote_count') + 1)
                Vote.objects.create(user=request.user, election=election, candidate=new_candidate)
            return redirect('election_results', pk=election.id)
        return self.get(request, *args, **kwargs)


class ElectionResultsView(LoginRequiredMixin, DetailView):
    model = Election
    template_name = 'polls/election_results.html'
    context_object_name = 'election'

    def dispatch(self, request, *args, **kwargs):
        election = self.get_object()
        if not election.is_closed and request.user.role == 'student':
            messages.error(request, "The results for this election are not yet available.")
            return redirect('election_detail', pk=election.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = {candidate: candidate.vote_count for candidate in self.object.candidates.all()}
        context['results'] = results
        return context


# Admin Views
class AdminElectionListView(IsAdminMixin, ListView):
    model = Election
    template_name = 'polls/admin_election_list.html'
    context_object_name = 'elections'


class AdminCloseElectionView(IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        election = get_object_or_404(Election, pk=self.kwargs['pk'])
        election.is_closed = True
        election.save()
        messages.success(request, f"The election '{election.name}' has been closed.")
        return redirect('admin_election_list')


class AdminElectionCreateView(IsAdminMixin, CreateView):
    model = Election
    form_class = ElectionForm
    template_name = 'polls/admin_election_form.html'
    success_url = reverse_lazy('admin_election_list')


class AdminElectionUpdateView(IsAdminMixin, UpdateView):
    model = Election
    form_class = ElectionForm
    template_name = 'polls/admin_election_form.html'
    success_url = reverse_lazy('admin_election_list')

    def dispatch(self, request, *args, **kwargs):
        election = self.get_object()
        if election.is_closed:
            messages.error(request, "You cannot edit a closed election.")
            return redirect('admin_election_list')
        return super().dispatch(request, *args, **kwargs)


class AdminElectionDeleteView(IsAdminMixin, DeleteView):
    model = Election
    template_name = 'polls/admin_election_delete.html'
    success_url = reverse_lazy('admin_election_list')
    context_object_name = 'election'


class AdminManageCandidatesView(IsAdminMixin, DetailView):
    model = Election
    template_name = 'polls/admin_manage_candidates.html'
    context_object_name = 'election'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidate_form'] = CandidateForm()
        return context

    def post(self, request, *args, **kwargs):
        election = self.get_object()
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.election = election
            username = form.cleaned_data.get('username')
            if username:
                candidate.user = User.objects.get(username=username)
            candidate.save()
            return redirect('admin_election_manage_candidates', pk=election.id)
        return self.get(request, *args, **kwargs)


class AdminCandidateUpdateView(IsAdminMixin, UpdateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'polls/admin_candidate_form.html'
    context_object_name = 'candidate'

    def get_success_url(self):
        return reverse_lazy('admin_election_manage_candidates', kwargs={'pk': self.object.election.id})

    def form_valid(self, form):
        candidate = form.save(commit=False)
        username = form.cleaned_data.get('username')
        if username:
            candidate.user = User.objects.get(username=username)
        else:
            candidate.user = None
        candidate.save()
        return redirect(self.get_success_url())


class AdminCandidateDeleteView(IsAdminMixin, DeleteView):
    model = Candidate
    template_name = 'polls/admin_candidate_delete.html'
    context_object_name = 'candidate'

    def get_success_url(self):
        return reverse_lazy('admin_election_manage_candidates', kwargs={'pk': self.object.election.id})


class AdminCandidateAddFieldView(IsAdminMixin, CreateView):
    model = CandidateField
    form_class = CandidateFieldForm
    template_name = 'polls/admin_candidate_field_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidate'] = get_object_or_404(Candidate, pk=self.kwargs['candidate_id'])
        return context

    def form_valid(self, form):
        candidate = get_object_or_404(Candidate, pk=self.kwargs['candidate_id'])
        field = form.save(commit=False)
        field.candidate = candidate
        field.save()
        return redirect('admin_candidate_edit', pk=candidate.id)

