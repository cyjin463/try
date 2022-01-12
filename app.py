# flask
from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

# mongo
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
# client = MongoClient('mongodb://test:test@3.83.182.90', 27017) --------------- 서버이용시 변경
db = client.jgati

SECRET_KEY = 'SPARTA'

import requests
from bs4 import BeautifulSoup

import jwt
import datetime
import hashlib
from werkzeug.utils import secure_filename

from datetime import datetime, timedelta

# ----------------페이지 관련 py code ----------------------------------------------------------------------
# ----------------index page 호출 -----------------------------------
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"ID": payload["id"]})
        return render_template('list.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("relogin"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("relogin"))

@app.route('/relogin')
def relogin():
    return render_template('index.html')

# ------------------------------- 회원가입 페이지 로드 / lsm -------------------------------
## 회원가입 페이지
@app.route('/joinGet')
def join_page():
   return render_template('join.html')

# ----------------list 페이지 이동 :  ASJ-----------------------------------
@app.route('/list')
def list_page():
    user = list(db.user_info.find({}, {"_id": False}))
    contents = list(db.write_info.find({}, {"_id": False}))
    return render_template("list.html", contents=contents, user=user)

# ---------------------------------------------------popup route   //  cyj
@app.route('/popup')
def pop():
    return render_template('popup.html')
#---------------------------------------------------------------------------------------------------------




# ----------------로그인 페이지 : 기능 ----------------------------------------------------------------------
# ----------------로그인 id/pw 작업 페이지:  ASJ-----------------------------------
## 로그인
@app.route('/api/login', methods=['POST'])
def login():
    id_receive = request.form['id']
    pw_receive = request.form['pw']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    find_user = db.user_info.find_one({'ID': id_receive, 'PWD': pw_hash})
    print("---------55555-----------")
    if find_user is not None:
        print("---------66666-----------")
        payload = {
         'id': id_receive,
         'exp': datetime.utcnow() + timedelta(seconds=20)  # 로그인 10분 유지
        }

        # ----------------토큰 생성 ----------------------------------------------------------------------
        ## 원본(잘못된 코드)
        # token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        ## 수정본
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # ----------------------------------------------------------------------------------------------

        print("---------777777-----------")
        return jsonify({'result': 'success', 'token': token, 's_msg': '아이디/비밀번호가 맞습니다.'})

        # 'token': token.decode('utf-8'),-------------------서버 이용시 변경

    else:
        return jsonify({'result': 'fail', 'f_msg': '아이디/비밀번호가 일치하지 않습니다.'})



# ---------------- 회원가입 페이지 : 기능 ----------------------------------------------------------------------
# ------------------------------- 회원가입 api / lsm -------------------------------
## 회원가입
@app.route('/api/membership', methods=['POST'])
def membership():
    id_receive = request.form['id_give']
    pw_receive = request.form['pwd_give']
    confirm_pwd_receive = request.form['confirm_pwd_give']
    email_receive = request.form['email_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    """
    ## 패스워드 confirm 로직 미완성 
        if (pw_receive != confirm_pwd_receive):
            return jsonify({'msg': '패스워드 재입력 확인 바랍니다.'})
        else:
            find_id = db.user_info.find_one({'ID': id_receive})

            if (find_id == None):
                doc = {
                    'ID': id_receive,
                    'PWD': pw_receive,
                    'EMAIL': email_receive
                }
                db.user_info.insert_one(doc)
                return jsonify({'msg': '회원가입 완료'})
            else:
                return jsonify({'msg': '아이디가 이미 존재합니다!'})
     """

    find_id = db.user_info.find_one({'ID': id_receive})

    if (find_id == None):
        doc = {
            'ID': id_receive,
            'PWD': pw_hash,
            'EMAIL': email_receive
        }
        db.user_info.insert_one(doc)
        return jsonify({'result': 'success', 'msg': '회원가입 완료'})
        # return jsonify({"result": "success"})
    else:
        return jsonify({"result": "fail", "msg": "아이디가 이미 존재합니다!"})
        # return jsonify({"result": "fail"})


# ------------------------------- 중복검사 api / lsm -------------------------------
## 중복검사
@app.route('/api/check', methods=['POST'])
def check():
    id_receive = request.form['id_give']

    find_id = db.user_info.find_one({'id': id_receive})

    if (find_id != None):
        return jsonify({'msg': '중복된 아이디입니다.'})
    else:
        return jsonify({'msg': '사용 가능한 아이디입니다.'})
#---------------------------------------------------------------------------------------------------------




# ---------------- 리스트 페이지 : 기능 ----------------------------------------------------------------------
# ---------------------------------------------------POST  //  cyj
# 작성데이터를 db에 저장하기 위한 코드
@app.route('/memo', methods=['POST'])
def art():
    title_receive = request.form['title_give']
    date_receive = request.form['date_give']
    place_receive = request.form['place_give']
    attendance_receive = request.form['attendance_give']
    content_receive = request.form['content_give']
    id_receive = request.form['id_give']

    if (title_receive == ''):
        return jsonify({'msg': '제목을 입력해주세요.'})
    elif (date_receive == ''):
        return jsonify({'msg': '날짜를 입력해주세요.'})
    elif (place_receive == ''):
        return jsonify({'msg': '장소를 입력해주세요.'})
    elif (attendance_receive == ''):
        return jsonify({'msg': '참석인원을 입력해주세요.'})
    elif (content_receive == ''):
        return jsonify({'msg': '설명을 입력해주세요.'})
    else:
        doc = {
            'title': title_receive,
            'date': date_receive,
            'place': place_receive,
            'attendance': attendance_receive,
            'content': content_receive,
            'writeID': id_receive,
            'count': 1
        }
        db.write_info.insert_one(doc)
        return jsonify({'msg': '작성완료!', 'result': 'success'})


# 카드 제거관련 -------------------------------------------------------------------------
# 해당카드에 대한 상세내용을 보여줄 때, 해당 카드데이터 팝업연결작업을 html에 script로 구현해놓은 상황 --> list.html(line 139) script : open_view(e) 참조
# 삭제해야할 카드 선택을 팝업 연결데이터를 가져와서 식별
# 그래서 팝업에 있는 데이터들을 변수지정하여 data:{}를 통해 연결 --> list.(line 162) script : delete_card() 참조
@app.route('/memo/delete', methods=['POST'])
def delete_card():
    # 해당 상세카드 data를 가져와 각각 변수지정
    title_receive = request.form['title_give']
    date_receive = request.form['date_give']
    attendance_receive = request.form['attendance_give']
    place_receive = request.form['place_give']
    content_receive = request.form['content_give']
    id_receive = request.form['id_give']
    count_receive = request.form['count_give']

    # 현재 count_give 가져운 count값이 str형식이므로 int형으로 변환
    int_like = int(count_receive);

    # db.write_info안에서 해당조건에 해당하는 document 삭제
    print("제목 :" + title_receive)
    print("일시 :" + date_receive)
    print("인원 :" + attendance_receive)
    print("장소 :" + place_receive)
    print("설명 :" + content_receive)
    print("id :" + id_receive)
    print("count :" + count_receive)
    print("제거 data input complete")

    db.write_info.delete_one({
        'title': title_receive,
        'date': date_receive,
        'place': place_receive,
        'attendance': attendance_receive,
        'content': content_receive,
        'writeID': id_receive,
        'count': int_like
    })

    return jsonify({'msg': '모집이 취소되었습니다!'})

# 카드 수정관련 -------------------------------------------------------------------------
@app.route('/memo/fix', methods=['POST'])
def fix_card():
    # 해당 상세카드 data를 가져와 각각 변수지정
    title_receive = request.form['title_give']
    date_receive = request.form['date_give']
    attendance_receive = request.form['attendance_give']
    place_receive = request.form['place_give']
    content_receive = request.form['content_give']
    id_receive = request.form['id_give']
    count_receive = request.form['count_give']

    # 현재 count_give 가져운 count값이 str형식이므로 int형으로 변환
    int_like = int(count_receive);

    # 팝업에서 수정된 data를 가져와 각각 변수지정
    fix_title_receive = request.form['fix_title_give']
    fix_date_receive = request.form['fix_date_give']
    fix_attendance_receive = request.form['fix_attendance_give']
    fix_place_receive = request.form['fix_place_give']
    fix_content_receive = request.form['fix_content_give']

    # db.write_info안에서 해당조건에 해당하는 document 수정
    print("제목 :" + title_receive)
    print("일시 :" + date_receive)
    print("인원 :" + attendance_receive)
    print("장소 :" + place_receive)
    print("설명 :" + content_receive)
    print("id :" + id_receive)
    print("count :" + count_receive)
    print("원본 data input complete")

    print("제목 :" + fix_title_receive)
    print("일시 :" + fix_date_receive)
    print("인원 :" + fix_attendance_receive)
    print("장소 :" + fix_place_receive)
    print("설명 :" + fix_content_receive)
    print("수정 data input complete")

    db.write_info.update_one({
        'title': title_receive,
        'date': date_receive,
        'place': place_receive,
        'attendance': attendance_receive,
        'content': content_receive,
        'writeID': id_receive,
        'count': int_like
    }, {'$set': {
        'title': fix_title_receive,
        'date': fix_date_receive,
        'place': fix_place_receive,
        'attendance': fix_attendance_receive,
        'content': fix_content_receive
    }})

    return jsonify({'msg': '모집 수정완료!'})

# 참가 신청관련 -------------------------------------------------------------------------
@app.route('/memo/tj', methods=['POST'])
def tj_card():
    # 해당 상세카드 data를 가져와 각각 변수지정
    title_receive = request.form['title_give']
    date_receive = request.form['date_give']
    attendance_receive = request.form['attendance_give']
    place_receive = request.form['place_give']
    content_receive = request.form['content_give']
    id_receive = request.form['id_give']
    like_receive = request.form['like_give']

    # 현재 like_receive로 가져운 count값이 str형식이므로 int형으로 변환
    int_like = int(like_receive);

    # 앞에 조건들은 부합하는 데이터를 찾기위한 조건 filter들
    # $set관련 부분은 int형으로 변환한 count값에 1추가 // 참가신청기능
    db.write_info.update_one({
        'title': title_receive,
        'date': date_receive,
        'place': place_receive,
        'attendance': attendance_receive,
        'content': content_receive,
        'writeID': id_receive,
        'count': int_like
    }, {'$set': {
        'count': int_like + 1,
    }})

    return jsonify({'msg': '참가신청 되었습니다!'})
# 참가 포기관련 -------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
   app.run('0.0.0.0',port=5002,debug=True)