# ============================================================
# RP9_FORM_ONLY_HDR_PRESENTATION.py
#
# KORRIGERAD PROPORTION:
#
# Yttre metasfär:
#     radie = R
#
# Två inre sfärer:
#     radie = r
#     centrumavstånd = r
#
# För att båda inre sfärerna samtidigt ska:
# 1. stå i halva-halva-relation,
# 2. vara symmetriskt centrerade,
# 3. tangera den yttre metasfären,
#
# gäller:
#
#     R = r + r/2
#     R = 3r/2
#     r = 2R/3
#
# Därmed:
#     centrum 1 = (-R/3, 0, 0)
#     centrum 2 = ( R/3, 0, 0)
#     centrumavstånd = 2R/3 = r
#
# Intersektionscirkelns radie:
#
#     r_i = sqrt(r^2 - (r/2)^2)
#         = sqrt(3)/2 * r
#         = R/sqrt(3)
#
# Presentationen innehåller endast:
# - grön metasfär
# - blå inre sfär
# - röd inre sfär
# - vit intersektionscirkel
# - vitt diameterstreck över intersektionscirkeln
#
# Inga mått, noder, axlar, kors, romber eller etiketter.
#
# Kräver:
#     pip install numpy plotly
# ============================================================

from __future__ import annotations

import webbrowser
from pathlib import Path

import numpy as np
import plotly.graph_objects as go


# ============================================================
# PARAMETRAR
# ============================================================

META_RADIUS = 3.0

SPHERE_RESOLUTION = 140
CIRCLE_RESOLUTION = 900

BACKGROUND_COLOR = "black"

META_COLOR = "#00C853"
BLUE_COLOR = "#087EA4"
RED_COLOR = "#C0392B"
WHITE_COLOR = "#FFFFFF"

META_OPACITY = 0.20
INNER_OPACITY = 0.48

INTERSECTION_WIDTH = 8
DIAMETER_WIDTH = 6

AUTO_OPEN_HTML = True

OUTPUT_METAPOTENTIAL = "01_METAPOTENTIAL_FORM.html"
OUTPUT_HDR = "02_HDR_FIRST_DIFFERENTIATION_FORM.html"


# ============================================================
# GEOMETRI
# ============================================================

def create_sphere(
    center: np.ndarray,
    radius: float,
    resolution: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    u = np.linspace(0.0, 2.0 * np.pi, resolution)
    v = np.linspace(0.0, np.pi, resolution)

    x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
    y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
    z = radius * np.outer(np.ones_like(u), np.cos(v)) + center[2]

    return x, y, z


def create_intersection_circle(
    center_1: np.ndarray,
    center_2: np.ndarray,
    sphere_radius: float,
    resolution: int,
) -> tuple[np.ndarray, float]:
    center_distance = float(np.linalg.norm(center_2 - center_1))

    if center_distance <= 0.0:
        raise ValueError("Centrumavståndet måste vara större än noll.")

    if center_distance >= 2.0 * sphere_radius:
        raise ValueError("Sfärerna överlappar inte.")

    midpoint = (center_1 + center_2) / 2.0

    intersection_radius = np.sqrt(
        sphere_radius**2 - (center_distance / 2.0) ** 2
    )

    theta = np.linspace(0.0, 2.0 * np.pi, resolution)

    # Sfärernas centrum ligger längs x-axeln.
    # Intersektionscirkeln ligger därför i planet x = 0.
    x = np.full_like(theta, midpoint[0])
    y = midpoint[1] + intersection_radius * np.cos(theta)
    z = midpoint[2] + intersection_radius * np.sin(theta)

    points = np.vstack((x, y, z))

    return points, float(intersection_radius)


def constant_colorscale(color: str) -> list[list[object]]:
    return [[0.0, color], [1.0, color]]


def sphere_trace(
    center: np.ndarray,
    radius: float,
    color: str,
    opacity: float,
) -> go.Surface:
    x, y, z = create_sphere(
        center=center,
        radius=radius,
        resolution=SPHERE_RESOLUTION,
    )

    return go.Surface(
        x=x,
        y=y,
        z=z,
        surfacecolor=np.zeros_like(x),
        colorscale=constant_colorscale(color),
        cmin=0.0,
        cmax=1.0,
        opacity=opacity,
        showscale=False,
        hoverinfo="skip",
        showlegend=False,
        lighting=dict(
            ambient=0.88,
            diffuse=0.58,
            specular=0.08,
            roughness=0.95,
            fresnel=0.02,
        ),
        lightposition=dict(
            x=100.0,
            y=100.0,
            z=100.0,
        ),
    )


# ============================================================
# LAYOUT
# ============================================================

def form_only_layout(radius: float) -> dict:
    limit = radius * 1.08

    hidden_axis = dict(
        visible=False,
        showgrid=False,
        showbackground=False,
        zeroline=False,
        showticklabels=False,
        title="",
        range=[-limit, limit],
    )

    return dict(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        scene=dict(
            bgcolor=BACKGROUND_COLOR,
            xaxis=hidden_axis,
            yaxis=hidden_axis,
            zaxis=hidden_axis,
            aspectmode="cube",
            camera=dict(
                # Frontal startvy längs x-axeln.
                # Intersektionscirkeln visas då som en cirkel.
                eye=dict(x=2.45, y=0.0, z=0.0),
                up=dict(x=0.0, y=0.0, z=1.0),
                center=dict(x=0.0, y=0.0, z=0.0),
                projection=dict(type="orthographic"),
            ),
        ),
    )


def export_html(fig: go.Figure, output_path: Path) -> None:
    fig.write_html(
        str(output_path),
        include_plotlyjs=True,
        full_html=True,
        auto_open=False,
        config={
            "displayModeBar": False,
            "scrollZoom": True,
            "responsive": True,
        },
    )

    if AUTO_OPEN_HTML:
        webbrowser.open(output_path.resolve().as_uri())


# ============================================================
# 1. METAPOTENTIAL
# ============================================================

def build_metapotential() -> go.Figure:
    center = np.array([0.0, 0.0, 0.0])

    fig = go.Figure(
        data=[
            sphere_trace(
                center=center,
                radius=META_RADIUS,
                color=META_COLOR,
                opacity=0.38,
            )
        ]
    )

    fig.update_layout(**form_only_layout(META_RADIUS))

    return fig


# ============================================================
# 2. H-D-R / FÖRSTA DIFFERENTIERINGENS FORM
# ============================================================

def build_hdr_form() -> go.Figure:
    meta_center = np.array([0.0, 0.0, 0.0])

    # Korrekt proportion:
    # r = 2R/3
    inner_radius = (2.0 / 3.0) * META_RADIUS

    # Halva-halva-relation:
    # centrumavståndet mellan sfärerna är lika med deras radie.
    center_distance = inner_radius

    center_1 = np.array(
        [-center_distance / 2.0, 0.0, 0.0]
    )
    center_2 = np.array(
        [center_distance / 2.0, 0.0, 0.0]
    )

    # Kontroll:
    # vardera inre sfär ska tangera metasfärens yta.
    outer_extent_1 = abs(center_1[0]) + inner_radius
    outer_extent_2 = abs(center_2[0]) + inner_radius

    if not np.isclose(outer_extent_1, META_RADIUS):
        raise RuntimeError("Blå sfär följer inte metasfärens proportion.")

    if not np.isclose(outer_extent_2, META_RADIUS):
        raise RuntimeError("Röd sfär följer inte metasfärens proportion.")

    intersection, intersection_radius = create_intersection_circle(
        center_1=center_1,
        center_2=center_2,
        sphere_radius=inner_radius,
        resolution=CIRCLE_RESOLUTION,
    )

    traces = [
        sphere_trace(
            center=meta_center,
            radius=META_RADIUS,
            color=META_COLOR,
            opacity=META_OPACITY,
        ),
        sphere_trace(
            center=center_1,
            radius=inner_radius,
            color=BLUE_COLOR,
            opacity=INNER_OPACITY,
        ),
        sphere_trace(
            center=center_2,
            radius=inner_radius,
            color=RED_COLOR,
            opacity=INNER_OPACITY,
        ),
        go.Scatter3d(
            x=intersection[0],
            y=intersection[1],
            z=intersection[2],
            mode="lines",
            line=dict(
                color=WHITE_COLOR,
                width=INTERSECTION_WIDTH,
            ),
            hoverinfo="skip",
            showlegend=False,
        ),
    ]

    fig = go.Figure(data=traces)
    fig.update_layout(**form_only_layout(META_RADIUS))

    return fig


# ============================================================
# KÖRNING
# ============================================================

def main() -> None:
    script_dir = Path(__file__).resolve().parent

    metapotential_path = script_dir / OUTPUT_METAPOTENTIAL
    hdr_path = script_dir / OUTPUT_HDR

    export_html(
        build_metapotential(),
        metapotential_path,
    )

    export_html(
        build_hdr_form(),
        hdr_path,
    )

    print("")
    print("KLART")
    print("")
    print("Korrekt proportion:")
    print(f"Metasfärens radie: {META_RADIUS}")
    print(
        "Inre sfärernas radie: "
        f"{(2.0 / 3.0) * META_RADIUS}"
    )
    print(
        "Centrumavstånd: "
        f"{(2.0 / 3.0) * META_RADIUS}"
    )
    print(
        "Intersektionscirkelns radie: "
        f"{META_RADIUS / np.sqrt(3.0)}"
    )
    print("")
    print(f"1. {metapotential_path}")
    print(f"2. {hdr_path}")
    print("")


if __name__ == "__main__":
    main()
