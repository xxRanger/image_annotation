from PIL import Image, ImageDraw,ImageFont
import requests
from io import BytesIO

def image_visualize(image_annotation,path=None,show=False,save=False):
    url = image_annotation['imgUrl']

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    w,h = img.size
    # print(w,h)
    draw=ImageDraw.Draw(img)
    font = ImageFont.truetype("times.ttf", 32)
    # draw worker annotation
    for annotation in image_annotation['annotation']:
        left_bottom = annotation['pos'][0]
        right_upper = annotation['pos'][1]

        left_bottom = (left_bottom.x * w, left_bottom.y * h)
        right_upper = (right_upper.x * w, right_upper.y * h)
        # left_upper = Point(left_bottom.x,right_upper.y)
        # right_bottom = Point(right_upper.x, left_bottom.y)
        draw.rectangle([left_bottom,right_upper],outline="red",width=8)
        draw.text(right_upper, str(annotation['label']), "red", font=font)
    # draw baseline
    for baseline in image_annotation['baseline']:
        left_bottom = baseline['pos'][0]
        right_upper = baseline['pos'][1]

        left_bottom = (left_bottom.x * w, left_bottom.y * h)
        right_upper = (right_upper.x * w, right_upper.y * h)

        draw.rectangle([left_bottom, right_upper], outline="yellow", width=4)
        draw.text(right_upper, str(baseline['label']), "yellow", font=font)

    # # draw cluster
    # for cluster in clusters['clusters']:
    #     left_bottom = cluster['center'][0]
    #     right_upper = cluster['center'][1]
    #
    #     left_bottom = (left_bottom.x * w, left_bottom.y * h)
    #     right_upper = (right_upper.x * w, right_upper.y * h)
    #
    #     draw.rectangle([left_bottom, right_upper], outline="green", width=8)
    # img.save("check"+str(num_people)+"/"+str(abnormal)+".jpg")
    # abnormal +=1
    if show:
        img.show()
    if save:
        if not path:
            raise Exception("path not specified")
        img.save(path)


def image_visualize_single_baseline(image_annotation, baseline, path=None,show=False,save=False):
    url = image_annotation['imgUrl']

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    w,h = img.size
    # print(w,h)
    draw=ImageDraw.Draw(img)

    # draw worker annotation
    font = ImageFont.truetype("times.ttf", 32)
    for annotation in image_annotation['annotation']:
        left_bottom = annotation['pos'][0]
        right_upper = annotation['pos'][1]

        left_bottom = (left_bottom.x * w, left_bottom.y * h)
        right_upper = (right_upper.x * w, right_upper.y * h)
        # left_upper = Point(left_bottom.x,right_upper.y)
        # right_bottom = Point(right_upper.x, left_bottom.y)
        draw.rectangle([left_bottom,right_upper],outline="red",width=8)
        draw.text(right_upper, str(annotation['label']), "red", font=font)

    # draw baseline
    left_bottom = baseline['pos'][0]
    right_upper = baseline['pos'][1]

    left_bottom = (left_bottom.x * w, left_bottom.y * h)
    right_upper = (right_upper.x * w, right_upper.y * h)
    # print(left_bottom)
    # print(right_upper)
    draw.rectangle([left_bottom, right_upper], outline="yellow", width=8)
    draw.text(right_upper, str(baseline['label']),"yellow",font= font)
    # draw.text(left_bottom, str(baseline['label']), "white", font=font)

    # draw cluster
    # for cluster in clusters['clusters']:
    #     left_bottom = cluster['center'][0]
    #     right_upper = cluster['center'][1]
    #
    #     left_bottom = (left_bottom.x * w, left_bottom.y * h)
    #     right_upper = (right_upper.x * w, right_upper.y * h)
    #
    #     draw.rectangle([left_bottom, right_upper], outline="green", width=8)
    # img.save("check"+str(num_people)+"/"+str(abnormal)+".jpg")
    # abnormal +=1
    if show:
        img.show()
    if save:
        if not path:
            raise Exception("path not specified")
        img.save(path)


def image_visualize_with_cluster(image_annotation,clusters,path=None,show=False,save=False):
    url = image_annotation['imgUrl']

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    w,h = img.size
    # print(w,h)
    draw=ImageDraw.Draw(img)

    # # draw worker annotation
    font = ImageFont.truetype("times.ttf", 40)
    for annotation in image_annotation['annotation']:
        left_bottom = annotation['pos'][0]
        right_upper = annotation['pos'][1]
        #
        left_bottom = (left_bottom.x * w, left_bottom.y * h)
        right_upper = (right_upper.x * w, right_upper.y * h)
        # # left_upper = Point(left_bottom.x,right_upper.y)
        # # right_bottom = Point(right_upper.x, left_bottom.y)
        # draw.rectangle([left_bottom,right_upper],outline="red",width=8)
        draw.text(right_upper, str(annotation['label']), "red", font=font)

    # draw baseline
    for baseline in image_annotation['baseline']:
        left_bottom = baseline['pos'][0]
        right_upper = baseline['pos'][1]

        left_bottom = (left_bottom.x * w, left_bottom.y * h)
        right_upper = (right_upper.x * w, right_upper.y * h)

        draw.rectangle([left_bottom, right_upper], outline="yellow", width=8)
        draw.text(right_upper, str(baseline['label']), "yellow", font=font)

    # draw cluster
    # for cluster in clusters:
    #     for center in cluster['center']:
    #         left_bottom = center[0]
    #         right_upper = center[1]
    #
    #         left_bottom = (left_bottom.x * w, left_bottom.y * h)
    #         right_upper = (right_upper.x * w, right_upper.y * h)
    #
    #         draw.rectangle([left_bottom, right_upper], outline="green", width=6)

    color_set = ['blue','orange','green','purple','brown','pink','gray','olive','cyan','white','black','lime',
                 'silver','antiquewhite', 'tan','darkolivegreen']
    # print(len(clusters))
    for i,cluster in enumerate(clusters):
        for annotation in cluster['annotation']:
            center = annotation['pos']
            left_bottom = center[0]
            right_upper = center[1]

            left_bottom = (left_bottom.x * w, left_bottom.y * h)
            right_upper = (right_upper.x * w, right_upper.y * h)
            center_point = ((right_upper[0] + left_bottom[0])/2, (right_upper[1]+left_bottom[1])/2)
            color = color_set[i]
            draw.rectangle([left_bottom, right_upper], outline=color, width=6)
            draw.text(center_point, str(i), color, font=font)

    # img.save("check"+str(num_people)+"/"+str(abnormal)+".jpg")
    # abnormal +=1
    if show:
        img.show()
    if save:
        if not path:
            raise Exception("path not specified")
        img.save(path)