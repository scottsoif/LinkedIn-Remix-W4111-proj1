
Scott Soifer (sas2412) and Asher Willner (ajw2210)
Project Part 3
4/8/20

Postgres SQL Account: sas2412

URL: 35.229.126.221:8111  // Server currently off. Contact sas2412@columbia.edu for demo

- Our web application accomplishes everything set forth in our proposal, and we added a couple of features as well. Our program allows the user to: 
	- see people's 1st, 2nd, and 3rd degree connections. 
	- browse school alumni
	- Find job postings and apply to them
	- Get posts (and comments on those posts) made by a user
	- Find average company salaries
	- Find the volunteers of a specific organization

- 2 interesting database features:
	1. Our application allows a user to select a person in the database from a drop down menu and then click to see his or her 1st, 2nd, or 3rd, degree connections. This is an interesting use of the database because it requires complex querying from the database, exactly pinpointing who the person's connections are. It requires multiples joins and understanding how to limit the results to just the 1st, 2nd, or 3rd degree connections without seeing the other connections as well. 

	2. Our application also allows a user to browse job postings from specific companies, and then apply to them. This is interesting because first it pulls available jobs from the database, and then based on who's applying, it adds that person and the relevant job information to the apply_for relation. Two tricky issues we needed to overcome was taking the relevant job information from the query to find the jobs and use it to enter into the apply_for relation, and also to prevent the system from crashing when the same person attempts to apply to a position multiple times. 
