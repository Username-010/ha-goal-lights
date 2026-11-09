# Goal Lights

Home Assistant integration that **flashes your lights** and **plays a goaltune** when your team scores, at kick-off, and at the start of the second half — then restores the previous colour.

Goaltune can be a **YouTube link** or a **local mp3/mp4** from the Home Assistant media browser.

Not soccer-only. Any sport works as long as you have a score sensor with:

- state `PRE` / `IN` / `POST` ([Team Tracker](https://github.com/vasqued2/ha-teamtracker) does this)
- attribute `team_score`
- optional `clock` / `quarter` (for second half)

## What you get

| Piece | Role |
| --- | --- |
| Flash | Alternates club colours on any RGB lights, then snapshot-restore |
| Goaltune | YouTube (Cast) **or** a file you uploaded to `/media` |
| Watch switch | Live goals only fire when Watch is on. Test buttons always work |
| Test buttons | Goal / kick-off / 2nd half on the device and on the card |
| Card | Score, live badge, watch toggle, one-tap tests |

One config entry per team. Feyenoord + Oranje + Srbija = three entries.

## Install (HACS)

1. Install **Team Tracker** from HACS (optional **Team Tracker Card**).
2. HACS → Integrations → ⋮ → Custom repositories → add `https://github.com/Username-010/ha-goal-lights` as **Integration**.
3. Download **Goal Lights**, restart Home Assistant.
4. Settings → Devices & services → Add **Goal Lights**.
5. Paste a YouTube URL *or* pick a local file. Pick the TV/speaker.

Card:

```yaml
type: custom:goal-lights-card
tracker: sensor.man_cave_feyenoord
team: feyenoord
watch: switch.goal_lights_watch
outline_color: "#c8102e"
```

Resource (if the card is missing): `/goal_lights/goal-lights-card.js` as a **JavaScript module**.

## Services

- `goal_lights.celebrate` — flash + goaltune, honours Watch (`team: feyenoord`)
- `goal_lights.test` — always runs (dashboard test knobs)
- `goal_lights.flash` — same as test/goal

An external poller (FotMob etc.) can `POST /api/services/goal_lights/celebrate` with `{"team": "feyenoord"}`. Turn **Listen to Team Tracker** off in that case so you don’t double-fire.

## Local files

1. HA → Media → upload `feyenoord.mp3` (or mp4)
2. In the Goal Lights options, pick that file under **local media**
3. Leave YouTube empty if you only want the file. If both are set, YouTube wins.

## Notes

- RGBIC “half and half” from the Tuya app is not exposed in Home Assistant. The whole light flashes between colours.
- Unavailable lights are skipped.
- Cloud lights are a bit laggy; ~0.35s between flips is the default.

## License

MIT
