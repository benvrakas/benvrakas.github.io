---
title: 1000 W LED Gobo Projector
years: 2025 – 2026 · in progress
order: 2
areas: electrical, software, mechanical, fabrication
tags: KiCad (4-layer), SAMD51 / CAN, PMBus, Liquid cooling, Embedded C++, Power electronics
summary: A liquid-cooled 1000 W LED projector for gobo (patterned-light) projection, with my own controller board, firmware, optics housing and frame.
hero: fixture-3
links: Firmware & board repository | https://github.com/benvrakas/1000W-LED-Controller
---
Gobo projectors throw a patterned image, like a logo or texture, onto walls and floors. Commercial fixtures in this power class are expensive and closed. This one is built around a single **1000 W LED** with **liquid cooling**, a custom optics housing and a controller I designed from the PCB up.

:::video projection | Projection test

## System

- **Light engine:** a 1000 W LED on a liquid cold plate, cooled by a pump, reservoir and fans, behind a large lens and the gobo/lens assembly.
- **Power:** a Mean Well **UHP-1500-48** supply driven either by analog current control or digitally over **CAN/PMBus**, with slew-limited current setpoints.
- **Controller:** an Adafruit **Feather M4 CAN (SAMD51)** on my own **4-layer KiCad board**, with isolated interfaces, fan and pump drivers, tachometer and thermistor inputs, and an OLED, rotary encoder and power button for the UI.
- **Frame:** houses the PSU, cooling loop and electronics, with the head mounted on top.

:::gallery
led-cold-plate | LED on the liquid cold plate
led-mount | Printed LED mount and lens seat
psu | Mean Well UHP-1500 supply during bring-up
pump-reservoir | Pump and reservoir
frame-interior | Inside the frame: loop, wiring and fans
head-assembled | Early assembled head
:::

## Firmware {: theme=code }

PlatformIO / Arduino C++ structured like a small product rather than a sketch:

- **Finite state machine** (`INIT → RUN → ERROR_KILL`) driven from the main loop. `ERROR_KILL` latches and only clears on reset, or on a deliberate button hold that ignores just the faulted channel until the next power cycle.
- **Dependency injection:** a composition root builds every driver (tachometers, CAN and analog PSU backends, OLED, thermistors), and services receive only the hardware they need.
- **Services** for PSU control (setpoint, slew limiting, CAN-vs-analog routing), cooling (fan and pump duty curves on LED and water temperature), input and UI.
- **Fault monitoring** on LED temperature, water temperature, pump, every fan, PSU comms and the encoder, with blink codes on the status LED as a fallback display.
- Standalone bench firmwares for testing fans, tachometers and the PSU in isolation.

## Controller board

The controller went from a hand-wired perfboard prototype to a custom PCB, and was then revised into a 4-layer board.

:::gallery
perfboard-proto | Perfboard prototype: Feather, level shifters, connectors
perfboard-wiring | Hand-wired prototype, underside
schematic-v1 | First schematic
pcb-layout-v1 | First layout
pcb-3d-v1 | First board, 3D view
controller-proto | First PCB during bring-up
:::

:::gallery
schematic-v2 | Revised schematic
pcb-3d-v2 | Revised 4-layer board with the Feather M4 CAN
controller-installed | Installed in the frame with the OLED and encoder UI
controller-running | Running in the fixture
blower | Head blower
:::

## Optics and housing {: theme=lab }

:::gallery
cad-housing-1 | Lens housing in CAD
cad-housing-2 | Front view
cad-housing-section | Section through the housing and lens train
led-through-lens | LED seen through the condenser lens
lens-assembly | Lens assembly and blower
lens-head | Printed lens head with honeycomb snoot
:::

:::gallery
fixture | Complete fixture on its yoke
fixture-2 | Head and frame
beam-on | First light
:::

:::video projection-2 | Gobo projection

## In use

Projecting a text gobo across the side of a multi-story building at night.

:::gallery
projection-building | Building-scale projection
projection-building-close | Detail
:::
