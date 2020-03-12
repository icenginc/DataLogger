import sqlite3

def getData(systemNum, date):

    conn = sqlite3.connect('../_database/temperatures.db')

    statement = "SELECT * FROM dataTable WHERE system = '" + systemNum + "' AND strftime('%Y-%m-%d',date) = date('" + date + "') LIMIT 10"

    print(statement)

    cursor = conn.cursor()
    cursor.execute(statement)

    rows = cursor.fetchall()

    for item in rows:
            print(item)


    conn.close()


getData("RPI_001", "2017-06-02")
