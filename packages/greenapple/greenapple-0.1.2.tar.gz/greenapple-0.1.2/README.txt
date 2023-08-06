#create a student
import greenapple

gco=greenapple.model.ConnectOperations()
gco.con.dbengine="MySQL"
gco.con.database="eshule"
gco.con.username="root"
gco.con.password="root"

student={"first_name":"'Alexandria'","last_name":"'Nandyose'","table":"student","clause":"where id = 4"}
student["last_name"]="'Marvin Stevens'"
gco.insert(student)

dataset=gco.select_dataset({"table":"student","clause":"where id=8"})
for record in dataset:
    print record


Postgresql Example

import greenapple

gco=greenapple.model.ConnectOperations()
gco.con.dbengine="PSQL"
gco.con.database="eshule"
gco.con.username="root"
gco.con.password="root"

student={"first_name":"'Emmaculate'","last_name":"'Akongo'","table":"student"}
gco.insert(student)
student["last_name"]="'Opata'"
student["clause"]="where id =1";
gco.update(student)

dataset=gco.select_dataset({"table":"student"})
for record in dataset:
    print record



