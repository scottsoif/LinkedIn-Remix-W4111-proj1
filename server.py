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

  cursor = g.conn.execute("SELECT id,li_user.name FROM person, li_user WHERE person.person_id=li_user.id")
  names = []
  for result in cursor:
  	names.append(result)
  cursor.close()

  cursor = g.conn.execute("select id, name from school, li_user where school_id=id")
  schools = []
  for result in cursor:
    schools.append(result)
    #names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT id,li_user.name FROM organization, li_user WHERE organization.organization_id=li_user.id")
  companies = []
  for result in cursor:
  	companies.append(result)
  cursor.close()


  context = dict(data = names, rData = connections,
                data2=schools, rData2 = alumni,
                data3 = companies, rData3 = jobs)

  return render_template("index.html", **context)



@app.route('/clearResults', methods=['POST'])
def clearResults():
  connections.clear()
  return redirect("/")

@app.route('/goHome', methods=['POST'])
def another():
  return redirect("/")


# data
@app.route('/getDegConnects', methods=['POST'])
def getDegConnects():
    print(f"\n\n{request.form}")
    # gets user and def from post request
    user_id = request.form['user_id']
    deg = request.form['degree']

    connections.clear() # empties list so no double values

    if deg=="first":
        con2 = "(SELECT c2_id FROM connection WHERE c1_id={}) t".format(user_id)
        con2names = "Select name From li_user, {} Where li_user.id=t.c2_id".format(con2)
        cursor = g.conn.execute(con2names)
        for result in cursor:
            print(result[0])
            connections.append(result[0])
        cursor.close()

    elif deg=="second":
        cursor = g.conn.execute(
        '''
        Select x.name target, y.name mutual, z.name as second
        from li_user x, li_user y, li_user z
        where (x.id,y.id,z.id) =
        (select p.c1_id target, p.c2_id mutual, s.c2_id secondDegree
        from connection p join connection s on p.c2_id=s.c1_id
        where p.c1_id != s.c2_id and p.c1_id={} and s.c2_id not in
        (select c2_id from connection where c1_id={}))
        '''.format(user_id,user_id))

        for result in cursor:
            for i in result[1:]:  # inner loop to remove tuple
              print(i)
              connections.append(i)
            #names.append(result['name'])  # can also be accessed using result[0]
        cursor.close()
    '''
    else if deg=="third":
        cursor = g.conn.execute("SELECT id,li_user.name FROM person, li_user WHERE person.person_id=li_user.id")
        for result in cursor:
            names.append(result)
            #names.append(result['name'])  # can also be accessed using result[0]
        cursor.close()
    '''
    print(f"\nUser: {user_id}\nDegrees you want:  {deg}\n\n")
    if len(connections)==0: connections.append("No results found :{")
    # context = dict(rData = connections)

    # return render_template("result.html", **context)
    return redirect('/')

# data 2
@app.route('/getAlumni', methods=['POST'])
def getAlumni():
    alumni.clear()
    print(f"\n\n{request.form}")
    school_id = request.form['school_id']

    print(f"School id: {school_id}\n\n")
    return redirect('/')

@app.route('/getAlumni', methods=['POST'])
def getAlumni():
    print(f"\n\n{request.form}")
    school_id = request.form['school_id']
    cursor = g.conn.execute('''
    Select name
    From alumni a, li_user l
    Where a.person_id = l.id and a.school_id = {}
    '''.format(school_id))
    for result in cursor:
        print(result[0])
    print(f"School id: {school_id}\n\n")
    return redirect('/')

# data 3
@app.route('/getJobs', methods=['POST'])
def getJobs():
    jobs.clear()
    print(f"\n\n{request.form}")
    job_id = request.form['job_id']

    print(f"Job id: {job_id}\n\n")
    return redirect('/')



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
