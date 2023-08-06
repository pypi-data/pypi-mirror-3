'''
Created on Feb 2, 2012

@author: mistaguy

@summary: uses the connect class to provide a database abstract layer to tables

'''

from Connect import Connect
import MySQLdb
import psycopg2
class ConnectOperations:
    """
    This Class is the base CRUD class for all database tables models.
    It use an instance of the Connect class    """
    
    def __init__(self):
        """
        constructor
        """        
        return      
    con=Connect()
    def insert(self,obj):
        """
        Creates a new Record to the database
        """
        #valid fields
        if not obj["table"]:
            print "Missing Table"
            return
        try:
            
            print "Attempting to Populate Records"
            attributes=""
            values=""
            table=obj["table"]
            for o in obj:
                if o=="clause" or o=="table":
                    print ""
                else:
                    attributes=o+","+attributes
                    values=obj[o]+","+values 
            #remove the last comma    
            attributes=attributes[0:len(attributes)-1] 
            values=values[0:len(values)-1]       
            sqlstr="INSERT INTO " + table + "(" + attributes + ")VALUES(" + values + ")"       
            result= self.con.nonequery(sqlstr)
            print "Record Inserted"
            return result
        except MySQLdb.Error or psycopg2.Error, e:
            if self.con.dbengine=="MySQL":
                print e.message
            elif self.con.dbengine=="PSQL":
                print e.message
            print "may be make sure your dictionary values corresponds to the table in your database"
            
            return
    
    
    def update(self, obj):        
        """
        modify a record.        
        """
        if not obj["table"]:
            print "Missing Table"
            return
        try:
            if not obj.has_key("clause"): 
                obj["clause"]=" "
            print "Attempting to Modify a Record"
            statement = ""
            for o in obj:
                if o=="clause" or o=="table":
                    print ""
                else:
                    statement= (o+"="+obj[o]+",")+statement
                
            #remove the last comma    
            statement=statement[0:len(statement)-1] 
            sqlstr="UPDATE " + obj["table"] + " SET "+statement +" "+obj["clause"]
            result=self.con.nonequery(sqlstr)
            
            print "Record Updated"
            return result
    
        except:
            print "may be make sure your dictionary values corresponds to the table in your database"
            
            return
    
    def select_dataset(self,obj ):
        """
        returns a dataset OR datasets
        """           

        print "Attempting to select record"
     
        if not obj.has_key("clause"): 
            obj["clause"]=" "
        if not obj.has_key("attributes"): 
            obj["attributes"]="*"
        try:
            
            
            sqlstr="SELECT " + obj["attributes"] + " FROM " + obj["table"] + " " + obj["clause"]
            
            result=self.con.filling(sqlstr)
            print "Records Selected"
            return result
        except MySQLdb.Error,e:
            if self.con.dbengine=="MySQL":
                print e.message
            
            print "may be make sure your dictionary values corresponds to the table in your database"
            
            return
    ''' def select_single_dataset(self, obj):
        """
       return one dataset
        """  
        try:   
            if not obj.has_key("clause"):                 
                print "You must provide a 'clause' dictionary key with values eg where id =1"
                return
            if not obj.has_key("attribute"):                 
                print "You must provide an 'attribute' dictionary key with values eg id"
                return
            print "attempting to select single record"
            sqlstr=Connect().scalar("SELECT " + obj["attribute"] + " FROM " + obj["table"] + " " + obj["clause"])
            print sqlstr
            result=sqlstr
            print "single record selected"
            return result
        except:
            print "may be make sure your dictionary values corresponds to the table in your database"
            
            return
    '''
    def delete(self, obj):
        """
        remove a record       
        """   
        try: 
            if not obj.has_key("clause"): 
                print "You must provide a where clause dictionary key with values eg where id =1"
              
                return
            print "Attempting to delete a record or records"  
            result=self.con.nonequery("DELETE FROM " +obj["table"]+ " " + obj["clause"])
            print "single record(s) deleted"              
            return result
        except:
            print "may be make sure your dictionary values corresponds to the table in your database"
            
            return