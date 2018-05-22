import re

import cx_Oracle


db_conn = None
db_cursor = None


def connect_db():
    host = "172.21.104.120"
    port = "1521"
    sid = "cqd1"
    dsn = cx_Oracle.makedsn(host, port, sid)
    conn = cx_Oracle.connect("mylooktest", "mylooktest", dsn)
    cursor = cx_Oracle.Cursor(conn)
    return (conn, cursor)


def get_country_operator_mapping(plmn):

    final_country = None
    final_operator = None

    if not plmn:
        return (final_country, final_operator)

    '''
    1. ignore white spaces and split with . (to take care of xxxxxx.0
    2. ignore English char
    3. ignore special char, ex. *^%$()-, etc.
    '''
    tmp_result = plmn.strip().split(".")
    real_plmn = re.sub("[A-Za-z]", "", tmp_result[0])
    real_plmn = ''.join(e for e in real_plmn if e.isalnum())

    plmn1 = real_plmn[:3]
    plmn2 = real_plmn[3:]

    sql = "select country, operator from md_mcc_mnc where mcc = '" + \
        plmn1 + "' and mcn ='" + plmn2 + "'"
    if plmn1 and plmn2:
        global db_cursor
        db_cursor.execute(sql)

        for eachrow in db_cursor:
            final_country = eachrow[0]
            final_operator = eachrow[1]

    return (final_country, final_operator)


def get_cr_list_with_plmn():
    result = []
    sql = "select cr_id, plmn1 from cr where plmn1 is not null and (plmn1 != 'NA' and plmn1 != 'na')"
    db_cursor.execute(sql)

    for eachrow in db_cursor:
        cr_id = eachrow[0]
        plmn = eachrow[1]
        result.append({cr_id: plmn})
    return result


def update_cr(cr_id, country, operator):
    update_sql = "update cr set country = '" + country + \
        "', operator = '" + operator + "' where cr_id = '" + cr_id + "'"
    db_cursor.execute(update_sql)


# ---------------------main---------------------
if __name__ == "__main__":
    try:
        db_conn, db_cursor = connect_db()
        all_cr_list = get_cr_list_with_plmn()
        print('cr list len: ' + str(len(all_cr_list)))
        count_total = 0

        for data in all_cr_list:
            for key in data:
                print('crid', key, data[key])
                (country, operator) = get_country_operator_mapping(data[key])
                print('country:', country, 'operator:', operator)
                if country and operator:
                    update_cr(key, country, operator)
                    count_total += 1
        print('start to commit data, qty:', count_total)
        db_conn.commit()
    except cx_Oracle.DatabaseError as e:
        print('DB connect exception: ' + str(e))
    except Exception as e:
        print('general exception: ' + str(e))
