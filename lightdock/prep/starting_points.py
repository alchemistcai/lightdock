"""Calculate the position of a set of points around a protein."""

import numpy as np
import math
import freesasa
from scipy.cluster.vq import kmeans2
from scipy.spatial import distance, KDTree
from prody import parsePDB, confProDy
from lightdock.constants import MIN_SURFACE_DENSITY

confProDy(verbosity='info')


def points_on_sphere(number_of_points):
    """Creates a list of points using a spiral method.
    
    Based on method of 'Minimal Discrete Energy on the Sphere' (E. B. Saff, E.A. 
    Rakhmanov and Y.M. Zhou), Mathematical Research Letters, Vol. 1 (1994), pp. 647-662.
    
    Spiral method: Spiral from top of sphere to bottom of sphere, with points 
    places at distances the same as the distance between coils of the spiral.
    """
    points = []
    increment = math.pi * (3. - math.sqrt(5.))
    offset = 2./number_of_points
    for point in range(number_of_points):
        y = point * offset - 1.0 + (offset / 2.0)
        r = math.sqrt(1 - y*y)
        phi = point * increment
        points.append([math.cos(phi)*r, y, math.sin(phi)*r])
    return points


def calculate_surface_points(receptor, ligand, num_points, rec_translation, 
    num_sphere_points=100, is_membrane=False):
    """Calculates the position of num_points on the surface of the given protein"""
    if num_points <= 0: 
        return []
    
    receptor_atom_coordinates = receptor.representative(is_membrane)

    distances_matrix_rec = distance.pdist(receptor_atom_coordinates)
    receptor_max_diameter = np.max(distances_matrix_rec)
    distances_matrix_lig = distance.pdist(ligand.representative())
    ligand_max_diameter = np.max(distances_matrix_lig)
    surface_distance = ligand_max_diameter / 4.0

    # Surface
    pdb_file_name = receptor.structure_file_names[receptor.representative_id]
    surface = parsePDB(pdb_file_name).select('protein and surface or nucleic and name P')
    coords = surface.getCoords()

    # SASA
    structure = freesasa.Structure(pdb_file_name)
    result = freesasa.calc(structure)
    total_sasa = result.totalArea()
    density = total_sasa / num_points
    num_points = math.ceil(total_sasa / MIN_SURFACE_DENSITY)

    # Surface clusters
    if len(coords) > num_points:
        surface_clusters = kmeans2(data=coords, k=num_points, minit='points', iter=100)
        surface_centroids = surface_clusters[0]
    else:
        surface_centroids = coords

    # Create points over the surface of each surface cluster
    sampling = []
    for sc in surface_centroids:
        sphere_points = np.array(points_on_sphere(num_sphere_points))
        surface_points = sphere_points * surface_distance + sc
        sampling.append(surface_points)
    
    # Filter out not compatible points
    centroids_kd_tree = KDTree(surface_centroids)
    for i_centroid in range(len(sampling)):
        # print('.', end="", flush=True)
        centroid = surface_centroids[i_centroid]
        # Search for this centroid neighbors 
        centroid_neighbors = centroids_kd_tree.query_ball_point(centroid, r=20.)
        # For each neighbor, remove points too close
        for n in centroid_neighbors:
            points_to_remove = []
            if n != i_centroid:
                for i_p, p in enumerate(sampling[i_centroid]):
                    if np.linalg.norm(p - surface_centroids[n]) <= surface_distance:
                        points_to_remove.append(i_p)
                points_to_remove = list(set(points_to_remove))
                sampling[i_centroid] = [sampling[i_centroid][i_p] \
                    for i_p in range(len(sampling[i_centroid])) if i_p not in points_to_remove]

    s = []
    for points in sampling:
        s.extend(points)

    if len(s) > num_points:
        # Final cluster of points
        s_clusters = kmeans2(data=s, k=num_points, minit='points', iter=100)
        s = s_clusters[0]
    
    for p in s:
        p += rec_translation

    return s, receptor_max_diameter, ligand_max_diameter
