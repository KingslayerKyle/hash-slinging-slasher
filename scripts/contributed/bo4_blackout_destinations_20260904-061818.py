#!/usr/bin/env python3
"""Targeted Blackout destinations sound asset generator for BO4.

Generates candidates for the 44 specific blk\\ directories discovered in bo4_snd_dirs:
  - wz_escape spawn horn
  - asylum (amb_spooky_2d, bathroom, water/pipe, whispers)
  - docks (amb/buoy)
  - estates basketball (bounces generic/soft, entity_impact, victim_impact)
  - hydro fans
  - nuketown raven_flap
  - dest_door zmb_hits
  - box electrical/sparks
  - doors, gates, elevator, coolers, stashes, perks/paranoia
"""
import sys

TAILS = [
    ".ln100.pc.snd", ".ll100.pc.snd", ".sn100.pc.snd", ".sl100.pc.snd"
]

def generate():
    seen = set()
    def emit(s):
        if s not in seen:
            seen.add(s)
            print(s)

    # 1. wz_escape spawn_horn
    d = "blk\\maps\\wz_escape\\spawn_horn"
    for base in ["spawn_horn", "horn", "wz_escape_spawn_horn", "escape_spawn_horn", "horn_lp", "spawn_horn_start", "spawn_horn_stop"]:
        for t in TAILS:
            emit(f"{d}\\{base}{t}")
        for i in range(10):
            for t in TAILS:
                emit(f"{d}\\{base}_{i:02d}{t}")
                emit(f"{d}\\{base}_{i}{t}")

    # 2. asylum
    asy = "blk\\maps\\wz_open_skyscrapers\\destinations\\asylum"
    # amb_spooky_2d
    for i in range(25):
        for base in ["amb_spooky_2d", "spooky_2d", "amb_spooky"]:
            for t in TAILS:
                emit(f"{asy}\\amb_spooky_2d\\{base}_{i:02d}{t}")
                emit(f"{asy}\\amb_spooky_2d\\{base}_{i}{t}")

    # bathroom
    for i in range(15):
        for base in ["bathroom", "amb_bathroom", "drip", "water_drip", "toilet", "sink", "pipes"]:
            for t in TAILS:
                emit(f"{asy}\\bathroom\\{base}_{i:02d}{t}")
                emit(f"{asy}\\bathroom\\{base}{t}")

    # water/pipe
    for i in range(15):
        for base in ["water_pipe", "pipe", "pipe_drip", "water_drip", "drip", "leak", "pipe_leak", "water_flow", "pipe_flow", "water_stream"]:
            for t in TAILS:
                emit(f"{asy}\\water\\pipe\\{base}_{i:02d}{t}")
                emit(f"{asy}\\water\\pipe\\{base}{t}")
                emit(f"{asy}\\water\\{base}_{i:02d}{t}")

    # whispers
    for i in range(25):
        for base in ["whispers", "whisper", "amb_whispers", "amb_whisper", "ghost_whisper", "ghost"]:
            for t in TAILS:
                emit(f"{asy}\\whispers\\{base}_{i:02d}{t}")
                emit(f"{asy}\\whispers\\{base}_{i}{t}")

    # 3. docks amb/buoy
    docks_buoy = "blk\\maps\\wz_open_skyscrapers\\destinations\\docks\\amb\\buoy"
    for i in range(15):
        for base in ["buoy", "amb_buoy", "buoy_bell", "bell", "buoy_horn", "horn", "buoy_ring", "chime"]:
            for t in TAILS:
                emit(f"{docks_buoy}\\{base}_{i:02d}{t}")
                emit(f"{docks_buoy}\\{base}_{i}{t}")
                emit(f"{docks_buoy}\\{base}{t}")
                emit(f"blk\\maps\\wz_open_skyscrapers\\destinations\\docks\\amb\\{base}_{i:02d}{t}")

    # 4. estates basketball
    est = "blk\\maps\\wz_open_skyscrapers\\destinations\\estates\\basketball"
    for sub, bases in [
        ("bounces\\generic", ["bounce", "basketball_bounce", "bounce_gen", "ball_bounce"]),
        ("bounces\\soft", ["bounce_soft", "bounce", "basketball_bounce_soft", "soft_bounce", "ball_bounce_soft"]),
        ("entity_impact", ["entity_impact", "impact", "basketball_impact", "entity_hit", "ball_impact"]),
        ("victim_impact", ["victim_impact", "impact", "basketball_victim_impact", "victim_hit", "ball_hit"]),
    ]:
        for b in bases:
            for i in range(15):
                for t in TAILS:
                    emit(f"{est}\\{sub}\\{b}_{i:02d}{t}")
                    emit(f"{est}\\{sub}\\{b}_{i}{t}")
                    emit(f"{est}\\{sub}\\{b}{t}")

    # 5. hydro fans
    hydro = "blk\\maps\\wz_open_skyscrapers\\destinations\\hydro\\fans"
    for base in ["fan", "fans", "fan_loop", "fans_loop", "fan_lp", "fans_lp", "fan_large", "fan_med", "fan_sml", "hydro_fan_lp", "hydro_fan"]:
        for t in TAILS:
            emit(f"{hydro}\\{base}{t}")
        for i in range(10):
            for t in TAILS:
                emit(f"{hydro}\\{base}_{i:02d}{t}")

    # 6. nuketown raven_flap
    nuke = "blk\\maps\\wz_open_skyscrapers\\destinations\\nuketown\\raven_flap"
    for base in ["raven_flap", "flap", "raven", "raven_wings", "wing_flap", "bird_flap"]:
        for i in range(15):
            for t in TAILS:
                emit(f"{nuke}\\{base}_{i:02d}{t}")
                emit(f"{nuke}\\{base}_{i}{t}")
                emit(f"{nuke}\\{base}{t}")

    # 7. dest_door zmb_hits
    door = "blk\\dest_door\\zmb_hits"
    for base in ["zmb_hits", "zmb_hit", "door_hit", "zmb_door_hit", "hit", "slam", "wood_hit", "metal_hit"]:
        for i in range(15):
            for t in TAILS:
                emit(f"{door}\\{base}_{i:02d}{t}")
                emit(f"{door}\\{base}_{i}{t}")

    # 8. box electrical & sparks
    for sub, bases in [
        ("box\\electrical", ["electrical", "electric", "box_electrical", "hum", "buzz", "current"]),
        ("box\\sparks", ["sparks", "spark", "box_sparks", "zap", "short"]),
    ]:
        for b in bases:
            for i in range(15):
                for t in TAILS:
                    emit(f"blk\\{sub}\\{b}_{i:02d}{t}")
                    emit(f"blk\\{sub}\\{b}{t}")

    # 9. paranoia perk
    par = "blk\\perks\\paranoia"
    for base in ["paranoia", "alert", "warn", "activate", "ping", "paranoia_alert", "paranoia_warn", "paranoia_ping", "paranoia_act"]:
        for t in TAILS:
            emit(f"{par}\\{base}{t}")
        for i in range(10):
            for t in TAILS:
                emit(f"{par}\\{base}_{i:02d}{t}")

    # 10. coolers, stashes, bj_cache
    for folder, obj in [("coolers", "cooler"), ("stashes", "stash"), ("bj_cache", "cache")]:
        for act in ["open", "close", "start", "stop", "use", "interact", "unlock"]:
            for t in TAILS:
                emit(f"blk\\{folder}\\{obj}_{act}{t}")
                emit(f"blk\\{folder}\\{act}{t}")

if __name__ == "__main__":
    generate()
