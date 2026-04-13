import sys
import os
import rasterio
import numpy as np

def convertToOBJ(input_filename, output_filename, z_scale=1.0, xy_scale=1.0):
    with rasterio.open(input_filename) as src:
        metadata = src.meta
        band = src.read(1).astype(np.float32)
        height = metadata['height']
        width = metadata['width']
        nodata = src.nodata

        print("Metadata:")
        print(f"Coordinate Reference System: {metadata['crs']}")
        print(f"Width: {metadata['width']}")
        print(f"Height: {metadata['height']}")
        print(f"Latitude and Longitude Info: {src.bounds}")
        print(f"Transform Info: {src.transform}")

        vertices = []
        vertex_index = -np.ones((height, width), dtype=np.int32)

        v_count = 1
        for row in range(height):
            for col in range(width):
                z = band[row, col]

                if nodata is not None and np.isclose(z, nodata):
                    continue
                if np.isnan(z):
                    continue
                
                #store x,y,z values for each vertice
                x = col * xy_scale
                y = -row * xy_scale
                vertices.append((x, y, z * z_scale))

                vertex_index[row, col] = v_count
                v_count += 1

        #create vertice pairs for each triangle face in the mesh
        faces = []
        for row in range(height - 1):
            for col in range(width - 1):
                v1 = vertex_index[row, col]
                v2 = vertex_index[row, col + 1]
                v3 = vertex_index[row + 1, col]
                v4 = vertex_index[row + 1, col + 1]

                #for each square, assign two triangles defined by their vertices
                if v1 > 0 and v2 > 0 and v3 > 0 and v4 > 0:
                    faces.append((v1, v3, v4))
                    faces.append((v1, v4, v2))

        #center the terrain to the center of the blender file (0,0)
        if vertices:
            xs = [v[0] for v in vertices]
            ys = [v[1] for v in vertices]
            x_center = (min(xs) + max(xs)) / 2.0
            y_center = (min(ys) + max(ys)) / 2.0
            vertices = [(x - x_center, y - y_center, z) for x, y, z in vertices]

        with open(output_filename, "w") as f:
            for v in vertices:
                f.write(f"v {v[0]} {v[1]} {v[2]}\n")
            for face in faces:
                f.write(f"f {face[0]} {face[1]} {face[2]}\n")

        print(f"OBJ saved to: {output_filename}")
        print(f"Vertices: {len(vertices)}")
        print(f"Faces: {len(faces)}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 5:
        print("Usage: python TIFF-ConversionOBJ.py <input_filename> [<output_filename>] [<height_scale_int>] [<pixel_width_int>]")
        sys.exit(1)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(input_filename)[0] + ".obj"
    z_scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    xy_scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0

    convertToOBJ(input_filename, output_filename, z_scale, xy_scale)