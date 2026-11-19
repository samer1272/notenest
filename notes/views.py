import io
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.text import slugify
from xhtml2pdf import pisa

from .forms import NoteForm
from .models import Note, Tag

NOTE_SORTS = {
    'default': ('-is_pinned', '-updated_at', '-pk'),
    'recent': ('-updated_at', '-pk'),
    'oldest': ('updated_at', 'pk'),
    'title': ('title', 'pk'),
}
NOTES_PER_PAGE = 4


def _pdf_link_callback(uri, rel):
    if uri.startswith('/static/'):
        static_file = uri.replace('/static/', '', 1)
        for static_dir in settings.STATICFILES_DIRS:
            candidate = os.path.join(str(static_dir), static_file)
            if os.path.exists(candidate):
                return candidate
    return uri


def _get_note_list(request):
    notes = Note.objects.filter(user=request.user).prefetch_related('tags')
    available_tags = Tag.objects.filter(user=request.user).order_by('name', 'pk')
    search_query = request.GET.get('q', '').strip()
    pinned_filter = request.GET.get('pinned', '')
    if pinned_filter not in ('', 'pinned', 'unpinned'):
        pinned_filter = ''
    sort_order = request.GET.get('sort', 'default')
    if sort_order not in NOTE_SORTS:
        sort_order = 'default'

    requested_tag_ids = request.GET.getlist('tags')
    available_tag_ids = set(available_tags.values_list('pk', flat=True))
    selected_tag_ids = []
    for tag_id in requested_tag_ids:
        try:
            tag_pk = int(tag_id)
        except (TypeError, ValueError):
            continue
        if tag_pk in available_tag_ids and tag_pk not in selected_tag_ids:
            selected_tag_ids.append(tag_pk)

    if search_query:
        notes = notes.filter(
            Q(title__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(tags__name__icontains=search_query)
        ).distinct()
    if pinned_filter == 'pinned':
        notes = notes.filter(is_pinned=True)
    elif pinned_filter == 'unpinned':
        notes = notes.filter(is_pinned=False)
    if selected_tag_ids:
        notes = notes.filter(tags__pk__in=selected_tag_ids).distinct()

    notes = notes.order_by(*NOTE_SORTS[sort_order])
    page_obj = Paginator(notes, NOTES_PER_PAGE).get_page(request.GET.get('page'))
    pagination_query = request.GET.copy()
    pagination_query.pop('page', None)

    return {
        'notes': page_obj.object_list,
        'page_obj': page_obj,
        'search_query': search_query,
        'pinned_filter': pinned_filter,
        'sort_order': sort_order,
        'available_tags': available_tags,
        'selected_tag_ids': selected_tag_ids,
        'has_active_filters': bool(search_query or pinned_filter or selected_tag_ids),
        'pagination_query': pagination_query.urlencode(),
    }


def _pdf_filename_for_note(note):
    title = slugify(note.title)[:40] or 'note'
    return f'{title}_{note.pk}.pdf'


def _build_pdf_response(note):
    html_string = render_to_string('notes/pdf_template.html', {'note': note})
    pdf_buffer = io.BytesIO()
    pdf_result = pisa.CreatePDF(io.StringIO(html_string), pdf_buffer, link_callback=_pdf_link_callback)
    if pdf_result.err:
        return None

    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{_pdf_filename_for_note(note)}"'
    return response


@login_required(login_url='login')
def home(request):
    return render(request, 'home.html', _get_note_list(request))


def about(request):
    return render(request, 'about.html')


@login_required(login_url='login')
def add_note(request):
    form = NoteForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        note = form.save(commit=False)
        note.user = request.user
        note.save()
        form.save_m2m()
        form.save_new_tags(note)
        messages.success(request, 'Note created.')
        return redirect('home')
    return render(request, 'notes/note_form.html', {'form': form, 'page_title': 'New note'})


@login_required(login_url='login')
def note_detail(request, pk):
    note = get_object_or_404(Note.objects.prefetch_related('tags'), pk=pk, user=request.user)
    return render(request, 'notes/note_detail.html', {'note': note})


@login_required(login_url='login')
def edit_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    form = NoteForm(request.POST or None, instance=note, user=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        form.save_new_tags(note)
        messages.success(request, 'Note updated.')
        return redirect('note_detail', pk=note.pk)
    return render(request, 'notes/note_form.html', {'form': form, 'note': note, 'page_title': 'Edit note'})


@login_required(login_url='login')
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted.')
        return redirect('home')
    return render(request, 'notes/note_confirm_delete.html', {'note': note})


@login_required(login_url='login')
def export_pdf(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    response = _build_pdf_response(note)
    if response is None:
        return HttpResponse('PDF export failed while generating the document.', status=500)
    return response