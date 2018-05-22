'''
Created on Dec 20, 2017

@author: claire
'''


class CrReviewErrorCode:
    UnknownError = 1
    QueryDefineNotFoundError = 2
    CrListNotFoundError = 3
    CrNewListNotFoundError = 4
    CrUpdateInfoNotFoundError = 5
    CrUpdateListNotFoundError = 6
    HwPrjUpdateInfoNotFoundError = 7
    HwPrjCreateInfoNotFoundError = 8
    WrongParamError = 9
    SyncFunctionNotFoundError = 10
    DataSourceIncompleteError = 11
    IncompleteParamError = 12
    SubmitReviewInfoNoKeyError = 13
    RecordUpdateInvalidError = 14
    DateTimeFormatInvalidError = 15


class CrReviewError(Exception):
    '''
    Base class for other exceptions
    '''

    def __init__(self, **kwargs):
        super(CrReviewError, self).__init__(**kwargs)
        self.code = CrReviewErrorCode.UnknownError
        self.msg = "CrReview Errors"


class QueryDefineNotFound(CrReviewError):
    '''
    Raise when the query define didn't found in db
    '''

    def __init__(self):
        super(QueryDefineNotFound, self).__init__()
        self.code = CrReviewErrorCode.QueryDefineNotFoundError
        self.msg = "no query define, couldn't use it to query WITS"


class CrListNotFound(CrReviewError):
    '''
    Raise when there's no cr list found in db, means no data sync for this activity
    '''

    def __init__(self):
        super(CrListNotFound, self).__init__()
        self.code = CrReviewErrorCode.CrListNotFoundError
        self.msg = "no cr list, don't need to sync data for activity"


class CrNewListNotFound(CrReviewError):
    '''
    Raise when there's no new cr list, means this sync without new CR
    '''

    def __init__(self):
        super(CrNewListNotFound, self).__init__()
        self.code = CrReviewErrorCode.CrNewListNotFoundError
        self.msg = "no cr new list, don't need to create new cr for this sync"


class CrUpdateInfoNotFound(CrReviewError):
    '''
    Raise when there's no cr update infor found from WITS, means no data update for this CR
    '''

    def __init__(self):
        super(CrUpdateInfoNotFound, self).__init__()
        self.code = CrReviewErrorCode.CrUpdateInfoNotFoundError
        self.msg = "no update infor for this CR, no need to update"


class CrUpdateListNotFound(CrReviewError):
    '''
    Raise when there's no update cr list, means this sync without update CR
    '''

    def __init__(self):
        super(CrUpdateListNotFound, self).__init__()
        self.code = CrReviewErrorCode.CrUpdateListNotFoundError
        self.msg = "no cr update list, don't need to update cr for this sync"


class HwPrjUpdateInfoNotFound(CrReviewError):
    '''
    Raise when there's no update hw prj info. from CRM, means this sync without update hw prj info.
    '''

    def __init__(self):
        super(HwPrjUpdateInfoNotFound, self).__init__()
        self.code = CrReviewErrorCode.HwPrjUpdateInfoNotFoundError
        self.msg = "no hw prj update info, don't need to update hw prj info for this sync"


class HwPrjCreateInfoNotFound(CrReviewError):
    '''
    Raise when there's no create hw prj info. from CRM, means this sync without create hw prj info.
    '''

    def __init__(self):
        super(HwPrjCreateInfoNotFound, self).__init__()
        self.code = CrReviewErrorCode.HwPrjCreateInfoNotFoundError
        self.msg = "no hw prj create info, don't need to create hw prj info for this sync"


class WrongParamError(CrReviewError):
    '''
    Raise when view parameters didn't match the requirement
    '''

    def __init__(self, **kwds):
        super(WrongParamError, self).__init__(**kwds)
        self.code = CrReviewErrorCode.WrongParamError
        # to-do : show the specific parameter
        self.msg = kwds.get("msg", "parameter wrong!")


class SyncFunctionNotFound(CrReviewError):
    '''
    Raise when there's no if else mapping for activity update status table id with sync function
    '''

    def __init__(self):
        super(SyncFunctionNotFound, self).__init__()
        self.code = CrReviewErrorCode.SyncFunctionNotFoundError
        self.msg = "no mapping for activity update status table id with sync function"


class DataSourceIncomplete(CrReviewError):
    '''
    Raise when couldn't get complete infor for both source and destination,
    to avoid wrong update or disable issue
    '''

    def __init__(self):
        super(DataSourceIncomplete, self).__init__()
        self.code = CrReviewErrorCode.DataSourceIncompleteError
        self.msg = "couldn't get complete infor for both source and destination"


class IncompleteParam(CrReviewError):
    '''
    Raise when view parameters didn't match the requirement
    '''

    def __init__(self, **kwds):
        super(IncompleteParam, self).__init__(**kwds)
        self.code = CrReviewErrorCode.IncompleteParamError
        # to-do : show the specific parameter
        self.msg = kwds.get("msg", "input parameters incomplete!")


class SubmitReviewInfoNoKey(CrReviewError):
    '''
    Raise when view key parameters didn't match the requirement
    '''

    def __init__(self, **kwds):
        super(SubmitReviewInfoNoKey, self).__init__(**kwds)
        self.code = CrReviewErrorCode.SubmitReviewInfoNoKeyError
        self.msg = kwds.get(
            "msg", "activity_id and cr_id is mandatory, couldn't be null")


class RecordUpdateInvalid(CrReviewError):
    '''
    Raise when other session update record after info query
    '''

    def __init__(self, **kwds):
        super(RecordUpdateInvalid, self).__init__(**kwds)
        self.code = CrReviewErrorCode.RecordUpdateInvalidError
        self.msg = kwds.get(
            "msg", "update fail because other session has been updated this record. Please reload!")


class DateTimeFormatInvalid(CrReviewError):
    '''
    Raise when str date time format is invalid
    '''

    def __init__(self, **kwds):
        super(DateTimeFormatInvalid, self).__init__(**kwds)
        self.code = CrReviewErrorCode.DateTimeFormatInvalidError
        self.msg = kwds.get(
            "msg", "updated_time is null or invalid format, please follow %Y-%m-%d %H:%M:%S")
