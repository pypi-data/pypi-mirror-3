# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: constants.py 37 2012-07-21 16:32:26Z griff1n $
# lib:  pysyncml.constants
# auth: griffin <griffin@uberdev.org>
# date: 2012/04/20
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.constants`` module defines all of the common SyncML
constants used throughout the SyncML protocol and the pysyncml
package.
'''

#: SyncML versions
SYNCML_VERSION_1_0                      = 'SyncML/1.0'
SYNCML_VERSION_1_1                      = 'SyncML/1.1'
SYNCML_VERSION_1_2                      = 'SyncML/1.2'
SYNCML_DTD_VERSION_1_0                  = '1.0'
SYNCML_DTD_VERSION_1_1                  = '1.1'
SYNCML_DTD_VERSION_1_2                  = '1.2'

#: SyncML alert/sync codes
ALERT_DISPLAY                           = 100
ALERT_TWO_WAY                           = 200
ALERT_SLOW_SYNC                         = 201
ALERT_ONE_WAY_FROM_CLIENT               = 202
ALERT_REFRESH_FROM_CLIENT               = 203
ALERT_ONE_WAY_FROM_SERVER               = 204
ALERT_REFRESH_FROM_SERVER               = 205
ALERT_TWO_WAY_BY_SERVER                 = 206
ALERT_ONE_WAY_FROM_CLIENT_BY_SERVER     = 207
ALERT_REFRESH_FROM_CLIENT_BY_SERVER     = 208
ALERT_ONE_WAY_FROM_SERVER_BY_SERVER     = 209
ALERT_REFRESH_FROM_SERVER_BY_SERVER     = 210
# alert codes 211-220 are reserved for future use

#: SyncML SyncCap SyncTypes
SYNCTYPE_AUTO                           = None
SYNCTYPE_TWO_WAY                        = 1
SYNCTYPE_SLOW_SYNC                      = 2
SYNCTYPE_ONE_WAY_FROM_CLIENT            = 3
SYNCTYPE_REFRESH_FROM_CLIENT            = 4
SYNCTYPE_ONE_WAY_FROM_SERVER            = 5
SYNCTYPE_REFRESH_FROM_SERVER            = 6
SYNCTYPE_SERVER_ALERTED                 = 7

#: SyncML synctype-to-alertcode mapping
# taking advantage of the fact that 1..7 maps to 200..206
# (more or less... "7" is a bit "nebulous"...)
SyncTypeToAlert = dict((i + 1, i + 200) for i in range(7))

#: SyncML XML namespaces
NAMESPACE_SYNCML                        = 'syncml:syncml1.2'
NAMESPACE_METINF                        = 'syncml:metinf'
NAMESPACE_DEVINF                        = 'syncml:devinf'
NAMESPACE_AUTH_BASIC                    = 'syncml:auth-basic'
NAMESPACE_AUTH_MD5                      = 'syncml:auth-md5'
NAMESPACE_FILTER_CGI                    = 'syncml:filtertype-cgi'

#: Commonly used content-types
TYPE_TEXT_PLAIN                         = 'text/plain'
TYPE_VCARD_V21                          = 'text/x-vcard'
TYPE_VCARD_V30                          = 'text/vcard'
TYPE_VCALENDAR                          = 'text/x-vcalendar'
TYPE_ICALENDAR                          = 'text/calendar'
TYPE_MESSAGE                            = 'text/message'
TYPE_SYNCML                             = 'application/vnd.syncml'
TYPE_SYNCML_DEVICE_INFO                 = 'application/vnd.syncml-devinf'
TYPE_SYNCML_ICALENDAR                   = 'application/vnd.syncml-xcal'
TYPE_SYNCML_EMAIL                       = 'application/vnd.syncml-xmsg'
TYPE_SYNCML_BOOKMARK                    = 'application/vnd.syncml-xbookmark'
TYPE_SYNCML_RELATIONAL_OBJECT           = 'application/vnd.syncml-xrelational'
TYPE_OMADS_FOLDER                       = 'application/vnd.omads-folder'
TYPE_OMADS_FILE                         = 'application/vnd.omads-file'
TYPE_OMADS_EMAIL                        = 'application/vnd.omads-email'
TYPE_SQL                                = 'application/sql'
TYPE_LDAP                               = 'text/directory'
TYPE_EMAIL                              = 'message/rfc2822'
TYPE_EMAIL_822                          = 'message/rfc822'
TYPE_SIF_CONTACT                        = 'text/x-s4j-sifc'
TYPE_SIF_NOTE                           = 'text/x-s4j-sifn'
TYPE_SIF_TASK                           = 'text/x-s4j-sift'

#: non-agent URI paths
URI_DEVINFO_1_0                         = 'devinf10'
URI_DEVINFO_1_1                         = 'devinf11'
URI_DEVINFO_1_2                         = 'devinf12'

#: Response codes
STATUS_IN_PROGRESS                      = 101
STATUS_OK                               = 200
STATUS_ITEM_ADDED                       = 201
STATUS_ACCEPTED_FOR_PROCESSING          = 202
STATUS_NONAUTHORIATATIVE_RESPONSE       = 203
STATUS_NO_CONTENT                       = 204
STATUS_RESET_CONTENT                    = 205
STATUS_PARTIAL_CONTENT                  = 206
STATUS_CONFLICT_RESOLVED_WITH_MERGE     = 207
STATUS_CONFLICT_RESOLVED_WITH_CLIENT_WINNING    = 208
STATUS_CONFLICT_RESOLVED_WITH_DUPLICATE         = 209
STATUS_DELETE_WITHOUT_ARCHIVE           = 210
STATUS_ITEM_NOT_DELETED                 = 211
STATUS_AUTHENTICATION_ACCEPTED          = 212
STATUS_CHUNKED_ITEM_ACCEPTED_AND_BUFFERED       = 213
STATUS_OPERATION_CANCELLED              = 214
STATUS_NOT_EXECUTED                     = 215
STATUS_ATOMIC_ROLLBACK_OK               = 216
STATUS_RESULT_ALERT                     = 221
STATUS_NEXT_MESSAGE                     = 222
STATUS_NO_END_OF_DATA                   = 223
STATUS_SUSPEND                          = 224
STATUS_RESUME                           = 225
STATUS_DATA_MANAGEMENT                  = 226
# status codes 227-250 are reserved for future use
STATUS_MULTIPLE_CHOICES                 = 300
STATUS_USE_PROXY                        = 305
STATUS_BAD_REQUEST                      = 400
STATUS_UNAUTHORIZED                     = 401
STATUS_NOT_FOUND                        = 404
STATUS_AUTHENTICATION_REQUIRED          = 407
STATUS_UNSUPPORTED_MEDIA                = 415
STATUS_REQUEST_SIZE_TOO_BIG             = 416
STATUS_ALREADY_EXISTS                   = 418
STATUS_SIZE_MISMATCH                    = 424
STATUS_COMMAND_FAILED                   = 500
STATUS_NOT_IMPLEMENTED                  = 501
STATUS_REFRESH_REQUIRED                 = 508
STATUS_ATOMIC_ROLLBACK_FAILED           = 516

#: SyncML codecs
CODEC_XML                               = 'xml'
CODEC_WBXML                             = 'wbxml'
FORMAT_B64                              = 'b64'
FORMAT_AUTO                             = 'auto'

#: SyncML nodes
NODE_SYNCML                             = 'SyncML'
NODE_SYNCBODY                           = 'SyncBody'

#: SyncML commands
CMD_SYNCHDR                             = 'SyncHdr'
CMD_SYNC                                = 'Sync'
CMD_ALERT                               = 'Alert'
CMD_STATUS                              = 'Status'
CMD_GET                                 = 'Get'
CMD_PUT                                 = 'Put'
CMD_ADD                                 = 'Add'
CMD_REPLACE                             = 'Replace'
CMD_DELETE                              = 'Delete'
CMD_RESULTS                             = 'Results'
CMD_ATOMIC                              = 'Atomic'
CMD_COPY                                = 'Copy'
CMD_EXEC                                = 'Exec'
CMD_MAP                                 = 'Map'
CMD_MAPITEM                             = 'MapItem'
CMD_SEARCH                              = 'Search'
CMD_SEQUENCE                            = 'Sequence'
CMD_FINAL                               = 'Final'

#: SyncML standard device types
DEVTYPE_HANDHELD                        = 'handheld'
DEVTYPE_PAGER                           = 'pager'
DEVTYPE_PDA                             = 'pda'
DEVTYPE_PHONE                           = 'phone'
DEVTYPE_SERVER                          = 'server'
DEVTYPE_SMARTPHONE                      = 'smartphone'
DEVTYPE_WORKSTATION                     = 'workstation'

#: Item status codes
ITEM_OK                                 = 0
ITEM_ADDED                              = 1
ITEM_MODIFIED                           = 2
ITEM_DELETED                            = 3
ITEM_SOFTDELETED                        = 4

#------------------------------------------------------------------------------
# end of $Id: constants.py 37 2012-07-21 16:32:26Z griff1n $
#------------------------------------------------------------------------------
