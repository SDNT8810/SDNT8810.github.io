# Davoud Nikkhouy Portfolio

Static portfolio and CV generator driven by `config_SDNT.yaml`.

The public domain is generated from `config_SDNT.yaml`; this project does not require a `CNAME` file.

## Local build

```powershell
python -m pip install -r requirements.txt
python build.py
python portfolio/server.py
```

Open `http://localhost:8000`.

Run the local servers directly in the terminal, not through `Start-Process` or another detached launcher. Closing that terminal will stop the server. Each server also writes a local PID file and replaces its previous run when started again.

If LaTeX is not installed yet, use `python build.py --no-pdf` to regenerate the portfolio data and CV TeX without compiling the PDF.

`portfolio/server.py` serves the repository root, including the app in `portfolio/` and public files in `materials/`, and exposes `POST /api/contact`.

## Contact Form

Create a local `.env` file from `.env.example`:

```env
CONTACT_EMAIL_ENABLED=false
CONTACT_RATE_LIMIT_MAX=50
CONTACT_RATE_LIMIT_WINDOW_SECONDS=900
BREVO_API_KEY=
SITE_DOMAIN=davoudnikkhouy.com
CONTACT_TO_EMAIL=davoudnikkhouy@gmail.com
CONTACT_FROM_EMAIL=verified-sender@davoudnikkhouy.com
CONTACT_FROM_NAME=Davoud Nikkhouy Portfolio
CONTACT_SUBJECT_PREFIX=[Portfolio]
```

`CONTACT_FROM_EMAIL` must be a sender verified in Brevo. Until Brevo is active, the form reports that email delivery is inactive and the site keeps direct email links available.

## Visibility

Most public content is controlled from the readable `config_SDNT.yaml` file. Main sections such as `Projects`, `Skills`, `Work_experience`, `Education`, `Publications`, `Referees`, and `social_media_links` use:

```yaml
value: "Visible text"
include: true
```

Set `include: false` to remove that item from the generated `materials/CV/CV.tex` and portfolio data. Parent flags are evaluated in cascade style by the generator: when a parent is off, its children are ignored without changing their own saved `include` values.

For a visual editor, run:

```powershell
python config_master_cv.py
```

Then open the printed localhost URL, toggle the checkboxes, and use `Export LaTeX + PDF`.

## Project media

Put project material inside each project folder under `materials/projects/`. The build script automatically finds:

- Images: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.svg`, `.avif`
- Videos: `.mp4`, `.webm`, `.ogg`, `.mov`, `.m4v`
- Documents: `.pdf`
- Descriptions: `description.md`, `description.txt`, `description.tex`, or `README.md`
- Optional metadata: `project.yaml`, `project.yml`, `metadata.yaml`, or `metadata.yml`

Run `python build.py` again after changing `config_SDNT.yaml` or project files. It regenerates `materials/CV/CV.tex`, `materials/CV/CV.pdf`, and `portfolio/portfolio-data.js`.

## VPS deployment

For low traffic, run `portfolio/server.py` behind Nginx. Nginx can serve static files directly and proxy `/api/contact` to Python, or Python can serve everything. The local Python server sends basic security headers, blocks dotfiles and directory listings, and supports byte-range requests for video previews. Nginx also handles byte ranges for MP4/WebM streaming. Runtime logs are written to `portfolio/portfolio-server.log` and `portfolio/portfolio-server.err.log`.
