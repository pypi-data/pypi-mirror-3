# Foundation Framework

from nspython import *
from nspython import _ffi

_ = load('Foundation')

class NSString(NSObject):
    
    def __str__(self):
        return _ffi.string(self.UTF8String())

at = lambda s: NSString.stringWithUTF8String_(_ffi.new('char[]', s.encode('utf8')))

# classes
class NSAffineTransform(NSObject): pass
class NSArray(NSObject): pass
class NSAssertionHandler(NSObject): pass
class NSAttributedString(NSObject): pass
class NSAutoreleasePool(NSObject): pass
class NSBundle(NSObject): pass
class NSCache(NSObject): pass
class NSCachedURLResponse(NSObject): pass
class NSCalendar(NSObject): pass
class NSCharacterSet(NSObject): pass
class NSClassDescription(NSObject): pass
class NSCoder(NSObject): pass
class NSConditionLock(NSObject): pass
class NSConnection(NSObject): pass
class NSData(NSObject): pass
class NSDate(NSObject): pass
class NSDateComponents(NSObject): pass
class NSDecimalNumberHandler(NSObject): pass
class NSDictionary(NSObject): pass
class NSDistantObjectRequest(NSObject): pass
class NSDistributedLock(NSObject): pass
class NSEnumerator(NSObject): pass
class NSError(NSObject): pass
class NSException(NSObject): pass
class NSExpression(NSObject): pass
class NSFileHandle(NSObject): pass
class NSFileManager(NSObject): pass
class NSFormatter(NSObject): pass
class NSGarbageCollector(NSObject): pass
class NSHTTPCookie(NSObject): pass
class NSHTTPCookieStorage(NSObject): pass
class NSHashTable(NSObject): pass
class NSHost(NSObject): pass
class NSIndexPath(NSObject): pass
class NSIndexSet(NSObject): pass
class NSInvocation(NSObject): pass
class NSLocale(NSObject): pass
class NSLock(NSObject): pass
class NSMapTable(NSObject): pass
class NSMetadataItem(NSObject): pass
class NSMetadataQuery(NSObject): pass
class NSMetadataQueryAttributeValueTuple(NSObject): pass
class NSMetadataQueryResultGroup(NSObject): pass
class NSMethodSignature(NSObject): pass
class NSNetService(NSObject): pass
class NSNetServiceBrowser(NSObject): pass
class NSNotification(NSObject): pass
class NSNotificationCenter(NSObject): pass
class NSNotificationQueue(NSObject): pass
class NSNull(NSObject): pass
class NSOperation(NSObject): pass
class NSOperationQueue(NSObject): pass
class NSOrthography(NSObject): pass
class NSPipe(NSObject): pass
class NSPointerArray(NSObject): pass
class NSPointerFunctions(NSObject): pass
class NSPort(NSObject): pass
class NSPortMessage(NSObject): pass
class NSPortNameServer(NSObject): pass
class NSPredicate(NSObject): pass
class NSProcessInfo(NSObject): pass
class NSRecursiveLock(NSObject): pass
class NSRunLoop(NSObject): pass
class NSScanner(NSObject): pass
class NSSet(NSObject): pass
class NSSortDescriptor(NSObject): pass
class NSSpellServer(NSObject): pass
class NSStream(NSObject): pass
# class NSString(NSObject): pass
class NSTask(NSObject): pass
class NSTextCheckingResult(NSObject): pass
class NSThread(NSObject): pass
class NSTimeZone(NSObject): pass
class NSTimer(NSObject): pass
class NSURL(NSObject): pass
class NSURLAuthenticationChallenge(NSObject): pass
class NSURLCache(NSObject): pass
class NSURLConnection(NSObject): pass
class NSURLCredential(NSObject): pass
class NSURLCredentialStorage(NSObject): pass
class NSURLDownload(NSObject): pass
class NSURLProtectionSpace(NSObject): pass
class NSURLProtocol(NSObject): pass
class NSURLRequest(NSObject): pass
class NSURLResponse(NSObject): pass
class NSUndoManager(NSObject): pass
class NSUserDefaults(NSObject): pass
class NSValue(NSObject): pass
class NSValueTransformer(NSObject): pass
class NSXMLNode(NSObject): pass
class NSXMLParser(NSObject): pass
# class NSDistantObject(NSProxy): pass
# class NSProtocolChecker(NSProxy): pass
class NSMutableData(NSData): pass
class NSCalendarDate(NSDate): pass
class NSNumber(NSValue): pass
class NSXMLDTD(NSXMLNode): pass
class NSXMLDTDNode(NSXMLNode): pass
class NSXMLDocument(NSXMLNode): pass
class NSXMLElement(NSXMLNode): pass
class NSMutableAttributedString(NSAttributedString): pass
class NSMutableCharacterSet(NSCharacterSet): pass
class NSMutableString(NSString): pass
class NSDateFormatter(NSFormatter): pass
class NSNumberFormatter(NSFormatter): pass
class NSMutableArray(NSArray): pass
class NSMutableDictionary(NSDictionary): pass
class NSDirectoryEnumerator(NSEnumerator): pass
class NSMutableIndexSet(NSIndexSet): pass
class NSMutableSet(NSSet): pass
class NSComparisonPredicate(NSPredicate): pass
class NSCompoundPredicate(NSPredicate): pass
class NSInputStream(NSStream): pass
class NSOutputStream(NSStream): pass
class NSMutableURLRequest(NSURLRequest): pass
class NSHTTPURLResponse(NSURLResponse): pass
class NSMachPort(NSPort): pass
class NSMessagePort(NSPort): pass
class NSSocketPort(NSPort): pass
class NSMachBootstrapServer(NSPortNameServer): pass
class NSMessagePortNameServer(NSPortNameServer): pass
class NSSocketPortNameServer(NSPortNameServer): pass
class NSBlockOperation(NSOperation): pass
class NSInvocationOperation(NSOperation): pass
class NSDistributedNotificationCenter(NSNotificationCenter): pass
class NSArchiver(NSCoder): pass
class NSKeyedArchiver(NSCoder): pass
class NSKeyedUnarchiver(NSCoder): pass
class NSPortCoder(NSCoder): pass
class NSUnarchiver(NSCoder): pass
class NSPurgeableData(NSMutableData): pass
class NSDecimalNumber(NSNumber): pass
class NSCountedSet(NSMutableSet): pass

# constants
_ffi.cdef('''
id NSAMPMDesignation;
id NSAppleEventManagerWillProcessFirstEventNotification;
id NSAppleScriptErrorAppName;
id NSAppleScriptErrorBriefMessage;
id NSAppleScriptErrorMessage;
id NSAppleScriptErrorNumber;
id NSAppleScriptErrorRange;
id NSArgumentDomain;
id NSAssertionHandlerKey;
id NSAverageKeyValueOperator;
id NSBuddhistCalendar;
id NSBundleDidLoadNotification;
id NSCharacterConversionException;
id NSChineseCalendar;
id NSClassDescriptionNeededForClassNotification;
id NSCocoaErrorDomain;
id NSConnectionDidDieNotification;
id NSConnectionDidInitializeNotification;
id NSConnectionReplyMode;
id NSCountKeyValueOperator;
id NSCurrencySymbol;
id NSCurrentLocaleDidChangeNotification;
id NSDateFormatString;
id NSDateTimeOrdering;
id NSDecimalDigits;
id NSDecimalNumberDivideByZeroException;
id NSDecimalNumberExactnessException;
id NSDecimalNumberOverflowException;
id NSDecimalNumberUnderflowException;
id NSDecimalSeparator;
id NSDefaultRunLoopMode;
id NSDestinationInvalidException;
id NSDidBecomeSingleThreadedNotification;
id NSDistinctUnionOfArraysKeyValueOperator;
id NSDistinctUnionOfObjectsKeyValueOperator;
id NSDistinctUnionOfSetsKeyValueOperator;
id NSEarlierTimeDesignations;
id NSErrorFailingURLStringKey;
id NSFTPPropertyActiveTransferModeKey;
id NSFTPPropertyFTPProxy;
id NSFTPPropertyFileOffsetKey;
id NSFTPPropertyUserLoginKey;
id NSFTPPropertyUserPasswordKey;
id NSFailedAuthenticationException;
id NSFileAppendOnly;
id NSFileBusy;
id NSFileCreationDate;
id NSFileDeviceIdentifier;
id NSFileExtensionHidden;
id NSFileGroupOwnerAccountID;
id NSFileGroupOwnerAccountName;
id NSFileHFSCreatorCode;
id NSFileHFSTypeCode;
id NSFileHandleConnectionAcceptedNotification;
id NSFileHandleDataAvailableNotification;
id NSFileHandleNotificationDataItem;
id NSFileHandleNotificationFileHandleItem;
id NSFileHandleNotificationMonitorModes;
id NSFileHandleOperationException;
id NSFileHandleReadCompletionNotification;
id NSFileHandleReadToEndOfFileCompletionNotification;
id NSFileImmutable;
id NSFileModificationDate;
id NSFileOwnerAccountID;
id NSFileOwnerAccountName;
id NSFilePathErrorKey;
id NSFilePosixPermissions;
id NSFileReferenceCount;
id NSFileSize;
id NSFileSystemFileNumber;
id NSFileSystemFreeNodes;
id NSFileSystemFreeSize;
id NSFileSystemNodes;
id NSFileSystemNumber;
id NSFileSystemSize;
id NSFileType;
id NSFileTypeBlockSpecial;
id NSFileTypeCharacterSpecial;
id NSFileTypeDirectory;
id NSFileTypeRegular;
id NSFileTypeSocket;
id NSFileTypeSymbolicLink;
id NSFileTypeUnknown;
id NSGenericException;
id NSGlobalDomain;
id NSGrammarCorrections;
id NSGrammarRange;
id NSGrammarUserDescription;
id NSGregorianCalendar;
id NSHTTPCookieComment;
id NSHTTPCookieCommentURL;
id NSHTTPCookieDiscard;
id NSHTTPCookieDomain;
id NSHTTPCookieExpires;
id NSHTTPCookieManagerAcceptPolicyChangedNotification;
id NSHTTPCookieManagerCookiesChangedNotification;
id NSHTTPCookieMaximumAge;
id NSHTTPCookieName;
id NSHTTPCookieOriginURL;
id NSHTTPCookiePath;
id NSHTTPCookiePort;
id NSHTTPCookieSecure;
id NSHTTPCookieValue;
id NSHTTPCookieVersion;
id NSHTTPPropertyErrorPageDataKey;
id NSHTTPPropertyHTTPProxy;
id NSHTTPPropertyRedirectionHeadersKey;
id NSHTTPPropertyServerHTTPVersionKey;
id NSHTTPPropertyStatusCodeKey;
id NSHTTPPropertyStatusReasonKey;
id NSHebrewCalendar;
id NSHelpAnchorErrorKey;
id NSHourNameDesignations;
id NSISO8601Calendar;
id NSInconsistentArchiveException;
id NSIndianCalendar;
id NSInternalInconsistencyException;
id NSInternationalCurrencyString;
id NSInvalidArchiveOperationException;
id NSInvalidArgumentException;
id NSInvalidReceivePortException;
id NSInvalidSendPortException;
id NSInvalidUnarchiveOperationException;
id NSInvocationOperationCancelledException;
id NSInvocationOperationVoidResultException;
id NSIsNilTransformerName;
id NSIsNotNilTransformerName;
id NSIslamicCalendar;
id NSIslamicCivilCalendar;
id NSJapaneseCalendar;
id NSKeyValueChangeIndexesKey;
id NSKeyValueChangeKindKey;
id NSKeyValueChangeNewKey;
id NSKeyValueChangeNotificationIsPriorKey;
id NSKeyValueChangeOldKey;
id NSKeyedUnarchiveFromDataTransformerName;
id NSLaterTimeDesignations;
id NSLoadedClasses;
id NSLocalNotificationCenterType;
id NSLocaleAlternateQuotationBeginDelimiterKey;
id NSLocaleAlternateQuotationEndDelimiterKey;
id NSLocaleCalendar;
id NSLocaleCollationIdentifier;
id NSLocaleCollatorIdentifier;
id NSLocaleCountryCode;
id NSLocaleCurrencyCode;
id NSLocaleCurrencySymbol;
id NSLocaleDecimalSeparator;
id NSLocaleExemplarCharacterSet;
id NSLocaleGroupingSeparator;
id NSLocaleIdentifier;
id NSLocaleLanguageCode;
id NSLocaleMeasurementSystem;
id NSLocaleQuotationBeginDelimiterKey;
id NSLocaleQuotationEndDelimiterKey;
id NSLocaleScriptCode;
id NSLocaleUsesMetricSystem;
id NSLocaleVariantCode;
id NSLocalizedDescriptionKey;
id NSLocalizedFailureReasonErrorKey;
id NSLocalizedRecoveryOptionsErrorKey;
id NSLocalizedRecoverySuggestionErrorKey;
id NSMachErrorDomain;
id NSMallocException;
id NSMaximumKeyValueOperator;
id NSMetadataQueryDidFinishGatheringNotification;
id NSMetadataQueryDidStartGatheringNotification;
id NSMetadataQueryDidUpdateNotification;
id NSMetadataQueryGatheringProgressNotification;
id NSMetadataQueryLocalComputerScope;
id NSMetadataQueryNetworkScope;
id NSMetadataQueryResultContentRelevanceAttribute;
id NSMetadataQueryUserHomeScope;
id NSMinimumKeyValueOperator;
id NSMonthNameArray;
id NSNegateBooleanTransformerName;
id NSNegativeCurrencyFormatString;
id NSNetServicesErrorCode;
id NSNetServicesErrorDomain;
id NSNextDayDesignations;
id NSNextNextDayDesignations;
id NSOSStatusErrorDomain;
id NSObjectInaccessibleException;
id NSObjectNotAvailableException;
id NSOldStyleException;
id NSOperationNotSupportedForKeyException;
id NSPOSIXErrorDomain;
id NSParseErrorException;
id NSPersianCalendar;
id NSPortDidBecomeInvalidNotification;
id NSPortReceiveException;
id NSPortSendException;
id NSPortTimeoutException;
id NSPositiveCurrencyFormatString;
id NSPriorDayDesignations;
id NSRangeException;
id NSRecoveryAttempterErrorKey;
id NSRegistrationDomain;
id NSRepublicOfChinaCalendar;
id NSRunLoopCommonModes;
id NSShortDateFormatString;
id NSShortMonthNameArray;
id NSShortTimeDateFormatString;
id NSShortWeekDayNameArray;
id NSStreamDataWrittenToMemoryStreamKey;
id NSStreamFileCurrentOffsetKey;
id NSStreamSOCKSErrorDomain;
id NSStreamSOCKSProxyConfigurationKey;
id NSStreamSOCKSProxyHostKey;
id NSStreamSOCKSProxyPasswordKey;
id NSStreamSOCKSProxyPortKey;
id NSStreamSOCKSProxyUserKey;
id NSStreamSOCKSProxyVersion4;
id NSStreamSOCKSProxyVersion5;
id NSStreamSOCKSProxyVersionKey;
id NSStreamSocketSSLErrorDomain;
id NSStreamSocketSecurityLevelKey;
id NSStreamSocketSecurityLevelNegotiatedSSL;
id NSStreamSocketSecurityLevelNone;
id NSStreamSocketSecurityLevelSSLv2;
id NSStreamSocketSecurityLevelSSLv3;
id NSStreamSocketSecurityLevelTLSv1;
id NSStringEncodingErrorKey;
id NSSumKeyValueOperator;
id NSSystemClockDidChangeNotification;
id NSSystemTimeZoneDidChangeNotification;
id NSTaskDidTerminateNotification;
id NSTextCheckingCityKey;
id NSTextCheckingCountryKey;
id NSTextCheckingJobTitleKey;
id NSTextCheckingNameKey;
id NSTextCheckingOrganizationKey;
id NSTextCheckingPhoneKey;
id NSTextCheckingStateKey;
id NSTextCheckingStreetKey;
id NSTextCheckingZIPKey;
id NSThisDayDesignations;
id NSThousandsSeparator;
id NSThreadWillExitNotification;
id NSTimeDateFormatString;
id NSTimeFormatString;
id NSURLAttributeModificationDateKey;
id NSURLAuthenticationMethodClientCertificate;
id NSURLAuthenticationMethodDefault;
id NSURLAuthenticationMethodHTMLForm;
id NSURLAuthenticationMethodHTTPBasic;
id NSURLAuthenticationMethodHTTPDigest;
id NSURLAuthenticationMethodNTLM;
id NSURLAuthenticationMethodNegotiate;
id NSURLAuthenticationMethodServerTrust;
id NSURLContentAccessDateKey;
id NSURLContentModificationDateKey;
id NSURLCreationDateKey;
id NSURLCredentialStorageChangedNotification;
id NSURLCustomIconKey;
id NSURLEffectiveIconKey;
id NSURLErrorDomain;
id NSURLErrorFailingURLErrorKey;
id NSURLErrorFailingURLPeerTrustErrorKey;
id NSURLErrorFailingURLStringErrorKey;
id NSURLErrorKey;
id NSURLFileAllocatedSizeKey;
id NSURLFileScheme;
id NSURLFileSizeKey;
id NSURLHasHiddenExtensionKey;
id NSURLIsAliasFileKey;
id NSURLIsDirectoryKey;
id NSURLIsHiddenKey;
id NSURLIsPackageKey;
id NSURLIsRegularFileKey;
id NSURLIsSymbolicLinkKey;
id NSURLIsSystemImmutableKey;
id NSURLIsUserImmutableKey;
id NSURLIsVolumeKey;
id NSURLLabelColorKey;
id NSURLLabelNumberKey;
id NSURLLinkCountKey;
id NSURLLocalizedLabelKey;
id NSURLLocalizedNameKey;
id NSURLLocalizedTypeDescriptionKey;
id NSURLNameKey;
id NSURLParentDirectoryURLKey;
id NSURLProtectionSpaceFTP;
id NSURLProtectionSpaceFTPProxy;
id NSURLProtectionSpaceHTTP;
id NSURLProtectionSpaceHTTPProxy;
id NSURLProtectionSpaceHTTPS;
id NSURLProtectionSpaceHTTPSProxy;
id NSURLProtectionSpaceSOCKSProxy;
id NSURLTypeIdentifierKey;
id NSURLVolumeAvailableCapacityKey;
id NSURLVolumeIsJournalingKey;
id NSURLVolumeLocalizedFormatDescriptionKey;
id NSURLVolumeResourceCountKey;
id NSURLVolumeSupportsCasePreservedNamesKey;
id NSURLVolumeSupportsCaseSensitiveNamesKey;
id NSURLVolumeSupportsHardLinksKey;
id NSURLVolumeSupportsJournalingKey;
id NSURLVolumeSupportsPersistentIDsKey;
id NSURLVolumeSupportsSparseFilesKey;
id NSURLVolumeSupportsSymbolicLinksKey;
id NSURLVolumeSupportsZeroRunsKey;
id NSURLVolumeTotalCapacityKey;
id NSURLVolumeURLKey;
id NSUnarchiveFromDataTransformerName;
id NSUndefinedKeyException;
id NSUnderlyingErrorKey;
id NSUndoManagerCheckpointNotification;
id NSUndoManagerDidOpenUndoGroupNotification;
id NSUndoManagerDidRedoChangeNotification;
id NSUndoManagerDidUndoChangeNotification;
id NSUndoManagerWillCloseUndoGroupNotification;
id NSUndoManagerWillRedoChangeNotification;
id NSUndoManagerWillUndoChangeNotification;
id NSUnionOfArraysKeyValueOperator;
id NSUnionOfObjectsKeyValueOperator;
id NSUnionOfSetsKeyValueOperator;
id NSUserDefaultsDidChangeNotification;
id NSWeekDayNameArray;
id NSWillBecomeMultiThreadedNotification;
id NSXMLParserErrorDomain;
id NSYearMonthWeekDesignations;
''')
NSAMPMDesignation = _.NSAMPMDesignation
NSAppleEventManagerWillProcessFirstEventNotification = _.NSAppleEventManagerWillProcessFirstEventNotification
NSAppleEventTimeOutDefault = -1.0
NSAppleEventTimeOutNone = -2.0
NSAppleScriptErrorAppName = _.NSAppleScriptErrorAppName
NSAppleScriptErrorBriefMessage = _.NSAppleScriptErrorBriefMessage
NSAppleScriptErrorMessage = _.NSAppleScriptErrorMessage
NSAppleScriptErrorNumber = _.NSAppleScriptErrorNumber
NSAppleScriptErrorRange = _.NSAppleScriptErrorRange
NSArgumentDomain = _.NSArgumentDomain
NSAssertionHandlerKey = _.NSAssertionHandlerKey
NSAverageKeyValueOperator = _.NSAverageKeyValueOperator
NSBuddhistCalendar = _.NSBuddhistCalendar
NSBundleDidLoadNotification = _.NSBundleDidLoadNotification
NSCharacterConversionException = _.NSCharacterConversionException
NSChineseCalendar = _.NSChineseCalendar
NSClassDescriptionNeededForClassNotification = _.NSClassDescriptionNeededForClassNotification
NSCocoaErrorDomain = _.NSCocoaErrorDomain
NSConnectionDidDieNotification = _.NSConnectionDidDieNotification
NSConnectionDidInitializeNotification = _.NSConnectionDidInitializeNotification
NSConnectionReplyMode = _.NSConnectionReplyMode
NSCountKeyValueOperator = _.NSCountKeyValueOperator
NSCurrencySymbol = _.NSCurrencySymbol
NSCurrentLocaleDidChangeNotification = _.NSCurrentLocaleDidChangeNotification
NSDateFormatString = _.NSDateFormatString
NSDateTimeOrdering = _.NSDateTimeOrdering
NSDeallocateZombies = False
NSDebugEnabled = False
NSDecimalDigits = _.NSDecimalDigits
NSDecimalNumberDivideByZeroException = _.NSDecimalNumberDivideByZeroException
NSDecimalNumberExactnessException = _.NSDecimalNumberExactnessException
NSDecimalNumberOverflowException = _.NSDecimalNumberOverflowException
NSDecimalNumberUnderflowException = _.NSDecimalNumberUnderflowException
NSDecimalSeparator = _.NSDecimalSeparator
NSDefaultRunLoopMode = _.NSDefaultRunLoopMode
NSDestinationInvalidException = _.NSDestinationInvalidException
NSDidBecomeSingleThreadedNotification = _.NSDidBecomeSingleThreadedNotification
NSDistinctUnionOfArraysKeyValueOperator = _.NSDistinctUnionOfArraysKeyValueOperator
NSDistinctUnionOfObjectsKeyValueOperator = _.NSDistinctUnionOfObjectsKeyValueOperator
NSDistinctUnionOfSetsKeyValueOperator = _.NSDistinctUnionOfSetsKeyValueOperator
NSEarlierTimeDesignations = _.NSEarlierTimeDesignations
NSErrorFailingURLStringKey = _.NSErrorFailingURLStringKey
NSFTPPropertyActiveTransferModeKey = _.NSFTPPropertyActiveTransferModeKey
NSFTPPropertyFTPProxy = _.NSFTPPropertyFTPProxy
NSFTPPropertyFileOffsetKey = _.NSFTPPropertyFileOffsetKey
NSFTPPropertyUserLoginKey = _.NSFTPPropertyUserLoginKey
NSFTPPropertyUserPasswordKey = _.NSFTPPropertyUserPasswordKey
NSFailedAuthenticationException = _.NSFailedAuthenticationException
NSFileAppendOnly = _.NSFileAppendOnly
NSFileBusy = _.NSFileBusy
NSFileCreationDate = _.NSFileCreationDate
NSFileDeviceIdentifier = _.NSFileDeviceIdentifier
NSFileExtensionHidden = _.NSFileExtensionHidden
NSFileGroupOwnerAccountID = _.NSFileGroupOwnerAccountID
NSFileGroupOwnerAccountName = _.NSFileGroupOwnerAccountName
NSFileHFSCreatorCode = _.NSFileHFSCreatorCode
NSFileHFSTypeCode = _.NSFileHFSTypeCode
NSFileHandleConnectionAcceptedNotification = _.NSFileHandleConnectionAcceptedNotification
NSFileHandleDataAvailableNotification = _.NSFileHandleDataAvailableNotification
NSFileHandleNotificationDataItem = _.NSFileHandleNotificationDataItem
NSFileHandleNotificationFileHandleItem = _.NSFileHandleNotificationFileHandleItem
NSFileHandleNotificationMonitorModes = _.NSFileHandleNotificationMonitorModes
NSFileHandleOperationException = _.NSFileHandleOperationException
NSFileHandleReadCompletionNotification = _.NSFileHandleReadCompletionNotification
NSFileHandleReadToEndOfFileCompletionNotification = _.NSFileHandleReadToEndOfFileCompletionNotification
NSFileImmutable = _.NSFileImmutable
NSFileModificationDate = _.NSFileModificationDate
NSFileOwnerAccountID = _.NSFileOwnerAccountID
NSFileOwnerAccountName = _.NSFileOwnerAccountName
NSFilePathErrorKey = _.NSFilePathErrorKey
NSFilePosixPermissions = _.NSFilePosixPermissions
NSFileReferenceCount = _.NSFileReferenceCount
NSFileSize = _.NSFileSize
NSFileSystemFileNumber = _.NSFileSystemFileNumber
NSFileSystemFreeNodes = _.NSFileSystemFreeNodes
NSFileSystemFreeSize = _.NSFileSystemFreeSize
NSFileSystemNodes = _.NSFileSystemNodes
NSFileSystemNumber = _.NSFileSystemNumber
NSFileSystemSize = _.NSFileSystemSize
NSFileType = _.NSFileType
NSFileTypeBlockSpecial = _.NSFileTypeBlockSpecial
NSFileTypeCharacterSpecial = _.NSFileTypeCharacterSpecial
NSFileTypeDirectory = _.NSFileTypeDirectory
NSFileTypeRegular = _.NSFileTypeRegular
NSFileTypeSocket = _.NSFileTypeSocket
NSFileTypeSymbolicLink = _.NSFileTypeSymbolicLink
NSFileTypeUnknown = _.NSFileTypeUnknown
NSFoundationVersionNumber = 751.63
NSGenericException = _.NSGenericException
NSGlobalDomain = _.NSGlobalDomain
NSGrammarCorrections = _.NSGrammarCorrections
NSGrammarRange = _.NSGrammarRange
NSGrammarUserDescription = _.NSGrammarUserDescription
NSGregorianCalendar = _.NSGregorianCalendar
NSHTTPCookieComment = _.NSHTTPCookieComment
NSHTTPCookieCommentURL = _.NSHTTPCookieCommentURL
NSHTTPCookieDiscard = _.NSHTTPCookieDiscard
NSHTTPCookieDomain = _.NSHTTPCookieDomain
NSHTTPCookieExpires = _.NSHTTPCookieExpires
NSHTTPCookieManagerAcceptPolicyChangedNotification = _.NSHTTPCookieManagerAcceptPolicyChangedNotification
NSHTTPCookieManagerCookiesChangedNotification = _.NSHTTPCookieManagerCookiesChangedNotification
NSHTTPCookieMaximumAge = _.NSHTTPCookieMaximumAge
NSHTTPCookieName = _.NSHTTPCookieName
NSHTTPCookieOriginURL = _.NSHTTPCookieOriginURL
NSHTTPCookiePath = _.NSHTTPCookiePath
NSHTTPCookiePort = _.NSHTTPCookiePort
NSHTTPCookieSecure = _.NSHTTPCookieSecure
NSHTTPCookieValue = _.NSHTTPCookieValue
NSHTTPCookieVersion = _.NSHTTPCookieVersion
NSHTTPPropertyErrorPageDataKey = _.NSHTTPPropertyErrorPageDataKey
NSHTTPPropertyHTTPProxy = _.NSHTTPPropertyHTTPProxy
NSHTTPPropertyRedirectionHeadersKey = _.NSHTTPPropertyRedirectionHeadersKey
NSHTTPPropertyServerHTTPVersionKey = _.NSHTTPPropertyServerHTTPVersionKey
NSHTTPPropertyStatusCodeKey = _.NSHTTPPropertyStatusCodeKey
NSHTTPPropertyStatusReasonKey = _.NSHTTPPropertyStatusReasonKey
NSHangOnUncaughtException = False
NSHebrewCalendar = _.NSHebrewCalendar
NSHelpAnchorErrorKey = _.NSHelpAnchorErrorKey
NSHourNameDesignations = _.NSHourNameDesignations
NSISO8601Calendar = _.NSISO8601Calendar
NSInconsistentArchiveException = _.NSInconsistentArchiveException
NSIndianCalendar = _.NSIndianCalendar
# (NSHashTableCallBacks)NSIntHashCallBacks
# (NSMapTableKeyCallBacks)NSIntMapKeyCallBacks
# (NSMapTableValueCallBacks)NSIntMapValueCallBacks
# (NSHashTableCallBacks)NSIntegerHashCallBacks
# (NSMapTableKeyCallBacks)NSIntegerMapKeyCallBacks
# (NSMapTableValueCallBacks)NSIntegerMapValueCallBacks
NSInternalInconsistencyException = _.NSInternalInconsistencyException
NSInternationalCurrencyString = _.NSInternationalCurrencyString
NSInvalidArchiveOperationException = _.NSInvalidArchiveOperationException
NSInvalidArgumentException = _.NSInvalidArgumentException
NSInvalidReceivePortException = _.NSInvalidReceivePortException
NSInvalidSendPortException = _.NSInvalidSendPortException
NSInvalidUnarchiveOperationException = _.NSInvalidUnarchiveOperationException
NSInvocationOperationCancelledException = _.NSInvocationOperationCancelledException
NSInvocationOperationVoidResultException = _.NSInvocationOperationVoidResultException
NSIsNilTransformerName = _.NSIsNilTransformerName
NSIsNotNilTransformerName = _.NSIsNotNilTransformerName
NSIslamicCalendar = _.NSIslamicCalendar
NSIslamicCivilCalendar = _.NSIslamicCivilCalendar
NSJapaneseCalendar = _.NSJapaneseCalendar
NSKeepAllocationStatistics = True
NSKeyValueChangeIndexesKey = _.NSKeyValueChangeIndexesKey
NSKeyValueChangeKindKey = _.NSKeyValueChangeKindKey
NSKeyValueChangeNewKey = _.NSKeyValueChangeNewKey
NSKeyValueChangeNotificationIsPriorKey = _.NSKeyValueChangeNotificationIsPriorKey
NSKeyValueChangeOldKey = _.NSKeyValueChangeOldKey
NSKeyedUnarchiveFromDataTransformerName = _.NSKeyedUnarchiveFromDataTransformerName
NSLaterTimeDesignations = _.NSLaterTimeDesignations
NSLoadedClasses = _.NSLoadedClasses
NSLocalNotificationCenterType = _.NSLocalNotificationCenterType
NSLocaleAlternateQuotationBeginDelimiterKey = _.NSLocaleAlternateQuotationBeginDelimiterKey
NSLocaleAlternateQuotationEndDelimiterKey = _.NSLocaleAlternateQuotationEndDelimiterKey
NSLocaleCalendar = _.NSLocaleCalendar
NSLocaleCollationIdentifier = _.NSLocaleCollationIdentifier
NSLocaleCollatorIdentifier = _.NSLocaleCollatorIdentifier
NSLocaleCountryCode = _.NSLocaleCountryCode
NSLocaleCurrencyCode = _.NSLocaleCurrencyCode
NSLocaleCurrencySymbol = _.NSLocaleCurrencySymbol
NSLocaleDecimalSeparator = _.NSLocaleDecimalSeparator
NSLocaleExemplarCharacterSet = _.NSLocaleExemplarCharacterSet
NSLocaleGroupingSeparator = _.NSLocaleGroupingSeparator
NSLocaleIdentifier = _.NSLocaleIdentifier
NSLocaleLanguageCode = _.NSLocaleLanguageCode
NSLocaleMeasurementSystem = _.NSLocaleMeasurementSystem
NSLocaleQuotationBeginDelimiterKey = _.NSLocaleQuotationBeginDelimiterKey
NSLocaleQuotationEndDelimiterKey = _.NSLocaleQuotationEndDelimiterKey
NSLocaleScriptCode = _.NSLocaleScriptCode
NSLocaleUsesMetricSystem = _.NSLocaleUsesMetricSystem
NSLocaleVariantCode = _.NSLocaleVariantCode
NSLocalizedDescriptionKey = _.NSLocalizedDescriptionKey
NSLocalizedFailureReasonErrorKey = _.NSLocalizedFailureReasonErrorKey
NSLocalizedRecoveryOptionsErrorKey = _.NSLocalizedRecoveryOptionsErrorKey
NSLocalizedRecoverySuggestionErrorKey = _.NSLocalizedRecoverySuggestionErrorKey
NSMachErrorDomain = _.NSMachErrorDomain
NSMallocException = _.NSMallocException
NSMaximumKeyValueOperator = _.NSMaximumKeyValueOperator
NSMetadataQueryDidFinishGatheringNotification = _.NSMetadataQueryDidFinishGatheringNotification
NSMetadataQueryDidStartGatheringNotification = _.NSMetadataQueryDidStartGatheringNotification
NSMetadataQueryDidUpdateNotification = _.NSMetadataQueryDidUpdateNotification
NSMetadataQueryGatheringProgressNotification = _.NSMetadataQueryGatheringProgressNotification
NSMetadataQueryLocalComputerScope = _.NSMetadataQueryLocalComputerScope
NSMetadataQueryNetworkScope = _.NSMetadataQueryNetworkScope
NSMetadataQueryResultContentRelevanceAttribute = _.NSMetadataQueryResultContentRelevanceAttribute
NSMetadataQueryUserHomeScope = _.NSMetadataQueryUserHomeScope
NSMinimumKeyValueOperator = _.NSMinimumKeyValueOperator
NSMonthNameArray = _.NSMonthNameArray
NSNegateBooleanTransformerName = _.NSNegateBooleanTransformerName
NSNegativeCurrencyFormatString = _.NSNegativeCurrencyFormatString
NSNetServicesErrorCode = _.NSNetServicesErrorCode
NSNetServicesErrorDomain = _.NSNetServicesErrorDomain
NSNextDayDesignations = _.NSNextDayDesignations
NSNextNextDayDesignations = _.NSNextNextDayDesignations
# (NSHashTableCallBacks)NSNonOwnedPointerHashCallBacks
# (NSMapTableKeyCallBacks)NSNonOwnedPointerMapKeyCallBacks
# (NSMapTableValueCallBacks)NSNonOwnedPointerMapValueCallBacks
# (NSMapTableKeyCallBacks)NSNonOwnedPointerOrNullMapKeyCallBacks
# (NSHashTableCallBacks)NSNonRetainedObjectHashCallBacks
# (NSMapTableKeyCallBacks)NSNonRetainedObjectMapKeyCallBacks
# (NSMapTableValueCallBacks)NSNonRetainedObjectMapValueCallBacks
NSOSStatusErrorDomain = _.NSOSStatusErrorDomain
# (NSHashTableCallBacks)NSObjectHashCallBacks
NSObjectInaccessibleException = _.NSObjectInaccessibleException
# (NSMapTableKeyCallBacks)NSObjectMapKeyCallBacks
# (NSMapTableValueCallBacks)NSObjectMapValueCallBacks
NSObjectNotAvailableException = _.NSObjectNotAvailableException
NSOldStyleException = _.NSOldStyleException
NSOperationNotSupportedForKeyException = _.NSOperationNotSupportedForKeyException
# (NSHashTableCallBacks)NSOwnedObjectIdentityHashCallBacks
# (NSHashTableCallBacks)NSOwnedPointerHashCallBacks
# (NSMapTableKeyCallBacks)NSOwnedPointerMapKeyCallBacks
# (NSMapTableValueCallBacks)NSOwnedPointerMapValueCallBacks
NSPOSIXErrorDomain = _.NSPOSIXErrorDomain
NSParseErrorException = _.NSParseErrorException
NSPersianCalendar = _.NSPersianCalendar
# (NSHashTableCallBacks)NSPointerToStructHashCallBacks
NSPortDidBecomeInvalidNotification = _.NSPortDidBecomeInvalidNotification
NSPortReceiveException = _.NSPortReceiveException
NSPortSendException = _.NSPortSendException
NSPortTimeoutException = _.NSPortTimeoutException
NSPositiveCurrencyFormatString = _.NSPositiveCurrencyFormatString
NSPriorDayDesignations = _.NSPriorDayDesignations
NSRangeException = _.NSRangeException
NSRecoveryAttempterErrorKey = _.NSRecoveryAttempterErrorKey
NSRegistrationDomain = _.NSRegistrationDomain
NSRepublicOfChinaCalendar = _.NSRepublicOfChinaCalendar
NSRunLoopCommonModes = _.NSRunLoopCommonModes
NSShortDateFormatString = _.NSShortDateFormatString
NSShortMonthNameArray = _.NSShortMonthNameArray
NSShortTimeDateFormatString = _.NSShortTimeDateFormatString
NSShortWeekDayNameArray = _.NSShortWeekDayNameArray
NSStreamDataWrittenToMemoryStreamKey = _.NSStreamDataWrittenToMemoryStreamKey
NSStreamFileCurrentOffsetKey = _.NSStreamFileCurrentOffsetKey
NSStreamSOCKSErrorDomain = _.NSStreamSOCKSErrorDomain
NSStreamSOCKSProxyConfigurationKey = _.NSStreamSOCKSProxyConfigurationKey
NSStreamSOCKSProxyHostKey = _.NSStreamSOCKSProxyHostKey
NSStreamSOCKSProxyPasswordKey = _.NSStreamSOCKSProxyPasswordKey
NSStreamSOCKSProxyPortKey = _.NSStreamSOCKSProxyPortKey
NSStreamSOCKSProxyUserKey = _.NSStreamSOCKSProxyUserKey
NSStreamSOCKSProxyVersion4 = _.NSStreamSOCKSProxyVersion4
NSStreamSOCKSProxyVersion5 = _.NSStreamSOCKSProxyVersion5
NSStreamSOCKSProxyVersionKey = _.NSStreamSOCKSProxyVersionKey
NSStreamSocketSSLErrorDomain = _.NSStreamSocketSSLErrorDomain
NSStreamSocketSecurityLevelKey = _.NSStreamSocketSecurityLevelKey
NSStreamSocketSecurityLevelNegotiatedSSL = _.NSStreamSocketSecurityLevelNegotiatedSSL
NSStreamSocketSecurityLevelNone = _.NSStreamSocketSecurityLevelNone
NSStreamSocketSecurityLevelSSLv2 = _.NSStreamSocketSecurityLevelSSLv2
NSStreamSocketSecurityLevelSSLv3 = _.NSStreamSocketSecurityLevelSSLv3
NSStreamSocketSecurityLevelTLSv1 = _.NSStreamSocketSecurityLevelTLSv1
NSStringEncodingErrorKey = _.NSStringEncodingErrorKey
NSSumKeyValueOperator = _.NSSumKeyValueOperator
NSSystemClockDidChangeNotification = _.NSSystemClockDidChangeNotification
NSSystemTimeZoneDidChangeNotification = _.NSSystemTimeZoneDidChangeNotification
NSTaskDidTerminateNotification = _.NSTaskDidTerminateNotification
NSTextCheckingCityKey = _.NSTextCheckingCityKey
NSTextCheckingCountryKey = _.NSTextCheckingCountryKey
NSTextCheckingJobTitleKey = _.NSTextCheckingJobTitleKey
NSTextCheckingNameKey = _.NSTextCheckingNameKey
NSTextCheckingOrganizationKey = _.NSTextCheckingOrganizationKey
NSTextCheckingPhoneKey = _.NSTextCheckingPhoneKey
NSTextCheckingStateKey = _.NSTextCheckingStateKey
NSTextCheckingStreetKey = _.NSTextCheckingStreetKey
NSTextCheckingZIPKey = _.NSTextCheckingZIPKey
NSThisDayDesignations = _.NSThisDayDesignations
NSThousandsSeparator = _.NSThousandsSeparator
NSThreadWillExitNotification = _.NSThreadWillExitNotification
NSTimeDateFormatString = _.NSTimeDateFormatString
NSTimeFormatString = _.NSTimeFormatString
NSURLAttributeModificationDateKey = _.NSURLAttributeModificationDateKey
NSURLAuthenticationMethodClientCertificate = _.NSURLAuthenticationMethodClientCertificate
NSURLAuthenticationMethodDefault = _.NSURLAuthenticationMethodDefault
NSURLAuthenticationMethodHTMLForm = _.NSURLAuthenticationMethodHTMLForm
NSURLAuthenticationMethodHTTPBasic = _.NSURLAuthenticationMethodHTTPBasic
NSURLAuthenticationMethodHTTPDigest = _.NSURLAuthenticationMethodHTTPDigest
NSURLAuthenticationMethodNTLM = _.NSURLAuthenticationMethodNTLM
NSURLAuthenticationMethodNegotiate = _.NSURLAuthenticationMethodNegotiate
NSURLAuthenticationMethodServerTrust = _.NSURLAuthenticationMethodServerTrust
NSURLContentAccessDateKey = _.NSURLContentAccessDateKey
NSURLContentModificationDateKey = _.NSURLContentModificationDateKey
NSURLCreationDateKey = _.NSURLCreationDateKey
NSURLCredentialStorageChangedNotification = _.NSURLCredentialStorageChangedNotification
NSURLCustomIconKey = _.NSURLCustomIconKey
NSURLEffectiveIconKey = _.NSURLEffectiveIconKey
NSURLErrorDomain = _.NSURLErrorDomain
NSURLErrorFailingURLErrorKey = _.NSURLErrorFailingURLErrorKey
NSURLErrorFailingURLPeerTrustErrorKey = _.NSURLErrorFailingURLPeerTrustErrorKey
NSURLErrorFailingURLStringErrorKey = _.NSURLErrorFailingURLStringErrorKey
NSURLErrorKey = _.NSURLErrorKey
NSURLFileAllocatedSizeKey = _.NSURLFileAllocatedSizeKey
NSURLFileScheme = _.NSURLFileScheme
NSURLFileSizeKey = _.NSURLFileSizeKey
NSURLHasHiddenExtensionKey = _.NSURLHasHiddenExtensionKey
NSURLIsAliasFileKey = _.NSURLIsAliasFileKey
NSURLIsDirectoryKey = _.NSURLIsDirectoryKey
NSURLIsHiddenKey = _.NSURLIsHiddenKey
NSURLIsPackageKey = _.NSURLIsPackageKey
NSURLIsRegularFileKey = _.NSURLIsRegularFileKey
NSURLIsSymbolicLinkKey = _.NSURLIsSymbolicLinkKey
NSURLIsSystemImmutableKey = _.NSURLIsSystemImmutableKey
NSURLIsUserImmutableKey = _.NSURLIsUserImmutableKey
NSURLIsVolumeKey = _.NSURLIsVolumeKey
NSURLLabelColorKey = _.NSURLLabelColorKey
NSURLLabelNumberKey = _.NSURLLabelNumberKey
NSURLLinkCountKey = _.NSURLLinkCountKey
NSURLLocalizedLabelKey = _.NSURLLocalizedLabelKey
NSURLLocalizedNameKey = _.NSURLLocalizedNameKey
NSURLLocalizedTypeDescriptionKey = _.NSURLLocalizedTypeDescriptionKey
NSURLNameKey = _.NSURLNameKey
NSURLParentDirectoryURLKey = _.NSURLParentDirectoryURLKey
NSURLProtectionSpaceFTP = _.NSURLProtectionSpaceFTP
NSURLProtectionSpaceFTPProxy = _.NSURLProtectionSpaceFTPProxy
NSURLProtectionSpaceHTTP = _.NSURLProtectionSpaceHTTP
NSURLProtectionSpaceHTTPProxy = _.NSURLProtectionSpaceHTTPProxy
NSURLProtectionSpaceHTTPS = _.NSURLProtectionSpaceHTTPS
NSURLProtectionSpaceHTTPSProxy = _.NSURLProtectionSpaceHTTPSProxy
NSURLProtectionSpaceSOCKSProxy = _.NSURLProtectionSpaceSOCKSProxy
NSURLTypeIdentifierKey = _.NSURLTypeIdentifierKey
NSURLVolumeAvailableCapacityKey = _.NSURLVolumeAvailableCapacityKey
NSURLVolumeIsJournalingKey = _.NSURLVolumeIsJournalingKey
NSURLVolumeLocalizedFormatDescriptionKey = _.NSURLVolumeLocalizedFormatDescriptionKey
NSURLVolumeResourceCountKey = _.NSURLVolumeResourceCountKey
NSURLVolumeSupportsCasePreservedNamesKey = _.NSURLVolumeSupportsCasePreservedNamesKey
NSURLVolumeSupportsCaseSensitiveNamesKey = _.NSURLVolumeSupportsCaseSensitiveNamesKey
NSURLVolumeSupportsHardLinksKey = _.NSURLVolumeSupportsHardLinksKey
NSURLVolumeSupportsJournalingKey = _.NSURLVolumeSupportsJournalingKey
NSURLVolumeSupportsPersistentIDsKey = _.NSURLVolumeSupportsPersistentIDsKey
NSURLVolumeSupportsSparseFilesKey = _.NSURLVolumeSupportsSparseFilesKey
NSURLVolumeSupportsSymbolicLinksKey = _.NSURLVolumeSupportsSymbolicLinksKey
NSURLVolumeSupportsZeroRunsKey = _.NSURLVolumeSupportsZeroRunsKey
NSURLVolumeTotalCapacityKey = _.NSURLVolumeTotalCapacityKey
NSURLVolumeURLKey = _.NSURLVolumeURLKey
NSUnarchiveFromDataTransformerName = _.NSUnarchiveFromDataTransformerName
NSUndefinedKeyException = _.NSUndefinedKeyException
NSUnderlyingErrorKey = _.NSUnderlyingErrorKey
NSUndoManagerCheckpointNotification = _.NSUndoManagerCheckpointNotification
NSUndoManagerDidOpenUndoGroupNotification = _.NSUndoManagerDidOpenUndoGroupNotification
NSUndoManagerDidRedoChangeNotification = _.NSUndoManagerDidRedoChangeNotification
NSUndoManagerDidUndoChangeNotification = _.NSUndoManagerDidUndoChangeNotification
NSUndoManagerWillCloseUndoGroupNotification = _.NSUndoManagerWillCloseUndoGroupNotification
NSUndoManagerWillRedoChangeNotification = _.NSUndoManagerWillRedoChangeNotification
NSUndoManagerWillUndoChangeNotification = _.NSUndoManagerWillUndoChangeNotification
NSUnionOfArraysKeyValueOperator = _.NSUnionOfArraysKeyValueOperator
NSUnionOfObjectsKeyValueOperator = _.NSUnionOfObjectsKeyValueOperator
NSUnionOfSetsKeyValueOperator = _.NSUnionOfSetsKeyValueOperator
NSUserDefaultsDidChangeNotification = _.NSUserDefaultsDidChangeNotification
NSWeekDayNameArray = _.NSWeekDayNameArray
NSWillBecomeMultiThreadedNotification = _.NSWillBecomeMultiThreadedNotification
NSXMLParserErrorDomain = _.NSXMLParserErrorDomain
NSYearMonthWeekDesignations = _.NSYearMonthWeekDesignations
# (NSPoint)NSZeroPoint
# (NSRect)NSZeroRect
# (NSSize)NSZeroSize
NSZombieEnabled = False

# enums
NSASCIIStringEncoding = 1
NSAdminApplicationDirectory = 4
NSAggregateExpressionType = 14
NSAllApplicationsDirectory = 100
NSAllDomainsMask = 65535
NSAllLibrariesDirectory = 101
NSAllPredicateModifier = 1
NSAnchoredSearch = 8
NSAndPredicateType = 1
NSAnyPredicateModifier = 2
NSApplicationDirectory = 1
NSApplicationSupportDirectory = 14
NSArgumentEvaluationScriptError = 3
NSArgumentsWrongScriptError = 6
NSAtomicWrite = 1
NSAttributedStringEnumerationLongestEffectiveRangeNotRequired = 1048576
NSAttributedStringEnumerationReverse = 2
NSAutosavedInformationDirectory = 11
NSBackwardsSearch = 4
NSBeginsWithComparison = 5
NSBeginsWithPredicateOperatorType = 8
NSBetweenPredicateOperatorType = 100
NSBinarySearchingFirstEqual = 256
NSBinarySearchingInsertionIndex = 1024
NSBinarySearchingLastEqual = 512
NSBlockExpressionType = 19
NSBundleExecutableArchitectureI386 = 7
NSBundleExecutableArchitecturePPC = 18
NSBundleExecutableArchitecturePPC64 = 16777234
NSBundleExecutableArchitectureX86_64 = 16777223
NSCachesDirectory = 13
NSCalculationDivideByZero = 4
NSCalculationLossOfPrecision = 1
NSCalculationNoError = 0
NSCalculationOverflow = 3
NSCalculationUnderflow = 2
NSCannotCreateScriptCommandError = 10
NSCaseInsensitivePredicateOption = 1
NSCaseInsensitiveSearch = 1
NSCollectorDisabledOption = 2
NSConstantValueExpressionType = 0
NSContainerSpecifierError = 2
NSContainsComparison = 7
NSContainsPredicateOperatorType = 99
NSCoreServiceDirectory = 10
NSCustomSelectorPredicateOperatorType = 11
NSDataReadingMapped = 1
NSDataReadingUncached = 2
NSDataSearchAnchored = 2
NSDataSearchBackwards = 1
NSDataWritingAtomic = 1
NSDateFormatterBehavior10_0 = 1000
NSDateFormatterBehavior10_4 = 1040
NSDateFormatterBehaviorDefault = 0
NSDateFormatterFullStyle = 4
NSDateFormatterLongStyle = 3
NSDateFormatterMediumStyle = 2
NSDateFormatterNoStyle = 0
NSDateFormatterShortStyle = 1
NSDayCalendarUnit = 16
NSDecimalMaxSize = 8
NSDecimalNoScale = 32767
NSDemoApplicationDirectory = 2
NSDesktopDirectory = 12
NSDeveloperApplicationDirectory = 3
NSDeveloperDirectory = 6
NSDiacriticInsensitivePredicateOption = 2
NSDiacriticInsensitiveSearch = 128
NSDirectPredicateModifier = 0
NSDirectoryEnumerationSkipsHiddenFiles = 4
NSDirectoryEnumerationSkipsPackageDescendants = 2
NSDirectoryEnumerationSkipsSubdirectoryDescendants = 1
NSDocumentDirectory = 9
NSDocumentationDirectory = 8
NSDownloadsDirectory = 15
NSEndsWithComparison = 6
NSEndsWithPredicateOperatorType = 9
NSEnumerationConcurrent = 1
NSEnumerationReverse = 2
NSEqualToComparison = 0
NSEqualToPredicateOperatorType = 4
NSEraCalendarUnit = 2
NSEvaluatedObjectExpressionType = 1
NSEverySubelement = 1
NSExecutableArchitectureMismatchError = 3585
NSExecutableErrorMaximum = 3839
NSExecutableErrorMinimum = 3584
NSExecutableLinkError = 3588
NSExecutableLoadError = 3587
NSExecutableNotLoadableError = 3584
NSExecutableRuntimeMismatchError = 3586
NSFileErrorMaximum = 1023
NSFileErrorMinimum = 0
NSFileLockingError = 255
NSFileManagerItemReplacementUsingNewMetadataOnly = 1
NSFileManagerItemReplacementWithoutDeletingBackupItem = 2
NSFileNoSuchFileError = 4
NSFileReadCorruptFileError = 259
NSFileReadInapplicableStringEncodingError = 261
NSFileReadInvalidFileNameError = 258
NSFileReadNoPermissionError = 257
NSFileReadNoSuchFileError = 260
NSFileReadTooLargeError = 263
NSFileReadUnknownError = 256
NSFileReadUnknownStringEncodingError = 264
NSFileReadUnsupportedSchemeError = 262
NSFileWriteInapplicableStringEncodingError = 517
NSFileWriteInvalidFileNameError = 514
NSFileWriteNoPermissionError = 513
NSFileWriteOutOfSpaceError = 640
NSFileWriteUnknownError = 512
NSFileWriteUnsupportedSchemeError = 518
NSFileWriteVolumeReadOnlyError = 642
NSForcedOrderingSearch = 512
NSFormattingError = 2048
NSFormattingErrorMaximum = 2559
NSFormattingErrorMinimum = 2048
NSFoundationVersionNumber10_0 = 397.39999999999998
NSFoundationVersionNumber10_1 = 425.00000000000000
NSFoundationVersionNumber10_1_1 = 425.00000000000000
NSFoundationVersionNumber10_1_2 = 425.00000000000000
NSFoundationVersionNumber10_1_3 = 425.00000000000000
NSFoundationVersionNumber10_1_4 = 425.00000000000000
NSFoundationVersionNumber10_2 = 462.00000000000000
NSFoundationVersionNumber10_2_1 = 462.00000000000000
NSFoundationVersionNumber10_2_2 = 462.00000000000000
NSFoundationVersionNumber10_2_3 = 462.00000000000000
NSFoundationVersionNumber10_2_4 = 462.00000000000000
NSFoundationVersionNumber10_2_5 = 462.00000000000000
NSFoundationVersionNumber10_2_6 = 462.00000000000000
NSFoundationVersionNumber10_2_7 = 462.69999999999999
NSFoundationVersionNumber10_2_8 = 462.69999999999999
NSFoundationVersionNumber10_3 = 500.00000000000000
NSFoundationVersionNumber10_3_1 = 500.00000000000000
NSFoundationVersionNumber10_3_2 = 500.30000000000001
NSFoundationVersionNumber10_3_3 = 500.54000000000002
NSFoundationVersionNumber10_3_4 = 500.56000000000000
NSFoundationVersionNumber10_3_5 = 500.56000000000000
NSFoundationVersionNumber10_3_6 = 500.56000000000000
NSFoundationVersionNumber10_3_7 = 500.56000000000000
NSFoundationVersionNumber10_3_8 = 500.56000000000000
NSFoundationVersionNumber10_3_9 = 500.57999999999998
NSFoundationVersionNumber10_4 = 567.00000000000000
NSFoundationVersionNumber10_4_1 = 567.00000000000000
NSFoundationVersionNumber10_4_10 = 567.28999999999996
NSFoundationVersionNumber10_4_11 = 567.36000000000001
NSFoundationVersionNumber10_4_2 = 567.12000000000000
NSFoundationVersionNumber10_4_3 = 567.21000000000004
NSFoundationVersionNumber10_4_4_Intel = 567.23000000000002
NSFoundationVersionNumber10_4_4_PowerPC = 567.21000000000004
NSFoundationVersionNumber10_4_5 = 567.25000000000000
NSFoundationVersionNumber10_4_6 = 567.25999999999999
NSFoundationVersionNumber10_4_7 = 567.26999999999998
NSFoundationVersionNumber10_4_8 = 567.27999999999997
NSFoundationVersionNumber10_4_9 = 567.28999999999996
NSFoundationVersionNumber10_5 = 677.00000000000000
NSFoundationVersionNumber10_5_1 = 677.10000000000002
NSFoundationVersionNumber10_5_2 = 677.14999999999998
NSFoundationVersionNumber10_5_3 = 677.19000000000005
NSFoundationVersionNumber10_5_4 = 677.19000000000005
NSFoundationVersionNumber10_5_5 = 677.21000000000004
NSFoundationVersionNumber10_5_6 = 677.22000000000003
NSFoundationVersionNumber10_5_7 = 677.24000000000001
NSFoundationVersionNumber10_5_8 = 677.25999999999999
NSFoundationVersionNumber10_6 = 751.00000000000000
NSFoundationVersionNumber10_6_1 = 751.00000000000000
NSFoundationVersionNumber10_6_2 = 751.13999999999999
NSFoundationVersionNumber10_6_3 = 751.21000000000004
NSFoundationVersionWithFileManagerResourceForkSupport = 412
NSFunctionExpressionType = 4
NSGEOMETRY_TYPES_SAME_AS_CGGEOMETRY_TYPES = None
NSGreaterThanComparison = 4
NSGreaterThanOrEqualToComparison = 3
NSGreaterThanOrEqualToPredicateOperatorType = 3
NSGreaterThanPredicateOperatorType = 2
NSHPUXOperatingSystem = 4
NSHTTPCookieAcceptPolicyAlways = 0
NSHTTPCookieAcceptPolicyNever = 1
NSHTTPCookieAcceptPolicyOnlyFromMainDocumentDomain = 2
NSHashTableCopyIn = 65536
NSHashTableObjectPointerPersonality = 512
NSHashTableStrongMemory = 0
NSHashTableZeroingWeakMemory = 1
NSHourCalendarUnit = 32
NSINTEGER_DEFINED = 1
NSISO2022JPStringEncoding = 21
NSISOLatin1StringEncoding = 5
NSISOLatin2StringEncoding = 9
NSInPredicateOperatorType = 10
NSIndexSubelement = 0
NSInputMethodsDirectory = 16
NSIntegerMax = 2147483647
NSIntegerMin = -2147483648
NSInternalScriptError = 8
NSInternalSpecifierError = 5
NSIntersectSetExpressionType = 6
NSInvalidIndexSpecifierError = 4
NSItemReplacementDirectory = 99
NSJapaneseEUCStringEncoding = 3
NSKeyPathExpressionType = 3
NSKeySpecifierEvaluationScriptError = 2
NSKeyValueChangeInsertion = 2
NSKeyValueChangeRemoval = 3
NSKeyValueChangeReplacement = 4
NSKeyValueChangeSetting = 1
NSKeyValueIntersectSetMutation = 3
NSKeyValueMinusSetMutation = 2
NSKeyValueObservingOptionInitial = 4
NSKeyValueObservingOptionNew = 1
NSKeyValueObservingOptionOld = 2
NSKeyValueObservingOptionPrior = 8
NSKeyValueSetSetMutation = 4
NSKeyValueUnionSetMutation = 1
NSKeyValueValidationError = 1024
NSLessThanComparison = 2
NSLessThanOrEqualToComparison = 1
NSLessThanOrEqualToPredicateOperatorType = 1
NSLessThanPredicateOperatorType = 0
NSLibraryDirectory = 5
NSLikePredicateOperatorType = 7
NSLiteralSearch = 2
NSLocalDomainMask = 2
NSLocaleLanguageDirectionBottomToTop = 4
NSLocaleLanguageDirectionLeftToRight = 1
NSLocaleLanguageDirectionRightToLeft = 2
NSLocaleLanguageDirectionTopToBottom = 3
NSLocaleLanguageDirectionUnknown = 0
NSMACHOperatingSystem = 5
NSMacOSRomanStringEncoding = 30
NSMachPortDeallocateNone = 0
NSMachPortDeallocateReceiveRight = 2
NSMachPortDeallocateSendRight = 1
NSMapTableCopyIn = 65536
NSMapTableObjectPointerPersonality = 512
NSMapTableStrongMemory = 0
NSMapTableZeroingWeakMemory = 1
NSMappedRead = 1
NSMatchesPredicateOperatorType = 6
NSMaxXEdge = None
NSMaxYEdge = None
NSMiddleSubelement = 2
NSMinXEdge = None
NSMinYEdge = None
NSMinusSetExpressionType = 7
NSMinuteCalendarUnit = 64
NSMonthCalendarUnit = 8
NSMoviesDirectory = 17
NSMusicDirectory = 18
NSNEXTSTEPStringEncoding = 2
NSNetServiceNoAutoRename = 1
NSNetServicesActivityInProgress = -72003
NSNetServicesBadArgumentError = -72004
NSNetServicesCancelledError = -72005
NSNetServicesCollisionError = -72001
NSNetServicesInvalidError = -72006
NSNetServicesNotFoundError = -72002
NSNetServicesTimeoutError = -72007
NSNetServicesUnknownError = -72000
NSNetworkDomainMask = 4
NSNoScriptError = 0
NSNoSpecifierError = 0
NSNoSubelement = 4
NSNoTopLevelContainersSpecifierError = 1
NSNonLossyASCIIStringEncoding = 7
NSNotEqualToPredicateOperatorType = 5
NSNotFound = 2147483647
NSNotPredicateType = 0
NSNotificationCoalescingOnName = 1
NSNotificationCoalescingOnSender = 2
NSNotificationDeliverImmediately = 1
NSNotificationNoCoalescing = 0
NSNotificationPostToAllSessions = 2
NSNotificationSuspensionBehaviorCoalesce = 2
NSNotificationSuspensionBehaviorDeliverImmediately = 4
NSNotificationSuspensionBehaviorDrop = 1
NSNotificationSuspensionBehaviorHold = 3
NSNumberFormatterBehavior10_0 = 1000
NSNumberFormatterBehavior10_4 = 1040
NSNumberFormatterBehaviorDefault = 0
NSNumberFormatterCurrencyStyle = 2
NSNumberFormatterDecimalStyle = 1
NSNumberFormatterNoStyle = 0
NSNumberFormatterPadAfterPrefix = 1
NSNumberFormatterPadAfterSuffix = 3
NSNumberFormatterPadBeforePrefix = 0
NSNumberFormatterPadBeforeSuffix = 2
NSNumberFormatterPercentStyle = 3
NSNumberFormatterRoundCeiling = 0
NSNumberFormatterRoundDown = 2
NSNumberFormatterRoundFloor = 1
NSNumberFormatterRoundHalfDown = 5
NSNumberFormatterRoundHalfEven = 4
NSNumberFormatterRoundHalfUp = 6
NSNumberFormatterRoundUp = 3
NSNumberFormatterScientificStyle = 4
NSNumberFormatterSpellOutStyle = 5
NSNumericSearch = 64
NSOSF1OperatingSystem = 7
NSObjectAutoreleasedEvent = 3
NSObjectExtraRefDecrementedEvent = 5
NSObjectExtraRefIncrementedEvent = 4
NSObjectInternalRefDecrementedEvent = 7
NSObjectInternalRefIncrementedEvent = 6
NSOpenStepUnicodeReservedBase = 62464
NSOperationNotSupportedForKeyScriptError = 9
NSOperationNotSupportedForKeySpecifierError = 6
NSOperationQueueDefaultMaxConcurrentOperationCount = -1
NSOperationQueuePriorityHigh = 4
NSOperationQueuePriorityLow = -4
NSOperationQueuePriorityNormal = 0
NSOperationQueuePriorityVeryHigh = 8
NSOperationQueuePriorityVeryLow = -8
NSOrPredicateType = 2
NSOrderedAscending = -1
NSOrderedDescending = 1
NSOrderedSame = 0
NSPicturesDirectory = 19
NSPointerFunctionsCStringPersonality = 768
NSPointerFunctionsCopyIn = 65536
NSPointerFunctionsIntegerPersonality = 1280
NSPointerFunctionsMachVirtualMemory = 4
NSPointerFunctionsMallocMemory = 3
NSPointerFunctionsObjectPersonality = 0
NSPointerFunctionsObjectPointerPersonality = 512
NSPointerFunctionsOpaqueMemory = 2
NSPointerFunctionsOpaquePersonality = 256
NSPointerFunctionsStrongMemory = 0
NSPointerFunctionsStructPersonality = 1024
NSPointerFunctionsZeroingWeakMemory = 1
NSPositionAfter = 0
NSPositionBefore = 1
NSPositionBeginning = 2
NSPositionEnd = 3
NSPositionReplace = 4
NSPostASAP = 2
NSPostNow = 3
NSPostWhenIdle = 1
NSPreferencePanesDirectory = 22
NSPrinterDescriptionDirectory = 20
NSPropertyListBinaryFormat_v1_0 = 200
NSPropertyListErrorMaximum = 4095
NSPropertyListErrorMinimum = 3840
NSPropertyListImmutable = 0
NSPropertyListMutableContainers = 1
NSPropertyListMutableContainersAndLeaves = 2
NSPropertyListOpenStepFormat = 1
NSPropertyListReadCorruptError = 3840
NSPropertyListReadStreamError = 3842
NSPropertyListReadUnknownVersionError = 3841
NSPropertyListWriteStreamError = 3851
NSPropertyListXMLFormat_v1_0 = 100
NSQuarterCalendarUnit = 2048
NSRandomSubelement = 3
NSReceiverEvaluationScriptError = 1
NSReceiversCantHandleCommandScriptError = 4
NSRelativeAfter = 0
NSRelativeBefore = 1
NSRequiredArgumentsMissingScriptError = 5
NSRoundBankers = 3
NSRoundDown = 1
NSRoundPlain = 0
NSRoundUp = 2
NSSaveOptionsAsk = 2
NSSaveOptionsNo = 1
NSSaveOptionsYes = 0
NSScannedOption = 1
NSSecondCalendarUnit = 128
NSSharedPublicDirectory = 21
NSShiftJISStringEncoding = 8
NSSolarisOperatingSystem = 3
NSSortConcurrent = 1
NSSortStable = 16
NSStreamEventEndEncountered = 16
NSStreamEventErrorOccurred = 8
NSStreamEventHasBytesAvailable = 2
NSStreamEventHasSpaceAvailable = 4
NSStreamEventNone = 0
NSStreamEventOpenCompleted = 1
NSStreamStatusAtEnd = 5
NSStreamStatusClosed = 6
NSStreamStatusError = 7
NSStreamStatusNotOpen = 0
NSStreamStatusOpen = 2
NSStreamStatusOpening = 1
NSStreamStatusReading = 3
NSStreamStatusWriting = 4
NSStringEncodingConversionAllowLossy = 1
NSStringEncodingConversionExternalRepresentation = 2
NSStringEnumerationByComposedCharacterSequences = 2
NSStringEnumerationByLines = 0
NSStringEnumerationByParagraphs = 1
NSStringEnumerationBySentences = 4
NSStringEnumerationByWords = 3
NSStringEnumerationLocalized = 1024
NSStringEnumerationReverse = 256
NSStringEnumerationSubstringNotRequired = 512
NSSubqueryExpressionType = 13
NSSunOSOperatingSystem = 6
NSSymbolStringEncoding = 6
NSSystemDomainMask = 8
NSTaskTerminationReasonExit = 1
NSTaskTerminationReasonUncaughtSignal = 2
NSTextCheckingAllCustomTypes = 0
NSTextCheckingAllSystemTypes = -1
NSTextCheckingAllTypes = -1
NSTextCheckingTypeAddress = 16
NSTextCheckingTypeCorrection = 512
NSTextCheckingTypeDash = 128
NSTextCheckingTypeDate = 8
NSTextCheckingTypeGrammar = 4
NSTextCheckingTypeLink = 32
NSTextCheckingTypeOrthography = 1
NSTextCheckingTypeQuote = 64
NSTextCheckingTypeReplacement = 256
NSTextCheckingTypeSpelling = 2
NSTimeIntervalSince1970 = 978307200.00000000
NSTimeZoneNameStyleDaylightSaving = 2
NSTimeZoneNameStyleGeneric = 4
NSTimeZoneNameStyleShortDaylightSaving = 3
NSTimeZoneNameStyleShortGeneric = 5
NSTimeZoneNameStyleShortStandard = 1
NSTimeZoneNameStyleStandard = 0
NSUIntegerMax = 4294967295
NSURLBookmarkCreationMinimalBookmark = 512
NSURLBookmarkCreationPreferFileIDResolution = 256
NSURLBookmarkCreationSuitableForBookmarkFile = 1024
NSURLBookmarkResolutionWithoutMounting = 512
NSURLBookmarkResolutionWithoutUI = 256
NSURLCacheStorageAllowed = 0
NSURLCacheStorageAllowedInMemoryOnly = 1
NSURLCacheStorageNotAllowed = 2
NSURLCredentialPersistenceForSession = 1
NSURLCredentialPersistenceNone = 0
NSURLCredentialPersistencePermanent = 2
NSURLErrorBadServerResponse = -1011
NSURLErrorBadURL = -1000
NSURLErrorCancelled = -999
NSURLErrorCannotCloseFile = -3002
NSURLErrorCannotConnectToHost = -1004
NSURLErrorCannotCreateFile = -3000
NSURLErrorCannotDecodeContentData = -1016
NSURLErrorCannotDecodeRawData = -1015
NSURLErrorCannotFindHost = -1003
NSURLErrorCannotLoadFromNetwork = -2000
NSURLErrorCannotMoveFile = -3005
NSURLErrorCannotOpenFile = -3001
NSURLErrorCannotParseResponse = -1017
NSURLErrorCannotRemoveFile = -3004
NSURLErrorCannotWriteToFile = -3003
NSURLErrorClientCertificateRejected = -1205
NSURLErrorClientCertificateRequired = -1206
NSURLErrorDNSLookupFailed = -1006
NSURLErrorDataLengthExceedsMaximum = -1103
NSURLErrorDownloadDecodingFailedMidStream = -3006
NSURLErrorDownloadDecodingFailedToComplete = -3007
NSURLErrorFileDoesNotExist = -1100
NSURLErrorFileIsDirectory = -1101
NSURLErrorHTTPTooManyRedirects = -1007
NSURLErrorNetworkConnectionLost = -1005
NSURLErrorNoPermissionsToReadFile = -1102
NSURLErrorNotConnectedToInternet = -1009
NSURLErrorRedirectToNonExistentLocation = -1010
NSURLErrorResourceUnavailable = -1008
NSURLErrorSecureConnectionFailed = -1200
NSURLErrorServerCertificateHasBadDate = -1201
NSURLErrorServerCertificateHasUnknownRoot = -1203
NSURLErrorServerCertificateNotYetValid = -1204
NSURLErrorServerCertificateUntrusted = -1202
NSURLErrorTimedOut = -1001
NSURLErrorUnknown = -1
NSURLErrorUnsupportedURL = -1002
NSURLErrorUserAuthenticationRequired = -1013
NSURLErrorUserCancelledAuthentication = -1012
NSURLErrorZeroByteResource = -1014
NSURLHandleLoadFailed = 3
NSURLHandleLoadInProgress = 2
NSURLHandleLoadSucceeded = 1
NSURLHandleNotLoaded = 0
NSURLRequestReloadIgnoringCacheData = 1
NSURLRequestReloadIgnoringLocalAndRemoteCacheData = 4
NSURLRequestReloadIgnoringLocalCacheData = 1
NSURLRequestReloadRevalidatingCacheData = 5
NSURLRequestReturnCacheDataDontLoad = 3
NSURLRequestReturnCacheDataElseLoad = 2
NSURLRequestUseProtocolCachePolicy = 0
NSUTF16BigEndianStringEncoding = -1879047936
NSUTF16LittleEndianStringEncoding = -1811939072
NSUTF16StringEncoding = 10
NSUTF32BigEndianStringEncoding = -1744830208
NSUTF32LittleEndianStringEncoding = -1677721344
NSUTF32StringEncoding = -1946156800
NSUTF8StringEncoding = 4
NSUncachedRead = 2
NSUndefinedDateComponent = 2147483647
NSUndoCloseGroupingRunLoopOrdering = 350000
NSUnicodeStringEncoding = 10
NSUnionSetExpressionType = 5
NSUnknownKeyScriptError = 7
NSUnknownKeySpecifierError = 3
NSUserCancelledError = 3072
NSUserDirectory = 7
NSUserDomainMask = 1
NSValidationErrorMaximum = 2047
NSValidationErrorMinimum = 1024
NSVariableExpressionType = 2
NSVolumeEnumerationProduceFileReferenceURLs = 4
NSVolumeEnumerationSkipHiddenVolumes = 2
NSWeekCalendarUnit = 256
NSWeekdayCalendarUnit = 512
NSWeekdayOrdinalCalendarUnit = 1024
NSWidthInsensitiveSearch = 256
NSWindows95OperatingSystem = 2
NSWindowsCP1250StringEncoding = 15
NSWindowsCP1251StringEncoding = 11
NSWindowsCP1252StringEncoding = 12
NSWindowsCP1253StringEncoding = 13
NSWindowsCP1254StringEncoding = 14
NSWindowsNTOperatingSystem = 1
NSWrapCalendarComponents = 1
NSXMLAttributeCDATAKind = 6
NSXMLAttributeDeclarationKind = 10
NSXMLAttributeEntitiesKind = 11
NSXMLAttributeEntityKind = 10
NSXMLAttributeEnumerationKind = 14
NSXMLAttributeIDKind = 7
NSXMLAttributeIDRefKind = 8
NSXMLAttributeIDRefsKind = 9
NSXMLAttributeKind = 3
NSXMLAttributeNMTokenKind = 12
NSXMLAttributeNMTokensKind = 13
NSXMLAttributeNotationKind = 15
NSXMLCommentKind = 6
NSXMLDTDKind = 8
NSXMLDocumentHTMLKind = 2
NSXMLDocumentIncludeContentTypeDeclaration = 262144
NSXMLDocumentKind = 1
NSXMLDocumentTextKind = 3
NSXMLDocumentTidyHTML = 512
NSXMLDocumentTidyXML = 1024
NSXMLDocumentValidate = 8192
NSXMLDocumentXHTMLKind = 1
NSXMLDocumentXInclude = 65536
NSXMLDocumentXMLKind = 0
NSXMLElementDeclarationAnyKind = 18
NSXMLElementDeclarationElementKind = 20
NSXMLElementDeclarationEmptyKind = 17
NSXMLElementDeclarationKind = 11
NSXMLElementDeclarationMixedKind = 19
NSXMLElementDeclarationUndefinedKind = 16
NSXMLElementKind = 2
NSXMLEntityDeclarationKind = 9
NSXMLEntityGeneralKind = 1
NSXMLEntityParameterKind = 4
NSXMLEntityParsedKind = 2
NSXMLEntityPredefined = 5
NSXMLEntityUnparsedKind = 3
NSXMLInvalidKind = 0
NSXMLNamespaceKind = 4
NSXMLNodeCompactEmptyElement = 4
NSXMLNodeExpandEmptyElement = 2
NSXMLNodeIsCDATA = 1
NSXMLNodeOptionsNone = 0
NSXMLNodePreserveAll = -1048546
NSXMLNodePreserveAttributeOrder = 2097152
NSXMLNodePreserveCDATA = 16777216
NSXMLNodePreserveCharacterReferences = 134217728
NSXMLNodePreserveDTD = 67108864
NSXMLNodePreserveEmptyElements = 6
NSXMLNodePreserveEntities = 4194304
NSXMLNodePreserveNamespaceOrder = 1048576
NSXMLNodePreservePrefixes = 8388608
NSXMLNodePreserveQuotes = 24
NSXMLNodePreserveWhitespace = 33554432
NSXMLNodePrettyPrint = 131072
NSXMLNodeUseDoubleQuotes = 16
NSXMLNodeUseSingleQuotes = 8
NSXMLNotationDeclarationKind = 12
NSXMLParserAttributeHasNoValueError = 41
NSXMLParserAttributeListNotFinishedError = 51
NSXMLParserAttributeListNotStartedError = 50
NSXMLParserAttributeNotFinishedError = 40
NSXMLParserAttributeNotStartedError = 39
NSXMLParserAttributeRedefinedError = 42
NSXMLParserCDATANotFinishedError = 63
NSXMLParserCharacterRefAtEOFError = 10
NSXMLParserCharacterRefInDTDError = 13
NSXMLParserCharacterRefInEpilogError = 12
NSXMLParserCharacterRefInPrologError = 11
NSXMLParserCommentContainsDoubleHyphenError = 80
NSXMLParserCommentNotFinishedError = 45
NSXMLParserConditionalSectionNotFinishedError = 59
NSXMLParserConditionalSectionNotStartedError = 58
NSXMLParserDOCTYPEDeclNotFinishedError = 61
NSXMLParserDelegateAbortedParseError = 512
NSXMLParserDocumentStartError = 3
NSXMLParserElementContentDeclNotFinishedError = 55
NSXMLParserElementContentDeclNotStartedError = 54
NSXMLParserEmptyDocumentError = 4
NSXMLParserEncodingNotSupportedError = 32
NSXMLParserEntityBoundaryError = 90
NSXMLParserEntityIsExternalError = 29
NSXMLParserEntityIsParameterError = 30
NSXMLParserEntityNotFinishedError = 37
NSXMLParserEntityNotStartedError = 36
NSXMLParserEntityRefAtEOFError = 14
NSXMLParserEntityRefInDTDError = 17
NSXMLParserEntityRefInEpilogError = 16
NSXMLParserEntityRefInPrologError = 15
NSXMLParserEntityRefLoopError = 89
NSXMLParserEntityReferenceMissingSemiError = 23
NSXMLParserEntityReferenceWithoutNameError = 22
NSXMLParserEntityValueRequiredError = 84
NSXMLParserEqualExpectedError = 75
NSXMLParserExternalStandaloneEntityError = 82
NSXMLParserExternalSubsetNotFinishedError = 60
NSXMLParserExtraContentError = 86
NSXMLParserGTRequiredError = 73
NSXMLParserInternalError = 1
NSXMLParserInvalidCharacterError = 9
NSXMLParserInvalidCharacterInEntityError = 87
NSXMLParserInvalidCharacterRefError = 8
NSXMLParserInvalidConditionalSectionError = 83
NSXMLParserInvalidDecimalCharacterRefError = 7
NSXMLParserInvalidEncodingError = 81
NSXMLParserInvalidEncodingNameError = 79
NSXMLParserInvalidHexCharacterRefError = 6
NSXMLParserInvalidURIError = 91
NSXMLParserLTRequiredError = 72
NSXMLParserLTSlashRequiredError = 74
NSXMLParserLessThanSymbolInAttributeError = 38
NSXMLParserLiteralNotFinishedError = 44
NSXMLParserLiteralNotStartedError = 43
NSXMLParserMisplacedCDATAEndStringError = 62
NSXMLParserMisplacedXMLDeclarationError = 64
NSXMLParserMixedContentDeclNotFinishedError = 53
NSXMLParserMixedContentDeclNotStartedError = 52
NSXMLParserNAMERequiredError = 68
NSXMLParserNMTOKENRequiredError = 67
NSXMLParserNamespaceDeclarationError = 35
NSXMLParserNoDTDError = 94
NSXMLParserNotWellBalancedError = 85
NSXMLParserNotationNotFinishedError = 49
NSXMLParserNotationNotStartedError = 48
NSXMLParserOutOfMemoryError = 2
NSXMLParserPCDATARequiredError = 69
NSXMLParserParsedEntityRefAtEOFError = 18
NSXMLParserParsedEntityRefInEpilogError = 20
NSXMLParserParsedEntityRefInInternalError = 88
NSXMLParserParsedEntityRefInInternalSubsetError = 21
NSXMLParserParsedEntityRefInPrologError = 19
NSXMLParserParsedEntityRefMissingSemiError = 25
NSXMLParserParsedEntityRefNoNameError = 24
NSXMLParserPrematureDocumentEndError = 5
NSXMLParserProcessingInstructionNotFinishedError = 47
NSXMLParserProcessingInstructionNotStartedError = 46
NSXMLParserPublicIdentifierRequiredError = 71
NSXMLParserSeparatorRequiredError = 66
NSXMLParserSpaceRequiredError = 65
NSXMLParserStandaloneValueError = 78
NSXMLParserStringNotClosedError = 34
NSXMLParserStringNotStartedError = 33
NSXMLParserTagNameMismatchError = 76
NSXMLParserURIFragmentError = 92
NSXMLParserURIRequiredError = 70
NSXMLParserUndeclaredEntityError = 26
NSXMLParserUnfinishedTagError = 77
NSXMLParserUnknownEncodingError = 31
NSXMLParserUnparsedEntityError = 28
NSXMLParserXMLDeclNotFinishedError = 57
NSXMLParserXMLDeclNotStartedError = 56
NSXMLProcessingInstructionKind = 5
NSXMLTextKind = 7
NSYearCalendarUnit = 4
NS_BLOCKS_AVAILABLE = 1
NS_BigEndian = 2
NS_LittleEndian = 1
NS_UNICHAR_IS_EIGHT_BIT = 0
NS_UnknownByteOrder = 0
