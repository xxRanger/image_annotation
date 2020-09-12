from collections import  namedtuple
from .box import *
import sys


# this is just a coarse lower bound
def is_box_annotate_sameobj_coarse(b1, b2):
    delta = 0
    alpha = 2.0 / 3
    # alpha = 3/4
    overlap = box_overlap(b1, b2)
    # calculate area of the three boxes
    area_overlap = box_area(overlap)
    if area_overlap == 0:
        # skip non-overlap
        return False
    area_cluster_center = box_area(b1)
    area_candidate_box = box_area(b2)
    if area_overlap > (1 - (1 - 0.5 * delta) * alpha) * (area_cluster_center + area_candidate_box):
        return True
    return False

# # more accurate lower bound
def is_box_annotate_sameobj(b1, b2):
    def corner_box(b):
        left_bottom = b[0]
        left_upper = Point(b[0].x, b[1].y)
        right_upper = b[1]
        right_bottom =Point(b[1].x, b[0].y)

        width = b[1].x - b[0].x
        height = b[1].y - b[0].y

        cb = []
        area = box_area(b)
        min_width = alpha * area / height
        min_height = alpha * area / width

        # left bottom
        # min height
        cb.append((
            left_bottom,
            Point(right_bottom.x, right_bottom.y + min_height)
        ))
        # min width
        cb.append((
            left_bottom,
            Point(left_bottom.x + min_width, left_upper.y )
        ))

        #left upper
        #min height
        cb.append((
            Point(left_upper.x, left_upper.y - min_height),
            right_upper
        ))
        #min width
        cb.append((
            left_bottom,
            Point(left_upper.x + min_width, left_upper.y)
        ))

        #right_upper
        #min height
        cb.append((
            Point(left_upper.x, left_upper.y - min_height),
            right_upper
        ))
        #min width
        cb.append((
            Point(right_upper.x - min_width, right_bottom.y),
            right_upper
        ))

        #right bottom
        #min height
        cb.append((
            left_bottom,
            Point(right_bottom.x, right_bottom.y + min_height)
        ))
        #min width
        cb.append((
            Point(right_bottom.x - min_width, right_bottom.y),
            right_upper
        ))

        return cb

    delta = 0
    alpha = 2.0 / 3
    # alpha = 3/4
    overlap = box_overlap(b1, b2)

    area_overlap = box_area(overlap)
    if area_overlap == 0:
        # skip non-overlap
        return False

    # gamma = 4  # theoretically, its 1/alpha
    # if box_area(b1) > gamma* box_area(b2) or box_area(b2)>gamma*box_area(b1):
    #     return False

    # calculate area of the three boxes

    b1_cb = corner_box(b1)
    b2_cb = corner_box(b2)
    min_overlap_area = 1<<31
    for cb1 in b1_cb:
        for cb2 in b2_cb:
            overlap = box_overlap(cb1,cb2)
            overlap_area = box_area(overlap)
            min_overlap_area = min(min_overlap_area, overlap_area)
    # maximum overlap area should be small than delta * min(S_b1, S_b2)
    area_b1 = box_area(b1)
    area_b2 = box_area(b2)
    # if min_overlap_area <= delta * min(area_b1, area_b2):
    #     return False
    # return True
    gamma = 0
    if min_overlap_area/max(area_b1,area_b2) <= gamma:
        return False
    return True


#center_theory: assume the ideal box is proportion to the real box
# def is_box_annotate_sameobj(b1, b2):
#     def min_ideal_box(b):
#         left_bottom = b[0]
#         left_upper = Point(b[0].x, b[1].y)
#         right_upper = b[1]
#         right_bottom =Point(b[1].x, b[0].y)
#
#         width = b[1].x - b[0].x
#         height = b[1].y - b[0].y
#
#         center = Point(left_bottom.x + width/2, left_bottom.y + height/2)
#
#         sqrt_alpha = alpha**0.5
#         return (
#             Point(center.x - sqrt_alpha * width/2, center.y - sqrt_alpha * height/2),
#             Point(center.x + sqrt_alpha*width/2, center.y + sqrt_alpha*height/2)
#         )
#
#     delta = 0
#     alpha = 2.0 / 3
#     # alpha = 3/4
#     overlap = box_overlap(b1, b2)
#
#     area_overlap = box_area(overlap)
#     if area_overlap == 0:
#         # skip non-overlap
#         return False
#
#     # gamma = 4  # theoretically, its 1/alpha
#     #     # if box_area(b1) > gamma* box_area(b2) or box_area(b2)>gamma*box_area(b1):
#     #     #     return False
#
#     # calculate area of the three boxes
#
#     b1_cb = min_ideal_box(b1)
#     b2_cb = min_ideal_box(b2)
#     overlap_cb = box_overlap(b1_cb, b2_cb)
#     overlap_area = box_area(overlap_cb)
#
#     # maximum overlap area should be small than delta * min(S_b1, S_b2)
#     area_b1 = box_area(b1)
#     area_b2 = box_area(b2)
#     # if min_overlap_area <= delta * min(area_b1, area_b2):
#     #     return False
#     # return True
#     gamma = 0.1
#     if overlap_area/max(area_b1,area_b2) > gamma:
#         return True
#     return False





def box_match_center(center, box):
    if not isinstance(center,list):
        raise Exception("center should be list")

    is_box_match = False
    # size_fit = True
    for cb in center:
        if is_box_annotate_sameobj(cb, box):
            is_box_match = True
            break
        # area_cb = box_area(cb)
        # area_box = box_area(box)
        # if area_cb > area_box * 4 or area_box > area_cb *4:
        #     size_fit = False
        #     break
    # return is_box_match and size_fit
    return is_box_match

def box_overlap_center(center, box):
    if not isinstance(center,list):
        raise Exception("center should be list")

    is_overlap = False
    for cb in center:
        overlap = box_overlap(cb,box)
        overlap_area = box_area(overlap)
        if overlap_area>0:
            is_overlap = True
    return is_overlap


def box_clustering(all_annotations):
    # create new cluster for oversize box
    image_clusters = []
    for image_annotation in all_annotations:
        # cluster annotation for each image
        worker_annotations = image_annotation['annotation']
        candidate_annotations = set(range(len(worker_annotations)))  # only use indexes in worker_annotations
        clusters = []

        # rank annotaion according to their area
        worker_annotations.sort(key=lambda x: box_area(x['pos']), reverse=True)

        while len(candidate_annotations) != 0:
            # get initial cluster center
            initial_index = candidate_annotations.pop()
            initial_annotation = worker_annotations[initial_index]
            cluster_center = initial_annotation['pos']  #

            cluster_annotations = []  # record annotation belong to this cluster
            cluster_annotations.append(initial_annotation)
            # find box belongs to the cluster
            for index in list(candidate_annotations):
                annotation = worker_annotations[index]
                # judge if the box are annotating the same object with the cluster centers
                candidate_box = annotation['pos']
                # first calculate overlap area
                overlap = box_overlap(cluster_center, candidate_box)
                # calculate area of the three boxes
                area_overlap = box_area(overlap)
                if area_overlap == 0:
                    # skip non-overlap
                    continue
                # area_cluster_center = box_area(cluster_center)
                # area_candidate_box = box_area(candidate_box)
                # if area_overlap > (1 - (1-0.5*delta)*alpha)* (area_cluster_center + area_candidate_box):
                if is_box_annotate_sameobj(cluster_center, candidate_box):
                    # if overlap
                    # print("overlap")
                    cluster_center = overlap
                    cluster_annotations.append(annotation)
                    candidate_annotations.remove(index)
                else:
                    # print(area_overlap, area_cluster_center, area_candidate_box)
                    pass

            cluster = {
                'center': [cluster_center],
                'annotation': cluster_annotations
            }
            clusters.append(cluster)
        image_clusters.append({
            'id': image_annotation['id'],
            'imgUrl': image_annotation['imgUrl'],
            'baseline': image_annotation['baseline'],
            'clusters': clusters
        })
        # break
    return image_clusters

def box_clustering_tolerate(all_annotations):
    # def split_oversize_box_in_cluster(cluster, cluster_annotation_index):
    #     # calculate average box area
    #     cluster_annotations = cluster['annotation']
    #     total_box_area = 0
    #     for annotation in cluster_annotations:
    #         box = annotation['pos']
    #         total_box_area += box_area(box)
    #     average_area = total_box_area / len(cluster_annotations)

    image_clusters = []
    for image_annotation in all_annotations:
        # cluster annotation for each image
        worker_annotations = image_annotation['annotation']
        candidate_annotations = set(range(len(worker_annotations)))  # only use indexes in worker_annotations
        clusters = []

        # rank annotaion according to their area
        worker_annotations.sort(key=lambda x: box_area(x['pos']), reverse=True)

        while len(candidate_annotations) != 0:
            # get initial cluster center
            initial_index = candidate_annotations.pop()
            initial_annotation = worker_annotations[initial_index]
            cluster_center = [initial_annotation['pos']]  #

            cluster_annotations = []  # record annotation belong to this cluster
            cluster_annotations.append(initial_annotation)
            # find box belongs to the cluster
            for index in list(candidate_annotations):
                annotation = worker_annotations[index]
                # judge if the box are annotating the same object with the cluster centers
                candidate_box = annotation['pos']
                # first calculate overlap area
                # overlap = box_overlap(cluster_center, candidate_box)
                # calculate area of the three boxes
                # area_overlap = box_area(overlap)
                # if area_overlap == 0:
                #     skip non-overlap
                    # continue
                # area_cluster_center = box_area(cluster_center)
                # area_candidate_box = box_area(candidate_box)
                # if area_overlap > (1 - (1-0.5*delta)*alpha)* (area_cluster_center + area_candidate_box):
                if box_match_center(cluster_center, candidate_box):
                    cluster_center.append(candidate_box)
                    cluster_annotations.append(annotation)
                    candidate_annotations.remove(index)
                else:
                    # print(area_overlap, area_cluster_center, area_candidate_box)
                    pass
            cluster = {
                'center': cluster_center,
                'annotation': cluster_annotations
            }
            # split_oversize_box_in_cluster(cluster, cluster_annotation_index)
            clusters.append(cluster)
        image_clusters.append({
            'id': image_annotation['id'],
            'imgUrl': image_annotation['imgUrl'],
            'baseline': image_annotation['baseline'],
            'clusters': clusters
        })
        # break
    return image_clusters