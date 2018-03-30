#!/usr/bin/python
import pymysql
import copy
import time
import datetime
from datetime import timedelta


class DB:
    def getIntent(self, i):
        return MyuSQL().get('intent', i)

    def getMatchRate(self, i):
        return MyuSQL().get('match_rate', i)

    def getIProblem(self, i):
        return MyuSQL().get('IPNO', i)

    def getProblem(self, i):
        return MyuSQL().get('PNO', i)

    def getEndTime(self, i):
        return MyuSQL().getQ('end_time', i)

    def getHP(self, end_time):
        return MyuSQL().getH('heart_point', end_time)

    def setCscore(self, score):
        return MyuSQL().set('Cscore', score)

    def setIscore(self, score):
        return MyuSQL().set('Iscore', score)

    def setMscore(self, score):
        return MyuSQL().set('Mscore', score)

    def setHscore(self, score):
        return MyuSQL().set('Hscore', score)

    def compareProblem(self, i):
        iProblem = self.getIProblem(i)
        problem = self.getProblem(i)
        if iProblem == problem:
            return 1
        else:
            return 0

    def getNLPdata(self, i):
        nlp = MyuSQL().getNLP(i)
        return nlp

    def insertRecord(self, nlp):
        return MyuSQL().insert(nlp["Aid"], nlp["match_rate"], nlp["intent"], nlp["IPNO"], nlp["PNO"])

    def getLastAnalysisId(self):
        return MyuSQL().getLuisId()

    def insertDefault(self, Lid):
        PNO = self.getProblem(Lid)
        return MyuSQL().insert(Lid, 0.7687746, "Worst", PNO, PNO)


class Scoring:
    def calculateScore(self, i):
        score = {}
        score["Cscore"] = self.calculateCscore(DB().compareProblem(i), i)
        score["Iscore"] = self.calculateIscore(DB().getIntent(i), i)
        score["Mscore"] = self.calculateMscore(DB().getMatchRate(i), i)
        score["Hscore"] = self.calculateHscore(DB().getHP(DB().getEndTime(i), i), i)
        if score["Cscore"] == 0:
            score["Iscore"] = 0
            score["Mscore"] = 0
        DB().setCscore(score["Cscore"], i)
        DB().setIscore(score["Iscore"], i)
        DB().setMscore(score["Mscore"], i)
        DB().setHscore(score["Hscore"], i)
        return score

    def calculateCscore(self, compare):
        Cscore = compare * 20
        return Cscore

    def calculateIscore(self, intent):
        if intent == "best":
            return 30
        else:
            return 0

    def calculateMscore(self, matchrate):
        Mscore = matchrate * 30
        return Mscore

    def calculateHscore(self, hp):
        Hscore = 0;
        count = 0;
        while hp[count] is not None:
            number = int(hp[count][0])
            Hscore += number
            count += 1
        Hscore /= count
        return Hscore * 5

    def pushDefault(self, Lid):
        DB().insertDefault(Lid)

class Query:
    def login(self):
        host = 'localhost'
        port = 3306
        user = 'user'
        password = 'password'
        database = 'interview'
        charset = 'utf8'
        return pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)

    def getExecute(self, sql):
        connect = self.login()
        cursor = connect.cursor()
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            connect.close()
            return result
        except:
            print("ge")
            connect.close()

    def getExecute2(self, sql, i):
        connect = self.login()
        cursor = connect.cursor()
        try:
            cursor.execute(sql, (i))
            result = cursor.fetchone()
            connect.close()
            return result
        except:
            print("ge")
            connect.close()

    def getExecute3(self, sql, i, j):
        connect = self.login()
        cursor = connect.cursor()
        try:
            cursor.execute(sql, (i, j))
            result = cursor.fetchall()
            connect.close()
            return result
        except:
            print("ge")
            connect.close()

    def setExecute3(self, sql, data, aid):
        connect = self.login()
        cursor = connect.cursor()
        try:
            cursor.execute(sql, (data, aid))
            connect.commit()
        except:
            print("se")
        finally:
            connect.close()

    def setExecute6(self, sql, Aid, match_rate, intent, IPNO, PNO):
        connect = self.login()
        cursor = connect.cursor()
        try:
            cursor.execute(sql, (Aid, match_rate, intent, IPNO, PNO))
            connect.commit()
        except:
            print("se")
        finally:
            connect.close()

    def initDB(self, sql):
        connect = self.login()
        cursor = connect.cursor()
        try:
            cursor.execute(sql)
            connect.commit()
        except:
            print("init")
        finally:
            connect.close()



class MyuSQL:
    def get(self, record, i):
        tup = Query().getExecute2("select " + record + " from answer WHERE Aid = %s", i)
        return tup[0]

    def getLuisId(self):
        tup = Query().getExecute("select id from analysis order by id desc limit 1")
        return tup[0]

    def getH(self, record, end_time):
        plus_time = copy.deepcopy(end_time) + timedelta(minutes=1)
        tup = Query().getExecute3("select " + record + " from heart_rate WHERE time between %s and %s", str(end_time), str(plus_time))
        return tup

    def getQ(self, record, i):
        tup = Query().getExecute2("select " + record + " from question WHERE Qid = %s", i)
        return tup[0]

    def getNLP(self, i):
        nlp = {}
        nlp["Aid"] = i
        tup1 = Query().getExecute2("select intentScore from analysis WHERE id = %s", i)
        tup2 = Query().getExecute2("select score from analysis WHERE id = %s", i)
        tup3 = Query().getExecute2("select intent from analysis WHERE id = %s", i)
        tup4 = Query().getExecute2("select PNO from question WHERE Qid = %s", i)
        nlp["match_rate"] = tup1[0]
        nlp["intent"] = tup2[0]
        nlp["IPNO"] = self.searchPNO(tup3[0])
        nlp["PNO"] = tup4[0]

        return nlp

    def searchPNO(self, ipno):
        tup = Query().getExecute2("select Pid from problem WHERE p_text = %s", ipno)
        result = tup[0]
        return result

    def set(self, record, data, i):
        Query().setExecute3("UPDATE answer SET " + record + " = %s WHERE Aid = %s", data, i)
        result = self.get(record, i)
        return result

    def insert(self, Aid, match_rate, intent, IPNO, PNO):
        try:
            Query().setExecute6("insert into answer (Aid, match_rate, intent, IPNO, PNO) values (%s, %s, %s, %s, %s)", Aid, match_rate, intent, IPNO, PNO)
        except:
            Query().setExecute6("insert into answer (Aid, match_rate, intent, IPNO, PNO) values (%s, %s, %s, %s, %s)", Aid, match_rate, intent, IPNO, PNO)

    def initTable(self):
        Query().initTable("delete from answer")


def Score():
    db = DB()
    scoring = Scoring()
    _time = 0
    Bug = True
    while True:
        try:
            Lid = db.getLastAnalysisId()
            if Lid > 4:
                Bug = False
                i=1
                while i < 6:
                    db.insertDefault(db.getNLPdata(i))
                    scoring.calculateScore(i)
                    i+=1
        except:
            Bug = True
            loopCounter = 0
        finally:
            if Bug is True and loopCounter > 240:
                while Lid < 5:
                    Lid += 1
                    scoring.pushDefault(Lid)
            print(str(_time) + "초 경과")
            _time += 1
            time.sleep(1)
            loopCounter += 1

Score()