
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


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@35.243.220.243/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.243.220.243/proj1part2"
#
DATABASEURI = "postgresql://sas2412:5419@35.231.103.173/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
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
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT id,li_user.name FROM person, li_user WHERE person.person_id=li_user.id")
  names = []
  for result in cursor:
  	names.append(result)
  cursor.close()

  cursor = g.conn.execute("SELECT id,li_user.name FROM organization, li_user WHERE organization.organization_id=li_user.id")
  companies = []
  for result in cursor:
  	companies.append(result)
  cursor.close()

  context = dict(data = names, data3 = companies)

  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/getDegConnects', methods=['POST'])
def getDegConnects():
    print(f"\n\n{request.form}")
    user_id = request.form['user_id']
    deg = request.form['degree']

    if deg=="first":
        con2 = "(SELECT c2_id FROM connection WHERE c1_id={}) t".format(user_id)
        con2names = "Select name From li_user, {} Where li_user.id=t.c2_id".format(con2)
        cursor = g.conn.execute(con2names)
        for result in cursor:
            print(result[0])
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
            print(result)
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
    print(f"User: {user_id}\nDegrees you want:  {deg}\n\n")
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
