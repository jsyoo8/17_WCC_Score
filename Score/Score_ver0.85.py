#!/usr/bin/python
import pymysql
import copy
import time
import datetime
from datetime import timedelta


class DB:
    def getIntent(self):
        return MyuSQL().get('intent')

    def getMatchRate(self):
        return MyuSQL().get('match_rate')

    def getIProblem(self):
        return MyuSQL().get('IPNO')

    def getProblem(self):
        return MyuSQL().get('PNO')

    def getEndTime(self, i):
        return MyuSQL().getQ('end_time', i)

    def getHP(self, end_time):
        empty = "empty"
        if end_time == empty:
            result = ( )
            return result
        else:
            return MyuSQL().getH('heart_point', end_time)

    def setCscore(self, score):
        return MyuSQL().set('Cscore', score)

    def setIscore(self, score):
        return MyuSQL().set('Iscore', score)

    def setMscore(self, score):
        return MyuSQL().set('Mscore', score)

    def setHscore(self, score):
        return MyuSQL().set('Hscore', score)

    def compareProblem(self):
        iProblem = self.getIProblem()
        problem = self.getProblem()
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
        return MyuSQL().getLast()


class Scoring:
    def calculateScore(self, i):
        score = {}
        score["Cscore"] = self.calculateCscore(DB().compareProblem())
        score["Iscore"] = self.calculateIscore(DB().getIntent())
        score["Mscore"] = self.calculateMscore(DB().getMatchRate())
        score["Hscore"] = self.calculateHscore(DB().getHP(DB().getEndTime(i)))
        if score["Cscore"] == 0:
            score["Iscore"] = 0
            score["Mscore"] = 0
        DB().setCscore(score["Cscore"])
        DB().setIscore(score["Iscore"])
        DB().setMscore(score["Mscore"])
        DB().setHscore(score["Hscore"])
        return score

    def calculateCscore(self, compare):
        empty = "empty"
        if compare != empty:
            Cscore = compare * 20
            return Cscore

    def calculateIscore(self, intent):
        empty = "empty"
        if intent != empty:
            if intent == "best":
                return 30
            else:
                return 0

    def calculateMscore(self, matchrate):
        empty = "empty"
        if matchrate != empty:
            Mscore = matchrate * 30
            return Mscore

    def calculateHscore(self, hp):
        result = ( )
        Hscore = 0;
        count = 0;
        if hp is not result:
            if hp[count] is not None:
                number = int(hp[count][0])
                Hscore += number
                count += 1
            Hscore /= count
            return Hscore * 5


class Query:
    def login(self):
        host = 'localhost'
        port = 3306
        user = 'root'
        password = 'password'
        database = 'interview'
        charset = 'utf8'
        return pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)

    def getExecute(self, sql):
        connect = self.login()
        cursor = connect.cursor()
        try:
            cursor.execute(sql)
            if cursor.description is not None:
                result = cursor.fetchone()
                if result is None:
                    result = ("empty",)
        except:
            result = ("empty",)
        finally:
            connect.close()
        return result

    def getExecute2(self, sql, i):
        connect = self.login()
        cursor = connect.cursor()
        try:
            cursor.execute(sql, (i))
            if cursor.description is not None:
                result = cursor.fetchone()
                if result is None:
                    result = ("empty",)
        except:
            result = ("empty",)
        finally:
            connect.close()
        return result

    def getExecute3(self, sql, i, j):
        connect = self.login()
        cursor = connect.cursor()
        try:
            cursor.execute(sql, (i, j))
            if cursor.description is not None:
                result = cursor.fetchall()
                if result is None:
                    result = ("empty",)
        except:
            result = ("empty",)
        finally:
            connect.close()
        return result

    def setExecute3(self, sql, data, aid):
        connect = self.login()
        cursor = connect.cursor()
        cursor.execute(sql, (data, aid))
        connect.commit()
        connect.close()

    def setExecute6(self, sql, Aid, match_rate, intent, IPNO, PNO):
        connect = self.login()
        cursor = connect.cursor()
        cursor.execute(sql, (Aid, match_rate, intent, IPNO, PNO))
        connect.commit()
        connect.close()


class MyuSQL:
    def get(self, record):
        tup = Query().getExecute("select " + record + " from answer order by Aid desc limit 1")
        return tup[0]

    def getLuisId(self):
        tup = Query().getExecute("select id from anlalysis order by id desc limit 1")
        return tup[0]

    def getH(self, record, end_time):
        if end_time == "empty":
            return ("empty",)
        else:
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
        #tup5 = Query().getExecute()
        nlp["match_rate"] = tup1[0]
        nlp["intent"] = tup2[0]
        ipno = tup3[0]
        tup = Query().getExecute2("select Pid from problem WHERE p_text = %s", ipno)
        nlp["IPNO"] = tup[0]
        nlp["PNO"] = tup4[0]
        #nlp["Aid"] =

        return nlp

    def set(self, record, data):
        tup = Query().getExecute("select Aid from answer order by Aid desc limit 1")
        Query().setExecute3("UPDATE answer SET " + record + " = %s WHERE Aid = %s", data, tup[0])
        result = self.get(record)
        return result

    def insert(self, Aid, match_rate, intent, IPNO, PNO):
        empty = "empty"
        result = self.get("Aid")
        if type(result) is str:
            if match_rate != empty:
                if intent != empty:
                    if IPNO != empty:
                        if PNO != empty:
                            Query().setExecute6(
                                "insert into answer (Aid, match_rate, intent, IPNO, PNO) values (%s, %s, %s, %s, %s)", Aid, match_rate, intent, PNO, PNO)
            Aid = result
        else:
            Luisid = self.getLuisId()
            if Aid > result:
                Query().setExecute6(
                    "insert into answer (Aid, match_rate, intent, IPNO, PNO) values (%s, %s, %s, %s, %s)", Aid, match_rate, intent, PNO, PNO)
            if type(Luisid) is not str:
                if Luisid == Aid:
                    Query().setExecute6("update answer set match_rate=%s, intent=%s, IPNO=%s, PNO=%s where Aid = %s", match_rate, intent, PNO, PNO, Aid)
            Aid = result
        return Aid

    def getLast(self):
        tup = Query().getExecute("select id from analysis order by id desc limit 1")
        return tup[0]


def Score():
    db = DB()
    scoring = Scoring()

    i = 1
    last = db.getLastAnalysisId()
    if last == "empty":
        last = 5
    result = {}
    while i <= last:
        nlp = db.getNLPdata(i)
        db.insertRecord(nlp)
        scoring.calculateScore(i)
        i += 1
    return result


i = 0
while True:
    Score()
    print(str(i) + "초 경과")
    i += 1
    time.sleep(1)
