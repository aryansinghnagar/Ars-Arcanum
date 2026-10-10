# UI Visual Presets & Procedural Typewriter Sound Studio

## Overview
The **Ars Arcanum UI Theme & Procedural Sound Studio** (`arcanum theme-studio`) delivers a 100% offline, zero-asset atmospheric aesthetic and acoustic drafting environment.

## 1. 11 Atmospheric Visual Presets
The studio defines comprehensive CSS variable token sets across 11 distinct aesthetic palettes:
- `sovereign-dark`: Obsidian void, celestial cyan, and sovereign purple default.
- `classic-light`: Clean publishing manuscript, slate typography on crisp ivory.
- `retro`: 1980s phosphor terminal, warm amber glow, and vintage monospace.
- `futuristic`: High-altitude starship cockpit, electric neon cyan, and dark void.
- `retrofuturistic`: 1980s Outrun aesthetic, hot neon magenta, cyan grid, and deep violet.
- `fantastical`: Arcane illuminated manuscript, burnished gold, amethyst, and parchment.
- `grim`: Weathered ash, desaturated iron, and dried crimson grimdark tone.
- `edgy`: High-contrast pitch black, radioactive acid green, and razor crimson.
- `cozy`: Autumnal terracotta, warm hazelnut wood, matcha green, and cream.
- `scifi`: Deep cobalt orbital vessel instrumentation and starlight white.
- `horror`: Abyssal necrotic void, bruised violet, and eerie spectral green.

## 2. 10 Multi-Generation Typewriter Acoustic Models
All typewriter and keyboard sounds are synthesized mathematically on the fly in pure JavaScript via the Web Audio API without reading external audio files:
1. `remington_1890`: Heavy cast-iron carriage impact, deep mechanical body, antique brass resonance.
2. `royal_1930`: Classic mechanical typewriter slug hit, snappy metal clack, distinct release.
3. `selectric_1960`: Electric typeball solenoid snap, motor hum pulse, rapid corporate keystroke.
4. `smith_corona_1980`: Electronic portable typewriter daisywheel strike, high-speed plastic snap.
5. `cherry_blue`: Tactile clicky mechanical keyboard, crisp leaf pop, light bottom-out thud.
6. `thock`: Lubed linear switches on brass plate, deep bass acoustic pop, muffled bottom-out.
7. `cyber_terminal`: Retro-futuristic terminal reed relay, electronic frequency chirp, laser precision.
8. `steampunk`: Brass clockwork escapement tick, miniature steam hiss, precision gear click.
9. `scribe_quill`: Parchment surface friction scratch, ink flow stroke, delicate nib tap.
10. `gothic_relic`: Stone tablet impact, heavy chisel thud, flint resonance ping.

## 3. Mathematical & Acoustic Foundations
$$\Delta f = f_0 \cdot (1 + \epsilon), \quad \epsilon \sim \mathcal{U}(-0.04, +0.04)$$
$$\text{Gain } G = G_0 \cdot (1 + \delta), \quad \delta \sim \mathcal{U}(-0.10, +0.10)$$

Special physical keys:
- **Spacebar**: Low-frequency resonant wooden/chassis body thud ($\sim 115\text{ Hz} \to 45\text{ Hz}$).
- **Enter**: Carriage return slide friction + dual harmonic brass bell chime ($1760\text{ Hz} + 3520\text{ Hz}$).
- **Backspace**: Double-click escapement ratchet clack ($2400\text{ Hz}$).

## 4. Content Security Policy Guarantee
Every generated report and visualizer studio enforces strict air-gapped isolation:
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
```

## 5. Usage & CLI Dispatch
```bash
# Launch interactive standalone Theme Studio in browser
arcanum theme-studio --open

# Export standalone HTML studio
arcanum theme-studio --html dist/theme_studio.html

# Set initial visual preset and sound model
arcanum theme-studio -p retro -s remington_1890

# CLI configuration subcommands
arcanum config theme retro
arcanum config sound-preset royal_1930
arcanum config crt-fx enable
```
