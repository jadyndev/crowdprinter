#!/usr/bin/env python3

import pathlib
import subprocess
import tempfile

BASE_DIR = pathlib.Path(__file__).parent


def text_to_stl(text, f_stl):
    path_lib = BASE_DIR / "generate_braille_lib.scad"
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False) as f_scad:
        f_scad.write(f'BrailleText1="{text.lower()}";')
        f_scad.write(f'ProfilText1="{text}";')
        f_scad.write(f"include<{path_lib}>;")
        f_scad.flush()
        subprocess.check_call(
            [
                "openscad",
                f_scad.name,
                "-o",
                f_stl.name,
                "--export-format",
                "stl",
            ]
        )


def stl_to_png(path_stl, f_png):
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False) as f_scad:
        f_scad.write(f'import("{path_stl}");')
        f_scad.flush()
        subprocess.check_call(
            [
                "xvfb-run",
                "-a",
                "openscad",
                f_scad.name,
                "-o",
                f_png.name,
                "--export-format",
                "png",
                "--imgsize=800,800",
            ]
        )


def stl_to_gcode(path_stl, f_gcode):
    path_pp_script = BASE_DIR / "insert_m600.py"
    subprocess.check_call(
        [
            "prusa-slicer",
            path_stl,
            "--post-process",
            path_pp_script,
            "--export-gcode",
            "--output",
            f_gcode.name,
        ]
    )
