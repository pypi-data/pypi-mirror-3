'''
Created on Feb 2, 2012

@author: mistaguy
-This file must contain any database connection wanted
'''

import MySQLdb
import psycopg2
from _mysql_exceptions import MySQLError
class Connect:
    """This class for creating a connection to the database engine
       This the Core SQL Engine Class   
    """     
    server = "127.0.0.1"
    database = "eshule"
    username = "root"
    password = "root"
    portnumber = 3306
    dbengine="MySQL"
    items={}
    def __init__(self):
        """
        Optionally pass in an initial dictionary of connection items
        """                 
           
        return       
    def __set_connection__(self):
        self.items["server"] =self.server
                
        self.items["database"] = self.database
               
        self.items["username"] = self.username
                
        self.items["dbengine"] = self.dbengine
                  
        self.items["password"] = self.password 
        
    def filling(self, sqlstr):
        """
        Gets a dataset
        """
        #set connection dictionary keys
        self.__set_connection__()
        
        # Open database connection
        
        if self.dbengine=="MySQL":
            try:
                connection=MySQLdb.connect(host=self.items['server'],db=self.items['database'],user=self.items['username'],passwd=self.items['password'])
     
                # prepare a cursor object using cursor() method
                cursor =connection.cursor()
            
                # Execute the SQL command
                cursor.execute(sqlstr)
                # Fetch all the rows in a list of lists.
                results = cursor.fetchall()
                return results
            except:            
                MySQLError
                return None
            connection.close()
        elif self.dbengine=="PSQL":
            try:
                connection=psycopg2.connect(host=self.items['server'],dbname=self.items['database'],user=self.items['username'],password=self.items['password'])
     
                # prepare a cursor object using cursor() method
                cursor =connection.cursor()
              
                # Execute the SQL command
                cursor.execute(sqlstr)
                # Fetch all the rows in a list of lists.
                results = cursor.fetchall()
                return results
            except: 
                return None
                connection.close()
                
        elif self.dbengine=="Oracle":
            try:
                connection=MySQLdb.connect(host=self.items['server'],db=self.items['database'],user=self.items['username'],passwd=self.items['password'])
     
                # prepare a cursor object using cursor() method
                cursor =connection.cursor()
          
                # Execute the SQL command
                cursor.execute(sqlstr)
                # Fetch all the rows in a list of lists.
                results = cursor.fetchall()
                return results
            except: 
                return None
            connection.close()
            
        
        
        

    def nonequery(self, sqlstr):
        """
        Executes Queries that do not return Datasets
        """
        #set connection dictionary keys
        self.__set_connection__()
        if self.dbengine=="MySQL":
            try:
                # Open database connection
                connection=MySQLdb.connect(host=self.items['server'],db=self.items['database'],user=self.items['username'],passwd=self.items['password'])
                # prepare a cursor object using cursor() method
                cursor =connection.cursor()
         
                # Execute the SQL command
                cursor.execute(sqlstr)
                # Commit your changes in the database
                connection.commit()
                return True
            except MySQLdb.Error, e:            
                MySQLError
                #Roll Back incase of failure
                #connection.roleback()
                print "Error %d: %s" % (e.args[0], e.args[1])
                return False
            connection.close() 
        elif self.dbengine=="PSQL":
            try:
                # Open database connection
                connection=psycopg2.connect(host=self.items['server'],dbname=self.items['database'],user=self.items['username'],password=self.items['password'])
                # prepare a cursor object using cursor() method
                cursor =connection.cursor()
            
                # Execute the SQL command
                cursor.execute(sqlstr)
                # Commit your changes in the database
                connection.commit()
                return True
            except:            
                MySQLError
                #Roll Back incase of failure
                #connection.roleback()
                print "Error has occured"
                return False
            connection.close()
            
        elif self.dbengine=="Oracle":
            try:
                # Open database connection
                connection=MySQLdb.connect(host=self.items['server'],db=self.items['database'],user=self.items['username'],passwd=self.items['password'])
                # prepare a cursor object using cursor() method
                cursor =connection.cursor()            
                # Execute the SQL command
                cursor.execute(sqlstr)
                # Commit your changes in the database
                connection.commit()
                return True
            except:            
                MySQLError
                #Roll Back incase of failure
                #connection.roleback()
                print "Error has occured"
                return False
            connection.close()
            
       

    def scalar(self, sqlstr):
        """
        return a Dataset
        """
        #set connection dictionary keys
        self.__set_connection__()
        if self.dbengine=="MySQL":
            try:
                # Open database connection
                connection=MySQLdb.connect(host=self.items['server'],db=self.items['database'],user=self.items['username'],passwd=self.items['password'])
                # prepare a cursor object using cursor() method
                cursor =connection.cursor()
            
                # Execute the SQL command
                cursor.execute(sqlstr)
                # Fetch a single row using fetchone() method.
                result = cursor.fetchone()
                return result
            except:            
                MySQLError            
                return None
            connection.close()
        elif self.dbengine=="PSQL":
            try:
                # Open database connection
                connection=psycopg2.connect(host=self.items['server'],dbname=self.items['database'],user=self.items['username'],password=self.items['password'])
                # prepare a cursor object using cursor() method
                cursor =connection.cursor()
            
                # Execute the SQL command
                cursor.execute(sqlstr)
                # Fetch a single row using fetchone() method.
                result = cursor.fetchone()
                return result
            except:         
                          
                return None
        
        elif self.dbengine=="Oracle":
            try:
                # Open database connection
                connection=MySQLdb.connect(host=self.items['server'],db=self.items['database'],user=self.items['username'],passwd=self.items['password'])
                # prepare a cursor object using cursor() method
                cursor =connection.cursor()
            
                # Execute the SQL command
                cursor.execute(sqlstr)
                # Fetch a single row using fetchone() method.
                result = cursor.fetchone()
                return result
            except:           
                           
                return None
            connection.close()