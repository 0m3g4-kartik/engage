from flask import *  
import sqlite3
from sqlite3.dbapi2 import Error
from urllib.parse import unquote,unquote_plus
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import os 
import sys
import time
from crontab import CronTab
options = ChromeOptions()
options.add_argument('headless')
options.add_argument('no-sandbox')
admin_bot = webdriver.Chrome(chrome_options=options)
time.sleep(5)
app = Flask(__name__)  
app.secret_key = "flag{admin_hacked}"  
def touch(fname):
    try:
        os.utime(fname, None)
    except OSError:
        open(fname, 'a').close()

touch('db.sqlite3')
_conn = sqlite3.connect('db.sqlite3')
_conn.execute('create table if not exists cash (id integer primary key, name TEXT, money integer)')
_conn.execute('create table if not exists comment (id integer primary key, name TEXT, comment TEXT)')
_conn.close() 

my_cron = CronTab(user=True)
job= my_cron.new(command='python3 /src/app/cron_job.py 2>/src/app/error.log')
job.minute.every(4)
my_cron.write()

class Comment(object):
    def __init__(self, name, text):
        self.name = name
        self.comment = text
        
@app.route('/')  
def home(): 
    if 'name' in session:
        return make_response(render_template("index.html",name=session['name'],login=True))
    return make_response(render_template("index.html"))  

@app.route('/category') 
def category():
    return make_response(render_template("cat.html"))

@app.route('/register')  
def register():
    if 'name' in session:
        return redirect('/')  
    return make_response(render_template("signup.html"))  

@app.route('/login',methods = ["GET","POST"])  
def login():
    if 'name' in session:
        return redirect('/')  
    return make_response(render_template("login.html"))  
 
@app.route('/success',methods = ["POST"])  
def success():
    if 'name' in session:
        return redirect('/')
    if request.method == "POST":  
        name=request.form['name']
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute('select name from cash where name= ?',[name])
        if len(c.fetchall())!=0 :
            conn.commit()
            conn.close()
            return make_response(render_template('error.html',msg="username exists already"))
        c.execute('insert into cash(name, money) values (?, ?)',(name,1000))
        conn.commit()
        conn.close()
        session['name']=name
        response=make_response(redirect('/'))
        return response

@app.route('/complaints')  
def comp():  
    return make_response(render_template('report.html'))

@app.route('/comment', methods=['POST'])
def comment():
    comment_name = request.form['name']
    comment_text = request.form['comment']
    conn = sqlite3.connect('db.sqlite3')
    with conn:
        conn.execute('insert into comment(name, comment) values (?, ?)', (comment_name, comment_text))
    conn.commit()
    conn.close()
    return make_response(redirect('/coat'))

@app.route('/logout')  
def logout():  
    if 'name' in session:   
        name=session['name']
        try : 
            conn = sqlite3.connect('db.sqlite3')
            c= conn.cursor()
            c.execute('delete from cash where name= ?',(name,))
            sys.stdout.flush()
            conn.commit()
            conn.close()
        except:
            pass
        session.pop('name',None)
        return make_response(redirect('/register'))
    else:  
        return make_response(redirect('/register')) 

@app.route('/report', methods=['POST'])
def report():
    link = request.form['url']
    if link[0:4]=='http' :
        admin_bot.get('http://0.0.0.0:16052')
        admin_bot.add_cookie({'name':'flag','value':'hacking_the_admin_cookie_was_easy_131852149','httpOnly':False})
        admin_bot.execute_script("window.alert = function() {};")
        time.sleep(5)
        admin_bot.get(link)
        time.sleep(5)
        admin_bot.delete_cookie('flag')
        return make_response(render_template('report.html',msg="Admin will view your issue shortly."))
    else :
        return make_response(render_template('error.html',msg="Error ! Report URL should be of this site"))

@app.route('/coat')
def view_comment():
    conn = sqlite3.connect('db.sqlite3')
    comments = []
    c = conn.cursor()
    for row in c.execute('select name, comment from comment '):
        comments.append(Comment(*row))
    return render_template('desc.html', comments=comments)

@app.route('/wallet')  
def wallet():  
    if 'name' in session:  
        name = session['name'] 
        try : 
            conn = sqlite3.connect('db.sqlite3')
            c= conn.cursor()
            c.execute('select money from cash where name= ?',(name,))
            money=c.fetchone()[0]
            if(money >= 69696969):
                money='flag{huge_Cashhh_123222}'
            conn.commit()
            conn.close()
        except:
            return make_response(render_template('error.html',msg="User does not exist"))
        return make_response(render_template('Wallet.html',money=money))  
    else:  
        return make_response(redirect('/register')) 

@app.route('/admin_transfer',methods = ["POST"])  
def ad():  
    if request.remote_addr == '127.0.0.1':
        account= request.form['account']
        try:
            amount = int(request.form['cash'])
        except:
            amount = 0
        try : 
            conn = sqlite3.connect('db.sqlite3')
            c= conn.cursor()
            c.execute('select money from cash where name= ?',[account])
            if len(c.fetchall())==0 :
                conn.commit()
                conn.close()
                return make_response(render_template('error.html',msg="user does not exist"))
            c.execute('select money from cash where name= ?',[account])
            cash=c.fetchone()[0]
            cash=cash+amount
            c.execute('update cash set money=? where name= ?',[cash,account])
            conn.commit()
            conn.close()
        except:
            return make_response(render_template('error.html',msg="user does not exist"))
        return make_response(redirect('/'))
    else :
        return make_response(render_template('error.html',msg="only admin can access this endpoint"))
    
@app.route('/transfer',methods = ["POST"])  
def transfer():  
    if 'name' in session:  
        name = session['name']
        account= request.form['account']
        if name == account :
            return make_response(redirect('/wallet'))
        try:
            amount = int(request.form['cash'])
        except:
            amount = 0
        try : 
            conn = sqlite3.connect('db.sqlite3')
            c= conn.cursor()
            c.execute('select money from cash where name= ?',[account])
            if len(c.fetchall())==0 :
                conn.commit()
                conn.close()
                return make_response(render_template('error.html',msg="user does not exist"))
            c.execute('select money from cash where name= ?',[name])
            money=c.fetchone()[0]
            if money >= amount :
                money=money-amount
            else :
                amount=money
                money=0
            c.execute('update cash set money=? where name= ?',[money,name])
            c.execute('select money from cash where name= ?',[account])
            cash=c.fetchone()[0]
            cash=cash+amount
            c.execute('update cash set money=? where name= ?',[cash,account])
            conn.commit()
            conn.close()
        except:
            return make_response(render_template('error.html',msg="user does not exist"))
        return make_response(redirect('/wallet'))  
    else:  
        return make_response(redirect('/register'))

@app.route('/flag', methods=['GET', 'POST'])
def flag():
    if request.remote_addr == '127.0.0.1':
        return app.secret_key
    else:
        return {"error": "The flag can only be accessed from inside the server i.e. from localhost(127.0.0.1)"}

if __name__ == '__main__':  
    app.debug = True
    app.run('0.0.0.0', 16052)