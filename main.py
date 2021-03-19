from cymruwhois import Client
from flask import Flask, request, jsonify, render_template, redirect
import socket,re, sqlite3, uuid

app = Flask(__name__)
DATABASE = 'database.db'

@app.route('/api/<ip>')
def api(ip):
    c = Client()
    r = c.lookup(ip)
    print(r.asn)
    print(r.owner)
    asno = r.asn     #as number
    asname = r.owner #as name
    res = jsonify(ASN=asno, AS=asname)
    return res

@app.route('/')
def main():
    return '<b>@DAWID<br><br> ### PASTEBIN WITH ASN/AS + ENDPOINT ###</b> <br><br>NEW PASTE <b>/newpaste</b> <br><br>VIEW PASTE <b>/paste/<:id></b><br><br>GET AS&ASN <b>/API/:IP</b>'

@app.route('/newpaste')
def newpaste():
    return render_template('t1.html')

@app.route('/addpastetodb', methods=['POST'])
def add():
        print(request.form['textareaInput'])
        fstring=request.form['textareaInput']
        originalstring=request.form['textareaInput']
        
        
        ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', fstring ) # extracting the IP addresses
        lst=[]
        c = Client()
        for index,item in enumerate(ip):
            r = c.lookup(ip[index])
            #print(r.asn)
            if r.asn != 'NA': 
                print(r.asn, index, ip[index], r.owner)
                lst.append([index,ip[index],r.asn,r.owner,r.cc])
                #1 -index, 2-ip, 3-Asnumber, 4-Asname, 5-Location
        #print(lst)

        for i in lst:
            #print(i[1])#printing ips
            fstring = fstring.replace(i[1],'<a class="toolTipInfo" data-toggle="tooltip" title="AS number: '+i[2]+'&#013AS name: '+i[3]+'&#013Location: '+i[4]+'">'+i[1]+'</a>')
            
        fstring = fstring.replace('\n','<br>') #format to html

        uuid.uuid4()
        struuid = str(uuid.uuid4())
        uniqueid = uuid.uuid4().hex

        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("INSERT INTO pastes (paste, pasteparsed, routeid) VALUES (?,?,?)",(originalstring,fstring,uniqueid) )
        con.commit()

        cur.execute("select * from pastes")
        users = cur.fetchall(); 
        print(users)
        con.close()

        return redirect("/paste/"+uniqueid)

@app.route('/paste/<id>')
def u(id):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("select * from pastes where routeid = (?)",(id,))
        res = cur.fetchall()
        con.close() 
        #print(len(res))
        #print(printing...)
        #print(uzers)

        if len(res) == 1:
            for i in res:
                a = i[1] #unparsed
                b = i[2] #parsed
                 
                return render_template('t2.html',pasteparsed=b,pasteunparsed=a)
        else:
            return render_template('t3.html')

#####CREATING DB in SQLITE = one time use only ROUTE#####
@app.route('/create_database', methods=['GET', 'POST'])
def create_db():
    
    conn = sqlite3.connect(DATABASE)
    conn.execute('CREATE TABLE pastes (id INTEGER PRIMARY KEY AUTOINCREMENT, paste VARCHAR, pasteparsed VARCHAR, routeid text)')
    conn.commit()
    conn.close()

    return "db created"


app.debug = True
app.run()
