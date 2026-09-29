"""Build get.bambuddy.cool from the main-site pages.

The appliance is sold through Paddle, whose domain review wants a site about the
product it sells and nothing else. So the subdomain gets its own copy of the
appliance page and the legal pages, with a header and footer that carry only the
appliance, and every other link pointing back to bambuddy.cool.

Run after editing appliance.html, privacy-policy.html or legal-notice.html:

    python3 tools/build_appliance_site.py

The terms and refund pages are generated into appliance/ by
bambuddy-appliance/docs/legal/build_terms_pages.py and build_refund_page.py,
which use appliance/legal-notice.html as their template -- so run this first.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "appliance")
MAIN = "https://bambuddy.cool"
SUB = "https://get.bambuddy.cool"

# source page on the main site -> page on the subdomain
PAGES = {
    "appliance.html": "index.html",
    "privacy-policy.html": "privacy-policy.html",
    "legal-notice.html": "legal-notice.html",
}

# Pages that exist on the subdomain, so relative links to them stay relative.
LOCAL = {"privacy-policy.html", "legal-notice.html", "terms.html", "terms-de.html", "refund-policy.html"}

HEADER = """<header class="nav">
    <div class="shell nav-inner">
      <a href="/" class="nav-logo" aria-label="Bambuddy Appliance home">
        <img src="assets/img/logo_transparent.png" alt="Bambuddy">
      </a>

      <nav class="nav-links" id="nav-links">
        <a href="/#hardware" class="nav-link">Hardware</a>
        <a href="/#guide" class="nav-link">Setup</a>
        <a href="/#pricing" class="nav-link">Pricing</a>
        <a href="/#support" class="nav-link">Support</a>
        <a href="/#telemetry" class="nav-link">What it sends</a>

        <span class="nav-sep" aria-hidden="true"></span>

        <a href="https://bambuddy.cool/" class="nav-pill">Bambuddy</a>
      </nav>

      <div class="nav-actions">
        <a href="/#buy" class="btn btn-primary">Get notified</a>
        <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false" aria-controls="nav-links">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" aria-hidden="true">
            <line x1="3" y1="7" x2="21" y2="7"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="17" x2="21" y2="17"/>
          </svg>
        </button>
      </div>
    </div>
  </header>"""

FOOTER = """<footer class="footer">
    <div class="shell">
      <div class="footer-grid">
        <div class="footer-brand">
          <a href="/" aria-label="Bambuddy Appliance home">
            <img src="assets/img/logo_transparent.png" alt="Bambuddy">
          </a>
          <p>The Bambuddy Appliance: a Raspberry Pi 5 image you flash yourself, with updates that undo themselves.</p>
        </div>

        <div class="footer-col">
          <h4>Appliance</h4>
          <a href="/#hardware">Hardware</a>
          <a href="/#guide">Setup</a>
          <a href="/#pricing">Pricing</a>
          <a href="/#support">Support</a>
          <a href="assets/downloads/bambuddy-appliance-quickstart.pdf">Quickstart (PDF)</a>
        </div>
        <div class="footer-col">
          <h4>Bambuddy</h4>
          <a href="https://bambuddy.cool/">bambuddy.cool</a>
          <a href="https://bambuddy.cool/installation.html">Install it yourself, free</a>
          <a href="http://wiki.bambuddy.cool" target="_blank" rel="noopener">Documentation</a>
          <a href="https://github.com/maziggy/bambuddy" target="_blank" rel="noopener">GitHub</a>
        </div>
        <div class="footer-col">
          <h4>Contact</h4>
          <a href="mailto:support@bambuddy.cool">support@bambuddy.cool</a>
          <a href="/#buy">Questions before buying</a>
        </div>
      </div>

      <div class="footer-bottom">
        <p>
          Sold through our online reseller Paddle.com, the Merchant of Record for all our orders.<br>
          &copy; 2026 Martin Ziegler. Bambuddy is released under the AGPL-3.0 License. Not affiliated with Bambu Lab.
        </p>
        <div class="footer-legal">
          <a href="legal-notice.html">Legal notice</a>
          <a href="privacy-policy.html">Privacy policy</a>
          <a href="terms.html">Terms</a>
          <a href="refund-policy.html">Refund policy</a>
        </div>
      </div>
    </div>
  </footer>"""


def rewrite_link(match: re.Match) -> str:
    attr, target = match.group(1), match.group(2)
    page, _, anchor = target.partition("#")
    anchor = f"#{anchor}" if anchor else ""
    if page == "appliance.html":
        return f'{attr}="/{anchor}"'
    if page == "index.html":
        return f'{attr}="{MAIN}/{anchor}"'
    if page in LOCAL:
        return match.group(0)
    return f'{attr}="{MAIN}/{page}{anchor}"'


def build(source: str, target: str) -> None:
    html = open(os.path.join(ROOT, source)).read()

    head_end = html.index("<header")
    header_end = html.index("</header>") + len("</header>")
    footer_start = html.index('<footer class="footer">')
    footer_end = html.index("</footer>") + len("</footer>")

    head = html[:head_end]
    main = html[header_end:footer_start]
    tail = html[footer_end:]

    sub_url = f"{SUB}/" if target == "index.html" else f"{SUB}/{target}"
    head = head.replace(f"{MAIN}/{source}", sub_url).replace(f"{SUB}/appliance.html", sub_url)

    main = re.sub(r'(href)="((?!https?:|mailto:|#|/|assets/|css/|js/|img/|fonts/)[\w-]+\.html(?:#[\w-]*)?)"', rewrite_link, main)
    main = main.replace(f"{SUB}/terms.html", "terms.html").replace(f"{SUB}/refund-policy.html", "refund-policy.html")

    open(os.path.join(OUT, target), "w").write(head + HEADER + main + FOOTER + tail)


def main() -> None:
    for source, target in PAGES.items():
        build(source, target)
    print(f"built {len(PAGES)} pages into {OUT}")


if __name__ == "__main__":
    main()
