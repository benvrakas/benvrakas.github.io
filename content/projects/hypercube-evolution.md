---
title: HyperCube Evolution Printer
years: 2017 – 2019
order: 8
tags: CoreXY, RepRapFirmware, Duet, Printhead design, Open source
summary: A CoreXY 3D printer I built and reworked, with my first RepRapFirmware setup and a balanced direct-drive printhead I designed and published.
hero: rebuild-2019
links: Printhead files (Thingiverse) | https://www.thingiverse.com/thing:5377398
---
The HyperCube Evolution (HEVO) is the open-source successor to the HyperCube: a CoreXY belt system built around metric T-slot extrusion.

The recommended controller was a RAMPS board with cheap, loud stepper drivers. I used a **Duet WiFi running RepRapFirmware** instead. That was my first RRF machine, in 2017, and RRF has run my printers ever since, up to the [V-Labs Ender 3](v-labs-ender-3.html).

:::gallery
build-2018 | First build
duet-wiring | Duet WiFi electronics
rebuild-2019 | 2019 rebuild
:::

## Balanced direct-drive printhead

The stock HEVO uses a Bowden extruder. The direct-drive heads I found online all hung the motor off one side, so they twisted the carriage. My design puts the stepper on the opposite side from everything else so the head is balanced. The motor shaft passes straight through the block.

- Runs on 8 mm steel or 10 mm carbon fiber rods
- Wedges hold the eccentric bushings, with adjustable interference to remove play
- Integrated part cooling and belt tensioning

I also added a custom electronics enclosure, cable chains and a filament sensor.

:::gallery
printhead-1 | Balanced printhead on carbon rods
printhead-3 | Motor opposite the hotend
printhead-7 | Section through the carriage
printhead-5 | Belt clamps on the carriage
printhead-9 | Top view
printhead-real | Printed and assembled
:::
