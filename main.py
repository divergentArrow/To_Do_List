# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, url_for, redirect
import sqlite3 as SQL

app = Flask(__name__)

userLoggedIn = "" 

@app.route('/')
def login():
	return render_template('Login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
	msg=""
	if(request.method == 'POST'):
			mail = request.form['email']
			psw = request.form['psw']
			con=SQL.connect('users.db')
			cur = con.cursor()
			countUsers = con.execute("SELECT COUNT(UserID) FROM Login WHERE Username = ?;",(mail,))
			totalCount=countUsers.fetchone()[0]
			if(totalCount<1):#see if username already exists
				totalRows = con.execute("SELECT COUNT(UserID) FROM Login;")
				row = totalRows.fetchone()[0]
				if(row<1):
					newUserID = 1
				elif(row > 0 ):
					newUserID = row + 1
				ex = cur.execute("INSERT INTO Login (UserID,Username,Password) VALUES (?,?,?);",(newUserID,mail,psw))
				con.commit()
				global userLoggedIn
				userLoggedIn = mail
				return render_template('MainMenu.html')
			else:
				msg="Email already used, please use another email"
	        	con.rollback()
	        	return render_template('Login2.html', msg=msg)


@app.route('/verify', methods = ['GET','POST'])
def verify():
	if(request.method=='POST'):
		msg=""
		user=request.form['user']
		passWord = request.form['pass']
		global userLoggedIn
		con=SQL.connect('users.db')
		userList = con.execute("SELECT Username, Password FROM Login WHERE (Username=? AND Password=?);",(user,passWord))
		totalList=userList.fetchone()[0]
		if(totalList == 0): #no one with that name and/ or pass
			msg="Invalid Login Credentials"
			return render_template('Login2.html', msg=msg)
		else:
			userLoggedIn = user
			return render_template('MainMenu.html')


@app.route('/mainmenu')
def mainmenu():
    return render_template("MainMenu.html")
    
@app.route('/To_Do_List')
def viewList():
    con = SQL.connect('todo.db')
    global userLoggedIn
    cursor = con.execute("SELECT ID, Item, Due_Date, Category FROM ToDoList WHERE (UserID = ?);",(userLoggedIn,))
    return render_template('viewList.html', List = cursor.fetchall())

@app.route('/AddItemtoList')
def addItem():
    return render_template('addItemForm.html')

@app.route('/AddingResult', methods = ['POST', 'GET'])
def addItemResult():
    returnMessage = ""
    if(request.method == 'POST'):
        try:
            nme=request.form['nme']
            cat=request.form['cat']
            if(cat=='' or cat==' ' or cat=='None' or cat=='NA' or cat=='N/A' or cat=='none'):
            	cat=None
            dte=request.form['dte']
            if(dte=='' or dte==' ' or dte=='None' or dte=='NA' or dte=='N/A' or dte=='none'):
            	dte=None
            conn = SQL.connect('todo.db')
            cur=conn.cursor()
            exe = cur.execute("SELECT * FROM ToDoList Where ID = (SELECT MAX(ID) FROM ToDoList);")
            total = conn.execute("SELECT COUNT(Item) FROM ToDoList WHERE UserID=?;",(userLoggedIn,))
            print("total")
            row= total.fetchone()[0]
            if(row<1):
            	newID = 1
            elif(row > 0 ):
            	newID = row + 1
            ex = cur.execute("INSERT INTO ToDoList (ID, Item, Due_Date, Category, UserID) VALUES (?,?,?,?,?);",(newID,nme,dte,cat,userLoggedIn))
            conn.commit()
            returnMessage= "The item has been successfully added to your To-Do List!"
        except:
            conn.rollback()
            returnMessage = "There was an error adding an item to your To-Do List"
        finally:
            return render_template("addItemOutcome.html", returnMessage=returnMessage)

@app.route('/DeleteFromList')
def deleteItem():
	return render_template('deleteFromList.html')

@app.route('/DeleteItemResult', methods = ['POST', 'GET'])
def deleteResult():
	delMessage = ""
	if(request.method == 'POST'):
		try:
			global userLoggedIn
			nme=request.form['nme']
			dte=request.form['dte']
			con=SQL.connect('todo.db')
			cur=con.cursor()
			#ex = con.execute("DELETE FROM ToDoList WHERE (Item = ? AND Due_Date = ?);",(nme,dte))
			deleteit ="DELETE FROM ToDoList WHERE (Item = ? AND Due_Date = ? AND UserID=?);"
			if(dte=='' or dte==' ' or dte=='None' or dte=='NA' or dte=='N/A' or dte=='none'):
				dte=None
				deleteit ="DELETE FROM ToDoList WHERE (Item = ? AND UserID=? AND Due_Date IS NULL);"
				cur.execute(deleteit,(nme,userLoggedIn))
			else:
				cur.execute(deleteit,(nme,dte,userLoggedIn))
			#try using only item name and see if it works
			con.commit()
			delMessage="Item was deleted successfully"
		except:
			con.rollback()
			delMessage="there was an error in deleting the item from your to-do list"
		finally:
			return render_template("deleteResult.html", delMessage=delMessage)

@app.route('/deleteList')
def deleteAllList():
	message=""
	try:
		global userLoggedIn
		con=SQL.connect("todo.db")
		removeAll="DELETE FROM ToDoList WHERE UserID=?;"
		cur=con.cursor()
		cur.execute(removeAll,(userLoggedIn,))
		con.commit()
		message = "Successfully deleted To-Do List"
	except:
		con.rollback()
		message = "There was an error in deleting the List"
	finally:
		return render_template("deleteAll.html", message=message)

@app.route('/EditMenu')
def EditMenu():
	return render_template("EditMenu.html")

@app.route('/EditName')
def editName():
	return render_template("editName.html")

@app.route('/Edit_Item_Name_Result', methods=['GET','POST'])
def editNameResult():
	msg=""
	if(request.method=='POST'):
		try:
			nmeOld = request.form['nme1']
			dte = request.form['dte']
			if(dte=='' or dte==' 'or dte=='None' or dte=='NA' or dte=='N/A' or dte=='none'):
				dte=None
			nmeNew = request.form['nme2']
			con=SQL.connect('todo.db')
			cur=con.cursor()
			updateName = "UPDATE ToDoList SET Item = ? WHERE (Item = ? AND Due_Date = ? AND UserID=?);"
			if(dte==None):
				updateName = "UPDATE ToDoList SET Item = ? WHERE (Item = ? AND Due_Date IS NULL AND UserID =?);"
				cur.execute(updateName,(nmeNew,nmeOld,userLoggedIn))
			else:
				cur.execute(updateName,(nmeNew,nmeOld,dte,userLoggedIn))
			con.commit()
			msg="Successfully Updated Item Name"
		except:
			con.rollback()
			msg="There was an error in updating the item name"
		finally:
			return render_template('nameEditResult.html', msg=msg)
@app.route('/Edit_Due_Date')
def editDueDate():
	return render_template("editDueDate.html")

@app.route('/Edit_Due_Date_Result', methods = ['GET', 'POST'])
def editDueDateResult():
	msg=""
	if(request.method == 'POST'):
		global userLoggedIn
		try:
			nme=request.form['nme']
			dte1=request.form['dte1']
			
			dte2=request.form['dte2']
			if(dte2=='' or dte2==' ' or dte2=='None' or dte2=='NA' or dte2=='N/A' or dte2=='none'):
				dte2=None
			con=SQL.connect('todo.db')
			updateDate = "UPDATE ToDoList SET Due_Date = ? WHERE (Item = ? AND Due_Date = ? AND UserID = ?);"
			if(dte1=='' or dte1==' 'or dte1=='None' or dte1=='NA' or dte1=='N/A' or dte1=='none'):
				dte1=None
				updateDate = "UPDATE ToDoList SET Due_Date = ? WHERE (Item = ? AND UserID = ? AND Due_Date IS NULL);"
				con.execute(updateDate,(dte2,nme,userLoggedIn))
			else:
				con.execute(updateDate,(dte2,nme,dte1,userLoggedIn))
			con.commit()
			msg="Successfully Updated Due Date"
		except:
			con.rollback()
			msg="There was an error updating the Due Date"
		finally:
			return render_template('DueDateEditResult.html', msg=msg)

@app.route('/Edit_Category')
def editCategory():
	return render_template("EditCategory.html")

@app.route('/Edit_Category_Result', methods=['GET','POST'])
def categoryResult():
	messge=""
	if(request.method=='POST'):
		try:
			global userLoggedIn
			nme=request.form['nme']
			catOld=request.form['cat1']			
			catNew=request.form['cat2']
			con=SQL.connect('todo.db')
			cur=con.cursor()
			if(catNew=='' or catNew==' 'or catNew=='None' or catNew=='NA' or catNew=='N/A' or catNew=='none'):
				catNew=None
			catEdit="UPDATE ToDoList SET Category = ? WHERE (Item = ? AND Category = ? AND UserID=?);"
			if(catOld=='' or catOld==' ' or catOld=='None' or catOld=='NA' or catOld=='N/A' or catOld=='none'):
				catOld=None
				catEdit="UPDATE ToDoList SET Category = ? WHERE (Item = ? AND UserID = ? AND Category IS NULL);"
				cur.execute(catEdit,(catNew,nme,userLoggedIn))
			else:
				cur.execute(catEdit,(catNew,nme,catOld,userLoggedIn))
			con.commit()
			msg="Successfully Updated Item Category"
		except:
			con.rollback()
			msg="There was an error updating item category"
		finally:
			return render_template('EditCategoryOutcome.html', msg=msg)

if(__name__ == "__main__"):
   app.run(host = 'localhost',port = 9001,debug = True)
