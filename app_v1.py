from flask import Flask, render_template, request, session, flash, send_file,redirect
from Customer import read_data
import os
from datetime import datetime
import pandas as pd
import string
import random

path = os.path.join(os.getcwd(),"static","ds.xlsx")
path_backup = os.path.join(os.getcwd(),"static","backup","queue")
path_result = os.path.join(os.getcwd(),"static","backup","complete")
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'memcached'


global list_cus_mark, list_cus, all_list_cus_mark, list_completed,setdis, config, dtim_POS, counter_dis, list_pw
counter_dis = dict()
dtim_POS = list()
list_cus = dict()
setdis = set()
list_completed = list()
list_pw = list()


config = dict()
global PASSWORD
PASSWORD = "techhaus"
number_POS = 50
key_cus_mark = ["queue" + str(i) for i in range(number_POS)]
list_cus_mark = [[] for i in range(number_POS)]
all_list_cus_mark = dict(zip(key_cus_mark,list_cus_mark))
try:
    session['logged_in'] = False
except Exception as e:
    print(e)

def rm_all(path):
    for i in os.listdir(path):
        try:
            os.remove(path + "/" + i)
        except:
            continue

def save_backup(content,namefile):
    s = ""
    for li in content:
        for i in li:
            s += str(i.get("bib")) + "\t"
        s += "\n"
    with open(path_backup + "/" + namefile + ".txt","w") as fw:
        fw.write(s)

def save_compelete(content):
    s = ""
    for i in content:
        s += i[0] + "\t" + i[1] + "\t"  + str(i[2]) + "\n"
    with open(path_result + "/complete.txt","a") as fw:
        fw.write(s)

def load_complete():
    namefile = path_result + "/complete.txt"
    with open(namefile, "r") as f:
        for i in f:
            tmp = i.strip("\n").split("\t")
            list_completed.append(tmp[0])
            list_cus.get(tmp[0]).set_pick(tmp[2])
            list_cus.get(tmp[0]).set_pickedup(tmp[1])



def load_backup(content, namefile):
    with open(namefile,"r") as fr:
        for line in fr:
            sub = list()
            for bib in line.strip("\n").split("\t"):
                if bib.strip("\t").strip("\n") != "" and bib.strip("\t").strip("\n") not in list_completed:
                    sub.append(list_cus.get(bib).__dict__)
            content.append(sub)

def randompass():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(6))


@app.route('/admin/',methods=['POST','GET'])
def admin():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        number_pos = [x for x in range(number_POS)]
        data = {"noPOS": number_pos,
                "distance": setdis}
        return render_template("index.html",value=data)

@app.route('/upload', methods=['POST'])
def do_upload():
    try:
        form1 = request.files['file']
        form1.save(path)

        list_cus.clear()
        setdis.clear()

        data_cus_total, dis_total = read_data(path)

        for i in dis_total:
            setdis.add(i)
        for i in setdis:
            counter_dis.update({i:[0,0]})

        for key, val in data_cus_total.items():
            list_cus.update({key:val})
            counter_dis[val.distance][1] += 1

    except Exception as e:
        print(e)

    return redirect("/admin")

@app.route('/config', methods=['POST'])
def do_config():
    try:
        list_pw.clear()
        list_req = request.form.lists()
        key = list()
        val = list()
        for i in list_req:
            key.append(i[0])
            val.append(i[1])
            list_pw.append(randompass())
        config.update(dict(zip(key,val)))
    except Exception as e:
        print(e)
    return redirect("/admin")

@app.route('/load', methods=['POST'])
def do_load_Backup():
    load_complete()
    try:

        key_admin = request.form.get("key_admin")
        if key_admin == "1":
            for i in os.listdir(path_backup):
                path_file = os.path.join(path_backup,i)
                key = i.strip(".txt")
                load_backup(all_list_cus_mark.get(key),path_file)
    except Exception as e:
        print(e)
    return redirect("/admin")

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['pw'] == "techhaus":
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return redirect("/admin")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect("/admin")

@app.route("/session_destroy",methods=["POST","GET"])
def destroy_session():
    session["index_session"] = None
    return redirect("/machine")

@app.route("/create_session",methods=["POST","GET"])
def init():
    try:
        id = int(request.form["index"]) - 1
        passw = request.form["pw"]
    except:
        return render_template("init.html", value={"error": "1"})

    if id > 50 or id < 0:
        return render_template("init.html", value={"error": "1"})

    if id >= len(list_pw):
        return render_template("init.html", value={"error": "3"})

    if list_pw[id] != passw:
        return render_template("init.html", value={"error": "2"})
    session["index_session"] = id
    return redirect("/machine")

@app.route('/machine',methods=["POST","GET"])
def refresh_data():
    if not session.get("index_session") and session.get("index_session") != 0:
        return render_template("init.html", value={"error": "0"})
    else:
        return render_template('clerk_page.html',value={"error": "1","id":session.get("index_session")})

@app.route('/update_data',methods=['POST','GET'])
def update_data():
    id = int(request.form["key"])
    loconf = config.get(str(id))
    if loconf:
        if loconf[0] != "True":
            data = {"data":list_cus_mark[id],
                    "error": "1"}
        else:
            data = {"data":list_cus_mark[id],
                    "error": "2"}
        return render_template("component.html", value=data)
    else:
        data = {"data":list_cus_mark[0],
                "error": "2"}
        return render_template("component.html", value=data)

@app.route('/modify_data',methods=['POST','GET'])
def modify_data():
    form = request.form.lists()
    key_delete = [x for x in form]
    id = int(request.form.get("id_pos"))
    loconf = config.get(str(id))
    if len(key_delete) != 0:
        if loconf[0] != "True":
            if len(list_cus_mark[id]) > 0:
                key_delete = key_delete[1][1][0]
                value = list_cus.get(key_delete).__dict__
                list_cus.get(key_delete).set_pickedup(datetime.now().__str__().split(".")[0])
                dtim_POS.append((datetime.now().__str__().split(".")[0],id))
                list_cus_mark[id].remove([value])
                list_completed.append(value.get("bib"))
                counter_dis[value.get("distance")][0] += 1
                save_compelete([[key_delete,datetime.now().__str__(),id]])
                save_backup(list_cus_mark[id],key_cus_mark[id])
        else:
            if len(list_cus_mark[id]) > 0:
                sub_list = []
                key_delete = key_delete[1][1]
                sub_complete = list()
                for i in key_delete:
                    value = list_cus.get(i).__dict__
                    sub_list.append(value)
                    list_completed.append(value.get("bib"))
                    list_cus.get(i).set_pickedup(datetime.now().__str__())
                    dtim_POS.append((datetime.now().__str__(),id))
                    counter_dis[value.get("distance")][0] += 1
                    sub_complete.append([i,datetime.now().__str__(),id])
                list_cus_mark[id].remove(sub_list)
                save_compelete(sub_complete)
                save_backup(list_cus_mark[id],key_cus_mark[id])

    return redirect("/machine")

@app.route('/', methods=["POST","GET"])
def customer():
    lis_cus_queue = [z.get("bib")  for x in list_cus_mark for y in x for z in y]
    list_valid = []
    requests = request.form.lists()
    POS_checked = []
    POS_checking = []

    key_form = [x for x in requests]
    if len(key_form) < 1:
        return render_template("search_page.html",value={"error": "0"})
    if key_form[0][0] == "id_search" and key_form[0][1][0] != "":
        key = key_form[0][1][0]
        for k,i in list_cus.items():
            if i.compare(key):
                if i.bib not in list_completed and i.bib not in lis_cus_queue :
                    list_valid.append(i.__dict__)
                if i.bib in list_completed:
                    POS_checked.append([i.pPOS,i.dtime])
                if i.bib in lis_cus_queue:
                    POS_checking.append(i.pPOS)
        if len(list_valid) != 0:
            data = {"data":list_valid,
                    "error": "2"}
            return render_template("search_page.html", value=data)
        elif POS_checked.__len__() == 1:
            return render_template("search_page.html", value={"error":"5",
                                                              "POS": POS_checked[0][0],
                                                              "time": POS_checked[0][1] })
        elif POS_checking.__len__() == 1:
            return render_template("search_page.html", value={"error":"4",
                                                              "POS": POS_checking[0]})
        else:
            return render_template("search_page.html", value={"error":"3"})

    elif key_form[1][0] == "bib":
        if len(key_form[1][1]) < 2:
            index = 0
            lenpos = 999999
            key_complete = key_form[1][1][0]
            cus = list_cus.get(key_complete)
            for idx in range(len(config)):
                distance = config.get(str(idx))[0]
                if str(cus.distance) == str(distance):
                    if len(list_cus_mark[idx]) < lenpos :
                        lenpos = len(list_cus_mark[idx])
                        index = idx
            cus.set_pick(index + 1)
            list_cus_mark[index].append([cus.__dict__])
            save_backup(list_cus_mark[index],key_cus_mark[index])
            data = {"POS":index,
                    "error": "1"}

            return render_template("search_page.html", value=data)
        else:
            index_group = 0
            len_group = 9999999
            for i_g in range(len(config)):
                group = config.get(str(i_g))[0]
                if group == "True":
                    if len(list_cus_mark[i_g]) < len_group:
                        len_group = len(list_cus_mark[i_g])
                        index_group = i_g
            key_group = key_form[1][1]
            sub_list = []
            for i_c in key_group:
                cus = list_cus.get(i_c)
                cus.set_pick(index_group)
                sub_list.append(cus.__dict__)
            list_cus_mark[index_group].append(sub_list)
            save_backup(list_cus_mark[index_group],key_cus_mark[index_group])
            data = {"POS":index_group,
                    "error": "1"}
            return render_template("search_page.html", value=data)

@app.route('/download',methods=["GET","POST"])
def downloadFile ():

    data_file = {"bib":[],
                 "name":[],
                 "code":[],
                 "distance":[],
                 "passport":[],
                 "phone":[],
                 "dtime":[],
                 "pPOS":[]}

    for i in list_completed:
        cus = list_cus.get(i)
        data_file.get("bib").append(i)
        data_file.get("name").append(cus.name)
        data_file.get("code").append(cus.code)
        data_file.get("distance").append(cus.distance)
        data_file.get("passport").append(cus.passport)
        data_file.get("phone").append(cus.phone)
        data_file.get("dtime").append(cus.dtime)
        data_file.get("pPOS").append(cus.pPOS)
    df = pd.DataFrame.from_dict(data_file)
    name_file = path_result + "/resutl.xlsx"
    df.to_excel(name_file)
    return send_file(name_file, as_attachment=True)

@app.route('/clear')
def clear():
    rm_all(path_backup)
    rm_all(path_result)
    return admin()

@app.route("/admin/live/",methods=["GET","POST"])
def admin_live():
    return render_template("live_admin.html",value={"total":len(list_cus)})

@app.route("/completed",methods=["GET"])
def count_complete():
    return render_template("couter.html",value=counter_dis,total=[len(list_completed),len(list_cus)])

@app.route("/live",methods=["GET","POST"])
def live():
    res = []
    for i in list_completed:
        res.append(list_cus.get(i).__dict__)

    return render_template("compont_admin.html",value=res)

@app.route("/info",methods=["POST","GET"])
def info():
    key_form = request.form.get('id_search')
    list_valid = []
    if key_form != None:
        for k,i in list_cus.items():
            if i.compare(str(key_form)):
                list_valid.append(i.__dict__)
        if len(list_valid) != 0:
            data = {"data":list_valid,
                    "error": "2"}
            return render_template("search_information.html", value=data)
        else:
            return render_template("search_information.html", value={"error":"3"})
    else:
        return render_template("search_information.html", value={"error":"0"})

@app.route("/cf",methods=["GET","POST"])
def c():
    k = [int(key) for key,val in config.items()]
    v = [val for key,val in config.items()]
    value = list()

    for idx in range(len(list_pw)):

        value.append([k[idx], v[idx], list_pw[idx]])

    return render_template("cf.html",value=value)
if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'memcached'
    app.run(debug=True,port=8000)