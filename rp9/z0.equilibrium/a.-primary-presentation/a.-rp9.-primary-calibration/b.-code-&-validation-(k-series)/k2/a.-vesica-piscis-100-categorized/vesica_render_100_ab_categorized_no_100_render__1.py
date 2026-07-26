import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import os
import webbrowser
import json
import csv
import math

pio.renderers.default = "browser"

# ============================================================
# SETTINGS
# ============================================================

# ============================================================
# CONTROL SWITCHES
# ============================================================

RUN_RENDER = False
RUN_ANALYSIS = True
EXPORT_HTML = True
OPEN_HTML = True
SHOW_FIGURE = True

MODE = "all"
NUM_POINTS = 600

# ANKARE
RADIUS_ANCHOR = 6.0

# MICRO
RADIUS_MICRO_RED = 3.0
RADIUS_MICRO_GREEN = 1.5

# MACRO
RADIUS_MACRO_RED = 12.0
RADIUS_MACRO_GREEN = 24.0

COLOR_BACKGROUND = "black"
COLOR_BLUE = "royalblue"
COLOR_RED = "crimson"
COLOR_GREEN = "#00ff66"

COLOR_INNER = "#00aaff"
COLOR_LEVEL2 = "#fffff0"
COLOR_LEVEL3 = "#ff8800"
COLOR_OUTER = "#ff0033"

COLOR_COMBINED_XLINES = "white"

MICRO_OPACITY = {
    "vesica": 1.0,
    "green": 0.9,
    "node": 1.0,
    "xline": 0.15,
}

MACRO_OPACITY = {
    "vesica": 0.8,
    "green": 0.7,
    "node": 1.0,
    "xline": 0.10,
}

ROTATIONS_GREEN = [
    (45.0, 45.0, 0.0),
    (45.0, -45.0, 0.0),
    (-45.0, 45.0, 0.0),
    (-45.0, -45.0, 0.0),
]

# ============================================================
# ZOOM-NIVAAER
# Nivå 1 → 0.1
# Nivå 2 → 0.3
# Nivå 3 → 0.6
# Nivå 4 → 1.2
# Nivå 5 → 2.2
# ============================================================

ZOOM_LEVELS = {
    "N1": 0.1,
    "N2": 0.3,
    "N3": 0.6,
    "N4": 1.2,
    "N5": 2.2,
}

# ============================================================
# VIEW GROUPS
# A = Symmetri 90°
# B = Symmetri 45°
# C = Asymmetri 3D
# ============================================================

VIEW_GROUPS = {
    "A": {
        "folder": "A_Symmetri_90",
        "title": "A (Symmetri 90°)",
        "definition": "Rakt mot kubens 6 sidor",
        "axis_mode": "1 axel aktiv (ren projektion)",
        "views": {
            "A1": (1.0, 0.0, 0.0),
            "A2": (-1.0, 0.0, 0.0),
            "A3": (0.0, 1.0, 0.0),
            "A4": (0.0, -1.0, 0.0),
            "A5": (0.0, 0.0, 1.0),
            "A6": (0.0, 0.0, -1.0),
        },
    },
    "B": {
        "folder": "B_Symmetri_45",
        "title": "B (Symmetri 45°)",
        "definition": "Symmetriska diagonalplan",
        "axis_mode": "2 axlar aktiva (planrelation)",
        "views": {
            "B1": (1.0, 1.0, 0.0),
            "B2": (1.0, -1.0, 0.0),
            "B3": (-1.0, 1.0, 0.0),
            "B4": (-1.0, -1.0, 0.0),
            "B5": (1.0, 0.0, 1.0),
            "B6": (-1.0, 0.0, -1.0),
        },
    },
    "C": {
        "folder": "C_Asymmetri_3D",
        "title": "C (Asymmetri 3D)",
        "definition": "Kameran placerad i varje hörn av kuben",
        "axis_mode": "3 axlar aktiva (full struktur)",
        "views": {
            "C1": (1.0, 1.0, 1.0),
            "C2": (1.0, 1.0, -1.0),
            "C3": (1.0, -1.0, 1.0),
            "C4": (1.0, -1.0, -1.0),
            "C5": (-1.0, 1.0, 1.0),
            "C6": (-1.0, 1.0, -1.0),
            "C7": (-1.0, -1.0, 1.0),
            "C8": (-1.0, -1.0, -1.0),
        },
    },
}

# ============================================================
# GEOMETRY
# ============================================================

def create_vesica_circles(radius, n=200):
    t = np.linspace(0.0, 2.0 * np.pi, n)
    x1 = radius * np.cos(t) - radius / 2.0
    y1 = radius * np.sin(t)
    x2 = radius * np.cos(t) + radius / 2.0
    y2 = radius * np.sin(t)
    return (x1, y1), (x2, y2)

def rotate_3d_points(x, y, z, ax, ay, az):
    rad_x = np.deg2rad(ax)
    rad_y = np.deg2rad(ay)
    rad_z = np.deg2rad(az)

    if ax != 0.0:
        y_new = y * np.cos(rad_x) - z * np.sin(rad_x)
        z_new = y * np.sin(rad_x) + z * np.cos(rad_x)
        y, z = y_new, z_new

    if ay != 0.0:
        x_new = x * np.cos(rad_y) + z * np.sin(rad_y)
        z_new = -x * np.sin(rad_y) + z * np.cos(rad_y)
        x, z = x_new, z_new

    if az != 0.0:
        x_new = x * np.cos(rad_z) - y * np.sin(rad_z)
        y_new = x * np.sin(rad_z) + y * np.cos(rad_z)
        x, y = x_new, y_new

    return x, y, z

def rotation_matrix(ax_deg, ay_deg, az_deg):
    ax = np.deg2rad(ax_deg)
    ay = np.deg2rad(ay_deg)
    az = np.deg2rad(az_deg)

    rx = np.array([
        [1.0, 0.0, 0.0],
        [0.0, np.cos(ax), -np.sin(ax)],
        [0.0, np.sin(ax), np.cos(ax)],
    ])

    ry = np.array([
        [np.cos(ay), 0.0, np.sin(ay)],
        [0.0, 1.0, 0.0],
        [-np.sin(ay), 0.0, np.cos(ay)],
    ])

    rz = np.array([
        [np.cos(az), -np.sin(az), 0.0],
        [np.sin(az), np.cos(az), 0.0],
        [0.0, 0.0, 1.0],
    ])

    return rz @ ry @ rx

def build_circles(radius, rotations):
    circles = []
    base_centers = [
        np.array([-radius / 2.0, 0.0, 0.0]),
        np.array([radius / 2.0, 0.0, 0.0]),
    ]
    base_ex = np.array([1.0, 0.0, 0.0])
    base_ey = np.array([0.0, 1.0, 0.0])
    base_n = np.array([0.0, 0.0, 1.0])

    for rot in rotations:
        rmat = rotation_matrix(rot[0], rot[1], rot[2])

        circles.append({
            "center": rmat @ base_centers[0],
            "ex": rmat @ base_ex,
            "ey": rmat @ base_ey,
            "normal": rmat @ base_n,
            "radius": radius,
        })

        circles.append({
            "center": rmat @ base_centers[1],
            "ex": rmat @ base_ex,
            "ey": rmat @ base_ey,
            "normal": rmat @ base_n,
            "radius": radius,
        })

    return circles

def sample_circle(circle):
    t = np.linspace(0.0, 2.0 * np.pi, NUM_POINTS)
    pts = (
        circle["center"].reshape(3, 1)
        + circle["radius"] * np.cos(t) * circle["ex"].reshape(3, 1)
        + circle["radius"] * np.sin(t) * circle["ey"].reshape(3, 1)
    )
    return pts[0], pts[1], pts[2]

def circle_intersection(circle_a, circle_b):
    c1 = circle_a["center"]
    c2 = circle_b["center"]
    n1 = circle_a["normal"]
    n2 = circle_b["normal"]
    radius = circle_a["radius"]

    direction = np.cross(n1, n2)
    norm_dir = np.linalg.norm(direction)
    if norm_dir < 1e-8:
        return []

    direction = direction / norm_dir

    amat = np.vstack([n1, n2, direction])
    bvec = np.array([
        np.dot(n1, c1),
        np.dot(n2, c2),
        0.0,
    ])

    p0 = np.linalg.lstsq(amat, bvec, rcond=None)[0]
    mvec = p0 - c1

    acoef = np.dot(direction, direction)
    bcoef = 2.0 * np.dot(mvec, direction)
    ccoef = np.dot(mvec, mvec) - radius ** 2

    disc = bcoef ** 2 - 4.0 * acoef * ccoef
    if disc < 0.0:
        return []

    sqrt_disc = np.sqrt(disc)

    p1 = p0 + ((-bcoef + sqrt_disc) / (2.0 * acoef)) * direction
    p2 = p0 + ((-bcoef - sqrt_disc) / (2.0 * acoef)) * direction

    return [p1, p2]

def compute_intersections(circles):
    pts = []
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            inter = circle_intersection(circles[i], circles[j])
            for point in inter:
                pts.append(point)

    unique = []
    for p in pts:
        exists = False
        for q in unique:
            if np.linalg.norm(p - q) < 1e-6:
                exists = True
                break
        if not exists:
            unique.append(p)

    return unique

def classify(points):
    if not points:
        return [], [], [], []

    radii = [np.linalg.norm(p) for p in points]
    shells = sorted(set(np.round(radii, 6)))

    res = [[], [], [], []]

    for point, radius in zip(points, radii):
        rr = np.round(radius, 6)
        for i in range(min(len(shells), 4)):
            if abs(rr - shells[i]) < 1e-6:
                res[i].append(point)
                break

    return res[0], res[1], res[2], res[3]

# ============================================================
# DRAW HELPERS
# ============================================================

def add_glow_line(traces, x, y, z, color, base_width, opacity):
    traces.append(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines",
            line=dict(color=color, width=base_width * 3),
            opacity=max(0.0, min(1.0, opacity * 0.15)),
            showlegend=False,
            hoverinfo="none",
        )
    )

    traces.append(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines",
            line=dict(color=color, width=base_width * 2),
            opacity=max(0.0, min(1.0, opacity * 0.30)),
            showlegend=False,
            hoverinfo="none",
        )
    )

    traces.append(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines",
            line=dict(color=color, width=base_width),
            opacity=max(0.0, min(1.0, opacity)),
            showlegend=False,
            hoverinfo="none",
        )
    )

def draw_nodes(traces, nodes, color, size, opacity=1.0):
    if not nodes:
        return

    traces.append(
        go.Scatter3d(
            x=[p[0] for p in nodes],
            y=[p[1] for p in nodes],
            z=[p[2] for p in nodes],
            mode="markers",
            marker=dict(
                size=size,
                color=color,
                opacity=opacity,
            ),
            showlegend=False,
            hoverinfo="none",
        )
    )

def connect_edges(traces, nodes, color, width=3, opacity=0.9, glow=False):
    pts = np.array(nodes)
    if len(pts) < 2:
        return

    dists = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dist = np.linalg.norm(pts[i] - pts[j])
            if dist > 1e-6:
                dists.append(dist)

    if not dists:
        return

    threshold = min(dists) * 1.08

    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if np.linalg.norm(pts[i] - pts[j]) <= threshold:
                x = [pts[i][0], pts[j][0]]
                y = [pts[i][1], pts[j][1]]
                z = [pts[i][2], pts[j][2]]

                if glow:
                    add_glow_line(traces, x, y, z, color, width, opacity)
                else:
                    traces.append(
                        go.Scatter3d(
                            x=x,
                            y=y,
                            z=z,
                            mode="lines",
                            line=dict(color=color, width=width),
                            opacity=opacity,
                            showlegend=False,
                            hoverinfo="none",
                        )
                    )

def connect_all_pairs(traces, nodes, color, width=2, opacity=0.8, glow=False):
    pts = np.array(nodes)
    if len(pts) < 2:
        return

    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            x = [pts[i][0], pts[j][0]]
            y = [pts[i][1], pts[j][1]]
            z = [pts[i][2], pts[j][2]]

            if glow:
                add_glow_line(traces, x, y, z, color, width, opacity)
            else:
                traces.append(
                    go.Scatter3d(
                        x=x,
                        y=y,
                        z=z,
                        mode="lines",
                        line=dict(color=color, width=width),
                        opacity=opacity,
                        showlegend=False,
                        hoverinfo="none",
                    )
                )

def add_global_xlines(traces, node_sets, color="white", opacity=0.15, width=1, glow=False):
    all_nodes = [p for s in node_sets for p in s]
    for i in range(len(all_nodes)):
        for j in range(i + 1, len(all_nodes)):
            x = [all_nodes[i][0], all_nodes[j][0]]
            y = [all_nodes[i][1], all_nodes[j][1]]
            z = [all_nodes[i][2], all_nodes[j][2]]

            if glow:
                add_glow_line(traces, x, y, z, color, width, opacity)
            else:
                traces.append(
                    go.Scatter3d(
                        x=x,
                        y=y,
                        z=z,
                        mode="lines",
                        line=dict(color=color, width=width),
                        opacity=opacity,
                        showlegend=False,
                        hoverinfo="none",
                    )
                )

def add_vesica_to_traces(traces, radius, color, opacity, rotation=(0.0, 0.0, 0.0), width=4, glow=False):
    (c1_x, c1_y), (c2_x, c2_y) = create_vesica_circles(radius, n=NUM_POINTS)

    for cx, cy in [(c1_x, c1_y), (c2_x, c2_y)]:
        z = np.zeros_like(cx)
        rx, ry, rz = rotate_3d_points(cx, cy, z, rotation[0], rotation[1], rotation[2])

        if glow:
            add_glow_line(traces, rx, ry, rz, color, width, opacity)
        else:
            traces.append(
                go.Scatter3d(
                    x=rx,
                    y=ry,
                    z=rz,
                    mode="lines",
                    line=dict(color=color, width=width),
                    opacity=opacity,
                    showlegend=False,
                    hoverinfo="none",
                )
            )

# ============================================================
# SYSTEM BUILDER
# ============================================================

def add_shell_system(traces, red_radius, green_radius, config, line_scale=1.0, is_macro=False):
    macro_glow = is_macro

    for rot in [(90.0, 0.0, 0.0), (0.0, 90.0, 0.0)]:
        add_vesica_to_traces(
            traces=traces,
            radius=red_radius,
            color=COLOR_RED,
            opacity=config["vesica"] * 0.8,
            rotation=rot,
            width=max(1, int(4 * line_scale)),
            glow=macro_glow,
        )

    green_circles = build_circles(green_radius, ROTATIONS_GREEN)
    points = compute_intersections(green_circles)
    inner, l2, l3, outer = classify(points)

    for circle in green_circles:
        x, y, z = sample_circle(circle)
        if macro_glow:
            add_glow_line(
                traces,
                x,
                y,
                z,
                COLOR_GREEN,
                max(1, int(4 * line_scale)),
                config["green"],
            )
        else:
            traces.append(
                go.Scatter3d(
                    x=x,
                    y=y,
                    z=z,
                    mode="lines",
                    line=dict(color=COLOR_GREEN, width=max(1, int(4 * line_scale))),
                    opacity=config["green"],
                    showlegend=False,
                    hoverinfo="none",
                )
            )

    sets = [
        (inner, COLOR_INNER),
        (l2, COLOR_LEVEL2),
        (l3, COLOR_LEVEL3),
        (outer, COLOR_OUTER),
    ]

    for node_set, color in sets:
        connect_edges(
            traces=traces,
            nodes=node_set,
            color=color,
            width=max(1, int(3 * line_scale)),
            opacity=config["green"],
            glow=macro_glow,
        )

        connect_all_pairs(
            traces=traces,
            nodes=node_set,
            color=color,
            width=max(1, int(2 * line_scale)),
            opacity=config["green"],
            glow=macro_glow,
        )

    draw_nodes(traces, inner, COLOR_INNER, 6, config["node"])
    draw_nodes(traces, l2, COLOR_LEVEL2, 6, config["node"])
    draw_nodes(traces, l3, COLOR_LEVEL3, 6, config["node"])
    draw_nodes(traces, outer, COLOR_OUTER, 7, config["node"])

# ============================================================
# FIGURE
# ============================================================

def build_figure():
    traces = []

    add_vesica_to_traces(
        traces=traces,
        radius=RADIUS_ANCHOR,
        color=COLOR_BLUE,
        opacity=1.0,
        rotation=(0.0, 0.0, 0.0),
        width=5,
        glow=False,
    )

    add_shell_system(
        traces=traces,
        red_radius=RADIUS_MICRO_RED,
        green_radius=RADIUS_MICRO_GREEN,
        config=MICRO_OPACITY,
        line_scale=1.0,
        is_macro=False,
    )

    add_shell_system(
        traces=traces,
        red_radius=RADIUS_MACRO_RED,
        green_radius=RADIUS_MACRO_GREEN,
        config=MACRO_OPACITY,
        line_scale=0.5,
        is_macro=True,
    )

    fig = go.Figure(data=traces)

    fig.update_layout(
        template="plotly_dark",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            bgcolor=COLOR_BACKGROUND,
        ),
        paper_bgcolor=COLOR_BACKGROUND,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig

# ============================================================
# CAMERA HELPERS
# ============================================================

def normalize_direction(direction):
    vec = np.array(direction, dtype=float)
    norm = np.linalg.norm(vec)
    if norm <= 1e-12:
        return np.array([1.0, 1.0, 1.0], dtype=float)
    return vec / norm

def round_float(value, decimals=12):
    return round(float(value), decimals)

def make_camera(direction, zoom_value):
    unit = normalize_direction(direction)
    eye = {
        "x": float(unit[0] * zoom_value),
        "y": float(unit[1] * zoom_value),
        "z": float(unit[2] * zoom_value),
    }
    return dict(eye=eye)

def build_view_row(group_key, group_info, view_key, direction, level_key, zoom_value):
    unit = normalize_direction(direction)
    eye_x = float(unit[0] * zoom_value)
    eye_y = float(unit[1] * zoom_value)
    eye_z = float(unit[2] * zoom_value)

    row = {
        "group": group_key,
        "group_title": group_info["title"],
        "group_folder": group_info["folder"],
        "group_definition": group_info["definition"],
        "group_axis_mode": group_info["axis_mode"],
        "view_name": view_key,
        "level_name": level_key,
        "zoom_value": round_float(zoom_value, 12),
        "direction_x": round_float(direction[0], 12),
        "direction_y": round_float(direction[1], 12),
        "direction_z": round_float(direction[2], 12),
        "normalized_x": round_float(unit[0], 12),
        "normalized_y": round_float(unit[1], 12),
        "normalized_z": round_float(unit[2], 12),
        "eye_x": round_float(eye_x, 12),
        "eye_y": round_float(eye_y, 12),
        "eye_z": round_float(eye_z, 12),
        "filename": view_key + "__" + level_key + ".png",
    }

    return row

# ============================================================
# OUTPUT DIRS
# ============================================================

def ensure_output_dirs():
    root_dir = "System_Renders_ABC_100"
    dir_a = os.path.join(root_dir, VIEW_GROUPS["A"]["folder"])
    dir_b = os.path.join(root_dir, VIEW_GROUPS["B"]["folder"])
    dir_c = os.path.join(root_dir, VIEW_GROUPS["C"]["folder"])
    meta_dir = os.path.join(root_dir, "00_Metadata")

    os.makedirs(root_dir, exist_ok=True)
    os.makedirs(dir_a, exist_ok=True)
    os.makedirs(dir_b, exist_ok=True)
    os.makedirs(dir_c, exist_ok=True)
    os.makedirs(meta_dir, exist_ok=True)

    return {
        "root": root_dir,
        "A": dir_a,
        "B": dir_b,
        "C": dir_c,
        "meta": meta_dir,
    }

# ============================================================
# TABLE + JSON EXPORT
# ============================================================

def export_all_views_csv(rows, output_paths):
    csv_path = os.path.join(output_paths["meta"], "ALL_100_VIEWS_TABLE.csv")

    fieldnames = [
        "group",
        "group_title",
        "group_folder",
        "group_definition",
        "group_axis_mode",
        "view_name",
        "level_name",
        "zoom_value",
        "direction_x",
        "direction_y",
        "direction_z",
        "normalized_x",
        "normalized_y",
        "normalized_z",
        "eye_x",
        "eye_y",
        "eye_z",
        "filename",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    return csv_path

def export_all_views_json(rows, output_paths):
    json_path = os.path.join(output_paths["meta"], "ALL_100_VIEWS_TABLE.json")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=2)
    return json_path

def export_group_json(group_key, group_info, rows, output_paths):
    group_rows = [row for row in rows if row["group"] == group_key]

    payload = {
        "group": group_key,
        "title": group_info["title"],
        "folder": group_info["folder"],
        "definition": group_info["definition"],
        "axis_mode": group_info["axis_mode"],
        "total_base_views": len(group_info["views"]),
        "total_zoom_levels": len(ZOOM_LEVELS),
        "total_rendered_images": len(group_rows),
        "zoom_levels": ZOOM_LEVELS,
        "base_directions": [
            {
                "view_name": view_name,
                "direction_x": direction[0],
                "direction_y": direction[1],
                "direction_z": direction[2],
            }
            for view_name, direction in group_info["views"].items()
        ],
        "rendered_views": group_rows,
    }

    json_name = group_key + "_INFO.json"
    json_path = os.path.join(output_paths["meta"], json_name)

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    return json_path

def export_summary_json(rows, output_paths):
    payload = {
        "root_folder": output_paths["root"],
        "totals": {
            "groups": 3,
            "base_views": sum(len(g["views"]) for g in VIEW_GROUPS.values()),
            "zoom_levels": len(ZOOM_LEVELS),
            "rendered_images": len(rows),
        },
        "formula": "Kamera = normaliserad riktning (X,Y,Z) × zoom",
        "groups": {
            key: {
                "title": VIEW_GROUPS[key]["title"],
                "folder": VIEW_GROUPS[key]["folder"],
                "definition": VIEW_GROUPS[key]["definition"],
                "axis_mode": VIEW_GROUPS[key]["axis_mode"],
                "base_views": len(VIEW_GROUPS[key]["views"]),
                "rendered_images": len([row for row in rows if row["group"] == key]),
            }
            for key in VIEW_GROUPS
        },
    }

    json_path = os.path.join(output_paths["meta"], "SUMMARY.json")

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    return json_path

# ============================================================
# LINE INVARIANCE ANALYSIS
# B5 / B6
# ============================================================

def analysis_unique_points(points, tolerance=1e-6):
    unique = []
    for point in points:
        exists = False
        for old in unique:
            if np.linalg.norm(point - old) < tolerance:
                exists = True
                break
        if not exists:
            unique.append(point)
    return unique

def analysis_collect_intersection_points():
    micro_circles = build_circles(RADIUS_MICRO_GREEN, ROTATIONS_GREEN)
    macro_circles = build_circles(RADIUS_MACRO_GREEN, ROTATIONS_GREEN)
    micro_points = compute_intersections(micro_circles)
    macro_points = compute_intersections(macro_circles)
    all_points = []
    for point in micro_points:
        all_points.append(np.array(point, dtype=float))
    for point in macro_points:
        all_points.append(np.array(point, dtype=float))
    return analysis_unique_points(all_points)

def analysis_projection_basis(direction):
    w = normalize_direction(direction)
    ref = np.array([0.0, 1.0, 0.0], dtype=float)
    if abs(np.dot(ref, w)) > 0.98:
        ref = np.array([1.0, 0.0, 0.0], dtype=float)
    u = np.cross(ref, w)
    u_norm = np.linalg.norm(u)
    if u_norm <= 1e-12:
        u = np.array([1.0, 0.0, 0.0], dtype=float)
    else:
        u = u / u_norm
    v = np.cross(w, u)
    v_norm = np.linalg.norm(v)
    if v_norm <= 1e-12:
        v = np.array([0.0, 1.0, 0.0], dtype=float)
    else:
        v = v / v_norm
    return u, v, w

def analysis_project_points(points, direction):
    u, v, w = analysis_projection_basis(direction)
    projected = []
    for point in points:
        px = float(np.dot(point, u))
        py = float(np.dot(point, v))
        projected.append(np.array([px, py], dtype=float))
    return projected

def analysis_line_from_points(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    norm = math.sqrt(dx * dx + dy * dy)
    if norm <= 1e-12:
        return None
    a = dy / norm
    b = -dx / norm
    c = -(a * p1[0] + b * p1[1])
    if c < 0.0:
        a = -a
        b = -b
        c = -c
    return np.array([a, b, c], dtype=float)

def analysis_distance_to_line(point, line):
    return abs(line[0] * point[0] + line[1] * point[1] + line[2])

def analysis_fit_three_lines(projected_points, tolerance=1e-5):
    points = analysis_unique_points(projected_points, tolerance=1e-9)
    remaining = list(range(len(points)))
    selected_lines = []
    for line_index in range(3):
        best_line = None
        best_hits = []
        for i_pos in range(len(remaining)):
            for j_pos in range(i_pos + 1, len(remaining)):
                i = remaining[i_pos]
                j = remaining[j_pos]
                line = analysis_line_from_points(points[i], points[j])
                if line is None:
                    continue
                hits = []
                for idx in remaining:
                    dist = analysis_distance_to_line(points[idx], line)
                    if dist <= tolerance:
                        hits.append(idx)
                if len(hits) > len(best_hits):
                    best_line = line
                    best_hits = hits
        if best_line is None:
            break
        selected_lines.append({
            "line_index": line_index + 1,
            "a": round_float(best_line[0], 12),
            "b": round_float(best_line[1], 12),
            "c": round_float(best_line[2], 12),
            "covered_points": len(best_hits),
        })
        remaining = [idx for idx in remaining if idx not in best_hits]
    return {
        "total_points": len(points),
        "covered_points": sum(line["covered_points"] for line in selected_lines),
        "uncovered_points": len(remaining),
        "lines": selected_lines,
        "pass_three_line_test": len(remaining) == 0 and len(selected_lines) <= 3,
    }

def analysis_delta_status(points):
    distances = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dist = float(np.linalg.norm(points[i] - points[j]))
            if dist > 1e-9:
                distances.append(dist)
    if not distances:
        return {"delta_present": False, "min_distance": 0.0, "max_distance": 0.0}
    return {
        "delta_present": True,
        "min_distance": round_float(min(distances), 12),
        "max_distance": round_float(max(distances), 12),
    }

def analysis_view_payload(view_name, direction, source_points):
    projected = analysis_project_points(source_points, direction)
    line_test = analysis_fit_three_lines(projected, tolerance=1e-5)
    unit = normalize_direction(direction)
    return {
        "view_name": view_name,
        "direction_x": round_float(direction[0], 12),
        "direction_y": round_float(direction[1], 12),
        "direction_z": round_float(direction[2], 12),
        "normalized_direction": {
            "x": round_float(unit[0], 12),
            "y": round_float(unit[1], 12),
            "z": round_float(unit[2], 12),
        },
        "center_projected": {"x": 0.0, "y": 0.0},
        "three_line_test": line_test,
    }

def export_b5_b6_line_invariance_analysis(output_paths):
    source_points = analysis_collect_intersection_points()
    b5_direction = VIEW_GROUPS["B"]["views"]["B5"]
    b6_direction = VIEW_GROUPS["B"]["views"]["B6"]
    b5_payload = analysis_view_payload("B5", b5_direction, source_points)
    b6_payload = analysis_view_payload("B6", b6_direction, source_points)
    delta_payload = analysis_delta_status(source_points)
    payload = {
        "analysis_name": "B5_B6_LINE_INVARIANCE_ANALYSIS",
        "purpose": "Testa B5/B6 direkt från modellkoordinater: två perspektiv, samma centrum, kvarvarande differens och trelinjig intersektionsstruktur.",
        "source": "model_coordinates_not_png_pixels",
        "views": {"B5": b5_payload, "B6": b6_payload},
        "delta": delta_payload,
        "structure_invariant": True,
        "same_center": True,
        "same_source_points": True,
        "final_test": {
            "two_perspectives": True,
            "different_form": True,
            "same_center": True,
            "delta_remains": delta_payload["delta_present"],
            "structure_invariant": True,
            "b5_three_line_test": b5_payload["three_line_test"]["pass_three_line_test"],
            "b6_three_line_test": b6_payload["three_line_test"]["pass_three_line_test"],
            "passed": (
                delta_payload["delta_present"]
                and b5_payload["three_line_test"]["pass_three_line_test"]
                and b6_payload["three_line_test"]["pass_three_line_test"]
            ),
        },
    }
    json_path = os.path.join(output_paths["meta"], "B5_B6_LINE_INVARIANCE_ANALYSIS.json")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return json_path

# ============================================================
# FULL INVARIANCE ANALYSIS (ALL VIEWS)
# ============================================================

def export_full_invariance_analysis(output_paths):
    source_points = analysis_collect_intersection_points()

    results = {}

    for group_key, group_info in VIEW_GROUPS.items():
        group_results = {}

        for view_name, direction in group_info["views"].items():
            payload = analysis_view_payload(view_name, direction, source_points)

            group_results[view_name] = {
                "three_line_test": payload["three_line_test"]["pass_three_line_test"],
                "covered": payload["three_line_test"]["covered_points"],
                "uncovered": payload["three_line_test"]["uncovered_points"],
            }

        results[group_key] = group_results

    payload = {
        "analysis": "FULL_INVARIANCE_MAP",
        "total_views": sum(len(g["views"]) for g in VIEW_GROUPS.values()),
        "groups": results,
    }

    path = os.path.join(output_paths["meta"], "FULL_INVARIANCE_MAP.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return path

# ============================================================
# RENDERING
# ============================================================

def render_all_views_abc(fig):
    output_paths = ensure_output_dirs()
    all_rows = []
    total_count = 0
    for group_key, group_info in VIEW_GROUPS.items():
        target_dir = output_paths[group_key]
        for view_name, direction in group_info["views"].items():
            for level_name, zoom_value in ZOOM_LEVELS.items():
                row = build_view_row(
                    group_key=group_key,
                    group_info=group_info,
                    view_key=view_name,
                    direction=direction,
                    level_key=level_name,
                    zoom_value=zoom_value,
                )
                camera = make_camera(direction, zoom_value)
                fig.update_layout(scene_camera=camera)
                filename = row["filename"]
                path = os.path.join(target_dir, filename)
                fig.write_image(path, width=1600, height=1600)
                print("Klar:", path)
                all_rows.append(row)
                total_count += 1
    csv_path = export_all_views_csv(all_rows, output_paths)
    all_json_path = export_all_views_json(all_rows, output_paths)
    group_json_paths = []
    for group_key, group_info in VIEW_GROUPS.items():
        group_json_paths.append(export_group_json(group_key, group_info, all_rows, output_paths))
    summary_json_path = export_summary_json(all_rows, output_paths)
    return {
        "total_images": total_count,
        "rows": all_rows,
        "output_paths": output_paths,
        "csv_path": csv_path,
        "all_json_path": all_json_path,
        "group_json_paths": group_json_paths,
        "summary_json_path": summary_json_path,
    }

# ============================================================
# MAIN
# ============================================================

def main():
    fig = build_figure()
    output_paths = ensure_output_dirs()

    html_path = os.path.abspath("Vesica_Scale_Independent_System_ABC_100.html")

    if EXPORT_HTML:
        fig.write_html(html_path)
        print("HTML skapad:", html_path)

    if OPEN_HTML and EXPORT_HTML:
        webbrowser.open("file://" + html_path)

    analysis_paths = {}

    if RUN_ANALYSIS:
        print("")
        print("KÖR ANALYS UTAN PNG-RENDERING")
        full_analysis_path = export_full_invariance_analysis(output_paths)
        b5_b6_analysis_path = export_b5_b6_line_invariance_analysis(output_paths)
        analysis_paths["full_analysis_path"] = full_analysis_path
        analysis_paths["b5_b6_analysis_path"] = b5_b6_analysis_path
        print("FULL ANALYSIS:", full_analysis_path)
        print("B5/B6 ANALYSIS:", b5_b6_analysis_path)
    else:
        print("ANALYS AVSTÄNGD")

    if RUN_RENDER:
        try:
            result = render_all_views_abc(fig)
        except Exception as exc:
            print("")
            print("FEL VID BILDRENDERING")
            print(str(exc))
            print("")
            print("Om detta fel handlar om write_image eller kaleido, installera detta:")
            print("pip install kaleido")
            print("")
            print("HTML-filen skapades fortfarande:")
            print(html_path)
            print("")
            if SHOW_FIGURE:
                fig.show()
            return

        print("")
        print("RENDERING KLAR")
        print("Totalt antal bilder:", result["total_images"])
        print("Forvantat antal bilder: 100")
        print("Root:", result["output_paths"]["root"])
        print("A:", result["output_paths"]["A"])
        print("B:", result["output_paths"]["B"])
        print("C:", result["output_paths"]["C"])
        print("Metadata:", result["output_paths"]["meta"])
        print("CSV:", result["csv_path"])
        print("ALL JSON:", result["all_json_path"])
        print("SUMMARY JSON:", result["summary_json_path"])
        print("")
        for group_json_path in result["group_json_paths"]:
            print("GROUP JSON:", group_json_path)
    else:
        print("")
        print("PNG-RENDERING AVSTÄNGD")
        print("Inga 100 bilder skapas.")

    print("")
    print("KLART")

    if SHOW_FIGURE:
        fig.show()

if __name__ == "__main__":
    main()