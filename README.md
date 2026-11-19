# NoteNest

NoteNest is a small Django note-taking app. It gives each user a private place
to create notes, keep track of ideas with tags, pin important reminders, and
export a note as a PDF.

I built it with the standard Django account system and SQLite, so it is easy to
run locally while learning or developing the project.

## What you can do

- Sign up, sign in, and sign out
- Create, view, edit, and delete notes
- Search note titles, content, and tags
- Pin notes and filter the note list
- Sort notes by the latest update, creation date, or title
- Add tags by separating tag names with commas
- Add a short bio and profile picture
- Download an individual note as a PDF

## Requirements

- Windows with PowerShell
- Python 3.13
- The Python packages listed in `requirement.txt`

## Running it on your own computer

Open PowerShell in the project folder, then run:

```powershell
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirement.txt
python manage.py migrate
python manage.py runserver
```

The development server should start at <http://127.0.0.1:8000/>. Visit that
address in a browser and choose **Sign up** to create an account.

The project uses `db.sqlite3` for local data. Uploaded profile pictures are
stored in `media/profile_pics/`.

## Useful commands

Check Django configuration:

```powershell
python manage.py check
```

Run the test suite:

```powershell
python manage.py test
```

Apply changes to the database models:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Open Django's admin interface:

```powershell
python manage.py createsuperuser
python manage.py runserver
```

Then visit <http://127.0.0.1:8000/admin/>.

## A few project details

The main routes are:

- `/` for the user's note list
- `/notes/new/` to add a note
- `/accounts/signup/` to create an account
- `/accounts/login/` to log in
- `/accounts/profile/` to edit a profile

The app is split into two Django apps:

- `accounts` handles sign-up, login, logout, and profiles
- `notes` handles notes, tags, filtering, and PDF export

## Acknowledgements

AI tools helped create the front-end styling and design.

## Preparing for deployment

The settings are intended for local development by default. Before putting the
app on a public server:

1. Set `DJANGO_DEBUG=False` and set a private `DJANGO_SECRET_KEY`.
2. Add the public hostnames to `DJANGO_ALLOWED_HOSTS`.
3. Add HTTPS origins to `DJANGO_CSRF_TRUSTED_ORIGINS`.
4. Move the database and uploaded media to reliable production storage.
5. Configure static files and serve the app over HTTPS.
6. Run migrations and Django's deployment checks.

You can generate a secret key with:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then run:

```powershell
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```
