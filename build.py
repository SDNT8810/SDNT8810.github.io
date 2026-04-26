from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - gives a direct message for fresh VPS installs.
    print("PyYAML is required. Install it with: python -m pip install -r requirements.txt")
    sys.exit(1)


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config_SDNT.yaml"
PORTFOLIO_DIR = ROOT / "portfolio"
MATERIALS_DIR = ROOT / "materials"
CV_DIR = MATERIALS_DIR / "CV"
CV_TEX = CV_DIR / "CV.tex"
CV_PDF = CV_DIR / "CV.pdf"
SITE_DATA = PORTFOLIO_DIR / "portfolio-data.js"
PROJECTS_DIR = MATERIALS_DIR / "projects"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg", ".mov", ".m4v"}
DOCUMENT_EXTENSIONS = {".pdf"}
DESCRIPTION_FILES = [
    "description.md",
    "description.txt",
    "description.tex",
    "README.md",
    "readme.md",
]
PROJECT_METADATA_FILES = ["project.yaml", "project.yml", "metadata.yaml", "metadata.yml"]


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{CONFIG_PATH.name} must contain a YAML mapping at the top level.")
    return data


def included(node: Any) -> bool:
    return not (isinstance(node, dict) and node.get("include") is False)


def unwrap(node: Any) -> Any:
    """Remove include/value wrappers and drop anything marked include: false."""
    if isinstance(node, dict):
        if not included(node):
            return None
        keys = set(node.keys())
        if "value" in node and keys.issubset({"value", "include"}):
            return node.get("value")

        result: dict[str, Any] = {}
        for key, value in node.items():
            if key == "include":
                continue
            clean = unwrap(value)
            if clean is None:
                continue
            if clean == "" or clean == [] or clean == {}:
                continue
            result[key] = clean
        return result

    if isinstance(node, list):
        result_list = []
        for item in node:
            clean = unwrap(item)
            if clean is None:
                continue
            if clean == "" or clean == [] or clean == {}:
                continue
            result_list.append(clean)
        return result_list

    return node


def value_at(data: dict[str, Any], *path: str, default: Any = "") -> Any:
    node: Any = data
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    clean = unwrap(node)
    return default if clean is None else clean


def section_enabled(config: dict[str, Any], section: str) -> bool:
    site = config.get("site", {})
    sections = site.get("sections", {}) if isinstance(site, dict) else {}
    return included(site) and included(sections) and included(sections.get(section, {}))


def as_items(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, dict) and isinstance(value.get("items"), list):
        return value["items"]
    if isinstance(value, list):
        return value
    return []


def humanize_slug(value: str) -> str:
    value = re.sub(r"[_-]+", " ", value).strip()
    value = re.sub(r"\s+", " ", value)
    return value.title()


def make_slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return value.strip("-") or "project"


def normalize_date(value: Any) -> str:
    text = str(value or "").strip()
    if not text or text.lower() == "present":
        return text
    parts = re.split(r"[-/]", text)
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        year = parts[0]
        month = int(parts[1])
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        if 1 <= month <= 12:
            return f"{month_names[month - 1]} {year}"
    return text


def display_date_range(start: Any, end: Any) -> str:
    return join_nonempty([normalize_date(start), normalize_date(end)], " - ")


def sdnt_items(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key)
    if isinstance(value, dict):
        if not included(value):
            return []
        value = value.get("items", [])
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict) and included(item)]


def sdnt_first_value(data: dict[str, Any], key: str, default: str = "") -> str:
    node = data.get(key)
    if isinstance(node, dict) and included(node) and "value" in node:
        value = node.get("value", default)
    else:
        values = sdnt_items(data, key)
        if not values:
            return default
        value = values[0].get("value", default)
    return "" if value is None else str(value)


def sdnt_profile(data: dict[str, Any]) -> dict[str, Any]:
    profile = data.get("Profile")
    if isinstance(profile, dict) and included(profile):
        return profile
    return data


def split_skill_description(description: str) -> list[str]:
    text = str(description or "").strip()
    if not text:
        return []
    text = re.split(r"\s+for\s+", text, maxsplit=1, flags=re.IGNORECASE)[0]
    text = re.sub(r"\band\b", ",", text)
    return [item.strip(" .") for item in text.split(",") if item.strip(" .")]


def social_url(name: str, value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    normalized_name = name.lower()
    if text.startswith(("http://", "https://", "mailto:", "tel:")):
        return text
    if normalized_name == "whatsapp":
        digits = re.sub(r"[^\d]", "", text)
        return f"https://wa.me/{digits}" if digits else text
    if normalized_name == "telegram":
        return f"https://t.me/{text.lstrip('@')}"
    if "email" in normalized_name:
        return f"mailto:{text}"
    return text


def project_folder(category: str, title: str) -> str:
    category_path = str(category or "").strip()
    title_slug = make_slug(title)
    known = {
        "stm32-autopilot-and-embedded-robotics-systems": "Autopilot",
        "stm32-autopilot-system": "Autopilot",
        "hexa-leg-chandelier": "Hexa_Leg_Chandlier",
        "oxygen-salon": "Oxygen_Salon",
        "reformer": "Reformer",
        "stairmill": "StairMill",
        "3-axis-cnc-writer": "3_Axis_CNC_Writer",
        "5-axis-milling-machine": "5_Axis_Milling_Machine",
        "bunker-gcs": "Bunker_GCS",
        "helixabot": "Helixabot",
        "image-processing-robot": "Image_Processing",
        "ros-eth-technical-challenge": "ROS_ETH",
    }
    folder_name = known.get(title_slug) or re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_")
    return f"materials/projects/{category_path}/{folder_name}" if category_path and folder_name else ""


def normalize_sdnt_config(data: dict[str, Any]) -> dict[str, Any]:
    profile_data = sdnt_profile(data)
    name = str(profile_data.get("Name", "") or "").strip()
    family_name = str(profile_data.get("Family_Name", "") or "").strip()
    display_name = join_nonempty([name, family_name], " ") or "Davoud Nikkhouy"
    email = sdnt_first_value(profile_data, "Email")
    phone = sdnt_first_value(profile_data, "Phone")
    portfolio = sdnt_first_value(profile_data, "Portfolio", "https://davoudnikkhouy.com")

    social_links = []
    for link in sdnt_items(data, "social_media_links"):
        link_name = str(link.get("name", "") or "").strip()
        url = social_url(link_name, link.get("value"))
        if link_name and url:
            social_links.append({"name": link_name, "url": url})

    projects = []
    project_technologies: dict[str, list[str]] = {}
    for project in sdnt_items(data, "Projects"):
        title = str(project.get("name", "") or "").strip()
        if not title:
            continue
        technologies = as_items(project.get("technologies"))
        project_technologies[title] = [str(item) for item in technologies]
        category = str(project.get("category", "") or "").strip()
        projects.append(
            {
                "include": bool(project.get("include", True)),
                "title": title,
                "slug": make_slug(title),
                "category": humanize_slug(category),
                "folder": project_folder(category, title),
                "summary": project.get("description", ""),
                "role": project.get("ownership", ""),
                "technologies": technologies,
                "start_date": project.get("start_date", ""),
                "end_date": project.get("end_date", ""),
                "display_date": display_date_range(project.get("start_date", ""), project.get("end_date", "")),
                "location": project.get("location", ""),
            }
        )

    skill_groups = []
    for skill in sdnt_items(data, "Skills"):
        related = as_items(skill.get("related_projects"))
        items: list[str] = []
        for project_name in related:
            items.extend(project_technologies.get(str(project_name), []))
        if not items:
            items = split_skill_description(str(skill.get("description", "")))
        deduped = list(dict.fromkeys(item for item in items if item))
        skill_groups.append(
            {
                "include": bool(skill.get("include", True)),
                "name": skill.get("name", "Skills"),
                "items": deduped,
            }
        )

    work_items = []
    for item in sdnt_items(data, "Work_experience"):
        work_items.append(
            {
                "include": bool(item.get("include", True)),
                "title": item.get("title", ""),
                "company": item.get("company", ""),
                "location": item.get("location", ""),
                "start_date": item.get("start_date", ""),
                "end_date": item.get("end_date", ""),
                "display_date": display_date_range(item.get("start_date", ""), item.get("end_date", "")),
                "description": item.get("description", ""),
                "tasks": as_items(item.get("tasks")),
            }
        )

    education_items = []
    for item in sdnt_items(data, "Education"):
        thesis = item.get("Thesis") or item.get("thesis") or ""
        education_items.append(
            {
                "include": bool(item.get("include", True)),
                "degree": item.get("degree", ""),
                "field": item.get("field", ""),
                "branch": item.get("branch", ""),
                "institution": item.get("institution", ""),
                "location": item.get("location", ""),
                "start_date": item.get("start_date", ""),
                "end_date": item.get("end_date", ""),
                "display_date": display_date_range(item.get("start_date", ""), item.get("end_date", "")),
                "final_grade": item.get("GPD", ""),
                "thesis": thesis,
            }
        )

    publication_items = []
    for item in sdnt_items(data, "Publications"):
        venue = item.get("conference") or item.get("journal") or item.get("venue") or ""
        link = str(item.get("link", "") or "")
        publication_items.append(
            {
                "include": bool(item.get("include", True)),
                "year": str(item.get("year", "")),
                "title": item.get("title", ""),
                "authors": "; ".join(str(author) for author in as_items(item.get("authors"))),
                "venue": venue,
                "paper": link if link.lower().endswith(".pdf") else "",
                "link": "" if link.lower().endswith(".pdf") else link,
            }
        )

    referee_items = []
    for item in sdnt_items(data, "Referees"):
        referee_items.append(
            {
                "include": bool(item.get("include", True)),
                "name": item.get("name", ""),
                "position": item.get("position", ""),
                "institution": item.get("institution", ""),
                "email": item.get("email", ""),
                "phone": item.get("phone", ""),
                "description": item.get("description", ""),
            }
        )

    return {
        "site": {
            "include": True,
            "domain": "davoudnikkhouy.com",
            "title": f"{display_name} | Robotics and Embedded Systems Engineer",
            "description": f"Portfolio and CV for {display_name}, focused on robotics, embedded systems, control, and automation.",
            "language": "en",
            "cv_pdf": "/materials/CV/CV.pdf",
            "contact_api": "/api/contact",
            "hero_image": "/materials/profile_images/my_face_not_official.jpeg",
            "profile_image": "/materials/profile_images/profile_picture.jpg",
            "sections": {
                "include": True,
                "hero": {"include": True},
                "about": {"include": True},
                "skills": {"include": True},
                "experience": {"include": True},
                "projects": {"include": True},
                "education": {"include": True},
                "publications": {"include": True},
                "contact": {"include": True},
            },
        },
        "profile": {
            "include": True,
            "first_name": name,
            "last_name": family_name,
            "display_name": display_name,
            "headline": "Robotics and Embedded Systems Engineer",
            "location": "Milan, Italy",
            "home_address": sdnt_first_value(profile_data, "Home_address"),
            "about": unwrap(profile_data.get("ABOUT_ME", "")) or "",
            "contact": {
                "include": True,
                "email": email,
                "phone": phone,
                "portfolio": portfolio,
            },
            "links": social_links,
        },
        "skills": {"include": True, "groups": skill_groups},
        "work_experience": {"include": True, "items": work_items},
        "education": {"include": True, "items": education_items},
        "projects": {"include": True, "items": projects},
        "publications": {"include": True, "items": publication_items},
        "referees": {"include": True, "items": referee_items},
    }


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    if "site" in config or "profile" in config:
        return config
    return normalize_sdnt_config(config)


def read_text_preview(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1")
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", r"\1", text)
    text = re.sub(r"[#*_`>\[\]]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_description(folder: Path) -> str:
    for filename in DESCRIPTION_FILES:
        candidate = folder / filename
        if candidate.exists() and candidate.is_file():
            return read_text_preview(candidate)
    return ""


def load_project_metadata(folder: Path) -> dict[str, Any]:
    for filename in PROJECT_METADATA_FILES:
        candidate = folder / filename
        if not candidate.exists():
            continue
        with candidate.open("r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
        if isinstance(raw, dict) and included(raw):
            return unwrap(raw) or {}
    return {}


def discover_media(folder: Path) -> list[dict[str, str]]:
    if not folder.exists() or not folder.is_dir():
        return []

    media: list[dict[str, str]] = []
    ignored_names = set(DESCRIPTION_FILES + PROJECT_METADATA_FILES)
    for item in sorted(folder.rglob("*")):
        if not item.is_file() or item.name in ignored_names:
            continue
        suffix = item.suffix.lower()
        if suffix in IMAGE_EXTENSIONS:
            media_type = "image"
        elif suffix in VIDEO_EXTENSIONS:
            media_type = "video"
        elif suffix in DOCUMENT_EXTENSIONS:
            media_type = "document"
        else:
            continue
        media.append(
            {
                "type": media_type,
                "src": public_path(item),
                "title": humanize_slug(item.stem),
            }
        )
    return media


def public_path(path: Path | str) -> str:
    if isinstance(path, Path):
        try:
            value = path.relative_to(ROOT).as_posix()
        except ValueError:
            value = path.as_posix()
    else:
        value = str(path).replace("\\", "/")
    if value.startswith(("http://", "https://", "mailto:", "tel:", "/")):
        return value
    return "/" + value.lstrip("/")


def absolute_url(url: str, domain: str = "") -> str:
    if not url:
        return ""
    if url.startswith(("http://", "https://", "mailto:", "tel:")):
        return url
    base = domain.strip().rstrip("/")
    if base and not base.startswith(("http://", "https://")):
        base = "https://" + base
    if not base:
        return public_path(url)
    return f"{base}/{url.lstrip('/')}"


def leaf_project_dirs() -> list[Path]:
    if not PROJECTS_DIR.exists():
        return []
    result = []
    for folder in sorted(p for p in PROJECTS_DIR.rglob("*") if p.is_dir()):
        has_child_directory = any(child.is_dir() for child in folder.iterdir())
        if not has_child_directory:
            result.append(folder)
    return result


def normalize_project(raw_project: dict[str, Any], folder_hint: Path | None = None) -> dict[str, Any] | None:
    if not raw_project:
        raw_project = {}
    if not included(raw_project):
        return None

    project = unwrap(raw_project) or {}
    folder_value = project.get("folder")
    folder = folder_hint
    if folder_value:
        folder = (ROOT / folder_value).resolve()
    elif folder is None:
        folder = ROOT

    metadata = load_project_metadata(folder) if folder and folder.exists() else {}
    merged = {**metadata, **project}

    title = merged.get("title") or humanize_slug(folder.name if folder else "Project")
    category = merged.get("category")
    if not category and folder and PROJECTS_DIR in folder.parents:
        try:
            category = humanize_slug(folder.relative_to(PROJECTS_DIR).parts[0])
        except (ValueError, IndexError):
            category = "Project"

    summary = merged.get("summary") or merged.get("description") or ""
    if not summary and folder:
        summary = find_description(folder)

    technologies = as_items(merged.get("technologies"))
    links = as_items(merged.get("links"))
    folder_rel = folder.relative_to(ROOT).as_posix() if folder and folder.exists() else ""

    return {
        "title": title,
        "slug": merged.get("slug") or make_slug(title),
        "category": category or "Project",
        "summary": summary,
        "role": merged.get("role", ""),
        "technologies": technologies,
        "links": links,
        "folder": folder_rel,
        "media": discover_media(folder) if folder else [],
    }


def build_projects(config: dict[str, Any]) -> list[dict[str, Any]]:
    config = normalize_config(config)
    projects_config = config.get("projects", {})
    configured_projects = as_items(projects_config.get("items") if included(projects_config) else [])

    projects: list[dict[str, Any]] = []
    configured_folders: set[str] = set()
    for raw_project in configured_projects:
        project = normalize_project(raw_project)
        if not project:
            continue
        if project.get("folder"):
            configured_folders.add(project["folder"])
        projects.append(project)

    for folder in leaf_project_dirs():
        folder_rel = folder.relative_to(ROOT).as_posix()
        if folder_rel in configured_folders:
            continue
        project = normalize_project(load_project_metadata(folder), folder)
        if project:
            projects.append(project)

    return projects


def public_site_data(config: dict[str, Any]) -> dict[str, Any]:
    config = normalize_config(config)
    clean = unwrap(config) or {}
    site = clean.get("site", {})
    profile = clean.get("profile", {})
    contact = profile.get("contact", {})
    publications = as_items(clean.get("publications", {}).get("items") if isinstance(clean.get("publications"), dict) else [])
    for publication in publications:
        if isinstance(publication, dict):
            if publication.get("paper"):
                publication["paper"] = public_path(publication["paper"])
            if publication.get("link") and not publication["link"].startswith(("http://", "https://", "mailto:", "tel:")):
                publication["link"] = public_path(publication["link"])

    return {
        "site": {
            "domain": site.get("domain", ""),
            "title": site.get("title", ""),
            "description": site.get("description", ""),
            "language": site.get("language", "en"),
            "cvPdf": public_path(site.get("cv_pdf", "/materials/CV/CV.pdf")),
            "contactApi": site.get("contact_api", "/api/contact"),
            "heroImage": public_path(site.get("hero_image", "")) if site.get("hero_image") else "",
            "profileImage": public_path(site.get("profile_image", "")) if site.get("profile_image") else "",
            "sections": {
                "hero": section_enabled(config, "hero"),
                "about": section_enabled(config, "about"),
                "skills": section_enabled(config, "skills"),
                "experience": section_enabled(config, "experience"),
                "projects": section_enabled(config, "projects"),
                "education": section_enabled(config, "education"),
                "publications": section_enabled(config, "publications"),
                "contact": section_enabled(config, "contact"),
            },
        },
        "profile": {
            "displayName": profile.get("display_name", ""),
            "headline": profile.get("headline", ""),
            "location": profile.get("location", ""),
            "about": profile.get("about", ""),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
            "portfolio": contact.get("portfolio", ""),
            "links": as_items(profile.get("links")),
        },
        "skills": as_items(clean.get("skills", {}).get("groups") if isinstance(clean.get("skills"), dict) else []),
        "experience": as_items(clean.get("work_experience", {}).get("items") if isinstance(clean.get("work_experience"), dict) else []),
        "education": as_items(clean.get("education", {}).get("items") if isinstance(clean.get("education"), dict) else []),
        "publications": publications,
        "projects": build_projects(config) if included(config.get("projects", {})) else [],
    }


def tex_escape(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def tex_url(value: Any) -> str:
    text = str(value).replace("\\", "/")
    replacements = {
        "%": r"\%",
        "#": r"\#",
        "&": r"\&",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in text)


def display_url(url: str) -> str:
    if url.startswith("mailto:"):
        return url.removeprefix("mailto:")
    return url


def tex_href(url: str, label: str | None = None, *, show_url: bool = False) -> str:
    if not url:
        return ""
    visible_url = display_url(url)
    if show_url and label and label != visible_url:
        display = f"{label}: {visible_url}"
    else:
        display = label or visible_url
    return rf"\href{{{tex_url(url)}}}{{{tex_escape(display)}}}"


def join_nonempty(parts: list[str], separator: str = " | ") -> str:
    return separator.join(part for part in parts if part)


def render_itemize(items: list[str]) -> str:
    if not items:
        return ""
    lines = [r"\begin{itemize}"]
    for item in items:
        lines.append(rf"  \item {tex_escape(item)}")
    lines.append(r"\end{itemize}")
    return "\n".join(lines)


def render_cv(config: dict[str, Any]) -> str:
    config = normalize_config(config)
    clean = unwrap(config) or {}
    site = clean.get("site", {})
    profile = clean.get("profile", {})
    contact = profile.get("contact", {})
    links = as_items(profile.get("links"))
    domain = site.get("domain", "")

    name = profile.get("display_name") or join_nonempty(
        [profile.get("first_name", ""), profile.get("last_name", "")],
        " ",
    )
    headline = profile.get("headline", "")
    location = profile.get("location", "")
    address = profile.get("home_address", "")
    personal_details = [
        f"Work permit: {profile['work_permit']}" if profile.get("work_permit") else "",
        f"Nationality: {profile['nationality']}" if profile.get("nationality") else "",
        f"Date of birth: {profile['date_of_birth']}" if profile.get("date_of_birth") else "",
        f"Place of birth: {profile['place_of_birth']}" if profile.get("place_of_birth") else "",
        f"Gender: {profile['gender']}" if profile.get("gender") else "",
    ]

    contact_parts = [
        contact.get("phone", ""),
        tex_href(f"mailto:{contact.get('email')}", contact.get("email")) if contact.get("email") else "",
        tex_href(contact.get("portfolio"), contact.get("portfolio"), show_url=True) if contact.get("portfolio") else "",
    ]
    link_parts = [tex_href(link.get("url", ""), link.get("name", ""), show_url=True) for link in links if link.get("url")]

    lines = [
        r"\documentclass[10pt,a4paper]{article}",
        r"\usepackage[a4paper,margin=0.65in]{geometry}",
        r"\usepackage{titlesec}",
        r"\usepackage{enumitem}",
        r"\usepackage{xcolor}",
        r"\usepackage[hidelinks]{hyperref}",
        r"\setlength{\parindent}{0pt}",
        r"\setlength{\parskip}{3pt}",
        r"\setlist[itemize]{leftmargin=*,topsep=2pt,itemsep=1pt,parsep=0pt}",
        r"\titleformat{\section}{\large\bfseries}{}{0pt}{}[\titlerule]",
        r"\titlespacing*{\section}{0pt}{8pt}{4pt}",
        r"\pagestyle{empty}",
        r"\begin{document}",
        rf"{{\LARGE\bfseries {tex_escape(name)}}}\\",
    ]
    if headline:
        lines.append(rf"{tex_escape(headline)}\\")
    if any(personal_details):
        lines.append(rf"{tex_escape(join_nonempty(personal_details))}\\")
    if location or address:
        lines.append(rf"{tex_escape(join_nonempty([location, address]))}\\")
    if any(contact_parts):
        lines.append(join_nonempty(contact_parts) + r"\\")
    if any(link_parts):
        lines.append(join_nonempty(link_parts) + "\n")

    if profile.get("about"):
        lines.extend([r"\section*{Summary}", tex_escape(profile["about"])])

    skills = as_items(clean.get("skills", {}).get("groups") if isinstance(clean.get("skills"), dict) else [])
    if skills:
        lines.append(r"\section*{Core Skills}")
        for group in skills:
            items = as_items(group.get("items"))
            if items:
                lines.append(rf"\textbf{{{tex_escape(group.get('name', 'Skills'))}:}} {tex_escape(', '.join(items))}\\")

    keywords = as_items(clean.get("ats_keywords", {}).get("items") if isinstance(clean.get("ats_keywords"), dict) else [])
    if keywords:
        lines.extend([r"\section*{ATS Keywords}", tex_escape(", ".join(keywords))])

    experience = as_items(clean.get("work_experience", {}).get("items") if isinstance(clean.get("work_experience"), dict) else [])
    if experience:
        lines.append(r"\section*{Professional Experience}")
        for item in experience:
            title_line = join_nonempty([item.get("title", ""), item.get("company", "")], ", ")
            right = item.get("display_date") or join_nonempty([item.get("start_date", ""), item.get("end_date", "")], " - ")
            lines.append(rf"\textbf{{{tex_escape(title_line)}}} \hfill {tex_escape(right)}\\")
            if item.get("location"):
                lines.append(rf"{tex_escape(item['location'])}\\")
            if item.get("description"):
                lines.append(tex_escape(item["description"]))
            lines.append(render_itemize(as_items(item.get("tasks"))))
            lines.append(r"\vspace{2pt}")

    projects = build_projects(config) if included(config.get("projects", {})) else []
    if projects:
        lines.append(r"\section*{Selected Projects}")
        for project in projects:
            tech = as_items(project.get("technologies"))
            detail = join_nonempty([project.get("category", ""), project.get("role", "")], " - ")
            lines.append(rf"\textbf{{{tex_escape(project.get('title', 'Project'))}}} -- {tex_escape(detail)}\\")
            if project.get("summary"):
                lines.append(tex_escape(project["summary"]) + r"\\")
            if tech:
                lines.append(rf"\textit{{Technologies:}} {tex_escape(', '.join(tech))}\\")
            lines.append(r"\vspace{2pt}")

    education = as_items(clean.get("education", {}).get("items") if isinstance(clean.get("education"), dict) else [])
    if education:
        lines.append(r"\section*{Education}")
        for item in education:
            degree = join_nonempty([item.get("degree", ""), item.get("field", ""), item.get("branch", "")], ", ")
            date = item.get("display_date") or join_nonempty([item.get("start_date", ""), item.get("end_date", "")], " - ")
            lines.append(rf"\textbf{{{tex_escape(degree)}}} \hfill {tex_escape(date)}\\")
            school = join_nonempty([item.get("institution", ""), item.get("location", "")], ", ")
            if item.get("website"):
                school = join_nonempty([school, tex_href(item["website"], item["website"])])
            lines.append(school + r"\\")
            details = []
            if item.get("final_grade"):
                details.append(f"Final grade: {item['final_grade']}")
            if item.get("eqf_level"):
                details.append(f"Level in EQF: {item['eqf_level']}")
            if item.get("thesis"):
                details.append(f"Thesis: {item['thesis']}")
            if details:
                lines.append(tex_escape(" | ".join(details)) + r"\\")
            lines.append(r"\vspace{2pt}")

    publications = as_items(clean.get("publications", {}).get("items") if isinstance(clean.get("publications"), dict) else [])
    if publications:
        lines.append(r"\section*{Publications}")
        for item in publications:
            title = tex_escape(item.get("title", ""))
            year = tex_escape(item.get("year", ""))
            authors = tex_escape(item.get("authors", ""))
            venue = tex_escape(item.get("venue", ""))
            publication_url = absolute_url(item.get("link") or item.get("paper") or "", domain)
            link = tex_href(publication_url, "Paper", show_url=True) if publication_url else ""
            lines.append(rf"\textbf{{[{year}] {title}}}\\")
            lines.append(join_nonempty([authors, venue, link]) + r"\\")
            lines.append(r"\vspace{2pt}")

    referees = as_items(clean.get("referees", {}).get("items") if isinstance(clean.get("referees"), dict) else [])
    if referees:
        lines.append(r"\section*{References}")
        for item in referees:
            date = item.get("display_date") or join_nonempty([item.get("start_date", ""), item.get("end_date", "")], " - ")
            if date:
                lines.append(rf"\textbf{{{tex_escape(item.get('name', ''))}}} \hfill {tex_escape(date)}\\")
            else:
                lines.append(rf"\textbf{{{tex_escape(item.get('name', ''))}}}\\")
            details = [
                item.get("position", ""),
                item.get("institution", ""),
                item.get("email", ""),
                item.get("phone", ""),
                tex_href(item.get("link", ""), "Profile", show_url=True) if item.get("link") else "",
            ]
            lines.append(join_nonempty([tex_escape(part) if not part.startswith(r"\href") else part for part in details]) + r"\\")
            lines.append(r"\vspace{2pt}")

    lines.extend([r"\end{document}", ""])
    return "\n".join(line for line in lines if line is not None and line != "")


def write_site_data(config: dict[str, Any]) -> None:
    data = public_site_data(config)
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    SITE_DATA.parent.mkdir(parents=True, exist_ok=True)
    SITE_DATA.write_text(f"window.PORTFOLIO_DATA = {payload};\n", encoding="utf-8")


def cleanup_latex_files() -> None:
    for suffix in [".aux", ".fdb_latexmk", ".fls", ".log", ".out", ".synctex.gz"]:
        path = CV_DIR / f"CV{suffix}"
        if path.exists():
            path.unlink()


def compile_pdf() -> bool:
    commands = []
    if shutil.which("latexmk") and shutil.which("perl"):
        commands.append(["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "CV.tex"])
    if shutil.which("xelatex"):
        commands.append(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "CV.tex"])
    if shutil.which("pdflatex"):
        commands.append(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "CV.tex"])

    if not commands:
        print("No LaTeX engine found. CV.tex was generated, but CV.pdf was not.")
        return False

    for command in commands:
        try:
            result = subprocess.run(
                command,
                cwd=CV_DIR,
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired:
            print(f"{command[0]} timed out.")
            continue
        if result.returncode == 0 and CV_PDF.exists():
            cleanup_latex_files()
            return True
        print(f"{command[0]} failed. Trying the next LaTeX engine if available.")
        if result.stdout:
            print(result.stdout[-2000:])
        if result.stderr:
            print(result.stderr[-2000:])

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Generate CV.tex, CV.pdf, and portfolio-data.js from {CONFIG_PATH.name}.")
    parser.add_argument("--no-pdf", action="store_true", help="Generate CV.tex and site data without compiling CV.pdf.")
    args = parser.parse_args()

    config = load_config()
    CV_DIR.mkdir(parents=True, exist_ok=True)
    CV_TEX.write_text(render_cv(config), encoding="utf-8")
    write_site_data(config)

    pdf_ok = False
    if not args.no_pdf:
        pdf_ok = compile_pdf()

    print(f"Wrote {CV_TEX.name}")
    print(f"Wrote {SITE_DATA.name}")
    if args.no_pdf:
        print("Skipped PDF generation.")
    elif pdf_ok:
        print(f"Wrote {CV_PDF.name}")
    else:
        print("CV.pdf was not generated. Check the LaTeX output above.")
    return 0 if args.no_pdf or pdf_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
