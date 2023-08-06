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


