# Body Mesh Data

The 3D body-skin mesh that the FEM body-impact sound model is built on - notebook 03 (`03-kj-sound-reconstruction-body-thump.ipynb`) and `corridor/bodyfem.py`.

## Files

- `body-skin.obj` - the working mesh: the raw STL decimated by vertex clustering to a committable size (about 3,100 vertices, 11,700 triangles, ~370 KB), in metres
- `upper-torso.obj` - the isolated upper torso, written by notebook 03 from the working mesh
- `FMA7163-skin.stl` - the raw full-resolution skin mesh (about 1.59 M triangles, 79 MB); not committed, downloaded on demand

## Source

The raw mesh is the **skin** part (FMA7163) of **BodyParts3D**, the whole-body anatomical model from the Database Center for Life Science. It is mirrored as a binary STL in the `Kevin-Mattheus-Moerman/BodyParts3D` repository.

Download link:

<https://raw.githubusercontent.com/Kevin-Mattheus-Moerman/BodyParts3D/main/assets/BodyParts3D_data/stl/FMA7163.stl>

The STL is in millimetres; `ensure_body_mesh` in `corridor/bodyfem.py` scales it to metres and decimates it by vertex clustering. Notebook 03 calls it in the Data Acquisition step, so the STL is fetched automatically only when `body-skin.obj` is absent.

## Licence

BodyParts3D, (c) The Database Center for Life Science, licensed under CC Attribution-Share Alike 2.1 Japan.
