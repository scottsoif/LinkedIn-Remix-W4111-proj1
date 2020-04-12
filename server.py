# test merge
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

connections = []
alumni = []
jobs = []
avgSalaries = []
posts = []
nicePeople = []
applied = []

# drop downs
names = []
schools = []
companies = []
companies2 = []
users = []
volunteer = []
radio_but = ["checked","",""]


DATABASEURI = "postgresql://sas2412:5419@35.231.103.173/proj1part2"


# This line creates a database engine that knows how to connect to the URI above.
engine = create_engine(DATABASEURI)


# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
'''
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
'''
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
@app.route('/')
def index():

  print(request.args)
  names.clear()
  schools.clear()
  companies.clear()
  users.clear()
  volunteer.clear()

  cursor = g.conn.execute("SELECT id,li_user.name FROM person, li_user WHERE person.person_id=li_user.id")
  # names = []
  for result in cursor:
  	names.append([result,""])
  cursor.close()

  cursor = g.conn.execute("select id, name from school, li_user where school_id=id")
  # schools = []
  for result in cursor:
    schools.append([result,""])
    #names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT id,li_user.name FROM organization, li_user WHERE organization.organization_id=li_user.id")
  # companies = []
  for result in cursor:
  	companies.append([result,""])
  cursor.close()

  cursor = g.conn.execute("SELECT id,li_user.name FROM organization, li_user WHERE organization.organization_id=li_user.id")
   # companies2222222222 = []
  for result in cursor:
    companies2.append([result,""])
  cursor.close()

  cursor = g.conn.execute("SELECT id, name FROM li_user")
  # users = []
  for result in cursor:
      users.append([result,""])
  cursor.close()

  cursor = g.conn.execute("SELECT id,li_user.name FROM volunteer, li_user WHERE volunteer.organization_id=li_user.id group by id, name order by id")
  # volunteer = []
  for result in cursor:
      volunteer.append([result,""])
  cursor.close()

  context = dict(data = names, radData=radio_but, rData = connections, data2=schools, rData2 = alumni,  data3 = companies, rData3 = jobs,
                data4=companies2, rData4 = avgSalaries, data5 = users, rData5 = posts, data6 = volunteer, rData6 = nicePeople, rData7=applied)


  return render_template("index.html", **context)



@app.route('/clearResults', methods=['POST'])
def clearResults():
  clearHelper()
  return redirect("/")

def clearHelper():
  connections.clear()
  alumni.clear()
  jobs.clear()
  avgSalaries.clear()
  posts.clear()
  nicePeople.clear()
  applied.clear()


def resetDropDowns():   # removes the past user from top of form
  for idx, val in enumerate(names):
    names[idx][1] = ""
  for idx, val in enumerate(schools):
    schools[idx][1] = ""
  for idx, val in enumerate(companies):
    companies[idx][1] = ""
  for idx, val in enumerate(companies2):
    companies2[idx][1] = ""
  for idx, val in enumerate(users):
    users[idx][1] = ""
  for idx, val in enumerate(volunteer):
    volunteer[idx][1] = ""
  radio_but = ["checked","",""]

@app.route('/goHome', methods=['POST'])
def another():
  return redirect("/")


# data
@app.route('/getDegConnects', methods=['POST'])
def getDegConnects():
    resetDropDowns()
    print(f"\n\n{request.form}")
    # gets user and def from post request
    user_id = request.form['user_id']
    deg = request.form['degree']
    names[int(user_id)-1][1] = "selected"
    
    
    clearHelper() # empties list so no double values

    if deg=="first":
        radio_but = ["checked","",""]
        con2 = "(SELECT c2_id FROM connection WHERE c1_id={}) t".format(user_id)
        con2names = "Select name From li_user, {} Where li_user.id=t.c2_id".format(con2)
        cursor = g.conn.execute(con2names)
        for result in cursor:
            print(result[0])
            connections.append(result[0])
        cursor.close()
    
    elif deg=="second":
        radio_but = ["","checked",""]
        cursor = g.conn.execute(
        '''
        Select x.name target, y.name mutual, z.name as second
        from li_user x, li_user y, li_user z
        where (x.id,y.id,z.id) in
        (select p.c1_id target, p.c2_id mutual, s.c2_id secondDegree
        from connection p join connection s on p.c2_id=s.c1_id
        where p.c1_id != s.c2_id and p.c1_id={} and s.c2_id not in
        (select c2_id from connection where c1_id={}))
        '''.format(user_id,user_id))
        for result in cursor:
            print(result[2])
            connections.append(result[2])
            #names.append(result['name'])  # can also be accessed using result[0]
        cursor.close()

    elif deg=="third":
      radio_but = ["","","checked"]
      cursor = g.conn.execute(
      f'''SELECT li_user.name ThirdDegree FROM person, li_user 
      WHERE person.person_id=li_user.id and name not in 
      (Select name From li_user, (SELECT c2_id FROM connection 
      WHERE c1_id={user_id}) t Where li_user.id=t.c2_id) and name not in 
      (Select z.name as second from li_user x, li_user y, li_user z 
      where (x.id,y.id,z.id) in 
      (select p.c1_id target, p.c2_id mutual, s.c2_id secondDegree 
      from connection p join connection s on p.c2_id=s.c1_id 
      where p.c1_id != s.c2_id and p.c1_id={user_id} and s.c2_id not in 
      (select c2_id 
      from connection where c1_id={user_id}))) and id !={user_id}''')

      for result in cursor:
          print("third ***   ", result[0])
          connections.append(result[0])

      cursor.close()
        

    '''
    else if deg=="third":
        cursor = g.conn.execute("SELECT id,li_user.name FROM person, li_user WHERE person.person_id=li_user.id")
        for result in cursor:
            names.append(result)
            #names.append(result['name'])  # can also be accessed using result[0]
        cursor.close()
    '''
    print("looking for ** ", connections)
    print(f"\nUser: {user_id}\nDegrees you want:  {deg}\n\n")
    if len(connections)==0: connections.append("No results found :{")

    # return redirect('/#getDegConnects')
    context = dict(data = names, radData=radio_but, rData = connections, data2=schools, rData2 = alumni,  data3 = companies, rData3 = jobs,
                data4=companies2, rData4 = avgSalaries, data5 = users, rData5 = posts, data6 = volunteer, rData6 = nicePeople, rData7=applied)

    return render_template("index.html",scroll='getDegConnects', **context)

# data 2
@app.route('/getAlumni', methods=['POST'])
def getAlumni():
    clearHelper()
    resetDropDowns()
    print(f"\n\n{request.form}")
    school_id = request.form['school_id']
    schools[int(school_id)-21][1] = "selected"
    cursor = g.conn.execute(
    '''
    Select name
    From alumni a, li_user l
    Where a.person_id = l.id and a.school_id = {}
    '''.format(school_id)
    )
    for result in cursor:
        print(result[0])
        alumni.append(result[0])
    print(f"School id: {school_id}\n\n")
    cursor.close()
    # return redirect('/#getAlumni')
    context = dict(data = names, radData=radio_but, rData = connections, data2=schools, rData2 = alumni,  data3 = companies, rData3 = jobs,
                data4=companies2, rData4 = avgSalaries, data5 = users, rData5 = posts, data6 = volunteer, rData6 = nicePeople, rData7=applied)

    return render_template("index.html",scroll='getAlumni', **context)


# data 3
@app.route('/getJobs', methods=['POST'])
def getJobs():
    clearHelper()
    resetDropDowns()
    print(f"\n\n{request.form}")
    job_id = request.form['job_id']
    companies[int(job_id)-11][1] = "selected"
    cursor = g.conn.execute(
    '''
    Select l.name, j.level, j.description, job_id
    From job j, li_user l
    Where j.organization_id = l.id and j.organization_id = {}
    '''.format(job_id)
    )
    jobs.append(("Company","Job", "Job Description" , "Apply:\n Who are you?"))
    for result in cursor:
        print(result)
        jobs.append(result)
    print(f"Job id: {job_id}\n\n")
    # return redirect('/#getJobs')
    context = dict(data = names, radData=radio_but, rData = connections, data2=schools, rData2 = alumni,  data3 = companies, rData3 = jobs,
                data4=companies2, rData4 = avgSalaries, data5 = users, rData5 = posts, data6 = volunteer, rData6 = nicePeople, rData7=applied)

    return render_template("index.html",scroll='getJobs', **context)


@app.route('/getPosts', methods=['POST'])
def getPosts():
    clearHelper()
    resetDropDowns()
    print(f"\n\n{request.form}")
    id = request.form['user_id']
    users[int(id)-1][1] = "selected"
    cursor = g.conn.execute(
    '''
    Select l1.name, p.content, l2.name, c.content
    From post p, li_user l1, li_user l2, comment c
    Where p.author_id = l1.id and l1.id = {} and p.post_id = c.post_id and c.author_id = l2.id
    '''.format(id)
    )

    posts.append(("Author","Post", "Commenter" , "Comment"))
    for result in cursor:
        print(result)
        posts.append(result)
    print(f"Post id: {id}\n\n")
    # return redirect('/#getPosts')
    context = dict(data = names, radData=radio_but, rData = connections, data2=schools, rData2 = alumni,  data3 = companies, rData3 = jobs,
                data4=companies2, rData4 = avgSalaries, data5 = users, rData5 = posts, data6 = volunteer, rData6 = nicePeople, rData7=applied)
    # context['_anchor'] = 'getVols'
    return render_template("index.html",scroll = 'getPosts', **context) 


@app.route('/add', methods=['POST'])
def add():
  applied.clear()
  job_user_id = request.form['job_user_id'].split(',')
  job_id, user_id, *job_desc, user_name = job_user_id
  job_id = int(job_id)
  user_id = int(user_id)
  print(f"\n*** User, job_id, job_dec, name:\t {job_id, user_id, job_desc, user_name}")
  # applied.append(f"Congrats {user_name} on applying to {job_desc[0]}")

  res = engine.execute("""insert into apply_for (person_id ,job_id) 
                    select {},{} where not exists 
                    (select person_id, job_id from apply_for 
                    where person_id = {} and job_id={})""".format(user_id, job_id,user_id, job_id))
  if res.rowcount > 0:
    applied.append(f"Congrats {user_name} on applying to {job_desc[0]}")
  else:
    applied.append(f"{user_name} already applied to {job_desc[0]}")
  return redirect('/#getJobs')
  


@app.route('/getSalaries', methods=['POST'])
def getSalaries():
    clearHelper()
    resetDropDowns()
    print(f"\n\n{request.form}")
    org_id = request.form['org_id']
    companies2[int(org_id)-11][1] = "selected"
    cursor = g.conn.execute(
    '''
    select l.name, avg(salary)
    From employee e, li_user l
    Where e.organization_id = l.id and e.organization_id = {}
    Group by l.name '''.format(org_id) )

    for result in cursor:
      print(result[1])
      avgSalaries.append("${:,.2f}".format(result[1]))

    cursor.close()

    print(f"Salary id: {org_id}\n\n")
    # return redirect('/#getSalaries')
    context = dict(data = names, radData=radio_but, rData = connections, data2=schools, rData2 = alumni,  data3 = companies, rData3 = jobs,
                data4=companies2, rData4 = avgSalaries, data5 = users, rData5 = posts, data6 = volunteer, rData6 = nicePeople, rData7=applied)

    return render_template("index.html",scroll='getSalaries', **context) 

@app.route('/getVols', methods=['POST'])
def getVols():
    clearHelper()
    resetDropDowns()
    print(f"\n\n{request.form}")
    organization_id = request.form['organization_id']
    volunteer[int(organization_id)-18][1] = "selected"
    cursor = g.conn.execute(
    '''
    Select name
    From volunteer v, li_user l
    Where v.volunteer_id = l.id and v.organization_id = {}
    '''.format(organization_id)
    )
    for result in cursor:
        print(result[0])
        nicePeople.append(result[0])
    print(f"School id: {organization_id}\n\n")
    cursor.close()
    # return redirect('/#getVols')
    context = dict(data = names, radData=radio_but, rData = connections, data2=schools, rData2 = alumni,  data3 = companies, rData3 = jobs,
                data4=companies2, rData4 = avgSalaries, data5 = users, rData5 = posts, data6 = volunteer, rData6 = nicePeople, rData7=applied)

    return render_template("index.html", scroll='getVols', **context) 

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
