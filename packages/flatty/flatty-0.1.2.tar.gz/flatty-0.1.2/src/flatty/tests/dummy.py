from datetime import date
import flatty
import couchdb


dbname = 'flatty_couchdb_test'
server = couchdb.Server('http://localhost:5984/')
 
if dbname not in server:
	db = server.create(dbname)
else:
	db = server[dbname]



class Comment(flatty.Schema):
	user = str
	txt = str

class Book(flatty.Schema):
	name = str
	year = date
	comments = flatty.TypedList.set_type(Comment)

class Address(flatty.Schema):
	street = str
	city = str
	
class Library(flatty.couch.Document):
	name = str
	address = Address 
	books = flatty.TypedDict.set_type(Book)


library = Library(name='IT Library')
library.address = Address(street='Baker Street 221b', city='London')
library.books={}
library.books['978-1590593561'] = Book(name='Dive Into Python',
										year = date(2008,10,10))
library.books['978-0596158101'] = Book(name='Programming Python',
										year = date(2011,1,31))

library.books['978-0596158101'].comments = []
library.books['978-0596158101'].comments.append(
												Comment(user='Alex',
												txt='good Book')
												)

id, rev = library.store(db)