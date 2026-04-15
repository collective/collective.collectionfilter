# collective.collectionfilter — Developer Guide


## Package manager

This project uses [pnpm](https://pnpm.io/) as its package manager, managed via [Corepack](https://nodejs.org/api/corepack.html).
The exact version is pinned in `package.json` under `"packageManager"`.

Enable Corepack once (ships with Node.js >= 16):

```sh
corepack enable
```

After that, running `pnpm` will automatically use the pinned version — no manual pnpm installation required.


## Installation

Install all dependencies:

```sh
pnpm install
```

pnpm stores packages in a global content-addressable store and uses hard links, which makes subsequent installs very fast.


## Updating dependencies

To update all dependencies within the version ranges defined in `package.json`:

```sh
pnpm update
```

To interactively choose which packages to update (including major versions):

```sh
pnpm update --interactive --latest
```

After updating, commit the changed `pnpm-lock.yaml` together with `package.json`.


## Building the bundle

The build produces JavaScript bundles (via webpack) and CSS (via Sass + clean-css).

**Full production build:**

```sh
pnpm build
```

This runs both steps in sequence:

1. **JavaScript** — webpack in production mode (minified, optimised):
   ```sh
   pnpm build:webpack
   ```

2. **CSS** — compile SCSS to expanded CSS, then minify:
   ```sh
   pnpm build:css
   ```

**Watch modes for development:**

| Command | What it does |
|---|---|
| `pnpm watch:webpack` | Rebuilds JS on file changes |
| `pnpm watch:scss` | Rebuilds CSS on SCSS changes |
| `pnpm start` | Starts the webpack dev server |

Output files are written to `src/collective/collectionfilter/static/`.
Always commit the compiled static files together with their source changes.


## Commit and pull request workflow

This project follows the [conventional commits](https://www.conventionalcommits.org/) specification.

**Commit message format:**

```
<type>(<scope>): <short summary>

[optional body]

[optional footer]
```

Common types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

**Typical workflow:**

1. Fork the repository on GitHub and create a feature branch:
   ```sh
   git checkout -b feat/my-feature
   ```

2. Make your changes. If JS or SCSS is touched, rebuild the bundle:
   ```sh
   pnpm build
   ```

3. Run the tests before committing:
   ```sh
   tox
   ```

4. Commit with a descriptive message:
   ```sh
   git commit -m "feat: add support for multi-select filters"
   ```

5. Push the branch and open a pull request against `main` on GitHub:
   ```sh
   git push origin feat/my-feature
   ```

6. In the PR description, briefly explain *what* changed and *why*.
   Reference related issues with `Closes #<issue-number>` where applicable.
