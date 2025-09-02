# How to create a PyVista animation without recreating geometry

Goal: Efficiently animate changing geometry (deforming mesh, moving points, changing scalars) while avoiding the expensive remove/add cycle or re-instantiating glyphs each frame.

## Core Idea
Add a mesh (or glyphs) to a `pyvista.Plotter` once, keep a Python reference to the underlying PyVista dataset (e.g. `PolyData`, `UnstructuredGrid`, `StructuredGrid`), then mutate its point coordinates and/or data arrays in-place. Trigger a render (and optionally write a movie frame) after each update. This leverages VTK's pipeline so only the modified buffers are pushed to the GPU.

## When to use which update method
- Point motion / deformation: assign to `mesh.points[:]` (preferred) or call `mesh.translate`, `mesh.rotate_x/y/z`, etc.
- Scalar / vector field change: assign a NumPy array to `mesh.point_data["name"]` or `mesh.cell_data["name"]` (matching lengths) and then update active scalars if needed.
- Topology change (adding/removing cells): NOT in-place friendly; you must recreate or use a different mesh object.

`Plotter.update_coordinates` is deprecated (>= 0.43.0); direct mutation of `mesh.points` is the supported approach.

## Minimal deformation loop (interactive window)
```python
import numpy as np
import pyvista as pv

# Create base mesh (beam-like structured grid example)
x = np.linspace(0, 1, 30)
y = np.linspace(0, 0.2, 5)
z = np.linspace(0, 0.2, 5)
xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
pts = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])
mesh = pv.StructuredGrid()
mesh.points = pts
mesh.dimensions = xx.shape  # (nx, ny, nz)

pl = pv.Plotter()
pl.add_mesh(mesh, scalars=None, color='lightsteelblue', show_edges=True)
pl.show(auto_close=False)  # keep window open

n_frames = 60
for i, phase in enumerate(np.linspace(0, 2*np.pi, n_frames, endpoint=False)):
    # In-place update of y,z displacement (e.g., bending mode)
    disp = 0.05 * np.sin(2*np.pi*pts[:,0] + phase)
    mesh.points[:, 2] = pts[:, 2] + disp  # modify z only
    # Optionally update a scalar field
    mesh["amplitude"] = disp
    mesh.active_scalars_name = "amplitude"
    pl.render()  # redraw with mutated data

pl.close()
```
Key points:
- `mesh.points` shape: (N, 3). Must preserve shape; modify slice `mesh.points[:]` or columns.
- Do NOT reassign `mesh.points = new_array` with a different underlying object every frame in tight loops for performance; slice assignment reuses the VTK buffer. (Simple full reassign is still usually OK, but slice mutation is safest for zero reallocation.)

## Writing a GIF or MP4
```python
import pyvista as pv, numpy as np
pl = pv.Plotter(off_screen=True)  # off-screen for batch rendering
mesh = pv.Sphere(theta_resolution=90, phi_resolution=45)
pl.add_mesh(mesh, scalars=None, color='white')
pl.open_gif('pulse.gif')  # or pl.open_movie('pulse.mp4', framerate=30)

base_pts = mesh.points.copy()
for phase in np.linspace(0, 2*np.pi, 90, endpoint=False):
    scale = 1 + 0.25*np.sin(phase)
    # radial scaling about sphere center
    centered = base_pts - mesh.center
    mesh.points[:] = mesh.center + centered * scale
    mesh["scale"] = np.full(mesh.n_points, scale, float)
    mesh.active_scalars_name = "scale"
    pl.write_frame()  # captures current render

pl.close()
```
Notes:
- Call `pl.open_movie` (MP4) or `pl.open_gif` once before the loop.
- Use `pl.write_frame()` after updating coordinates and scalars.
- With glyph pipelines (`dataset.glyph()`), generate the glyph mesh once, add the resulting `PolyData`, then mutate its `points` or scalar arrays similarly.

## Live update with callback (`add_callback` / timer)
```python
import pyvista as pv, numpy as np
pl = pv.Plotter()
mesh = pv.ParametricSuperEllipsoid(n1=0.5, n2=0.5)
pl.add_mesh(mesh, scalars=None, color='orange')
base_pts = mesh.points.copy()
state = {"phase": 0.0}

def tick():
    state["phase"] += 0.1
    phase = state["phase"]
    r = 1 + 0.2*np.sin(phase)
    mesh.points[:] = mesh.center + (base_pts - mesh.center)*r
    mesh["r"] = np.full(mesh.n_points, r)
    mesh.active_scalars_name = "r"
    pl.render()

pl.add_callback(tick, interval=30)  # ~33 FPS
pl.show()
```
This avoids manual loop control; PyVista's internal timer drives updates.

## Updating only scalars (color animation)
```python
mesh = pv.Plane()
pl = pv.Plotter()
pl.add_mesh(mesh, scalars=None, cmap='viridis')
pl.show(auto_close=False)
base_x = mesh.points[:,0]
for t in np.linspace(0, 4*np.pi, 120):
    mesh["wave"] = np.sin(base_x*4 + t)
    mesh.active_scalars_name = "wave"
    pl.render()
pl.close()
```
No geometry changes; just replace or mutate the NumPy array backing the scalar field.

## Performance Tips
- Prefer in-place slice modification: `mesh.points[:,2] += dz`.
- Avoid creating many new NumPy arrays; reuse buffers (`base_pts` copy for reference, then mutate original).
- For very large meshes: disable lighting or edges, consider decimating for preview.
- Use `off_screen=True` for headless batch rendering (e.g., CI, servers).
- Adjust window size (`pl.window_size = (width, height)`) before opening movie to match output resolution.

## Common Pitfalls
| Pitfall | Fix |
|---------|-----|
| Calling `add_mesh` every frame | Add once; only mutate data arrays. |
| Using deprecated `update_coordinates` | Directly modify `mesh.points`. |
| Changing number/order of points | Not supported in-place; recreate mesh or preallocate. |
| Forgetting `pl.render()` (interactive) or `pl.write_frame()` (recording) | Call after each update. |
| Large memory usage from copies | Keep one `base_pts` copy; mutate original. |

## References
- PyVista Point Sets (geometry mutation): https://docs.pyvista.org/api/core/pointsets.html
- Movie/GIF creation example (`write_frame` pattern): https://docs.pyvista.org/examples/02-plot/movie_glyphs.html
- `Plotter.add_mesh` API: https://docs.pyvista.org/api/plotting/_autosummary/pyvista.Plotter.add_mesh.html

## Checklist for an animation without recreating geometry
1. Build or load mesh; keep reference.
2. Add mesh once with `pl.add_mesh(mesh, ...)`.
3. (Optional) Open movie/GIF writer.
4. Precompute any static baseline (`base_pts = mesh.points.copy()`).
5. Loop or callback: mutate `mesh.points` / scalar arrays in-place.
6. Render (`pl.render()`) or write frame (`pl.write_frame()`).
7. After loop: close plotter (and movie writer implicitly via `pl.close()`).

This approach yields smooth, efficient PyVista animations with minimal overhead.
