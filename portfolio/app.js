(function () {
  "use strict";

  const data = window.PORTFOLIO_DATA || {};
  const site = data.site || {};
  const profile = data.profile || {};
  const sections = site.sections || {};
  const app = document.querySelector("#app");

  let activeCategory = "All";
  let activeProject = null;
  let activeSlide = 0;
  let keydownBound = false;

  const escapeHtml = (value) =>
    String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const list = (value) => Array.isArray(value) ? value : [];

  const initials = (name) =>
    String(name || "DN")
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0])
      .join("")
      .toUpperCase();

  const sectionEnabled = (name) => sections[name] !== false;
  const firstMedia = (project) => list(project.media).find((item) => item.type === "image" || item.type === "video");
  const categories = () => ["All", ...Array.from(new Set(list(data.projects).map((project) => project.category).filter(Boolean)))];

  function linkHref(value, type) {
    if (!value) return "";
    if (type === "email") return `mailto:${value}`;
    if (type === "phone") return `tel:${String(value).replace(/[^\d+]/g, "")}`;
    return value;
  }

  function renderNav() {
    const items = [
      ["about", "About"],
      ["skills", "Skills"],
      ["experience", "Experience"],
      ["projects", "Projects"],
      ["education", "Education"],
      ["publications", "Publications"],
      ["contact", "Contact"],
    ].filter(([key]) => sectionEnabled(key));

    return `
      <header class="topbar">
        <div class="topbar-inner">
          <a class="brand" href="#top" aria-label="Home">
            <span class="brand-mark">${escapeHtml(initials(profile.displayName))}</span>
            <span class="brand-text">
              <strong>${escapeHtml(profile.displayName || "Davoud Nikkhouy")}</strong>
              <span>${escapeHtml(profile.headline || "Portfolio")}</span>
            </span>
          </a>
          <nav class="nav" aria-label="Primary">
            ${items.map(([key, label]) => `<a href="#${key}">${label}</a>`).join("")}
          </nav>
        </div>
      </header>
    `;
  }

  function sectionHead(kicker, title, side = "") {
    return `
      <div class="section-head">
        <div>
          <p class="section-kicker">${escapeHtml(kicker)}</p>
          <h2>${escapeHtml(title)}</h2>
        </div>
        ${side}
      </div>
    `;
  }

  function renderHero() {
    if (!sectionEnabled("hero")) return "";
    const stats = [
      [`${list(data.projects).length}+`, "documented projects"],
      [`${list(data.skills).length}`, "technical domains"],
      [`${list(data.publications).length}`, "publications"],
    ];
    const background = site.heroImage || site.profileImage || "";
    return `
      <section id="top" class="hero">
        ${background ? `<img class="hero-image" src="${escapeHtml(background)}" alt="" aria-hidden="true" />` : ""}
        <div class="hero-inner">
          <div class="hero-copy">
            <p class="eyebrow">${escapeHtml(profile.location || "Milan, Italy")}</p>
            <h1>${escapeHtml(profile.displayName || "Davoud Nikkhouy")}</h1>
            <p class="hero-lede">${escapeHtml(profile.headline || "")}</p>
            <p class="hero-lede">${escapeHtml(profile.about || "")}</p>
            <div class="hero-actions">
              ${site.cvPdf ? `<a class="button-link primary" href="${escapeHtml(site.cvPdf)}">Download CV</a>` : ""}
              ${sectionEnabled("projects") ? `<a class="button-link" href="#projects">View Projects</a>` : ""}
              ${sectionEnabled("contact") ? `<a class="button-link" href="#contact">Contact</a>` : ""}
            </div>
            <div class="hero-stats">
              ${stats.map(([value, label]) => `<div class="stat"><strong>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span></div>`).join("")}
            </div>
          </div>
        </div>
      </section>
    `;
  }

  function renderAbout() {
    if (!sectionEnabled("about")) return "";
    return `
      <section id="about" class="section">
        <div class="section-inner">
          ${sectionHead("Profile", "Engineering robotics from firmware to motion planning")}
          <div class="about-grid">
            <div class="profile-panel">
              <p>${escapeHtml(profile.about || "")}</p>
              <div class="chips">
                ${list(profile.links).slice(0, 6).map((link) => `<a class="chip" href="${escapeHtml(link.url)}" rel="noopener noreferrer">${escapeHtml(link.name)}</a>`).join("")}
              </div>
            </div>
            <aside class="profile-aside">
              ${site.profileImage ? `<img class="portrait" src="${escapeHtml(site.profileImage)}" alt="${escapeHtml(profile.displayName || "Profile photo")}" />` : ""}
              <div class="contact-panel">
                <dl class="info-list">
                  ${profile.location ? `<div><dt>Location</dt><dd>${escapeHtml(profile.location)}</dd></div>` : ""}
                  ${profile.email ? `<div><dt>Email</dt><dd><a href="${escapeHtml(linkHref(profile.email, "email"))}">${escapeHtml(profile.email)}</a></dd></div>` : ""}
                  ${profile.phone ? `<div><dt>Phone</dt><dd><a href="${escapeHtml(linkHref(profile.phone, "phone"))}">${escapeHtml(profile.phone)}</a></dd></div>` : ""}
                  ${profile.portfolio ? `<div><dt>Portfolio</dt><dd><a href="${escapeHtml(profile.portfolio)}">${escapeHtml(profile.portfolio)}</a></dd></div>` : ""}
                </dl>
              </div>
            </aside>
          </div>
        </div>
      </section>
    `;
  }

  function renderSkills() {
    if (!sectionEnabled("skills") || !list(data.skills).length) return "";
    return `
      <section id="skills" class="section">
        <div class="section-inner">
          ${sectionHead("Skills", "Technical range")}
          <div class="skills-grid">
            ${list(data.skills).map((group) => `
              <article class="skill-group">
                <h3>${escapeHtml(group.name || "Skills")}</h3>
                <div class="chips">${list(group.items).map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("")}</div>
              </article>
            `).join("")}
          </div>
        </div>
      </section>
    `;
  }

  function renderExperience() {
    if (!sectionEnabled("experience") || !list(data.experience).length) return "";
    return `
      <section id="experience" class="section">
        <div class="section-inner">
          ${sectionHead("Experience", "Recent work")}
          <div class="timeline">
            ${list(data.experience).map((item) => `
              <article class="timeline-item">
                <div class="item-top">
                  <div>
                    <h3>${escapeHtml(item.title || "")}</h3>
                    <div class="muted">${escapeHtml([item.company, item.location].filter(Boolean).join(", "))}</div>
                  </div>
                  <div class="item-date">${escapeHtml(item.display_date || [item.start_date, item.end_date].filter(Boolean).join(" - "))}</div>
                </div>
                ${item.description ? `<p>${escapeHtml(item.description)}</p>` : ""}
                ${list(item.tasks).length ? `<ul>${list(item.tasks).map((task) => `<li>${escapeHtml(task)}</li>`).join("")}</ul>` : ""}
              </article>
            `).join("")}
          </div>
        </div>
      </section>
    `;
  }

  function renderMediaPreview(project) {
    const media = firstMedia(project);
    if (media?.type === "image") {
      return `<img src="${escapeHtml(media.src)}" alt="${escapeHtml(media.title || project.title)}" loading="lazy" />`;
    }
    if (media?.type === "video") {
      return `<video src="${escapeHtml(media.src)}" muted playsinline preload="metadata"></video>`;
    }
    return `<span class="media-placeholder">${escapeHtml(initials(project.title))}</span>`;
  }

  function renderProjects() {
    if (!sectionEnabled("projects") || !list(data.projects).length) return "";
    const visibleProjects = activeCategory === "All"
      ? list(data.projects)
      : list(data.projects).filter((project) => project.category === activeCategory);
    const filterMarkup = `
      <div class="filters" role="list">
        ${categories().map((category) => `<button class="filter-button ${category === activeCategory ? "active" : ""}" type="button" data-category="${escapeHtml(category)}">${escapeHtml(category)}</button>`).join("")}
      </div>
    `;
    return `
      <section id="projects" class="section">
        <div class="section-inner">
          ${sectionHead("Projects", "Media-ready project archive", filterMarkup)}
          <div class="projects-grid">
            ${visibleProjects.map((project) => `
              <article class="project-card">
                <button type="button" data-project="${escapeHtml(project.slug)}">
                  <div class="project-media">
                    ${renderMediaPreview(project)}
                    <span class="media-count">${list(project.media).length} media</span>
                  </div>
                  <div class="project-body">
                    <span class="project-category">${escapeHtml(project.category || "Project")}</span>
                    <h3>${escapeHtml(project.title || "Project")}</h3>
                    <p class="project-summary">${escapeHtml(project.summary || "")}</p>
                    <div class="chips">${list(project.technologies).slice(0, 4).map((tech) => `<span class="chip">${escapeHtml(tech)}</span>`).join("")}</div>
                  </div>
                </button>
              </article>
            `).join("")}
          </div>
        </div>
      </section>
    `;
  }

  function renderEducation() {
    if (!sectionEnabled("education") || !list(data.education).length) return "";
    return `
      <section id="education" class="section">
        <div class="section-inner">
          ${sectionHead("Education", "Academic background")}
          <div class="education-grid">
            ${list(data.education).map((item) => `
              <article class="education-item">
                <div class="item-top">
                  <div>
                    <h3>${escapeHtml([item.degree, item.field, item.branch].filter(Boolean).join(", "))}</h3>
                    <div class="muted">${escapeHtml([item.institution, item.location].filter(Boolean).join(", "))}</div>
                  </div>
                  <div class="item-date">${escapeHtml(item.display_date || [item.start_date, item.end_date].filter(Boolean).join(" - "))}</div>
                </div>
                ${item.thesis ? `<p>${escapeHtml(item.thesis)}</p>` : ""}
                <div class="chips">
                  ${item.final_grade ? `<span class="chip">Grade: ${escapeHtml(item.final_grade)}</span>` : ""}
                  ${item.eqf_level ? `<span class="chip">${escapeHtml(item.eqf_level)}</span>` : ""}
                </div>
              </article>
            `).join("")}
          </div>
        </div>
      </section>
    `;
  }

  function renderPublications() {
    if (!sectionEnabled("publications") || !list(data.publications).length) return "";
    return `
      <section id="publications" class="section">
        <div class="section-inner">
          ${sectionHead("Publications", "Research output")}
          <div class="publication-list">
            ${list(data.publications).map((item) => `
              <article class="publication-item">
                <div class="item-top">
                  <strong>${escapeHtml(item.title || "")}</strong>
                  <span class="item-date">${escapeHtml(item.year || "")}</span>
                </div>
                <div class="muted">${escapeHtml([item.authors, item.venue].filter(Boolean).join(" | "))}</div>
                ${item.paper || item.link ? `<a href="${escapeHtml(item.paper || item.link)}" rel="noopener noreferrer">Open paper</a>` : ""}
              </article>
            `).join("")}
          </div>
        </div>
      </section>
    `;
  }

  function renderContact() {
    if (!sectionEnabled("contact")) return "";
    return `
      <section id="contact" class="section">
        <div class="section-inner">
          ${sectionHead("Contact", "Work together")}
          <div class="contact-grid">
            <div class="contact-panel">
              <dl class="info-list">
                ${profile.email ? `<div><dt>Email</dt><dd><a href="${escapeHtml(linkHref(profile.email, "email"))}">${escapeHtml(profile.email)}</a></dd></div>` : ""}
                ${profile.phone ? `<div><dt>Phone</dt><dd><a href="${escapeHtml(linkHref(profile.phone, "phone"))}">${escapeHtml(profile.phone)}</a></dd></div>` : ""}
                ${list(profile.links).map((link) => `<div><dt>${escapeHtml(link.name)}</dt><dd><a href="${escapeHtml(link.url)}" rel="noopener noreferrer">${escapeHtml(link.url)}</a></dd></div>`).join("")}
              </dl>
            </div>
            <form class="contact-form" id="contact-form">
              <label class="field"><span>Name</span><input name="name" autocomplete="name" required maxlength="120" /></label>
              <label class="field"><span>Email</span><input name="email" type="email" autocomplete="email" required maxlength="180" /></label>
              <label class="field"><span>Subject</span><input name="subject" required maxlength="160" /></label>
              <label class="field"><span>Message</span><textarea name="message" required maxlength="4000"></textarea></label>
              <input class="hidden" name="website" autocomplete="off" tabindex="-1" />
              <button class="button-link primary" type="submit">Send Message</button>
              <div class="form-status" role="status"></div>
            </form>
          </div>
        </div>
      </section>
    `;
  }

  function renderModal() {
    return `
      <div class="modal" id="project-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="modal-dialog">
          <div class="viewer">
            <div class="viewer-stage" id="viewer-stage"></div>
            <div class="viewer-controls">
              <button class="icon-button" type="button" data-slide="prev" aria-label="Previous slide">&lt;</button>
              <div class="slide-title" id="slide-title"></div>
              <button class="icon-button" type="button" data-slide="next" aria-label="Next slide">&gt;</button>
            </div>
          </div>
          <aside class="modal-side">
            <div class="modal-head">
              <div>
                <div class="project-category" id="modal-category"></div>
                <h3 id="modal-title"></h3>
              </div>
              <button class="icon-button" type="button" data-close aria-label="Close">&times;</button>
            </div>
            <div class="modal-content">
              <p id="modal-summary"></p>
              <div class="chips" id="modal-tech"></div>
              <div class="thumbnail-strip" id="thumbnail-strip"></div>
            </div>
            <div class="modal-actions" id="modal-actions"></div>
          </aside>
        </div>
      </div>
    `;
  }

  function renderFooter() {
    return `
      <footer class="footer">
        <div class="footer-inner">
          <span>${escapeHtml(profile.displayName || "Davoud Nikkhouy")}</span>
          <span>${escapeHtml(site.domain || "davoudnikkhouy.com")}</span>
        </div>
      </footer>
    `;
  }

  function render() {
    document.documentElement.lang = site.language || "en";
    document.title = site.title || "Davoud Nikkhouy";
    app.innerHTML = `
      <div class="site-shell">
        ${renderNav()}
        ${renderHero()}
        ${renderAbout()}
        ${renderSkills()}
        ${renderExperience()}
        ${renderProjects()}
        ${renderEducation()}
        ${renderPublications()}
        ${renderContact()}
        ${renderFooter()}
        ${renderModal()}
      </div>
    `;
    bindEvents();
  }

  function bindEvents() {
    document.querySelectorAll("[data-category]").forEach((button) => {
      button.addEventListener("click", () => {
        activeCategory = button.dataset.category || "All";
        render();
        document.querySelector("#projects")?.scrollIntoView();
      });
    });
    document.querySelectorAll("[data-project]").forEach((button) => {
      button.addEventListener("click", () => {
        const project = list(data.projects).find((item) => item.slug === button.dataset.project);
        if (project) openProject(project);
      });
    });
    document.querySelector("[data-close]")?.addEventListener("click", closeProject);
    document.querySelector("#project-modal")?.addEventListener("click", (event) => {
      if (event.target.id === "project-modal") closeProject();
    });
    document.querySelector('[data-slide="prev"]')?.addEventListener("click", () => changeSlide(-1));
    document.querySelector('[data-slide="next"]')?.addEventListener("click", () => changeSlide(1));
    if (!keydownBound) {
      document.addEventListener("keydown", handleKeydown);
      keydownBound = true;
    }
    document.querySelector("#contact-form")?.addEventListener("submit", submitContact);
  }

  function handleKeydown(event) {
    const modal = document.querySelector("#project-modal");
    if (!modal?.classList.contains("open")) return;
    if (event.key === "Escape") closeProject();
    if (event.key === "ArrowLeft") changeSlide(-1);
    if (event.key === "ArrowRight") changeSlide(1);
  }

  function openProject(project) {
    activeProject = project;
    activeSlide = 0;
    document.querySelector("#project-modal")?.classList.add("open");
    updateModal();
  }

  function closeProject() {
    document.querySelector("#project-modal")?.classList.remove("open");
    activeProject = null;
  }

  function changeSlide(direction) {
    const media = list(activeProject?.media);
    if (!media.length) return;
    activeSlide = (activeSlide + direction + media.length) % media.length;
    updateModal();
  }

  function mediaMarkup(media) {
    if (!media) {
      return `<div class="empty">Project media will appear here when files are added to the project folder.</div>`;
    }
    if (media.type === "image") {
      return `<img src="${escapeHtml(media.src)}" alt="${escapeHtml(media.title || "Project media")}" />`;
    }
    if (media.type === "video") {
      return `<video src="${escapeHtml(media.src)}" controls playsinline preload="metadata"></video>`;
    }
    return `
      <div class="document-slide">
        <strong>${escapeHtml(media.title || "Document")}</strong>
        <a class="button-link primary" href="${escapeHtml(media.src)}">Open Document</a>
      </div>
    `;
  }

  function thumbMarkup(media, index) {
    const active = index === activeSlide ? "active" : "";
    if (media.type === "image") {
      return `<button class="thumb ${active}" type="button" data-thumb="${index}"><img src="${escapeHtml(media.src)}" alt="" loading="lazy" /></button>`;
    }
    if (media.type === "video") {
      return `<button class="thumb ${active}" type="button" data-thumb="${index}"><video src="${escapeHtml(media.src)}" muted preload="metadata"></video></button>`;
    }
    return `<button class="thumb ${active}" type="button" data-thumb="${index}"><span>PDF</span></button>`;
  }

  function updateModal() {
    if (!activeProject) return;
    const media = list(activeProject.media);
    const current = media[activeSlide];
    document.querySelector("#modal-title").textContent = activeProject.title || "Project";
    document.querySelector("#modal-category").textContent = activeProject.category || "";
    document.querySelector("#modal-summary").textContent = activeProject.summary || "";
    document.querySelector("#modal-tech").innerHTML = list(activeProject.technologies).map((tech) => `<span class="chip">${escapeHtml(tech)}</span>`).join("");
    document.querySelector("#viewer-stage").innerHTML = mediaMarkup(current);
    document.querySelector("#slide-title").textContent = current ? `${activeSlide + 1} / ${media.length} - ${current.title || current.type}` : "No media";
    document.querySelector("#thumbnail-strip").innerHTML = media.map(thumbMarkup).join("");
    document.querySelector("#modal-actions").innerHTML = list(activeProject.links)
      .map((link) => `<a class="button-link" href="${escapeHtml(link.url)}" rel="noopener noreferrer">${escapeHtml(link.name || "Link")}</a>`)
      .join("");
    document.querySelectorAll("[data-thumb]").forEach((button) => {
      button.addEventListener("click", () => {
        activeSlide = Number(button.dataset.thumb);
        updateModal();
      });
    });
  }

  async function submitContact(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const status = form.querySelector(".form-status");
    const button = form.querySelector("button");
    const payload = Object.fromEntries(new FormData(form).entries());
    status.textContent = "Sending...";
    button.disabled = true;
    try {
      const response = await fetch(site.contactApi || "/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.error || "Message failed.");
      status.textContent = result.message || "Message received.";
      form.reset();
    } catch (error) {
      status.textContent = error.message || "Message failed.";
    } finally {
      button.disabled = false;
    }
  }

  render();
})();
