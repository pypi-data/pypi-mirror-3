from getpaid.core.interfaces import workflow_states
import MySQLdb
import logging

dblog = logging.getLogger('getpaid.pfgbuyableadapter')

def insertData(data):
    key = ''
    table = ''
    db = ''
    host = ''
    user = ''
    password = ''

    try:
        dbconn = MySQLdb.connect(host = host,
                                 user = user,
                                 passwd = password,
                                 db = db
                                 )
        dbconn.autocommit(False)
    except MySQLdb.Error, e:
        dblog.error("MySQL error %d: %s"  % (e.args[0], e.args[1]))
        return

    value_strings = list()
    for v in data.values():
        value_strings.append("AES_ENCRYPT('%s', '%s')" % (dbconn.escape_string(str(v)), key))

    try:
        cursor = dbconn.cursor()
        dblog.info("INSERT INTO %s (%s) VALUES (%s);" % (table, ", ".join([k for k in data.keys()]), ", ".join([v for v in value_strings])))
        cursor.execute("INSERT INTO %s (%s) VALUES (%s);" % (table, ", ".join([k for k in data.keys()]), ", ".join([v for v in value_strings])))
        dbconn.commit()
    except MySQLdb.Error, e:
        dbconn.rollback()
        dblog.error("Transaction aborted %d: %s" % (e.args[0], e.args[1]))
    cursor.close()
    dbconn.close()


def handlePaymentReceived( order, event ):
    if event.destination == workflow_states.order.finance.CHARGED:
        for item in order.shopping_cart.values():
            data = getattr(item,'data',None)
            if data:
                insertData(data)
