import logging
from pprint import pformat
import threading
import traceback

import cx_Oracle


class SQLHelper(object):

    CONN_STR = ""

    def __init__(self, connectString, logger=None):
        self.logger = logger if logger else logging.getLogger('aplogger')
        self._connStr = connectString if connectString else SQLHelper.CONN_STR
        if not SQLHelper.CONN_STR:
            SQLHelper.CONN_STR = connectString
        self.connect()
        self.lock = threading.Lock()

    def connect(self):
        """ Connect to the database. """

        try:
            self.conn = cx_Oracle.connect(self._connStr)
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            if error.code == 1017:
                self.logger.error('Please check your credentials.')
            else:
                self.logger.error('Database connection error: %s'.format(e))
            # Very important part!
            raise

        # If the database connection succeeded create the cursor
        # we-re going to use.
        self.cursor = self.conn.cursor()

    def __disconnect(self):
        """
        Disconnect from the database. If this fails, for instance
        if the connection instance doesn't exist we don't really care.
        """

        try:
            self.cursor.close()
            self.logger.info("DBs cursor closed.")
        except cx_Oracle.DatabaseError:
            self.logger.warning(
                "Ignoring close cursor error : %s", traceback.format_exc())
        except:
            self.logger.error(traceback.format_exc())
        finally:
            try:
                self.conn.close()
                self.logger.info("DB connection closed.")
            except cx_Oracle.DatabaseError:
                self.logger.warning(
                    "Ignoring close connection error : %s", traceback.format_exc())
            except:
                self.logger.error(traceback.format_exc())

    def execute(self, sql, bindvars=None, commit=False, no_of_records=1500, retry=3,):
        """
        Execute whatever SQL statements are passed to the method;
        commit if specified. Do not specify fetchall() in here as
        the SQL statement may not be a select.
        bindvars is a dictionary of variables you pass to execute.
        """
        self.MAXROWS_TO_FETCH = no_of_records
        for i in range(retry):
            try:
                self.lock.acquire()
                self.logger.info("[Execute SQL] %s %s", sql,
                                 "\n, vars : {}".format(pformat(bindvars)) if bindvars else "")

                if bindvars:
                    self.cursor.execute(sql, bindvars)
                else:
                    self.cursor.execute(sql)

                # Only commit if it-s necessary.
                if commit:
                    self.conn.commit()

                break

            except cx_Oracle.DatabaseError as e:
                error, = e.args
                self.logger.error(error.code)
                self.logger.error(error.message)
                self.logger.error(error.context)

                if error.code == 955:
                    self.logger.error('Table already exists')
                elif error.code == 1031:
                    self.logger.error("Insufficient privileges")
                elif error.code == 3114 or error.code == 3113:
                    if i < retry - 1:
                        self.logger.info("retrying....[%s]", i + 1)
                        self.connect()
                        continue

                if commit:
                    self.conn.rollback()
                # Raise the exception.
                raise

            # something we don't really care, just roll back & raise
            except Exception as e:
                self.logger.info(e.__dict__)
                if commit:
                    try:
                        self.conn.rollback()
                    except:
                        self.logger.error(traceback.format_exc())
                raise e

            finally:
                self.lock.release()

    def __del__(self):
        self.__disconnect()

    def getResult(self):
        # list of all dictionaries : each dictionary is column names and one
        # row of values
        _all = []
        try:
            _list_names = []  # list of table column names
            self.lock.acquire()
            if not hasattr(self, 'result_dict'):
                self.result_dict = {}
            if self.cursor.description is not None:
                for desc in self.cursor.description:
                    columnName = desc[0]
                    _list_names.append(columnName)
                row, count = self.cursor.fetchone(), 1
                while row and count <= self.MAXROWS_TO_FETCH:
                    # create dict of column name: value
                    self.result_dict = dict(zip(_list_names, row))
                    _all.append(self.result_dict)
                    row = self.cursor.fetchone()
                    count += 1
        finally:
            self.lock.release()
        return _all

    def printResult(self, results):
        msg = "\n"
        count = 1
        for result in results:
            msg += 'Fetching Result no : %d\n' % (count)
            msg += '-' * 40 + "\n"
            for k, v in result.iteritems():
                msg += '%s -> %s \n' % (k, repr(v))
            count += 1
        msg += '-' * 40 + "\n"
        msg += 'Total results : %d\n' % (count - 1)
        msg += '-' * 40 + "\n"
        self.logger.info(msg)

    def getTotalCount(self, sql, field_name):
        self.execute(sql)
        result = self.getResult()
        return result[0].get(field_name.upper(), 0)
