from distutils.core import setup
setup(
		name = "tablet",
		packages = ["tablet"],
		version = "0.9.3",
		description = "A tiny spreadsheet-like data structure and tool",
		url = "http://pypi.python.org/pypi/tablet",
		author = "Cho-Yi Chen",
		author_email = "ntu.joey@gmail.com",
		keywords = ["table", "spreadsheet", "tsv", "csv"],
		classifiers = [
			"Programming Language :: Python",
			"Development Status :: 4 - Beta",
			"Environment :: Console",
			"Intended Audience :: End Users/Desktop",
			"License :: OSI Approved :: BSD License",
			"Operating System :: OS Independent",
			"Topic :: Software Development :: Libraries :: Python Modules",
			"Topic :: Text Processing :: General",],
		long_description = """\
tablet
------

Tablet is a module that supports spreadsheet-like operations on tiny text tables.

Dealing with those tiny tables or spreadsheets (usually in CSV/TSV formats) is a daily chore.

The goal of this project is to provide a light-weighted and easy-to-use
tool that can handle daily-routines of manipulating tabular text data.

Inside the module, a "Table" class was defined to support all kinds of spreadsheet/table-like operations:
  * tsv/csv input/output
  * adding/removing rows and columns
  * lookup a key or keys
  * iterating
  * slicing
  * searching
  * sorting
  * filtering
  * grouping
  * joining
  * aggregating
  * removing duplicates
  * and more

Getting Started
---------------

Supposing a given csv file named <demo.csv>::

    Heat,Lane,LastName,FirstName,YOB,NOC,RT,Time
    1,1,SILADJI,Caba,1990,SRB,0.69,27.89
    1,2,SCOZZOLI,Fabio,1988,ITA,0.62,27.37
    1,3,SNYDERS,Glenn,1987,NZL,0.66,27.64
    1,4,MARKIC,Matjaz,1983,SLO,0.73,27.71
    1,5,GANGLOFF,Mark,1982,USA,0.67,27.57
    1,6,FELDWEHR,Hendrik,1986,GER,0.70,27.53
    1,7,BARTUNEK,Petr,1991,CZE,0.64,27.87
    1,8,POLYAKOV,Vladislav,1983,KAZ,0.77,27.81
    2,1,RICKARD,Brenton,1983,AUS,0.71,27.80
    2,2,AGACHE,Dragos,1984,ROU,0.76,27.71
    2,3,DALE OEN,Alexander,1985,NOR,0.70,27.33
    2,4,FRANCA DA SILVA,Felipe,1987,BRA,0.68,26.95
    2,5,DUGONJIC,Damir,1988,SLO,0.75,27.51
    2,6,VAN DER BURGH,Cameron,1988,RSA,0.63,26.90
    2,7,TRIZNOV,Aleksandr,1991,RUS,0.70,27.73
    2,8,STEKELENBURG,Lennart,1986,NED,0.69,27.51

Users can type the following statements to show the top 8 results:

>>> import tablet as T
>>> t = T.read('demo.csv', delim=',').sort('Time')
>>> for row in t[:8]:
...     print row[2], row[3], row[-1]
...
VAN DER BURGH Cameron 26.90
FRANCA DA SILVA Felipe 26.95
DALE OEN Alexander 27.33
SCOZZOLI Fabio 27.37
DUGONJIC Damir 27.51
STEKELENBURG Lennart 27.51
FELDWEHR Hendrik 27.53
GANGLOFF Mark 27.57

And output the top 8 results to a new tsv file:

>>> t2 = t.cut_cols(['LastName','FirstName','Time']).cut_rows(range(8))
>>> t2.show()
H ['LastName', 'FirstName', 'Time']
0 ['VAN DER BURGH', 'Cameron', '26.90']
1 ['FRANCA DA SILVA', 'Felipe', '26.95']
2 ['DALE OEN', 'Alexander', '27.33']
3 ['SCOZZOLI', 'Fabio', '27.37']
4 ['DUGONJIC', 'Damir', '27.51']
5 ['STEKELENBURG', 'Lennart', '27.51']
6 ['FELDWEHR', 'Hendrik', '27.53']
7 ['GANGLOFF', 'Mark', '27.57']
>>> t2.write('finalists.tsv')

"""
)

