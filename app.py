from flask import Flask, render_template, Response , redirect, request, url_for
from Customer import read_data
import os
path = os.path.join(os.getcwd(),"static","ds.xlsx")
path_backup = os.path.join(os.getcwd(),"static","backup","queue")
app = Flask(__name__)
global list_cus_mark, list_cus, all_list_cus_mark, list_completed,setdis, config
list_cus = read_data(path)[0]
setdis = read_data(path)[1]
list_completed = list()
config = dict()
number_POS = 2
key_cus_mark = ["queue" + str(i) for i in range(number_POS)]
list_cus_mark = [[] for i in range(number_POS)]
all_list_cus_mark = dict(zip(key_cus_mark,list_cus_mark))

def save_backup(content,namefile):
    s = ""
    for li in content:
        for i in li:
            s += str(i.get("bib")) + "\t"
        s += "\n"
    with open(path_backup + "/" + namefile + ".txt","w") as fw:
        fw.write(s)

def load_backup(content, namefile):
    with open(namefile,"r") as fr:
        for line in fr:
            sub = list()
            for bib in line.strip("\n").split("\t"):
                if bib.strip("\t").strip("\n") != "":
                    sub.append(list_cus.get(bib).__dict__)
            content.append(sub)



@app.route('/admin/',methods=['POST','GET'])
def admin():
    key_admin = request.form.get("key_admin")
    list_req = request.form.lists()
    if key_admin == "1":
        for i in os.listdir(path_backup):
            path_file = os.path.join(path_backup,i)
            key = i.strip(".txt")
            load_backup(all_list_cus_mark.get(key),path_file)
        return render_template("ádfasd/init_session.html")
    elif key_admin == "0":
        number_pos = [x for x in range(number_POS)]
        data = {"noPOS": number_pos,
                "distance": setdis}
        return render_template("ádfasd/option_admin.html", value=data)
    elif list_req:
        key = list()
        val = list()
        for i in list_req:
            key.append(i[0])
            val.append(i[1])
        config.update(dict(zip(key,val)))
        return render_template("admin.html")
    else:
        return render_template("admin.html")

@app.route('/customer0/', methods=["POST","GET"])
def post_index():
    list_valid = []
    requests = request.form.lists()
    loconf = config.get("0")
    key_form = [x for x in requests]
    if len(key_form) < 1:
        return render_template("ádfasd/customer.html")
    if key_form[0][0] == "id_search":
        key = key_form[0][1][0]
        if loconf[0] != "True":
            for k,i in list_cus.items():
                if i.compare(key):
                    if i.bib not in list_completed and str(i.distance) == loconf[0]:
                        list_valid.append(i.__dict__)
            if len(list_valid) != 0:
                data = {"data":list_valid,
                        "error": "1"}
                return render_template("ádfasd/res_customer.html", value=data)
            else:
                return render_template("ádfasd/notfound.html", value=list_valid)
        else:
            for k,i in list_cus.items():
                if i.compare(key):
                    if i.bib not in list_completed:
                        list_valid.append(i.__dict__)
            if len(list_valid) != 0:
                data = {"data":list_valid,
                        "error": "2"}
                return render_template("ádfasd/res_customer.html", value=data)
            else:
                return render_template("ádfasd/notfound.html", value=list_valid)

    elif key_form[0][0] == "bib":
        if loconf[0] != "True":
            key_complete = key_form[0][1][0]
            list_cus_mark[0].append([list_cus.get(key_complete).__dict__])
            save_backup(list_cus_mark[0],key_cus_mark[0])
            return render_template("ádfasd/init_session.html")
        else:
            key_complete = key_form[0][1]
            sub_list = []
            for i in key_complete:
                sub_list.append(list_cus.get(i).__dict__)
            list_cus_mark[0].append(sub_list)
            save_backup(list_cus_mark[0],key_cus_mark[0])
            return render_template("ádfasd/init_session.html")

@app.route('/clerk0/', methods=["POST","GET"])
def index_clerk():
    form = request.form.lists()
    key_delete = [x for x in form]
    loconf = config.get("0")
    if loconf[0] != "True":
        data = {"data":list_cus_mark[0],
                "error": "1"}
    else:
        data = {"data":list_cus_mark[0],
                "error": "2"}
    print(list_cus_mark[0])
    if len(key_delete) != 0:
        if loconf[0] != "True":
            if len(list_cus_mark[0]) > 0:
                key_delete = key_delete[0][1][0]
                value = list_cus.get(key_delete).__dict__
                list_cus_mark[0].remove([value])
                list_completed.append(value.get("bib"))
                save_backup(list_cus_mark[0],key_cus_mark[0])
        else:
            if len(list_cus_mark[0]) > 0:
                sub_list = []
                key_delete = key_delete[0][1]
                for i in key_delete:
                    value = list_cus.get(i).__dict__
                    sub_list.append(value)
                    list_completed.append(value.get("bib"))
                list_cus_mark[0].remove(sub_list)
                save_backup(list_cus_mark[0],key_cus_mark[0])


    return render_template("ádfasd/clerk.html", value=data)

#####------------------pair2---------------------############
@app.route('/customer1/', methods=["POST","GET"])
def post_index1():
    list_valid = []
    requests = request.form.lists()
    loconf = config.get("1")
    key_form = [x for x in requests]
    if len(key_form) < 1:
        return render_template("ádfasd/customer.html")
    if key_form[0][0] == "id_search":
        key = key_form[0][1][0]
        if loconf[0] != "True":
            for k,i in list_cus.items():
                if i.compare(key):
                    if i.bib not in list_completed and str(i.distance) == loconf[0]:
                        list_valid.append(i.__dict__)
            if len(list_valid) != 0:
                data = {"data":list_valid,
                        "error": "1"}
                return render_template("ádfasd/res_customer.html", value=data)
            else:
                return render_template("ádfasd/notfound.html", value=list_valid)
        else:
            for k,i in list_cus.items():
                if i.compare(key):
                    if i.bib not in list_completed:
                        list_valid.append(i.__dict__)
            if len(list_valid) != 0:
                data = {"data":list_valid,
                        "error": "2"}
                return render_template("ádfasd/res_customer.html", value=data)
            else:
                return render_template("ádfasd/notfound.html", value=list_valid)

    elif key_form[0][0] == "bib":
        if loconf[0] != "True":
            key_complete = key_form[0][1][0]
            list_cus_mark[1].append([list_cus.get(key_complete).__dict__])
            save_backup(list_cus_mark[1],key_cus_mark[1])
            return render_template("ádfasd/init_session.html")
        else:
            key_complete = key_form[0][1]
            sub_list = []
            for i in key_complete:
                sub_list.append(list_cus.get(i).__dict__)
            list_cus_mark[1].append(sub_list)
            save_backup(list_cus_mark[1],key_cus_mark[1])
            return render_template("ádfasd/init_session.html")

@app.route('/clerk1/', methods=["POST","GET"])
def index_clerk1():
    form = request.form.lists()
    key_delete = [x for x in form]
    loconf = config.get("1")
    if loconf[0] != "True":
        data = {"data":list_cus_mark[1],
                "error": "1"}
    else:
        data = {"data":list_cus_mark[1],
                "error": "2"}
    if len(key_delete) != 0:
        if loconf[0] != "True":
            if len(list_cus_mark[1]) > 0:
                key_delete = key_delete[0][1][0]
                value = list_cus.get(key_delete).__dict__
                list_cus_mark[1].remove([value])
                list_completed.append(value.get("bib"))
                save_backup(list_cus_mark[1],key_cus_mark[1])
        else:
            if len(list_cus_mark[1]) > 0:
                sub_list = []
                key_delete = key_delete[0][1]
                for i in key_delete:
                    value = list_cus.get(i).__dict__
                    sub_list.append(value)
                    list_completed.append(value.get("bib"))
                list_cus_mark[1].remove(sub_list)
                save_backup(list_cus_mark[1],key_cus_mark[1])


    return render_template("ádfasd/clerk.html", value=data)
#####------------------pair2---------------------############

#####------------------pair2---------------------############
#####------------------pair2---------------------############
#####------------------pair2---------------------############
#####------------------pair2---------------------############
#####------------------pair2---------------------############
#####------------------pair2---------------------############
#####------------------pair2---------------------############
#####------------------pair2---------------------############
#####------------------pair2---------------------############


if __name__ == '__main__':
    app.run(debug=True)