from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import os
from django.core.files.storage import FileSystemStorage
import pymysql
from datetime import date
from keras.models import model_from_json
import cv2
import io
import base64
import numpy as np
import matplotlib.pyplot as plt

global uname, utype, advice_user, advice_img
plants = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
          'Corn_(maize)___Common_rust_', 'Corn_(maize)___healthy', 'Corn_(maize)___Northern_Leaf_Blight', 'Grape___Black_rot', 'Grape___Esca_(Black_Measles)',
          'Grape___healthy', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight',
          'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
          'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tomato___Tomato_mosaic_virus', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus']


fertilizers = []
with open("messages.txt", "r") as file:
    for line in file:
        line = line.strip('\n')
        line = line.strip()
        fertilizers.append(line)
file.close()

def getModel():
    with open('model/model.json', "r") as json_file:
        loaded_model_json = json_file.read()
        model = model_from_json(loaded_model_json)
    json_file.close()    
    model.load_weights("model/model_weights.h5")
    model._make_predict_function()
    return model

def getFertilizer(name):
    global fertilizers
    details = "Fertilizer Details Not Available"
    for i in range(len(fertilizers)):
        arr = fertilizers[i].split(":")
        arr[0] = arr[0].strip()
        arr[1] = arr[1].strip()
        if arr[0] == name:
            details = arr[1]
            break
    return details        

def AutoDiseaseAction(request):
    if request.method == 'POST':
        global uname
        filename = request.FILES['t1'].name
        image = request.FILES['t1'].read() #reading uploaded file from user
        if os.path.exists("FarmerApp/static/"+filename):
            os.remove("FarmerApp/static/"+filename)
        with open("FarmerApp/static/"+filename, "wb") as file:
            file.write(image)
        file.close()
        model = getModel()
        img = cv2.imread("FarmerApp/static/"+filename)
        img = cv2.resize(img, (64,64))
        im2arr = np.array(img)
        im2arr = im2arr.reshape(1,64,64,3)
        test = np.asarray(im2arr)
        test = test.astype('float32')
        test = test/255
        preds = model.predict(test)
        predict = np.argmax(preds)
        img = cv2.imread("FarmerApp/static/"+filename)
        img = cv2.resize(img, (800,400))
        output = 'Crop Disease Recognize as : '+plants[predict]+"<br/>Remedies & Pesticidies = "+getFertilizer(plants[predict])
        cv2.putText(img, 'Crop Disease Recognize as : '+plants[predict], (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,0.8, (0, 255, 255), 2)
        plt.imshow(img)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        img_b64 = base64.b64encode(buf.getvalue()).decode()    
        context= {'data':output, 'img': img_b64}
        return render(request, 'UserScreen.html', context)

def Planning(request):
    if request.method == 'GET':
       return render(request, 'Planning.html', {})  

def PlanningAction(request):
    if request.method == 'POST':
        crop = request.POST.get('t1', False)
        with open("Planning/"+crop+".txt", "r", encoding='utf-8') as file:
            lines = file.readlines()
        file.close()
        data = ""
        for i in range(len(lines)):
            data += lines[i]+"<br/><br/>"
        context= {'data':data}
        return render(request, 'UserScreen.html', context)        

def AutoDisease(request):
    if request.method == 'GET':
       return render(request, 'AutoDisease.html', {})  

def AdminLoginAction(request):
    if request.method == 'POST':
        global uname
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        page = "AdminLogin.html"
        status = "Invalid Login" 
        if "admin" == username and "admin" == password:
            page = "AdminScreen.html"
            status = "Welcome Admin"
        context= {'data': status}
        return render(request, page, context)

def CheckAdviceStatus(request):
    if request.method == 'GET':
        global uname
        cols = ['Farmer ID', 'Symptoms', 'Crop Image', 'Expert Advice', 'Request Date']
        output = '<table border="1" align="center" width="100%"><tr>'
        font = '<font size="" color="black">'
        for i in range(len(cols)):
            output += "<td>"+font+cols[i]+"</font></td>"
        output += "</tr>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM query where email='"+uname+"'")
            rows = cur.fetchall()
            for row in rows:
                output += "<tr><td>"+font+str(row[0])+"</font></td>"
                output += "<td>"+font+str(row[1])+"</font></td>"
                output+='<td><img src="/static/files/'+row[2]+'" width="200" height="200"></img></td>'
                output += "<td>"+font+str(row[3])+"</font></td>"
                output += "<td>"+font+str(row[4])+"</font></td></tr>"                               
        output += "</table><br/><br/><br/><br/>"    
        context= {'data':output}
        return render(request, "UserScreen.html", context) 

def SeekAdviceAction(request):
    if request.method == 'POST':
        global uname
        symptoms = request.POST.get('t1', False)
        filename = request.FILES['t2'].name
        image = request.FILES['t2'].read() #reading uploaded file from user
        if os.path.exists("FarmerApp/static/files/"+filename):
            os.remove("FarmerApp/static/files/"+filename)
        with open("FarmerApp/static/files/"+filename, "wb") as file:
            file.write(image)
        file.close()    
        upload_date = str(date.today())
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO query VALUES('"+str(uname)+"','"+symptoms+"','"+filename+"','Pending','"+upload_date+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        context= {'data':'Your request forwarded to experts. Please wait till expert replied'}
        return render(request, "UserScreen.html", context)       

def SeekAdvice(request):
    if request.method == 'GET':
       return render(request, 'SeekAdvice.html', {})  

def AdminLogin(request):
    if request.method == 'GET':
       return render(request, 'AdminLogin.html', {})  

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})  

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def UserLoginAction(request):
    if request.method == 'POST':
        global uname
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        page = "UserLogin.html"
        status = "Invalid login or account activation pending"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select email,password,usertype, person_name FROM signup where status='Activated'")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and password == row[1]:
                    uname = username
                    status = "Welcome "+row[3]
                    if row[2] == 'Farmer':
                        page = "UserScreen.html"
                    else:
                        page = "ExpertScreen.html"
                    break		
        context= {'data': status}
        return render(request, page, context)

def AdvicePageAction(request):
    if request.method == 'POST':
        global advice_user, advice_img
        advice = request.POST.get('t1', False)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update query set advice='"+advice+"' where email='"+advice_user+"' and image='"+advice_img+"'"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        context= {'data':'Your advice successfully updated to farmer account'}
        return render(request, "ExpertScreen.html", context)
        

def ViewRequestAction(request):
    if request.method == 'GET':
        global uname, advice_user, advice_img
        advice_user = request.GET.get('t1', False)
        advice_img = request.GET.get('t2', False)
        return render(request, "AdvicePage.html", {})

def ViewRequest(request):
    if request.method == 'GET':
        global uname
        cols = ['Farmer ID', 'Symptoms', 'Crop Image', 'Expert Advice', 'Request Date', 'Give Advice']
        output = '<table border="1" align="center" width="100%"><tr>'
        font = '<font size="" color="black">'
        for i in range(len(cols)):
            output += "<td>"+font+cols[i]+"</font></td>"
        output += "</tr>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM query where advice='Pending'")
            rows = cur.fetchall()
            for row in rows:
                output += "<tr><td>"+font+str(row[0])+"</font></td>"
                output += "<td>"+font+str(row[1])+"</font></td>"
                output+='<td><img src="/static/files/'+row[2]+'" width="200" height="200"></img></td>'
                output += "<td>"+font+str(row[3])+"</font></td>"
                output += "<td>"+font+str(row[4])+"</font></td>"
                output+='<td><a href=\'ViewRequestAction?t1='+str(row[0])+'&t2='+str(row[2])+'\'><font size=3 color=black>Click Here to Advice</font></a></td></tr>'   
        output += "</table><br/><br/><br/><br/>"    
        context= {'data':output}
        return render(request, "ExpertScreen.html", context)     

def ActivateProfileAction(request):
    if request.method == 'GET':
        global uname
        user = request.GET.get('t1', False)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update signup set status='Activated' where email='"+user+"'"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        context= {'data':'User profile successfully activated'}
        return render(request, "AdminScreen.html", context)  

def ActivateProfile(request):
    if request.method == 'GET':
        global uname
        cols = ['Person Name', 'Email ID', 'Password', 'Contact No', 'Address', 'User Type', 'Account Status', 'Activate Account']
        output = '<table border="1" align="center" width="100%"><tr>'
        font = '<font size="" color="black">'
        for i in range(len(cols)):
            output += "<td>"+font+cols[i]+"</font></td>"
        output += "</tr>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM signup")
            rows = cur.fetchall()
            for row in rows:
                output += "<tr><td>"+font+str(row[0])+"</font></td>"
                output += "<td>"+font+str(row[1])+"</font></td>"
                output += "<td>"+font+str(row[2])+"</font></td>"
                output += "<td>"+font+str(row[3])+"</font></td>"
                output += "<td>"+font+str(row[4])+"</font></td>"
                output += "<td>"+font+str(row[5])+"</font></td>"
                output += "<td>"+font+str(row[6])+"</font></td>"
                if row[6] == "Activated":
                    output += "<td>"+font+"---</font></td></tr>"
                else:
                    output+='<td><a href=\'ActivateProfileAction?t1='+str(row[1])+'\'><font size=3 color=black>Click Here to Activate</font></a></td></tr>'                
        output += "</table><br/><br/><br/><br/>"    
        context= {'data':output}
        return render(request, "AdminScreen.html", context)     
         

def SignupAction(request):
    if request.method == 'POST':
        person = request.POST.get('t1', False)
        email = request.POST.get('t2', False)
        password = request.POST.get('t3', False)
        contact = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        utype = request.POST.get('t6', False)        
        output = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select email FROM signup")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == email:
                    output = email+" Username already exists"
                    break
        if output == 'none':
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO signup VALUES('"+person+"','"+email+"','"+password+"','"+contact+"','"+address+"','"+utype+"','Pending')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                output = 'Signup Process Completed'
        context= {'data':output}
        return render(request, 'Signup.html', context)
      
def UpdateProfile(request):
    if request.method == 'GET':
        global uname
        person=""
        email=""
        password=""
        contact=""
        address=""
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM signup where email='"+uname+"'")
            rows = cur.fetchall()
            for row in rows:
                person = row[0]
                email = row[1]
                password = row[2]
                contact = row[3]
                address = row[4]                
        output = '<table align="center" width="30%">'
        output += '<tr><td><font size="3" color="black">Person&nbsp;Name</b></td><td><input name="t1" type="text" size="30" value="'+person+'"></td></tr>'
        output += '<tr><td><font size="3" color="black">Email&nbsp;ID</b></td><td><input type="text" name="t2" style="font-family: Comic Sans MS" size="30" value="'+uname+'" readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black">Password</b></td><td><input name="t3" type="password" size="30" value="'+password+'"></td></tr>'
        output += '<tr><td><font size="3" color="black">Contact&nbsp;No</b></td><td><input name="t4" type="Text" size="15" value="'+contact+'"></td></td></tr>'
        output += '<tr><td><font size="3" color="black">Address</b></td><td><input name="t5" type="Text" size="70" value="'+address+'"></td></td></tr>'
        output += '<tr><td></td><td><input type="submit" value="Submit"></td>'
        context= {'data':output}
        return render(request, 'UpdateProfile.html', context)

def UpdateProfileAction(request):
    if request.method == 'POST':
        global uname
        status = ""
        usertype = ""
        person = request.POST.get('t1', False)
        email = request.POST.get('t2', False)
        password = request.POST.get('t3', False)
        contact = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select usertype, status FROM signup where email='"+uname+"'")
            rows = cur.fetchall()
            for row in rows:
                usertype = row[0]
                status = row[1]
                break
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "delete from signup where email='"+uname+"'"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'farmerroute',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO signup VALUES('"+person+"','"+email+"','"+password+"','"+contact+"','"+address+"','"+usertype+"','"+status+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            output = 'Profile updated successfully'
        context= {'data':output}
        return render(request, 'UserScreen.html', context)
    


