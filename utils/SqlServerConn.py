import configparser
cfg = configparser.ConfigParser()
cfg.read("D:/Shipdt/utils/sql.cfg")

import pyodbc
import numpy as np

class Conn(object):
	def __init__(self):
		self.driver = cfg.get("SQLSERV", "DRIVER")
		self.server = cfg.get("SQLSERV", "SERVER")
		self.database = cfg.get("SQLSERV", "DATABASE")

		self.conn = None
		self.cursor = None

	def Open(self):
		self.conn = pyodbc.connect("DRIVER={%s}; SERVER=%s; DATABASE=%s;"%(self.driver, self.server, self.database))
		self.cursor = self.conn.cursor()

	def Select(self, table=None, columns=None, conditions=None, groupby=None, having=None, orderby=None):
		try:
			comm = "SELECT " + ", ".join(columns) if len(columns) > 1 else "SELECT " + columns[0]
			comm += " FROM " + ",".join(table) if len(table) >1 else " FROM " + table[0]
			comm += " WHERE " + conditions if conditions else ""
			comm += " GROUP BY " + groupby if groupby else ""
			comm += " HAVING " + having if having else ""
			if orderby != None and len(orderby) >1:
				comm += " ORDER BY " + ", ".join(orderby)
			elif orderby != None and len(orderby) == 1:
				comm += " ORDER BY " + orderby[0]

			rows = self.cursor.execute(comm)
			cols = [col[0] for col in self.cursor.description]
		except Exception as e:
			return [None, "Perhaps command error: " + comm + "\n" + str(e), None]
		else:
			return [rows, comm, cols]

	def Insert(self, table=None, columns=None, values=None, encoding=False):
		try:
			if len(values)>1:
				if encoding:
					comm = "INSERT INTO " + table + "(" + ",".join(columns) + ") VALUES" + ",".join("(" + ",".join("N'" + k2 + "'" for k2 in k1) + ")" for k1 in values) + ";"
				else:
					comm = "INSERT INTO " + table + "(" + ",".join(columns) + ") VALUES" + ",".join("(" + ",".join("'" + k2 + "'" for k2 in k1) + ")" for k1 in values) + ";"
			else:
				if encoding:
					comm = "INSERT INTO " + table + "(" + ",".join(columns) + ") VALUES(" + ",".join("N'" + k + "'" for k in values[0]) + ");"
				else:
					comm = "INSERT INTO " + table + "(" + ",".join(columns) + ") VALUES(" + ",".join("'" + k + "'" for k in values[0]) + ");"

			try:
				self.cursor.execute(comm)
				self.conn.commit()
				return comm
			except Exception as e:
				return "\n".join([str(comm), str(e)])
		except Exception as e:
			return "Error: %s"%str(e)

	def Update(self, table=None, columns=None, values=None, conditions=None):
		try:
			comm = "UPDATE " + table + " SET "
			comm += ", ".join([(columns[k] + "='" + values[k]+"'") for k in range(len(values))])
			comm += " WHERE " + conditions if conditions else ""

			self.cursor.execute(comm)
			self.conn.commit()
			return comm
		except Exception as e:
			return comm + "\n" + "Values is not match with Columns or Something others error.\n" + str(e)

	def EXE_Procedure(self, spName, **kwargs):
		try:
			# vals = ",".join(["'{}'".format(str(kwargs[k])) if type(kwargs[k]) == str else str(kwargs[k]) for k in kwargs])
			# comm = "{" + "call {}({})".format(spName, vals) + "}"
			# comm = "EXEC {}({})".format(spName, vals)
			comm = "{" + "CALL {} (".format(spName) + ",".join(["?" for k in kwargs]) + ")}"
			vals = tuple([kwargs[k] for k in kwargs])
			rows = self.cursor.execute(comm, vals)
		except Exception as e:
			# print(comm, vals)
			return [None, "Parameter or SQL error.\n" + str(e)]
		else:
			return [rows, [comm, vals]]

	def Close(self):
		self.conn.close()
		self.conn = None
		self.cursor = None

