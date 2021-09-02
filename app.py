 #-*- coding:utf-8 -*-

import os
import config
from flask import Flask, request, render_template, Response, redirect, url_for, flash
from werkzeug.utils import secure_filename


app = Flask(__name__)

IP_ADDR = config.IP_HOME
IP_ADDR_OUT = config.IP_OUT
PORT = config.PORT_NO

app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
FILE_NAME=''
FILE_COUNT = 1

@app.route('/')
def home():
    global FILE_NAME
    FILE_NAME = ''
    return render_template('upload.html', IP_ADDR=IP_ADDR_OUT, PORT=PORT)

@app.route('/render/<int:year>/<int:month>')
def render_by_month(year, month):
    list_time = []
    list_time_new = []
    list_teller = []
    list_teller_new = []
    list_teller_idx = []
    list_teller_idx_new = []
    list_msg = []
    list_msg_new = []
    target_year = str(year)+'년'
    target_month = str(month)+'월'
    b_exit_flag = False
    b_init_flag = "0"
    HTML = 'talkThemeMonth.html'

    list_time, list_teller, list_teller_idx, list_msg = process_data()

    for index, value in enumerate(list_time):
        if index < 2:
            list_time_new.append(list_time[index])
            list_teller_new.append(list_teller[index])
            list_teller_idx_new.append(list_teller_idx[index])
            list_msg_new.append(list_msg[index])
            continue

        list_temp = value.split(' ', maxsplit=3)
        if len(list_temp) < 3:
            flash('Error while render_by_month: contact collinahn@gmail.com')
            return redirect('/')
        if list_temp[0].strip() == target_year and list_temp[1].strip() == target_month:
            list_time_new.append(list_time[index])
            list_teller_new.append(list_teller[index])
            list_teller_idx_new.append(list_teller_idx[index])
            list_msg_new.append(list_msg[index])
            b_exit_flag = True
            continue

        if b_exit_flag == True:
            list_time_new.append(' ')
            list_teller_new.append('INFO')
            list_teller_idx_new.append('1')
            list_msg_new.append(':D')

            list_time_new.append(' ')
            list_teller_new.append('INFO')
            list_teller_idx_new.append('0')
            list_msg_new.append(target_year + ' ' + target_month + '에 나눈 대화입니다.')
            return render_template(HTML, list_time=list_time_new, list_teller=list_teller_new, list_teller_idx=list_teller_idx_new, list_msg=list_msg_new, b_init_flag=b_init_flag)
    
    if b_exit_flag == True:
        list_time_new.append(' ')
        list_teller_new.append('INFO')
        list_teller_idx_new.append('1')
        list_msg_new.append(':D')

        list_time_new.append(' ')
        list_teller_new.append('INFO')
        list_teller_idx_new.append('0')
        list_msg_new.append(target_year + ' ' + target_month + '에 나눈 대화입니다.')
        return render_template(HTML, list_time=list_time_new, list_teller=list_teller_new, list_teller_idx=list_teller_idx_new, list_msg=list_msg_new, b_init_flag=b_init_flag)
    
    list_time_new.append(' ')
    list_teller_new.append('INFO')
    list_teller_idx_new.append('1')
    list_msg_new.append(':C')

    list_time_new.append(' ')
    list_teller_new.append('INFO')
    list_teller_idx_new.append('0')
    list_msg_new.append(target_year + ' ' + target_month + '에 나눈 대화가 없습니다.\n \'../render/2021/07\' 형식으로 다시 시도해보세요.')
    return render_template(HTML, list_time=list_time_new, list_teller=list_teller_new, list_teller_idx=list_teller_idx_new, list_msg=list_msg_new, b_init_flag=b_init_flag)


@app.route('/render/0')
def render_first():
    list_time = []
    list_teller = []
    list_teller_idx = []
    list_msg = []
    b_init_flag = "1"
    HTML = 'talkThemeMonth.html'

    list_time, list_teller, list_teller_idx, list_msg = process_data()

    return render_template(HTML, \
        list_time=list_time, list_teller=list_teller, list_teller_idx=list_teller_idx, list_msg=list_msg, \
        b_init_flag=b_init_flag)


@app.route('/render')
def render_last():
    list_time = []
    list_teller = []
    list_teller_idx = []
    list_msg = []
    HTML = 'talkTheme.html'

    list_time, list_teller, list_teller_idx, list_msg = process_data()

    return render_template(HTML, \
        list_time=list_time, list_teller=list_teller, list_teller_idx=list_teller_idx, list_msg=list_msg)


@app.route('/process', methods = ['GET', 'POST'])
def getdata():
    global FILE_NAME
    global FILE_COUNT
    FILE_NAME = ''
    try:
        if request.method == 'POST':    
            #없는경우
            if request.files['file'].filename == '':
                flash('No selected file')
                return redirect(url_for('/'))
            
            file = request.files['file']
                
            if file and allowed_file(file.filename):
                FILE_NAME = str(FILE_COUNT) + secure_filename(file.filename)

                # 업로드 ( .save(경로) )
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], FILE_NAME))
                FILE_COUNT += 1
                return redirect('/render')
            flash("Invalid File Format")
    except Exception as e:
        flash(e)
        return redirect('/')

# 파일이 허락된 형식인지검사
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1).pop().lower() in ALLOWED_EXTENSIONS


def process_data():
    global FILE_NAME
    list_time = []
    list_teller = []
    list_teller_idx = []
    list_msg = []
    name_participants = set()
    name_me = ''
    try:
        file_path = config.UPLOAD_FOLDER + FILE_NAME
        print(file_path)

        if FILE_NAME == '':
            flash("No file selected")
            return [], [], [], []

        with open(file_path, 'r', encoding='UTF-8-sig') as f:
            list_time, list_teller, list_msg, name_participants, name_me = \
                extract_data(f, list_time, list_teller, list_msg, name_participants)

        result_idx = '0'
        result_name = ''
        result_time = ''
        for index, value in enumerate(list_teller):
            if (value in name_participants) == True:
                if value != name_me:
                    list_teller_idx.append('1')     #상대방
                    result_idx = '1'
                    result_name = value
                    result_time = list_time[index]
                else:
                    list_teller_idx.append('0')     #자기자신
                    result_idx = '0'
                    result_time = list_time[index]
            else:
                list_teller[index] = result_name
                list_time[index] = result_time
                list_teller_idx.append(result_idx)

        print("length of each list(should be all-same):", \
            len(list_time), len(list_teller), len(list_teller_idx), len(list_msg))
        print("참여자:", name_participants, "나:", name_me)

        s = set([len(list_time), len(list_teller), len(list_teller_idx), len(list_msg)])
        if len(s) != 1:
            flash('warning: illegal format included in file\n contact collinahn@gmail.com for further details')
            FILE_NAME = ''
            return [], [], [], []

    except Exception as e:
        print(e)
        flash('warning: illegal format included') 
        return [], [], [], []

    return list_time, list_teller, list_teller_idx, list_msg


def extract_data(f, list_time, list_teller, list_msg, name_participants):
    name_me = f.readline()
    name_me = name_me[0:-11].strip()

    str_dividend = '=============v1.0============='
    str_copyright = '\nengine made by taeyoung\n \
        아직 로그인 및 세션 분리를 구현하지 않았습니다.\n \
        그룹 대화는 피아를 구분하지 못할 수도 있습니다.\n \
        현재 페이지 링크 공유시 웹페이지에 로드된 개인적 대화 내용이 유출될 수 있습니다.\n \
        첨부한 txt파일은 서버의 임시 메모리에 저장이 되었다가, 초기 화면(텍스트파일 첨부페이지)에서 새로고침하면 자동으로 파기됩니다.\n'
    str_participant = '>> ' + name_me + '님과의 대화를 불러옵니다. <<\n'
    str_info = f.readline()
    list_time.append(' ')
    list_teller.append(name_me)
    list_msg.append(str_dividend + str_copyright + str_dividend)

    list_time.append(' ')
    list_teller.append(name_me)
    list_msg.append(str_participant + str_info)

    
    for line in f:
        if line == '\n':
            continue
        
        #메시지에 뉴라인 문자가 포함된 경우 앞에 년도가 붙지 않는다.
        if not (line[0:2] == "20" and line[4] == "년") :
            list_time.append('-1')
            list_teller.append('-1')
            list_msg.append(line)
            continue

        if line.find(',') == -1:
            continue

        list_splitfirst = line.split(',', maxsplit=1)
        if len(list_splitfirst) == 2:
            if len(list_splitfirst[0]) < 18:
                list_time.append('-1')
                list_teller.append('-1')
                list_msg.append(line)
                continue
            list_time.append(list_splitfirst[0])
            list_splitsecond = list_splitfirst[1].split(':', maxsplit=1)
            if len(list_splitsecond) == 2:
                list_teller.append(list_splitsecond[0].strip())
                name_participants.add(list_splitsecond[0].strip())
                list_msg.append(list_splitsecond[1].lstrip())
            else:
                list_teller.append('-1')
                list_msg.append('\t**알림**\n 메시지 처리 형식에 어긋나 메시지를 추출하지 못하였습니다. txt파일을 직접 확인하세요')

        else:
            list_time.append('-1')
            list_teller.append('-1')
            list_msg.append('\t**알림**\n메시지 처리 형식에 어긋나 메시지를 추출하지 못하였습니다. txt파일을 직접 확인하세요')

    return list_time, list_teller, list_msg, name_participants, name_me


if __name__ == '__main__':
    app.secret_key = config.SECRET_KEY
    app.config['SESSION_TYPE'] = 'filesystem'

    app.debug = False
    app.run(host = config.IP_ADDR, port = config.PORT)