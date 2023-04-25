from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as dWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

import os, socket, requests, json
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from urllib.parse import quote
from math import radians, sin, asin, cos, sqrt
from time import sleep
from datetime import datetime as dt, timedelta as tdel


try:
	from utils.mail import Mail
	from utils.SqlServerConn import Conn
except:
	from .utils.mail import Mail
	from .utils.SqlServerConn import Conn

mail = Mail()
Conn = Conn()
local_ip    = socket.gethostbyname(socket.gethostname())
speShipType = ["拖轮/引航船", "集装箱船", "工作船", "油船", "客船"]
clsVSLName  = lambda vn: "".join([a for a in vn if a not in [" ", "."]]).upper()

debug = False

class getData(object):
	def chkCookieValue(self, **kwargs):
		# 控管cookie key value，約每10天更新一次
		if dt.now().day%10 == 0:
			try:
				stat, __key = self.get_key()
			except Exception as e:
				rstGetKey = [False, str(e)]
			else:
				if stat:
					rstGetKey = [True, __key]
					with open("D:/Shipdt/tools/kval.key", "w", encoding="utf-8") as wf:
						wf.write(__key)
				else:
					rstGetKey = [False, __key] # get_key回傳的錯誤
		else:
			try:
				with open("D:/Shipdt/tools/kval.key", "r") as rf:
					__key = rf.read()
			except Exception as e:
				rstGetKey = [False, str(e)]
			else:
				rstGetKey = [True, __key]
		return rstGetKey

	def getNow(self, fmt=None):
		now = dt.now()
		if fmt == None:
			return str(now.strftime("%Y-%m-%d %H:%M:%S"))
		else:
			return str(now.strftime(fmt))

	def getPvDays(self, pdy=1):
		# 預設取昨天
		now    = dt.now()
		delta  = tdel(pdy) # 單位天
		yester = now - delta # 減一天

		oy = str(yester.year)
		om = "0"+str(yester.month) if yester.month < 10 else str(yester.month)
		od = "0"+str(yester.day) if yester.day < 10 else str(yester.day)
		ot = oy+om+od
		return ot

	# With Sql Conn
	def getPvTimes(self, portID):
		Conn.Open()
		# 查詢條件為最接近昨日加上未被排除追蹤
		[rows, comm, _] = Conn.Select(
			table = ["IBTDB AS A JOIN PortDB AS B ON A.PortNo = B.SRNB"],
			columns = tuple(["MAX(A.RecTime) AS RecTime"]),
			conditions = "B.PortID = '{}' AND RecTime < '{}' AND A.Tracked = '0'".format(portID, self.getNow(fmt="%Y%m%d"))
		)
		row = rows.fetchall()
		Conn.Close()

		data = row[0][0]
		data = self.getPvDays() if data == None else data
		return data

	def get_key(self, consoleLog=False):
		try:
			options = webdriver.ChromeOptions()
			options.add_argument('--disable-gpu')
			options.add_experimental_option("excludeSwitches", ["enable-logging"]) # 不輸出log
			options.add_argument('--hide-scrollbars')  # 隱藏捲動軸, 應對一些特殊頁面
			# options.add_argument('blink-settings=imagesEnabled=false')  # 不載入圖片
			options.add_argument("--headless")  # 無介面
			options.add_argument("--incognito") # 無痕模式
			url = "http://www.shipdt.com/"
			uid = "shipdt - account"
			pwd = "shipdt - password"
			# timeout = 60 # sec

			# execute chrome driver
			driver = webdriver.Chrome(executable_path="tools/chromedriver.exe", options=options)
			driver.get(url); sleep(5)

			# 20230110 偵測彈出式視窗
			try:
				e_popsrc = dWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/img[2]")))
				e_popsrc.click(); sleep(0.5)
			except Exception as e:
				m = "Popout screen not exist or something wrong."
				if consoleLog:print(m)

			driver.switch_to.frame("iframeMap")
			try:
				e_lgn = dWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[8]")))
				e_lgn.click(); sleep(0.5)
			except Exception as e:
				m = "Open Login Page Timeout"
				if consoleLog:print(m)
				return [False, m]
			else:
				driver.switch_to.default_content()

			driver.switch_to.frame("loginIframe")
			try:
				inp_uid = dWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='app']/div/div[2]/form/div[1]/div/div/input")))
				inp_uid.send_keys(uid); sleep(0.25)
				inp_pwd = dWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='app']/div/div[2]/form/div[2]/div/div/input")))
				inp_pwd.send_keys(pwd); sleep(0.25)
				btn_smt = dWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='app']/div/div[2]/form/button")))
			except TimeoutException:
				m = "Login Timeout"
				if consoleLog:print(m)
				return [False, m]

			btn_smt.click(); sleep(5)
			driver.switch_to.default_content()

			cookies    = driver.get_cookies()
			cookie_key = [k["value"] for k in cookies if k["name"] == "__key"]
			__key      = cookie_key[0] if len(cookie_key) > 0 else ""
			if consoleLog: print(__key)
			return [True, __key]

		except Exception as e:
			return [False, str(e)]
		finally:
			sleep(3)
			driver.quit()

	def getTimeRng(self, preDays=7):
		now   = dt.now()
		delta = tdel(preDays) # Last week
		lwk   = now - delta

		sy  = str(lwk.year)
		sm  = "0"+str(lwk.month) if lwk.month < 10 else str(lwk.month)
		sd  = "0"+str(lwk.day) if lwk.day < 10 else str(lwk.day)
		stt = "{}-{}-{}+00%3A00%3A00".format(sy, sm, sd)

		ey  = str(now.year)
		em  = "0"+str(now.month) if now.month < 10 else str(now.month)
		ed  = "0"+str(now.day) if now.day < 10 else str(now.day)
		eH  = "0"+str(now.hour) if now.hour < 10 else str(now.hour)
		eM  = "0"+str(now.minute) if now.minute < 10 else str(now.minute)
		eS  = "0"+str(now.second) if now.second < 10 else str(now.second)
		edt = "{}-{}-{}+{}%3A{}%3A{}".format(ey, em, ed, eH, eM, eS)

		return [stt, edt]

	def getPortNo(self, PortID):
		return {
			"UyLYK6QpnDc=": "01", # Majuro
			"omORqog9iOE=": "02", # Pohnpei
			"CEC04XcMjzY=": "03", # Kosrae
			"qfIBr+HS7y8=": "04", # Tarawa
			"cui8x7FpRLk=": "05", # Rabaul
			"1fcKElcsVjc=": "06", # Funafuti
			"TtXhNB3cxN4=": "07", # Honiara
			"ng/puBXrHyQ=": "08", # Noro
			"1SynxGBLDzk=": "09", # PAGOPAGO
			"D9eJWGky+os=": "10", # Victoria
			"n/WOa7c0mMI=": "11", # Port_Victoria
			"Khw+OuYuzTQ=": "12", # Louis
			"B+RLL8zSdA8=": "13", # Diego_Suarez
			"6H2We6KdbSU=": "14", # Manta
			"ahSIOF8jtZc=": "15", # Posorja
			"ZxPAa7PYj+M=": "16", # Manzanillo
			"QzAghvV/9/g=": "17", # Mazatlan
			"xQQDdjKMsww=": "18", # Dakar
			"zJrLX2Y4VN8=": "19", # Abidjan
		}.get(PortID, PortID)

	# With Sql Conn
	def getVesselList(self, **kwargs):
		Conn.Open()
		# 只抓Tracked為1的狀態
		[rows, comm, _] = Conn.Select(
			table = ["VesselList"],
			columns = tuple(["CPNY", "VSLName1"]),
			conditions = "Tracked = '1'"
		)

		dbDatas = rows.fetchall()
		Conn.Close()

		CPNY, VSLName1 = [k for k in zip(*dbDatas)]
		VSLName1 = [clsVSLName(v) for v in VSLName1]
		return CPNY, VSLName1

	# With Sql Conn
	def getExtVesselList(self, **kwargs):
		Conn.Open()
		# 只抓Tracked為0的狀態
		[rows, comm, _] = Conn.Select(
			table = ["VesselList"],
			columns = tuple(["CPNY", "VSLName1"]),
			conditions = "Tracked = '0'"
		)

		dbDatas = rows.fetchall()
		Conn.Close()

		CPNY, VSLName1 = [k for k in zip(*dbDatas)]
		VSLName1 = [clsVSLName(v) for v in VSLName1]
		return CPNY, VSLName1

	# With Sql Conn
	def getYesterdayVSLList(self, **kwargs):
		try:
			portID = kwargs["PortID"] if "PortID" in kwargs.keys() else "UyLYK6QpnDc=" # 預設Majuro

			# 取得前次有記錄的日期(YYYYmmdd -> 8碼)
			ot = self.getPvTimes(portID = portID)

			Conn.Open()
			# 查詢條件為前次有紀錄的日期加上未被排除追蹤
			[rows, comm, _] = Conn.Select(
				table = ["IBTDB AS A JOIN PortDB AS B ON A.PortNo = B.SRNB"],
				columns = tuple(["A.MMSI AS MMSI", "A.VSLNM AS VSLNM", "A.IBT AS IBT", "B.PortID AS PortID"]),
				conditions = "A.RecTime='{}' AND PortID='{}' AND Tracked='0'".format(ot, portID)
			)

			dbDatas = rows.fetchall()
			Conn.Close()

			yester_Datas = {}
			for r in dbDatas:
				VSLNM, IBT, PortNM = r[1:]
				yester_Datas[r[0]] = { "VSLNM": VSLNM, "IBT": IBT, "PortNM":PortNM }
		except Exception as e:
			return [False, str(e)]
		else:
			if len(yester_Datas) > 0:
				return [True, yester_Datas]
			else:
				return [False, "Not Found"]

class vesselAPI(getData):
	def __init__(self):
		self.sess = requests.Session()
		# 設定重設3次
		self.sess.mount("http://", HTTPAdapter(max_retries=3))

	def queryVSL(self, **kwargs):
		mmsi        = kwargs["mmsi"]
		cookievalue = kwargs["token"]
		url         = "http://www.shipdt.com/lvservice/ship/getUnFocusShipDataNew?shipmmsi={}&aisstatu=1&cookievalue={}".format(mmsi, cookievalue)

		rtn_data = {}
		try:
			r        = self.sess.get(url, timeout=(30, 60))
			rsp_data = r.text
			datas    = json.loads(rsp_data)["data"]
			data     = json.loads(datas)

			rtn_data["imo"]       = str(data["result1"]["imo"])
			rtn_data["callsign"]  = str(data["result1"]["callsign"]).replace(" ", "")
			rtn_data["name"]      = str(data["result1"]["shipname"])
			rtn_data["type"]      = str(data["result1"]["shiptype"])
			rtn_data["dest_port"] = str(data["result1"]["dest_port"])
			rtn_data["dest_eta"]  = str(data["result1"]["eta"])[:5]

		except RequestException as e:
			rtn_data["imo"]       = ""
			rtn_data["callsign"]  = ""
			rtn_data["name"]      = ""
			rtn_data["type"]      = ""
			rtn_data["dest_port"] = ""
			rtn_data["dest_eta"]  = ""

		return rtn_data

	def Distense(self, **kwargs):
		# la 緯度 (φ), lg 經度 (λ)
		la1, lg1 = kwargs["pos1"]
		la2, lg2 = kwargs["pos2"]

		Th1 = radians(la1); Lm1 = radians(lg1)
		Th2 = radians(la2); Lm2 = radians(lg2)

		Phi = Th1-Th2 # Phi
		Lmb = Lm1-Lm2 # Lambda
		r   = 6378137

		Dis = 2*asin( sqrt( sin(Phi/2)**2 + cos(Th1)*cos(Th2)*(sin(Lmb/2)**2) ) )*r
		return round(Dis, 5)

	def TrulyIBT(self, **kwargs):
		__key     = kwargs["__key"]
		mmsi      = kwargs["mmsi"]
		url       = "http://www.shipdt.com/lvservice/ship/getUnFocusShipDataNew?shipmmsi={}&aisstatu=1&cookievalue={}".format(mmsi, __key)
		try:
			r = self.sess.get(url, timeout=(30, 60))
		except RequestException as e:
			exc = True
		else:
			exc = False

		try:
			if not exc and r.status_code == requests.codes.ok:
				try:
					respn = json.loads(r.text)["data"]
					result0 = json.loads(respn)["result0"]
					result1 = json.loads(respn)["result1"]
				except Exception as e:
					return [False, "No getUnFocusShipDataNew Data."]
				else:
					rst = {"Dis": "", "Time": "", "idx": "", "GPS": ""}

					speed = "0" if result1["speed"] == "" else float(result1["speed"])
					if speed > 1.0:
						return [False, "On Sea"]
					else:
						try:
							tt = dt.fromtimestamp(int(result0["anchorTime"]))

							y   = str(tt.year)
							m   = str(tt.month) if tt.month > 9 else "0"+str(tt.month)
							d   = str(tt.day) if tt.day > 9 else "0"+str(tt.day)

							# H = str(tt.hour) if tt.hour > 9 else "0"+str(tt.hour)
							# M = str(tt.minute) if tt.minute > 9 else "0"+str(tt.minute)
							# S = str(tt.second) if tt.second > 9 else "0"+str(tt.second)
						except:
							y = "0000"; m = "00"; d = "00"

						rst["Dis"]  = "0"
						rst["Time"] = "{}-{}-{}".format(y,m,d)
						rst["idx"]  = "0"
						rst["GPS"]  = "0,0"

						return [True, rst]
			else:
				return [False, "HTTP Error"]
		except Exception as e:
			return [False, str(e)]

	def TripHistory(self, **kwargs):
		__key     = kwargs["__key"]
		mmsi      = kwargs["mmsi"]
		GPS_Point = kwargs["GPS_Point"]
		stt, edt  = self.getTimeRng(preDays=7)
		url       = "http://www.shipdt.com/lvservice/ship/gettHisByTime?cookievalue={}&shipmmsi={}&startime={}&endtime={}".format(__key, mmsi, stt, edt)
		try:
			r = self.sess.get(url, timeout=(30, 60))
		except RequestException as e:
			exc = True
		else:
			exc = False

		try:
			if not exc and r.status_code == requests.codes.ok:
				try:
					respn = json.loads(r.text)["data"]
				except Exception as e:
					return [False, "No TripHistory Data."]
				else:
					minDis = 6378137
					rst = {"Dis": "", "Time": "", "idx": "", "GPS": ""}

					for k, data in enumerate(respn):
						try:
							la = round(float(data["lat"])/6e+5, 6)
							lg = round(float(data["lon"])/6e+5, 6)

							Dis = self.Distense(pos1=GPS_Point, pos2=[la, lg])
						except:
							la = 0; lg = 0; Dis = 0

						tt = data["pos_time"]
						try:
							tt  = dt.fromtimestamp(int(tt))
							y   = str(tt.year)
							m   = str(tt.month) if tt.month > 9 else "0"+str(tt.month)
							d   = str(tt.day) if tt.day > 9 else "0"+str(tt.day)

							# H = str(tt.hour) if tt.hour > 9 else "0"+str(tt.hour)
							# M = str(tt.minute) if tt.minute > 9 else "0"+str(tt.minute)
							# S = str(tt.second) if tt.second > 9 else "0"+str(tt.second)
						except:
							y = "0000"; m = "00"; d = "00"

						if Dis < minDis:
							minDis = Dis
							rst["Dis"]  = Dis
							rst["Time"] = "{}-{}-{}".format(y,m,d)
							rst["GPS"]  = "{},{}".format(la,lg)
							rst["idx"]  = str(k)
					return [True, rst]
			else:
				return [False, "HTTP Error"]
		except:
			return [False, str(e)]

	def disCompare(self, __key, vessels, defDis=100):
		if len(vessels) > 0:
			vslData    = {} # 暫存的全部船隻資料 dict[mmsi]=[shiptype, dest, eta]
			rstData    = [] # 作為回傳的比較資料 list[dict[mmsi]=[nm, mmsi, tp]]
			cprVslList = {} # 有被列入比較的船隻清單 > dict[mmsi]=vslname
			doCPR = True if len(vessels) > 1 else False # 若只有一艘船就不用比較

			if doCPR:
				for k1, v1 in enumerate(vessels):
					for k2, v2 in enumerate(vessels[k1+1:]):
						f1 = str(v1["fv"]); f2 = str(v2["fv"])
						m1 = str(v1["mm"]); m2 = str(v2["mm"])
						p1 = [v1["la"], v1["lg"]]
						p2 = [v2["la"], v2["lg"]]
						Dis = round(self.Distense(pos1=p1, pos2=p2), 5)

						# 取得船隻資料f1(以MMSI作為Key)
						if m1 not in vslData.keys():
							rtnDatas = self.queryVSL(mmsi=int(m1), token=__key)
							vslData[m1] = [f1, rtnDatas["type"], rtnDatas["dest_port"], rtnDatas["dest_eta"]]

						# 取得船隻資料f2(以MMSI作為Key)
						if m2 not in vslData.keys():
							rtnDatas = self.queryVSL(mmsi=int(m2), token=__key)
							vslData[m2] = [f2, rtnDatas["type"], rtnDatas["dest_port"], rtnDatas["dest_eta"]]

						# 從dict中取得資訊
						_, tp1, dest1, eta1 = vslData[m1]
						_, tp2, dest2, eta2 = vslData[m2]

						# 如果比較中的任一船隻屬於排除名單
						if tp1 in speShipType or tp2 in speShipType: continue

						# 先確認船隻距離(預設100m)且船隻型態不同才選擇輸出
						if Dis < defDis and tp1 != tp2:
							if m1 not in cprVslList: cprVslList[m1] = {"NM":f1, "MMSI":m1, "TP":tp1}
							if m2 not in cprVslList: cprVslList[m2] = {"NM":f2, "MMSI":m2, "TP":tp2}

							m = {
								"f1":f1, "tp1":tp1, "m1":m1,
								"f2":f2, "tp2":tp2, "m2":m2,
								"Dis":Dis
							}
							rstData.append(m)
					if v1 == vessels[len(vessels)-1]:
						break

			# 若只有一艘船的else
			else:
				fn = str(vessels[0]["fv"])
				mm = str(vessels[0]["mm"])
				rtnDatas = self.queryVSL(mmsi=int(mm), token=__key)
				vslData[mm] = [fn, rtnDatas["type"], rtnDatas["dest_port"], rtnDatas["dest_eta"]]

			if len(vslData) > 0 and rstData:
				return [True, rstData, vslData]
			else:
				return [False, "No Vessel be Compared.", vslData]
		else:
			print("No Data")

class procedure(vesselAPI):
	def partII(self, **kwargs):
		def partII_Templete1(rows=""):
			Content = """
			<table cellpadding='5px'>
				<thead>
					<tr>
						<th>Name</th>
						<th>Time</th>
					</tr>
				</thead>
				<tbody>
					<!--
						Following example below:
						<tr><td>Name</td><td class="cellCenter">Time</td></tr>
					-->
					{}
				</tbody>
			</table>
			""".format(rows)
			return Content

		def partII_Template2(err=""):
			Content = "<p>{}</p>".format(err)
			return Content

		__key        = kwargs["__key"]
		NT           = kwargs["NT"]
		portID       = kwargs["portID"]
		portGPS      = kwargs["portGPS"]
		htmlMsg      = kwargs["htmlMsg"]
		allVessels   = kwargs["allVessels"]
		vslData      = kwargs["vslData"]
		dbVSLList    = kwargs["dbVSLList"]
		dbCPNYList   = kwargs["dbCPNYList"]
		dbExtVSLList = kwargs["dbExtVSLList"]
		consoleLog   = False if "consoleLog" not in kwargs else kwargs["consoleLog"]
		testmode     = True if "testmode" not in kwargs else kwargs["testmode"]

		istIBTDB_Cols = tuple([
			"MMSI", "VSLNM", "FVTP", "IBT",
			"PortNo", "Dis", "GPS_Point", "RecTime"
		])
		istIBTDB_Vals = []
		recVessels    = []

		# ========== (補)Part II: 進港時間 (全部的船用清單及ShipType過濾) ==========
		# HTML Content -> PartII 標題改在模版裡預設

		try:
			chkRst = [] # 用於all的list，若全0代表都是排除清單的船
			msg2 = "" # 記錄每列結果
			for fv in allVessels:
				# 若整理後的船名存在於清單中或者ShipType不屬於例外
				mmsi = str(fv["mm"])

				# 條件應分開判斷，不在排除名單為前提再做後續動作
				if clsVSLName(fv["fv"]) not in dbExtVSLList:
					if vslData[mmsi][1] not in speShipType:
						try:
							cpny = dbCPNYList[dbVSLList.index(clsVSLName(fv["fv"]))] # 取得凍船公司名稱
						except:
							cpny = ""
						statVoyage, rstVoyage = self.TrulyIBT(mmsi=mmsi, __key=__key)
						if not statVoyage:
							statVoyage, rstVoyage = self.TripHistory(mmsi=mmsi, __key=__key, GPS_Point=portGPS)
					else:
						statVoyage = False
				else:
					statVoyage = False

				if statVoyage:
					chkRst+=[True]

					# P2 Data加入istIBTDB_Vals中
					istIBTDB_Vals.append([
						str(mmsi), str(fv["fv"]), vslData[mmsi][1], rstVoyage["Time"],
						self.getPortNo(portID), str(rstVoyage["Dis"]), rstVoyage["GPS"], NT
					])
					recVessels.append(str(mmsi))
					msg2 += "<tr><td>{}</td><td class=\"cellCenter\">{}</td></tr>".format(fv["fv"], rstVoyage["Time"])
				else:
					chkRst+=[False]

			else:
				# for跑完檢查chkRst的內容
				if not any(chkRst):
					htmlMsg = partII_Template2()

				if not testmode and len(istIBTDB_Vals) > 0:
					Conn.Open()
					if not debug:
						rst_IBTDB = Conn.Insert(
							table    = "IBTDB",
							columns  = istIBTDB_Cols,
							values   = istIBTDB_Vals,
							encoding = True
						)
					Conn.Close()

					# 編寫最後結果
					htmlMsg = partII_Templete1(msg2)

		except Exception as e:
			return [False, recVessels, _, partII_Template2(str(e))]
		else:
			return [True, recVessels, istIBTDB_Vals, htmlMsg]

	def partIII(self, **kwargs):
		def partIII_Templete1(rows=""):
			Content = """
			<table cellpadding='5px'>
				<thead>
					<tr>
						<th>Name</th>
						<th>Destination</th>
						<th>ETA</th>
					</tr>
				</thead>
				<tbody>
					<!--
						Following example below:
						<tr><td>Name</td><td>Destination</td><td class="cellCenter">ETA</td></tr>
					-->
					{}
				</tbody>
			</table>
			""".format(rows)
			return Content

		def partIII_Template2():
			Content = """<p></p>"""
			return Content

		__key        = kwargs["__key"]
		portID       = kwargs["portID"]
		recVessels   = kwargs["recVessels"]
		dbVSLList    = kwargs["dbVSLList"]
		dbCPNYList   = kwargs["dbCPNYList"]
		dbExtVSLList = kwargs["dbExtVSLList"]
		htmlMsg      = kwargs["htmlMsg"]
		consoleLog   = kwargs["consoleLog"] if "consoleLog" in globals() else False

		# HTML Content -> PartIII 標題改在模版裡預設

		FLAG = False # For all exist or not found

		try:
			# 看哪些船不見了 (運搬船查目的港)
			statYesterdayVSLList, rstYesterdayVSLList = self.getYesterdayVSLList(PortID = portID)

			# 記錄不見的船的[MMSI, VSLName]
			p3RtnList = []

			ytFlag = True
			msg3 = "" # 記錄每列結果
			if statYesterdayVSLList:
				for mmsi in rstYesterdayVSLList:
					# 若昨天的船未在今天的結果中
					if mmsi not in recVessels:
						rtnDatas = self.queryVSL(mmsi=mmsi, token=__key)
						imo = rtnDatas["imo"]
						fv  = rtnDatas["name"]
						tp  = rtnDatas["type"]

						if tp not in speShipType and tp != "渔船" and clsVSLName(fv) not in dbExtVSLList:
							# HTML Content -> 使用 table 呈現，格式 -> <tr><td></td>*3</tr> -> 搭配 3個 head
							msg3 += "<tr><td>{}</td><td>{}</td><td class=\"cellCenter\">{}</td></tr>".format(fv, rtnDatas["dest_port"], rtnDatas["dest_eta"])
							p3RtnList.append([mmsi, rtnDatas["name"]])
							ytFlag = False
				else:
					if ytFlag: # 判斷for裡的if有沒有執行
						FLAG = True # 用於決定要不要執行PartIV
			else:
				FLAG = True # 用於決定要不要執行PartIV
			htmlMsg = partIII_Templete1(msg3) if msg3 != "" else partIII_Template2()
		except Exception as e:
			return [False, htmlMsg, p3RtnList]
		else:
			if FLAG:
				return [False, htmlMsg, p3RtnList]
			else:
				return [True, htmlMsg, p3RtnList]

	def partIV(self, **kwargs):
		def partIV_Templete1(vsln="", rows=""):
			Content = """
			<h4>Vessel: {}</h4>
			<table cellpadding='5px'>
				<thead><tr><th>Name</th><th>RecordTime(From-To)</th></tr></thead>
				<tbody>{}</tbody>
			</table>
			""".format(vsln, rows)
			return Content

		def partIV_Template2(vsln = "", msg = ""):
			Content = """
			<h4>Vessel: {}</h4>
			<p>{}</p>
			""".format(vsln, msg)
			return Content

		p3RtnList  = [] if "p3RtnList" not in kwargs.keys() else kwargs["p3RtnList"]
		PortNo     = "01" if "PortID" not in kwargs.keys() else self.getPortNo(kwargs["PortID"]) # 預設Majuro
		htmlMsg    = kwargs["htmlMsg"]
		consoleLog = kwargs["consoleLog"] if "consoleLog" in globals() else False

		# HTML Content -> PartIV 標題改在模版裡預設

		# 船名預設為空
		vsln = ""
		if len(p3RtnList) > 0:
			try: # 負責主要的偵錯
				Conn.Open()

				for data in p3RtnList:
					mmsi, vsln = data
					eta = ""
					# HTML Content -> vsln改為傳入到模版中
					try: # 負責SQL的偵錯
						[rows, comm] = Conn.EXE_Procedure(
							spName="VSL_SEC_DATA",
							MMSI = mmsi,
							PortNo = PortNo
							)
						dbDatas = rows.fetchall()
					except Exception as e:
						pass
					else:
						tmp = ""
						if len(dbDatas) > 0:
							tmp_nmDict = {}
							for data in dbDatas:
								vslnm = data[0]
								eta = data[1]
								if vslnm not in tmp_nmDict:
									tmp_nmDict[vslnm] = {"eta": eta, "etd": ""}
								else:
									tmp_nmDict[vslnm]["etd"] = eta # 用最新的日期取代前一筆資料的日期
							else:
								for kynm in tmp_nmDict:
									st = tmp_nmDict[kynm]["eta"]
									ed = tmp_nmDict[kynm]["etd"]
									ed = st if ed == "" else ed # 如果etd為空，代表只有一筆資料因此eta=etd

									# HTML Content -> 使用 table 呈現，格式 -> <tr><td></td>*2</tr> -> 搭配 2個 head
									tmp += "<tr><td>{}</td><td class=\"cellCenter\">{}</td></tr>".format(
										kynm, "{} - {}".format(
											dt.strptime(st, "%Y%m%d").strftime("%Y/%m/%d"), # 記錄的起始日
											dt.strptime(ed, "%Y%m%d").strftime("%Y/%m/%d")  # 記錄的到期日
										)
									)
								else:
									htmlMsg += partIV_Templete1(vsln = vsln, rows = tmp)

						else:
							# 停泊期間無接觸船隻(另外查詢凍船的ETA)
							[rows, comm, _] = Conn.Select(
								table = ["IBTDB"],
								columns = tuple(["MIN(RecTime) AS RecTime"]),
								conditions = "MMSI = '{}' AND PortNo = '{}' AND Tracked = '0'".format(mmsi, PortNo)
								)
							row = rows.fetchall()
							eta = "19850101" if type(eta) == type(None) else str(row[0][0]).strip()

						# 最後該凍船排除追蹤
						if not debug:
							comm = Conn.Update(
								table 	= "IBTDB",
								columns = ["Tracked"],
								values 	= ["1"],
								conditions = "MMSI = '{}' AND PortNo = '{}' AND RecTime <= '{}'".format(mmsi, PortNo, self.getPvDays())
							) # 既然凍船出港, 不再追蹤過去

			except Exception as e:
				return [False, htmlMsg+partIV_Template2(vsln = str(vsln) + "Error", msg = str(e))]
			else:
				return [True, htmlMsg]
			finally:
				Conn.Close()

		# 若MMSIList為空的else處理
		else:
			return [False, ""]

	def main(self, __key, port, portGPS, consoleLog=False, testmode=True):
		def callError(htmlMsg, msg):
			# HTML Content
			htmlMsg += "<p>{}</p>".format(str(msg))
			return htmlMsg

		try:
			# HTML Content
			othlMsg         = "" # 記錄例外狀況
			PartI_Content   = "" # PartI   內容
			PartII_Content  = "" # PartII  內容
			PartIII_Content = "" # PartIII 內容
			PartIV_Content  = "" # PartIV  內容

			portNM, portID = port
			pageNum  = ""
			pageSize = ""
			maxDWT   = ""
			minDWT   = ""
			shipType = ""

			addition    = "{'portId':'%s','pageNum':'%s','pageSize':'%s','maxDWT':'%s','minDWT':'%s','shipType':'%s'}" % (portID, pageNum, pageSize, maxDWT, minDWT, shipType)
			cookievalue = "&cookievalue=%s" % (__key)
			url         = "http://www.shipdt.com/lvservice/port/600016?shipConditions="+quote(addition)+cookievalue
			r = requests.get(url)

			# 從資料庫中取得追蹤中的清單 2D List [[dbCPNYList], [dbVSLList]]
			dbCPNYList, dbVSLList = self.getVesselList()
			dbExtCPNYList, dbExtVSLList = self.getExtVesselList()

		except Exception as e:
			# HTML Content -> 隸屬PartI報錯範圍
			PartI_Content += "<p>Some error happened. -> {}</p>".format(str(e))

		else:
			if r.status_code == requests.codes.ok:
				# 印出目前處理的港口
				# HTML title 帶變數 portNM

				for tmp in range(1): # 利用for的break來中斷程式
					respn = json.loads(r.text)["data"]
					if "result" not in json.loads(respn):
						# HTML Content -> 此階段屬於 PartI 的執行範圍
						break
					else:
						datas = json.loads(respn)["result"]

					allVessels = [] # 該港全部的船隻

					# ========== Init: 準備相關變數 ==========
					NT = dt.now().strftime("%Y%m%d")

					istFVDB_Cols = tuple([
						"FV1MMSI", "FV1NM", "FV1TP",
						"FV2MMSI", "FV2NM", "FV2TP",
						"PortNo", "RecTime",
					])

					if datas:
						for data in datas:
							sn = data["sn"] if "sn" in data else "" # Vessel Name: shipdt回傳json中sn會掉key, 若找不到補空白
							mm = int(data["mmsi"]) # MMSI
							la = round(float(data["la"])/6e+5, 6) # Latitude
							lg = round(float(data["lg"])/6e+5, 6) # longitude
							allVessels.append({"fv":sn, "la":la, "lg":lg, "mm":mm}) # 依港口取回的在港清單
						else:
							rst = self.disCompare(__key, allVessels)

							istFVDB_Vals = []

							if rst and rst[0]:
								# 拆解disCompare回傳的資料
								rstData, vslData = rst[1:] # rstData: 比較後的資料；vslData: 該港全部的船隻資料

								# ========== Part I: 距離相近的船隻過濾 ==========
								# HTML Content -> PartI 標題改在模版裡預設

								for idx, rsdt in enumerate(rstData):
									f1  = rsdt["f1"]; tp1 = rsdt["tp1"]; m1 = rsdt["m1"]
									f2  = rsdt["f2"]; tp2 = rsdt["tp2"]; m2 = rsdt["m2"]
									Dis = rsdt["Dis"]

									# 若f1或f2在排除名單中，則做continue
									if clsVSLName(f1) in dbExtVSLList or clsVSLName(f2) in dbExtVSLList:
										continue

									# P1 Data加入istVals_Vals中
									istFVDB_Vals.append([
											str(m1), f1, tp1,
											str(m2), f2, tp2,
											self.getPortNo(portID), NT
										])

									# HTML Content -> 使用 ol > li 呈現
									PartI_Content += "<li>{} / {}</li>".format(f1, f2)
								else:
									# for結束後用 ol 包住 li
									PartI_Content = "<ol>{}</ol>".format(PartI_Content)

									if not testmode:
										Conn.Open()
										if not debug:
											rst_FVDB = Conn.Insert(
												table    = "FVDB",
												columns  = istFVDB_Cols,
												values   = istFVDB_Vals,
												encoding = True
											)
										Conn.Close()

								# ========== Part II: 進港時間 (全部的船用清單及ShipType過濾) ==========
								statPartII, recVessels, istIBTDB_Vals, PartII_Content = self.partII(
									__key      = __key,      NT         = NT,
									portID     = portID,     portGPS    = portGPS, htmlMsg = PartII_Content,
									allVessels = allVessels, vslData    = vslData,
									dbVSLList = dbVSLList, dbCPNYList = dbCPNYList, dbExtVSLList = dbExtVSLList,
									consoleLog = consoleLog, testmode   = testmode)

								if statPartII:
									# ========== Part III: 凍船目的港&ETA ==========
									statPartIII, PartIII_Content, p3RtnList = self.partIII(
										__key      = __key,      portID     = portID    , recVessels = recVessels,
										dbVSLList = dbVSLList, dbCPNYList = dbCPNYList, dbExtVSLList = dbExtVSLList,
										htmlMsg    = PartIII_Content, consoleLog = consoleLog) # 20211108改為 HTML Content

									if statPartIII:
										# ========== Part IV: 抓凍船在港期間經手過的船 ==========
										statPartIV, PartIV_Content = self.partIV(
											PortID  = portID,  p3RtnList  = p3RtnList,
											htmlMsg = PartIV_Content, consoleLog = consoleLog)

							else:
								# 若沒有船隻被比較到(轉載行為)
								_, vslData = rst[1:]

								# ========== (補)Part I: 距離相近的船隻過濾 ==========
								# HTML Content

								# ========== (補)Part II: 進港時間 (全部的船用清單及ShipType過濾) ==========
								statPartII, recVessels, istIBTDB_Vals, PartII_Content = self.partII(
									__key      = __key,      NT         = NT,
									portID     = portID,     portGPS    = portGPS, htmlMsg = PartII_Content,
									allVessels = allVessels, vslData    = vslData,
									dbVSLList = dbVSLList, dbCPNYList = dbCPNYList, dbExtVSLList = dbExtVSLList,
									consoleLog = consoleLog, testmode   = testmode)

								if statPartII:
									# ========== (補)Part III: 凍船目的港&ETA ==========
									statPartIII, PartIII_Content, p3RtnList = self.partIII(
										__key      = __key,      portID     = portID    , recVessels = recVessels,
										dbVSLList = dbVSLList, dbCPNYList = dbCPNYList, dbExtVSLList = dbExtVSLList,
										htmlMsg    = PartIII_Content, consoleLog = consoleLog)

									if statPartIII:
										# ========== (補)Part IV: 抓凍船在港期間經手過的船 ==========
										statPartIV, PartIV_Content = self.partIV(
											PortID  = portID,  p3RtnList  = p3RtnList,
											htmlMsg = PartIV_Content, consoleLog = consoleLog)
					else:
						# HTML Content
						PartI_Content = callError(PartI_Content, msg="API Error.")
						break

			else:
				# HTML Content
				PartI_Content = callError(PartI_Content, msg="API Error.")

		finally:
			return PartI_Content, PartII_Content, PartIII_Content, PartIV_Content

def genBody(Port="", PartI="", PartII="", PartIII="", PartIV=""):
	# 讀取body模版
	with open("D:/Shipdt/tools/body.txt", "r") as rf:
		body_Template = rf.read()

	# 設定空內容
	# if PartI == "": PartI = "<p></p>"
	# if PartII == "": PartII = "<tr>"+"<td></td>"*3+"</tr>"
	# if PartIII == "": PartIII = "<tr>"+"<td></td>"*3+"</tr>"
	# if PartIV == "": PartIV = "<p></p>"

	# body內容取代
	body_Template = body_Template.replace("@Port", Port)
	body_Template = body_Template.replace("@PartI_Content", PartI)
	body_Template = body_Template.replace("@PartII_Content", PartII)
	body_Template = body_Template.replace("@PartIII_Content", PartIII)
	body_Template = body_Template.replace("@PartIV_Content", PartIV)

	return body_Template

def genHTML(title="", body_Content=""):
	# 設定title為時間
	t = getData().getNow(fmt="%Y-%m-%d")
	if title == "": title = t+"_Report"

	# 讀取html本體
	with open("D:/Shipdt/tools/html.txt", "r") as rf:
		html_Content = rf.read()

	# html內容取代
	html_Content = html_Content.replace("@title_Content", title)
	html_Content = html_Content.replace("@body_Content", body_Content)

	return html_Content

def sentMail(m, f=None, debug=False):
	debugRcv_name = ""
	debugRcv_mail = []
	trulyRcv_name = ", ".join(["Ray", "Ray"])
	trulyRcv_mail = ["Ray@mail.idv.tw", "Ray@mail.idv.tw"]

	if debug:
		frnm = "Ray"; sender = "Ray@mail.idv.tw" # 寄件者名稱 / 寄件者信箱
		tonm = "Ray"; receivers = ["Ray@mail.idv.tw"] # 收件者清單 / 收件者信箱
		ccnm = "Ray"; cc = ["Ray@mail.idv.tw"] # 知會者清單 / 知會者信箱
		sbj = "【測試】 Shipdt Port Movement ({})".format(str(getData().getNow(fmt="%Y-%m-%d"))) # 主旨
	else:
		frnm = "Ray"; sender = "Ray@mail.idv.tw" # 寄件者名稱 / 寄件者信箱
		tonm = trulyRcv_name; receivers = trulyRcv_mail # 收件者清單 / 收件者信箱
		ccnm = "Ray"; cc = ["Ray@mail.idv.tw"] # 知會者清單 / 知會者信箱
		sbj = "【通知】 Shipdt Port Movement ({})".format(str(getData().getNow(fmt="%Y-%m-%d"))) # 主旨

	mail.sentMail(
		fr=sender, frnm=frnm,
		to=receivers, tonm=tonm,
		cc=cc, ccnm=ccnm,
		sbj=sbj, m=m, attFile=[f] if f != None else None
	)


if __name__ == '__main__':
	portList = {
		"Majuro":   {"portID": "UyLYK6QpnDc=", "GPS_Point": [7.155272, 171.188124]}, # Majuro
		"Pohnpei":  {"portID": "omORqog9iOE=", "GPS_Point": [6.981255, 158.198431]}, # Pohnpei
		"Kosrae":   {"portID": "CEC04XcMjzY=", "GPS_Point": [5.332344, 162.991832]}, # Kosrae
		"Tarawa":   {"portID": "qfIBr+HS7y8=", "GPS_Point": [1.405756, 172.924796]}, # Tarawa
		"Rabaul":   {"portID": "cui8x7FpRLk=", "GPS_Point": [-4.247005, 152.174807]}, # Rabaul
		"Funafuti": {"portID": "1fcKElcsVjc=", "GPS_Point": [-8.430738, 179.105698]}, # Funafuti
		"Honiara":  {"portID": "TtXhNB3cxN4=", "GPS_Point": [-9.398214, 159.988855]}, # Honiara
		"Noro":     {"portID": "ng/puBXrHyQ=", "GPS_Point": [-8.197176, 157.198211]}, # Noro
		"PAGOPAGO": {"portID": "1SynxGBLDzk=", "GPS_Point": [-14.291153, -170.670885]}, # PAGOPAGO
		### ===================  Except  =================== ###
		"Victoria": {"portID": "D9eJWGky+os=", "GPS_Point": [-4.616550, 55.470024]}, # Victoria, Mahe, Seychelles
		"Port_Victoria": {"portID": "n/WOa7c0mMI=", "GPS_Point": [-4.620753, 55.478349]}, # Port Victoria, Mahe, Seychelles
		"Louis": {"portID": "Khw+OuYuzTQ=", "GPS_Point": [-20.145988, 57.482251]}, # Port Louis, Mauritius
		"Diego_Suarez": {"portID": "B+RLL8zSdA8=", "GPS_Point": [-20.145988, 57.482251]}, # Madagascar Diego Suarez
		"Manta": {"portID": "6H2We6KdbSU=", "GPS_Point": [-0.919589, -80.697748]}, # Manta, Ecuador
		"Posorja": {"portID": "ahSIOF8jtZc=", "GPS_Point": [-2.709251, -80.239366]}, # Posorja, Ecuador
		"Manzanillo": {"portID": "ZxPAa7PYj+M=", "GPS_Point": [19.071432, -104.340740]}, # Manzanillo, Mexico
		"Mazatlan": {"portID": "QzAghvV/9/g=", "GPS_Point": [23.176648, -106.420758]}, # Mazatlan, Mexico
		"Dakar": {"portID": "xQQDdjKMsww=", "GPS_Point": [14.677963, -17.418604]}, # Dakar, Senagal
		"Abidjan": {"portID": "zJrLX2Y4VN8=", "GPS_Point": [5.248036, -4.002326]}, # Abidjan, Ivory Coast
	}

	# 初始化getData Class
	gt = getData()
	pd = procedure()

	# 控管cookie key value，約每10天更新一次
	stat, __key = gt.chkCookieValue()

	# 取得目前日期作為log檔名
	n  = dt.now()
	ny = str(n.year)
	nm = "0"+str(n.month) if n.month < 10 else str(n.month)
	nd = "0"+str(n.day) if n.day < 10 else str(n.day)
	nt = ny+nm+nd

	# 檢查資料夾是否存在否則建立
	# part1 for officially
	# part2 for backup
	pth1 = f"D:\\Shipdt\\web\\page\\{ny}\\{nm}"
	# pth2 = f"D:\\Backup\\Shipdt\\Web\\{ny}\\{nm}"
	if not os.path.isdir(pth1): os.makedirs(pth1)
	# if not os.path.isdir(pth2): os.makedirs(pth2)

	if debug:
		webfn  = pth1 + f"\\{nt}-test.html"
		# webfn2 = pth2 + f"\\{nt}-test.html"
	else:
		webfn  = pth1 + f"\\{nt}.html"
		# webfn2 = pth2 + f"\\{nt}.html"

	# 初始化HTML與Body
	HTML_Content = ""
	body_Content = ""

	if stat:
		m = []
		for ky in portList:
			# HTML Content
			PartI, PartII, PartIII, PartIV = pd.main(__key, [ky, portList[ky]["portID"]], portList[ky]["GPS_Point"], testmode=False)
			body_Content += genBody(Port=str(ky), PartI=PartI, PartII=PartII, PartIII=PartIII, PartIV=PartIV)

		else:
			# HTML Content 內容
			HTML_Content = genHTML(body_Content=body_Content)
			with open(webfn, "w", encoding="utf-8") as wf:
				wf.write(HTML_Content)
			# 同步寫入到備份資料夾中
			with open(webfn2, "w", encoding="utf-8") as wf:
				wf.write(HTML_Content)
			# sentMail(
			# 	m = "請參考附件\n\n清單管理：http://"+local_ip+":8066\n\n\n",
			# 	f = webfn,
			# 	debug = debug
			# ) # 舊的附件版
			if debug:
				sentMail(
					m = "每日報告：http://"+local_ip+":8066/page/\n\n清單管理：http://"+local_ip+":8066\n\n",
					f = webfn,
					debug = debug
				) # 202111212331新的網頁datepicker版(debug)
			else:
				sentMail(
					m = "每日報告：http://"+local_ip+":8066/page/\n\n清單管理：http://"+local_ip+":8066\n\n"
				) # 202111212331新的網頁datepicker版
	else:
		# print(__key)
		sentMail( m="Something wrong when get key.\n\nThe possible: {}".format(str(__key)), debug=debug )

	print("Done.")
	exit()