---
title: Modular Smart Light Panels
years: 2026 · in progress
order: 1
tags: KiCad, PCB design, CAN bus, ESP32, Mechanical design, System architecture
summary: Edge-lit hexagon, square and triangle panels that snap together in any layout, work out their own arrangement, and play effects mapped to the room rather than along a strip.
hero: room-evening
links: Repository | https://github.com/benvrakas/modular-smart-light-panels
---
Commercial light panels make you enter the layout by hand and treat the wall as a 2D strip. This system aims at **100+ panels across several rooms** (walls, ceilings, lofts) with two defining features:

1. **Self-configuring.** Panels snap together in any arrangement. The system discovers the full topology (which panel touches which, through which edge) and each panel's orientation, with no manual setup.
2. **Room-scale 3D effects.** Animations live in room coordinates, a sparse 3D voxel space, so effects flow continuously across walls and ceilings.

:::video effects-closeup | Rendered effect playback on a mixed cluster

## Architecture

- **Edge-lit optics.** Inward-facing RGBW LEDs on the perimeter boards light a shallow air gap with a white back reflector and a thin diffuser film. All shapes share a ≈100 mm edge, so triangles, squares and hexagons tile together. A hexagon fits on a common 220–256 mm print bed.
- **Passive edge boards.** Each side of a polygon is an identical straight PCB carrying LEDs, an ID resistor that encodes its position, and ten plated contacts. Board length per shape follows from the corner angle and a fixed seam inset.
- **One controller per panel.** A small 4-layer board (MCU, CAN transceiver, 24→5 V converter, LED rail switch, protection) sits behind the light chamber. One design serves every shape.
- **Spring-contact bridges.** A thin double-sided bridge PCB stands in the seam between panels, and low-cost SMT springs press on both panels' contacts. A printed clip snaps across the back of the seam with zero play.
- **Network.** Panels on one surface share a CAN segment owned by a snap-on ESP32 cluster controller, which bridges to Wi-Fi. A coordinator holds the room layout and runs the voxel engine.

:::gallery
exploded-hex | Exploded hexagon: diffuser, frame, edge boards and back plate
cad-assembly | Mixed cluster in CAD
seam-section | Section through a seam: bridge PCB and spring contacts
:::

## Boards

:::gallery
pcb-controller | Per-panel controller board
pcb-edge | Hexagon edge board: LEDs, ID circuit and seam contacts
pcb-spring-coupon | Test coupon for qualifying the spring contacts
pcb-controller-layout | Controller board layout
:::

## Effects in the room

Every image below is rendered from the design files, with effects placed in room coordinates.

:::gallery
fx-aurora | Aurora
fx-sunset | Sunset
fx-ocean | Ocean
fx-fire | Fire
max-night | Maximum brightness, night
vertical-corner | Wrapping an outside corner
:::

## Status

The design is specified in detail. Every choice is recorded as a numbered decision record, and figures are generated straight from the design files. Work is now heading toward the first physical prototype. Sister projects: **Smart Light Strips** (24 V RGBW strips with a custom ESP32-S3 controller) and **Voxlume**, which maps every LED into 3D room coordinates.
