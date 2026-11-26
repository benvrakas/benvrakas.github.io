---
title: UWRF Lunabotics Rover
years: 2020 – 2021
order: 8
areas: mechanical, electrical, printing
tags: Autodesk Inventor, BLDC / ODrive, Gearbox design, Mechanisms, Team founder
summary: A NASA moon-mining rover that my roommate and I started at UW–River Falls. I did the mechanical design: closed-loop hub-motor wheels, a deployable wheelbase and a bucket-chain excavator.
hero: bench
---
Lunabotics is NASA's competition for lunar mining robots. My roommate and I started a team at the University of Wisconsin–River Falls. COVID cancelled the in-person event, but we presented the robot to the judges over video. I led the mechanical design. *(I'm now in the early stages of a new Lunabotics team for 2027.)*

:::youtube oquR6lneSxE | Lunabotics 1
:::youtube 8W6bg1KmnDA | Lunabotics 3

:::gallery
render-rov | Front view in Inventor: excavator between the wheel modules
render-rov-2 | Full rover in Inventor
assembled | Built rover
:::

## Drive

Each wheel is **direct-drive**: a **900 W brushless gimbal motor** with a **600 PPR rotary encoder**, both wired to an **ODrive** for closed-loop control. My first wheel used a double leaf spring between rim and hub, but it (and its single-extrusion mount) didn't hold up. I switched to rigid wheels with a hexagonal pattern in place of spokes.

To get around the size limits, I designed a **wheel deployment system** that gives the rover a wider wheelbase than competitors once it's on the field. A servo on each wheel releases a four-bar linkage, which a 40 lb constant-force gas spring then drives out.

:::gallery
render-suspension | Wheel module with hex-pattern wheel
frame-wheels | Frame with all four wheel modules
drive-test | First drive test
:::

## Excavator

The digger is a **bucket-chain excavator** driven by a **4 kW BLDC motor** through reduction belts. The excavator pivots on a geared joint to set its dig angle, and the bucket lift rides a slide on 700 mm MGN12 linear rails, moved by two T8 lead screws. Both the dig angle and the slide lead screws are driven by **DC motors with encoders** through a scalable **two-stage planetary gearbox** I designed, which worked on the first try. The printed buckets have metal cutting edges and attach to roller chain at regular intervals. Spoil goes into a dump bin with its own sprocket drive, and the electronics plate carries the ODrives, a Jetson NX and the LiPo pack.

:::gallery
render-digger | Excavator assembly
gearbox | Planetary gearbox prototype
digger-chain | Bucket chain installed
bench | Integration on the bench
:::

:::youtube ElQYHP2dhhU | 3D-printed two-stage planetary reduction
