---
title: Satisfactory Mods
years: 2026
order: 5
codeart: UFUNCTION()
tags: C++, Unreal Engine, Multiplayer networking, Algorithms, Reverse engineering
summary: More than a dozen C++ mods for the factory game Satisfactory, including signal-free train traffic control, demand-driven train dispatch and fixes for server networking bugs.
links: GitHub | https://github.com/benvrakas?tab=repositories
---
Satisfactory is built on Unreal Engine. Its mod loader (SML) exposes the game's C++ classes, so these mods are native C++ that hooks into game systems, replicates state to multiplayer clients, and adds UI and chat commands.

## Highlights

### Auto Trains: traffic without signals
Every self-driving train books the track and switches on its route as **time slots** around the other trains (space-time planning). It then speeds up, slows down, waits or reroutes so that no two trains ever need the same track at the same time. Trains follow each other through roundabouts, take the fastest route given everyone's bookings, and docked trains book their departures ahead from their timetables. Nothing is written into vanilla save data.

### SmartTrains: demand-driven dispatch
Platforms get a role (supply, demand or sink) and an item list. Managed trains are shared out across consumer stations in proportion to what each one needs, its consumption rate times its loop's round-trip time, and each train runs one loop: fill at the suppliers, unload at the consumer, repeat. Everything is opt-in alongside vanilla trains.

### Depot Network Fix: server stability
On busy servers, the Dimensional Depot's item-count updates overflowed the reliable network buffer and got players kicked. This server-only mod merges the updates and sends them about once a second, holding back while a client is behind.

### Telescreen and BoomBoxPlus: synced media
**Telescreen** adds billboard-sized in-game screens that play the same video for every player, in sync, with 3D audio. A helper process fetches and decodes the media. **BoomBoxPlus** (v1.6) plays your own music, YouTube, SoundCloud and internet radio through the in-game Boom Box, synced across multiplayer with lyrics.

## All mods

| Mod | What it does |
|---|---|
| [AutoTrains](https://github.com/benvrakas/AutoTrains) | Train traffic control without block or path signals |
| [SmartTrains](https://github.com/benvrakas/SmartTrains) | Trains dispatched from supply to demand without fixed timetables |
| [FreightCarControl](https://github.com/benvrakas/FreightCarControl) | Per-stop, per-car load/unload rules in train timetables |
| [VehicleSettingsCopy](https://github.com/benvrakas/VehicleSettingsCopy) | Copy and paste vehicle timetables and fuel settings |
| [DepotNetworkFix](https://github.com/benvrakas/DepotNetworkFix) | Fixes "reliable buffer overflow" kicks from busy depots |
| [ContinuousElevatorSync](https://github.com/benvrakas/ContinuousElevatorSync) | Keeps a server-side mechanic on factory time under load |
| [ModularStationsGantryFix](https://github.com/benvrakas/ModularStationsGantryFix) | Stopgap crash fix for a popular third-party mod |
| [Telescreen](https://github.com/benvrakas/Telescreen) | Synced video, browser and remote-desktop screens |
| [BoomBoxPlus](https://github.com/benvrakas/BoomBoxPlus) | Your own music through the Boom Box, synced in multiplayer |
| [AdaVoicePackLoader](https://github.com/benvrakas/AdaVoicePackLoader) | Loads replacement voice-line packs |
| [ExactFoundationSnap](https://github.com/benvrakas/ExactFoundationSnap) | Exact rotation when snapping to foundations |
| [BetterMovement](https://github.com/benvrakas/BetterMovement) | Configurable slope sliding |
| [ConveyorLiftAutoConnect](https://github.com/benvrakas/ConveyorLiftAutoConnect) | Auto-connects conveyor lifts between stacked blueprints |
