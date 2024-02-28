# 人脸识别系统，同时提供对外的API接口

演示地址: [查看演示](http://helong.xyz:8000)

## 安装依赖

安装`dlib`

```shell
pip install dlib
```

安装`opencv`

```shell
pip install opencv-python
```

## 运行

```shell
python http_server.py
```

默认端口：`8000`

## API

### 获取所有人信息

```http request
GET /api/load_all_person HTTP/1.1
```

返回数据
```json5
{
  "code": 0,
  "message": "",
  "data": [
    {
      "person_id": 41,
      "name": "马传明",
      "create_time": 1708937800548,
      "faces": [
        {
          "face_id": 32,
          "face_img": "照片Base64",
          "face_value": [] // 人脸特征
        }
      ]
    }
  ]
}
```

### 添加人

```http request
POST /api/add_person_face HTTP/1.1
Content-Type: x-www-form-urlencoded

person_id=42&face_img=URL编码后的图片Base64
```

返回数据
```json5
{
  "code": 0,
  "message": "",
  "data": 33 // 人编号
}
```


### 删除人

```http request
POST /api/remove_person HTTP/1.1
Content-Type: x-www-form-urlencoded

person_id=人编号
```

返回数据
```json5
{
  "code": 0,
  "message": "",
  "data": ""
}
```

### 添加人脸

```http request
POST /api/add_person_face HTTP/1.1
Content-Type: x-www-form-urlencoded

person_id=人编号&face_img=URL编码后的图片Base64
```

返回数据
```json5
{
  "code": 0,
  "message": "",
  "data": 34
}
```

### 根据照片识别人

```http request
POST /api/get_person_by_face HTTP/1.1
Content-Type: x-www-form-urlencoded

face_img=URL编码后的图片Base64
```

返回数据
```json5
{
  "code": 0,
  "message": "",
  "data": {
    "person_id": 39,
    "name": "周星池",
    "diff": 0.42836527958967463 // 识别相似度，值越小越准确
  }
}
```
