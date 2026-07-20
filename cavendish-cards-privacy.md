# Privacy & security

Cavendish Cards is built to be a safe, quiet place. It gathers nothing about you, sends nothing anywhere, and keeps no accounts. This page says exactly what that means, in plain terms.

## The short version

- No accounts, no sign-in, no analytics, no tracking, no advertising, no cookies.
- Nothing you do here is sent to us or to anyone else. There is no server collecting spreads, clicks, or card choices.
- The only things kept are kept on your own device, for your own benefit, and you can clear them at any time.

## What "nothing stored" means

When we say the deck stores nothing, we mean nothing about you or a person. A spread you lay lives only in the page while it is open. Close the tab and it is gone. No spread, no card choice, and no reflection is ever recorded or transmitted. The deck makes needs sayable in the moment; it never turns them into data.

## What is kept on your device

Two things may be saved locally in your own browser. Both stay on your device, are never sent anywhere, and are yours to clear.

- **A theme preference.** If you use the light/dark toggle, your choice is saved so the site remembers it next time. Until you touch the toggle, the site simply follows your device's own light or dark setting and saves nothing.
- **An offline copy of the site.** So the deck keeps working without a connection, your browser holds a copy of the site's own files — pages, styles, card art, and fonts. This is the site caching itself for you, not a record of anything you did.

To remove both, clear this site's data in your browser (often listed as "clear site data" for cavendish.app).

## No third parties

The site loads only its own files. Fonts are served from cavendish.app, not from a font network. There are no third-party scripts, no embedded trackers, no external images, and no content delivery networks watching requests. Nothing on the page reaches out to another company.

## How the site is protected

The site is served only over an encrypted connection (HTTPS), and ships a set of rules that tell your browser to lock it down:

- **A strict content security policy.** The browser is told to load scripts, styles, fonts, images, and data only from cavendish.app. Inline scripts are refused unless they match a known fingerprint, which blocks injected or third-party code.
- **No embedding by strangers.** Other websites cannot frame the deck, apart from Stimpunks' own site. This guards against clickjacking.
- **Locked-down device access.** The page asks for no camera, microphone, or location, and the browser is told to deny them outright.
- **Careful content handling.** The browser is told not to second-guess file types, and to share only the minimum information about where you came from when you follow a link away.

The exact rules are public in the repository, in the `netlify.toml` file — you never have to take our word for it.

## Open to inspection

Nothing here is hidden. The whole site — every line of code, this policy, and the security rules themselves — is public and dedicated to the public domain under CC0. You can read it, run it yourself, or check any claim on this page against the source: [github.com/Stimpunks/Cavendish-Cards](https://github.com/Stimpunks/Cavendish-Cards).

## Questions

Cavendish Cards is a project of the [Stimpunks Foundation](https://stimpunks.org/). If anything here is unclear, or you would like something changed, the repository above is the place to reach us.
