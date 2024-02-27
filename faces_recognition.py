import dlib
import cv2
import os
import numpy
import base64

import numpy as np

currDir = os.path.dirname(os.path.abspath(__file__))

# 模型路径
predictor_path = (currDir + "/dat/shape_predictor_68_face_landmarks.dat").replace('\\', '/')
face_rec_model_path = (currDir + "/dat/dlib_face_recognition_resnet_model_v1.dat").replace('\\', '/')

# 读入模型
detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(predictor_path)
face_rec_model = dlib.face_recognition_model_v1(face_rec_model_path)


# 0.45
def compare_face_value(data1, data2):
    diff = 0
    for i in range(len(data1)):
        diff += (data1[i] - data2[i]) ** 2
    diff = numpy.sqrt(diff)
    return diff


def calc_face_value_by_base64img(base64_str):
    head, context = base64_str.split(",")  # 将base64_str以“,”分割为两部分
    img_b64decode = base64.b64decode(context)

    img_array = np.fromstring(img_b64decode, np.uint8)  # 转换np序列
    img = cv2.imdecode(img_array, cv2.COLOR_BGR2RGB)  # 转换Opencv格式
    return calc_img_face_value(img)


def calc_face_value_by_file(file_path):
    print("读取文件：" + file_path)
    # opencv 读取图片，并显示
    img = cv2.imread(file_path, cv2.IMREAD_COLOR)
    return calc_img_face_value(img)


def calc_img_face_value(img):
    # opencv的bgr格式图片转换成rgb格式
    b, g, r = cv2.split(img)
    img2 = cv2.merge([r, g, b])

    dets = detector(img, 1)  # 人脸标定
    print("Number of faces detected: {}".format(len(dets)))

    for index, face in enumerate(dets):
        print('face {}; left {}; top {}; right {}; bottom {}'.format(index, face.left(), face.top(), face.right(),
                                                                     face.bottom()))
        shape = shape_predictor(img2, face)  # 提取68个特征点

        # for i, pt in enumerate(shape.parts()):
        #     pt_pos = (pt.x, pt.y)
        #     cv2.circle(img, pt_pos, 2, (255, 0, 0), 1)
        # print("Part 0: {}, Part 1: {} ...".format(shape.part(0), shape.part(1)))
        # cv2.namedWindow(img_path + str(index), cv2.WINDOW_AUTOSIZE)
        # cv2.imshow(img_path + str(index), img)

        face_descriptor = face_rec_model.compute_face_descriptor(img2, shape)  # 计算人脸的128维的向量
        # print(face_descriptor)
        return face_descriptor

# u1 = calc_faces_value_by_file(currDir + "/faces/s1.jpg")
# print("------------------------------------------------")
# u2 = calc_faces_value_by_file(currDir + "/faces/s2.jpg")
# print("------------------------------------------------")
# compare_faces_value(u1, u2)
#
# k = cv2.waitKey(0)
# cv2.destroyAllWindows()
