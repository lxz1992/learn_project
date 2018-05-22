'''
Created on Dec 6, 2017

@author: claire
'''


class MdErrorCode:
    UnknownError = 1
    DbDataNotFoundError = 2
    ParseResultNotFoundError = 3
    CountryCodeNotFountError = 4
    HwTypeNotFoundError = 5
    OpNameNotFoundError = 6
    InvalidHwTypeError = 7
    CrTypeNotFoundError = 8
    InvalidCrTypeError = 9
    ParamNotFoundError = 10
    HwPrjIdNotFoundError = 11
    WwstaTop10InfoNotFoundError = 12
    MdStateNotFoundError = 13
    MeaTop10NotFoundError = 14
    InvalidYearIntervalError = 15


class MdError(Exception):
    '''
    Base class for other exceptions
    '''

    def __init__(self, **kwargs):
        super(MdError, self).__init__(**kwargs)
        self.code = MdErrorCode.UnknownError
        self.msg = "Md Errors"


class DbDataNotFound(MdError):
    '''
    Raise when the query result from db is null
    '''

    def __init__(self):
        super(DbDataNotFound, self).__init__()
        self.code = MdErrorCode.DbDataNotFoundError
        self.msg = "return result is null from db"


class ParseResultNotFound(MdError):
    '''
    Raise when the final result is null
    '''

    def __init__(self):
        super(ParseResultNotFound, self).__init__()
        self.code = MdErrorCode.ParseResultNotFoundError
        self.msg = "parse result is null but source data is not null"


class CountryCodeNotFount(MdError):
    '''
    Raise when return result to view and didn't find any country code given that this are query result from wwstatisticmap table
    '''

    def __init__(self):
        super(CountryCodeNotFount, self).__init__()
        self.code = MdErrorCode.ParseResultNotFoundError
        self.msg = "couldn't find any country code mapping"


class HwTypeNotFound(MdError):
    '''
    Raise when input param null for hw_type in PrjStatusView
    '''

    def __init__(self):
        super(HwTypeNotFound, self).__init__()
        self.code = MdErrorCode.HwTypeNotFoundError
        self.msg = "please input param for hw_type"


class OpNameNotFound(MdError):
    '''
    Raise when input params for null op_name but Operator hw_type in PrjStatusView or prj_type in PrjListView
    '''

    def __init__(self):
        super(OpNameNotFound, self).__init__()
        self.code = MdErrorCode.OpNameNotFoundError
        self.msg = "please input param op_name, do not leave op_name null"


class InvalidHwType(MdError):
    '''
    Raise when input params hw_type value is not acceptable in PrjStatusView
    '''

    def __init__(self):
        super(InvalidHwType, self).__init__()
        self.code = MdErrorCode.InvalidHwTypeError
        self.msg = "please input valid hw_type!"


class CrTypeNotFound(MdError):
    '''
    Raise when input param null for cr_type in CrListView
    '''

    def __init__(self):
        super(CrTypeNotFound, self).__init__()
        self.code = MdErrorCode.CrTypeNotFoundError
        self.msg = "please input param for cr_type"


class InvalidCrType(MdError):
    '''
    Raise when input params cr_type value is not acceptable in CrListView
    '''

    def __init__(self):
        super(InvalidCrType, self).__init__()
        self.code = MdErrorCode.InvalidCrTypeError
        self.msg = "please input valid cr_type!"


class ParamNotFound(MdError):
    '''
    Raise when input param null for particular cr_type in CrListView
    '''

    def __init__(self):
        super(ParamNotFound, self).__init__()
        self.code = MdErrorCode.ParamNotFoundError
        self.msg = "please input param for cr_type"


class HwPrjIdNotFound(MdError):
    '''
    Raise when input param null for hw_prj_id in CrListbyPrjView
    '''

    def __init__(self):
        super(HwPrjIdNotFound, self).__init__()
        self.code = MdErrorCode.HwPrjIdNotFoundError
        self.msg = "please input param for hw_prj_id"


class WwstaTop10InfoNotFound(MdError):
    '''
    Raise when there's no create info for WwstaTop10
    '''

    def __init__(self):
        super(WwstaTop10InfoNotFound, self).__init__()
        self.code = MdErrorCode.WwstaTop10InfoNotFoundError
        self.msg = "no data for WwstatisticTop10 table"


class MdStateNotFound(MdError):
    '''
    Raise when there's no valid Md state input from front-end
    '''

    def __init__(self):
        super(MdStateNotFound, self).__init__()
        self.code = MdErrorCode.MdStateNotFoundError
        self.msg = "invalid input for md state"


class MeaTop10NotFound(MdError):
    '''
    Raise when there's no MeaTop10 data
    '''

    def __init__(self):
        super(MeaTop10NotFound, self).__init__()
        self.code = MdErrorCode.MeaTop10NotFoundError
        self.msg = "There's no Mea Top10 data"


class InvalidYearInterval(MdError):
    '''
    Raise when from_year is not earlier that to_year
    '''

    def __init__(self):
        super(InvalidYearInterval, self).__init__()
        self.code = MdErrorCode.InvalidYearIntervalError
        self.msg = "from_year should always earlier than to_year"
