from box import *
from box.box import Point
import json

def sanitize_mark_detail(annotation):
    labelTag = "tagOption"
    labelFieldTag = "id"
    startPosTag = "startPoint"
    endPosTag = "endPoint"
    if not isinstance(annotation, dict):
        raise Exception("annotation should be dictionary object (a mark)")
    # remove useless field
    label = annotation[labelTag][labelFieldTag]
    start_pos = annotation[startPosTag]
    end_pos = annotation[endPosTag]
    # part of the position is not correct, correct the position
    correct_start_pos = {}
    correct_start_pos['x'] = min(start_pos['x'], end_pos['x'])
    correct_start_pos['y'] = min(start_pos['y'], end_pos['y'])
    correct_end_pos = {}
    correct_end_pos['x'] = max(start_pos['x'], end_pos['x'])
    correct_end_pos['y'] = max(start_pos['y'], end_pos['y'])

    sanitized_annotation = {
        'label': label,
        'pos': (
            Point(correct_start_pos['x'], correct_start_pos['y']), Point(correct_end_pos['x'], correct_end_pos['y']))
    }
    return sanitized_annotation


def data_process(file_path):
    imgTag = "imgUrl"
    idTag = "id"
    auditorTag = "auditorId"  # + number
    markTag = "MarkDetailDto"  # + number

    all_annotations = []
    with open(file_path, 'r') as f:
        data = f.read()
        data = json.loads(data)
        for raw_annotation in data:  # for a single image
            # figure out the number of annotations
            count = 0

            for key in raw_annotation.keys():
                if auditorTag in key:
                    count += 1
            # get auditor id and mark details
            baseline = {}
            auditorId = []
            markDetais = []
            for key, value in raw_annotation.items():
                if auditorTag in key:
                    auditorId.append(value)
                    continue
                if markTag in key:
                    sanitized_mark = []
                    if value!=None:
                        value = eval(value)  # string to array
                        # the original mark detail has many useless field, sanitize the field
                        for v in value:
                            sanitized_mark.append(sanitize_mark_detail(v))  # sanitize each mark (json object)
                    markDetais.append(sanitized_mark)
            # test if our logic is right
            if count != len(auditorId) and count != len(markDetais):
                raise Exception("count and the length of auditorId and markDetails should be equal")

            # the first author is the baseline
            baseline_auditorId = auditorId[0]
            baseline_markDetail = markDetais[0]
            for baseline_mark in baseline_markDetail:
                baseline_mark['auditorId'] = baseline_auditorId

            # set annotation object for other user
            annotations = []
            for i in range(1, len(auditorId)):
                auditor_id = auditorId[i]
                for mark in markDetais[i]:
                    mark['auditorId'] = auditor_id
                    annotations.append(mark)
            # set object for this image annotations
            image_annotation = {}
            image_annotation[idTag] = raw_annotation[idTag]
            image_annotation[imgTag] = raw_annotation['imgUrl']
            image_annotation['baseline'] = baseline_markDetail
            image_annotation['annotation'] = annotations
            all_annotations.append(image_annotation)
    return all_annotations