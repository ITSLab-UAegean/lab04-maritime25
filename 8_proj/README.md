# Project 8: Formation Keeping

**Learning Objectives**:
- Upgrade naive follow-the-leader into station keeping: each vessel holds its own place in a formation instead of piling onto the scout
- Compute a GPS target from a distance and a compass bearing (converting meters to degrees)
- Tune fleet behaviour from configuration (`.env`) instead of hardcoded values

## What changed since Project 7

In Project 7 every follower aims at the scout's own position, so the fleet ends up stacked on top of the scout. Project 8 fixes that with three small changes:

**1. Formation stations** (`vessel_controller.py`). Each vessel now aims for its own station: a point `FORMATION_DISTANCE` meters away from the scout, at an angle measured relative to the scout's heading:

```python
FORMATION_ANGLES = {
    'VESSEL1': -135,   # port quarter (behind, to the left)
    'VESSEL2': 135,    # starboard quarter (behind, to the right)
    'VESSEL3': 180,    # directly astern
}
```

Because the angles are relative to the heading, the stations rotate with the scout; the formation stays "behind" it whichever way it turns. The new `offset_position()` helper turns "30 m at bearing X" into a latitude and longitude using a flat-earth approximation (one degree of latitude is about 111320 m), which is accurate to centimeters at these distances:

```python
def offset_position(self, lat, lon, bearing_deg, distance_m):
    bearing = radians(bearing_deg)
    dlat = distance_m * cos(bearing) / 111320
    dlon = distance_m * sin(bearing) / (111320 * cos(radians(lat)))
    return lat + dlat, lon + dlon
```

The scout's heading is already in every telemetry message, so `vessel.py` just passes it through to `follow_scout()`.

**2. Configurable telemetry rate** (`scout.py`, `vessel.py`). The hardcoded 5-second sleep is replaced by `TELEMETRY_INTERVAL` from `.env` (set to 1 s). Followers react to scout movement much sooner, and the safety check below runs on every scout update, so its blind window shrinks too.

**3. Wider keep-out**. `SAFE_FOLLOW_DISTANCE` is raised to 15 m in `.env`. With stations 30 m out, the keep-out no longer triggers during normal following; it is purely a collision guard for when the scout drives toward a follower. Keep it below `FORMATION_DISTANCE`, otherwise vessels would loiter before ever reaching their stations.

Everything else (commands, topics, arming, mode switching, goto throttling) is unchanged from Project 7.

## Running the Code

Same SITL fleet and ports as Project 7: every boat launches with two `--out` flags, the ground-station copy on 14550 and its own Python port (scout 14551, vessel1 14561, vessel2 14571, vessel3 14581).

```bash
python scout.py            # terminal 1
python vessel.py vessel1   # terminal 2
python vessel.py vessel2   # terminal 3
python vessel.py vessel3   # optional, terminal 4
```

Commands are the same per-vessel topics as Project 7, for example:

```bash
mosquitto_pub -h <broker> -p 1883 -u team1 -P team1 \
  -t 'team1/yoursurname/vessel1/commands' -m '{"command": "follow"}' -q 1
```

## What You Will Observe

- On `follow`, each vessel drives to its own station near the scout instead of crowding it: vessel1 behind-left, vessel2 behind-right, vessel3 directly astern, each about `FORMATION_DISTANCE` meters out.
- When the scout moves, the whole formation follows and re-forms behind it, whatever direction it heads.
- During a turn the stations sweep around the scout and the followers cut the corner, then settle back into place. This is expected: they chase station points, they do not trace arcs.
- When the scout stops, the stations freeze with it (the `scout_has_moved` gate suppresses new gotos), so the formation parks around the scout.
- "Too close to scout" loitering now appears only if the scout drives at a follower.
