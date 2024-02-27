import json
import os
import traceback
import urllib
import sqlite3
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from faces_recognition import calc_face_value_by_base64img, compare_face_value

currDir = os.path.dirname(os.path.abspath(__file__))


def add_person(args):
    name = args['name']
    sql = "insert into person (name, del_flag, create_time) " \
          "values (?, ?, ?)"
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute(sql, (name, 0, int(time.time() * 1000)))
    person_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return person_id


def remove_person(args):
    person_id = args['person_id']
    sql = "update person set del_flag=1 where person_id=? and del_flag=0 "
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute(sql, (person_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return


def add_person_face(args):
    person_id = args['person_id']
    face_img = args['face_img']
    face_value = calc_face_value_by_base64img(face_img)
    if face_value is None:
        raise Exception('人脸识别失败')
    else:
        sql = "insert into person_face (person_id, face_img, face_value, del_flag, create_time) " \
              "values (?, ?, ?, ?, ?)"
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(sql, (
            person_id, face_img, json.dumps(list(face_value), ensure_ascii=False), 0, int(time.time() * 1000)))
        face_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return face_id


def get_person_by_face(args):
    face_img = args['face_img']
    face_value = calc_face_value_by_base64img(face_img)
    if face_value is None:
        raise Exception('人脸识别失败')
    else:
        sql = "SELECT p.person_id, p.name, f.face_id, f.face_value " \
              "FROM person p " \
              "left join person_face f on f.person_id=p.person_id and p.del_flag=0 " \
              "where p.del_flag=0 " \
              "order by p.create_time desc "
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(sql)
        person_faces = cursor.fetchall()
        cursor.close()
        conn.close()

        results = []
        for person_face in person_faces:
            diff = compare_face_value(face_value, json.loads(person_face[3]))
            results.append({
                'person_id': person_face[0],
                'name': person_face[1],
                'diff': diff,
            })
        if len(results) == 0:
            raise Exception('未找到此人信息')
        else:
            results = sorted(results, key=lambda x: x['diff'])
            r = results[0]
            if r['diff'] < 0.45:
                return r
            raise Exception('未找到此人信息')


def load_all_person(args):
    sql = "SELECT p.person_id, p.name, f.face_img, f.face_id, f.face_value, p.create_time " \
          "FROM person p " \
          "left join person_face f on f.person_id=p.person_id and p.del_flag=0 " \
          "where p.del_flag=0 " \
          "order by p.create_time desc "
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute(sql)
    person_faces = cursor.fetchall()
    cursor.close()
    conn.close()

    persons = dict()
    for person_face in person_faces:
        person_id = person_face[0]
        name = person_face[1]
        face_img = person_face[2]
        face_id = person_face[3]
        face_value = person_face[4]
        create_time = person_face[5]

        if person_id not in persons:
            persons[person_id] = {
                'person_id': person_id,
                'name': name,
                'create_time': create_time,
                'faces': []
            }
        if face_id is not None:
            persons[person_id]['faces'].append({
                'face_id': face_id,
                'face_img': face_img,
                'face_value': json.loads(face_value),
            })
    return list(persons.values())


def read_html_content(path):
    file = open(currDir + path, 'r', encoding='utf-8')
    content = file.read()
    file.close()
    return content


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _response(self, path, args):
        code = 200
        resp = {'code': 0, 'message': '', 'data': ''}

        try:
            if args:
                args = urllib.parse.parse_qs(args).items()
                args = dict([(k, v[0]) for k, v in args])
            else:
                args = {}

            if path == "" or path == "/":
                self.send_response(301)
                self.send_header("Location", "/ui/index.html")
                self.end_headers()
                return
            elif path.startswith("/ui/"):
                content = read_html_content(path)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(content.encode())
                return
            elif path == "/api/calc_faces_value":
                resp["data"] = list(calc_face_value_by_base64img(args['img']))
            elif path == "/api/add_person":
                resp["data"] = add_person(args)
            elif path == "/api/remove_person":
                remove_person(args)
            elif path == "/api/add_person_face":
                resp['data'] = add_person_face(args)
            elif path == "/api/get_person_by_face":
                resp['data'] = get_person_by_face(args)
            elif path == "/api/load_all_person":
                resp['data'] = load_all_person(args)
            else:
                code = 404
                resp["code"] = 404
                resp["message"] = "路径" + path + "不存在"
        except Exception as e:
            resp["code"] = 500
            resp["message"] = '服务器错误：' + str(e)
            print(str(e))
            print(traceback.format_exc())

        try:
            resp = json.dumps(resp, ensure_ascii=False)
        except Exception as e:
            resp["code"] = 500
            resp["message"] = '服务器返回数据错误：' + str(e)
            resp['data'] = ''
            resp = json.dumps(resp, ensure_ascii=False)
            print(str(e))
            print(traceback.format_exc())

        self.send_response(code)
        self.send_header('Content-type', 'text/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        self.wfile.write(resp.encode())

    def do_GET(self):
        path, args = urllib.parse.splitquery(self.path)
        self._response(path, args)

    def do_POST(self):
        args = self.rfile.read(int(self.headers['content-length'])).decode("utf-8")
        self._response(self.path, args)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()


http_server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
print("Http服务启动")
http_server.serve_forever()
