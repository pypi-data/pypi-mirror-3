This is a database layer object for python.
It connects to any database but for now support is for MySQL.
Postgresql and Oracle is in development. Other Databases will be integrated 
with time

How to setup
Add the module to your python path

How to use.

1.Write everything about an object in a dictionary. 
make sure the dictionary keys correspond to your database names.

2.Incase of delete sql statements and restricted sql statements, add 'clause' key
to the dictionary with an sql clause statement. eg where id>1.

3.use the dictionary key 'attribute' to specify database fields.

An Example

'''
Created on Feb 3, 2012

@author: mistaguy
'''
#create a student
import greenapple
gco=greenapple.model.ConnectOperations()

student={"first_name":"'Guy'","last_name":"'Acellam'","table":"student","clause":"where id = 1"}
#gco.insert(student)
student["last_name"]="'Marvin Stevens'"
#gco.update(student)
dataset=gco.select_dataset({"table":"student"})
for record in dataset:
    print record



