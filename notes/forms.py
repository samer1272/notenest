from django import forms

from .models import Note, Tag


class NoteForm(forms.ModelForm):
    new_tags = forms.CharField(
        required=False,
        label='Add tags',
        help_text='Separate multiple tags with commas.',
    )

    class Meta:
        model = Note
        fields = ['title', 'content', 'tags', 'is_pinned']
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.filter(user=user) if user else Tag.objects.none()
        self.order_fields(['title', 'content', 'tags', 'new_tags', 'is_pinned'])

    def clean_new_tags(self):
        cleaned_names = {}
        for name in self.cleaned_data['new_tags'].split(','):
            name = name.strip()
            if len(name) > 50:
                raise forms.ValidationError('Tags must be 50 characters or fewer.')
            if name:
                cleaned_names.setdefault(name.casefold(), name)
        return list(cleaned_names.values())

    def save_new_tags(self, note):
        for name in self.cleaned_data['new_tags']:
            tag = (
                Tag.objects.filter(user=note.user, name__iexact=name).first()
                or Tag.objects.create(user=note.user, name=name)
            )
            note.tags.add(tag)