#!/usr/bin/env python

from WWScraper import WWScraper
import MySQLdb as mdb
import time
import sys
import getopt
import logging

def main(user,passwd,max_entries=None):
    
    robber = WWScraper.WWScrape()
    conn = mdb.connect('localhost',
                       'webuser','password',
                       'freepoints',
                       charset = "utf8",use_unicode=True)
  
    # Create our connection and rebuild the points database
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS points_data")
    c.execute('''
        CREATE TABLE IF NOT EXISTS points_data (name TEXT, 
            id VARcHAR(20) NOT NULL, servings TEXT, points INTEGER,
            PRIMARY KEY (id)) DEFAULT CHARACTER SET=utf8 ENGINE=MyISAM
    ''')

    c.execute('''
        CREATE FULLTEXT INDEX points_data_ftidx ON points_data (name)
    ''')

    robber.connect(user,passwd)

    totals = {}
    for i in range(97,123):
        print "Searching: %s" % (chr(i))
        foods = robber.food_search(chr(i),max_entries)
        dup_entries = 0
        for food in foods:
            try:
                c.execute(u'''
                            INSERT INTO points_data (name,id,servings, points) 
                            VALUES (%s,%s,%s,%s)''', food)
            except mdb.Error, e:
                dup_entries = dup_entries+1
        conn.commit()
        print "Inserted %s of %s, skipping %s as duplicates" % ( 
                                 len(foods)-dup_entries,len(foods),dup_entries)
        time.sleep(3) 
        totals[chr(i)] = len(foods)-dup_entries
    c.close()

    total_entries=0
    for i in range(97,123):
        print "%s - Inserted: %s" % (chr(i),totals[chr(i)])
        total_entries = total_entries + totals[chr(i)]
    print "------------------------"
    print "Total Inserted: %s" % (total_entries)

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:p:m:", 
                                   ["help", "username=","password=","max="]) 
    except getopt.GetoptError, err:
        print str(err) 
        sys.exit(2)

    username = None
    password = None
    max_entries = None
    for o, a in opts:
        if o in ("-u","--username"):
            username = a
        elif o in ("-p","--password"):
	    password = a
        elif o in ("-m","--max"):
	    max_entries = int(a)
        else:
            pass

    # Actually run the grab
    main(username,password,max_entries)

