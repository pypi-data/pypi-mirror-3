#
# Copyright (c) 2006-2011, Prometheus Research, LLC
# See `LICENSE` for license information, `AUTHORS` for the list of authors.
#


"""
:mod:`htsql_engine.mysql.tr.dump`
=================================

This module adapts the SQL serializer for MySQL.
"""


from htsql.adapter import adapts
from htsql.domain import (BooleanDomain, NumberDomain, IntegerDomain,
                          StringDomain)
from htsql.tr.dump import (FormatName, FormatLiteral,
                           DumpDecimal, DumpFloat, DumpDate,
                           DumpTime, DumpDateTime,
                           DumpToDomain, DumpToInteger, DumpToFloat,
                           DumpToDecimal, DumpToString, DumpToDateTime,
                           DumpIsTotallyEqual)
from htsql.tr.fn.dump import (DumpTrunc, DumpTruncTo,
                              DumpDateIncrement, DumpDateTimeIncrement,
                              DumpDateDecrement, DumpDateTimeDecrement,
                              DumpDateDifference, DumpExtractSecond,
                              DumpConcatenate, DumpLike,
                              DumpMakeDate, DumpMakeDateTime,
                              DumpCombineDateTime, DumpSum)


class MySQLFormatName(FormatName):

    def __call__(self):
        self.stream.write(u"`%s`" % self.value.replace(u"`", u"``"))


class MySQLFormatLiteral(FormatLiteral):

    def __call__(self):
        self.stream.write(u"'%s'" % self.value.replace(u"\\", ur"\\")
                                              .replace(u"'", ur"\'")
                                              .replace(u"\n", ur"\n")
                                              .replace(u"\r", ur"\r"))


class MySQLDumpFloat(DumpFloat):

    def __call__(self):
        assert str(self.value) not in ['inf', '-inf', 'nan']
        value = repr(self.value)
        if 'e' not in value and 'E' not in value:
            value = value+'e0'
        if value[0] == "-":
            value = "(%s)" % value
        self.write(unicode(value))


class MySQLDumpDecimal(DumpDecimal):

    def __call__(self):
        assert self.value.is_finite()
        value = str(self.value)
        if 'E' in value:
            value = "CAST(%s AS DECIMAL(65,30))" % value
        elif '.' not in value:
            value = "%s." % value
        if value[0] == "-":
            value = "(%s)" % value
        self.write(unicode(value))


class MySQLDumpDate(DumpDate):

    def __call__(self):
        self.format("DATE({value:literal})", value=unicode(self.value))


class MySQLDumpTime(DumpTime):

    def __call__(self):
        self.format("TIME({value:literal})", value=unicode(self.value))


class MySQLDumpDateTime(DumpDateTime):

    def __call__(self):
        # MySQLdb driver does not handle datetime values with microseconds.
        value = self.value.replace(microsecond=0, tzinfo=None)
        self.format("TIMESTAMP({value:literal})", value=unicode(value))


class MySQLDumpToInteger(DumpToInteger):

    def __call__(self):
        self.format("CAST({base} AS SIGNED INTEGER)", base=self.base)


class MySQLDumpToFloat(DumpToFloat):

    def __call__(self):
        if isinstance(self.base.domain, NumberDomain):
            self.format("(1E0 * {base})", base=self.base)
        else:
            self.format("(1E0 * CAST({base} AS DECIMAL(65,30)))",
                        base=self.base)


class MySQLDumpToDecimal(DumpToDecimal):

    def __call__(self):
        self.format("CAST({base} AS DECIMAL(65,30))", base=self.base)


class MySQLDumpToString(DumpToString):

    def __call__(self):
        self.format("CAST({base} AS CHAR)", base=self.base)


class MySQLDumpToDateTime(DumpToDateTime):

    def __call__(self):
        self.format("CAST({base} AS DATETIME)", base=self.base)


class MySQLDumpBooleanToString(DumpToDomain):

    adapts(BooleanDomain, StringDomain)

    def __call__(self):
        if self.base.is_nullable:
            self.format("(CASE WHEN {base} THEN 'true'"
                        " WHEN NOT {base} THEN 'false' END)",
                        base=self.base)
        else:
            self.format("(CASE WHEN {base} THEN 'true' ELSE 'false' END)",
                        base=self.base)


class MySQLDumpIsTotallyEqual(DumpIsTotallyEqual):

    def __call__(self):
        if self.signature.polarity == +1:
            self.format("({lop} <=> {rop})", self.arguments)
        if self.signature.polarity == -1:
            self.format("(NOT ({lop} <=> {rop}))", self.arguments)


class MySQLDumpTrunc(DumpTrunc):

    template = "TRUNCATE({op}, 0)"


class MySQLDumpTruncTo(DumpTruncTo):

    template = "TRUNCATE({op}, {precision})"


class MySQLDumpDateIncrement(DumpDateIncrement):

    template = "ADDDATE({lop}, {rop})"


class MySQLDumpDateTimeIncrement(DumpDateTimeIncrement):

    template = "ADDDATE({lop}, INTERVAL 86400 * {rop} SECOND)"


class MySQLDumpDateDecrement(DumpDateDecrement):

    template = "SUBDATE({lop}, {rop})"


class MySQLDumpDateTimeDecrement(DumpDateTimeDecrement):

    template = "SUBDATE({lop}, INTERVAL 86400 * {rop} SECOND)"


class MySQLDumpDateDifference(DumpDateDifference):

    template = "DATEDIFF({lop}, {rop})"


class MySQLDumpExtractSecond(DumpExtractSecond):

    template = "(1E0 * EXTRACT(SECOND FROM {op}))"


class MySQLDumpConcatenate(DumpConcatenate):

    template = "CONCAT({lop}, {rop})"


class MySQLDumpLike(DumpLike):

    def __call__(self):
        self.format("({lop} {polarity:not}LIKE {rop})",
                    self.arguments, self.signature)


class MySQLDumpMakeDate(DumpMakeDate):

    template = ("ADDDATE(ADDDATE(ADDDATE(DATE('2001-01-01'),"
                " INTERVAL ({year} - 2001) YEAR),"
                " INTERVAL ({month} - 1) MONTH),"
                " INTERVAL ({day} - 1) DAY)")


class MySQLDumpMakeDateTime(DumpMakeDateTime):

    def __call__(self):
        template = ("ADDDATE(ADDDATE(ADDDATE(TIMESTAMP('2001-01-01'),"
                    " INTERVAL ({year} - 2001) YEAR),"
                    " INTERVAL ({month} - 1) MONTH),"
                    " INTERVAL ({day} - 1) DAY)")
        if self.phrase.hour is not None:
            template = "ADDDATE(%s, INTERVAL {hour} HOUR)" % template
        if self.phrase.minute is not None:
            template = "ADDDATE(%s, INTERVAL {minute} MINUTE)" % template
        if self.phrase.second is not None:
            template = "ADDDATE(%s, INTERVAL {second} SECOND)" % template
        self.format(template, self.arguments)


class MySQLDumpCombineDateTime(DumpCombineDateTime):

    template = "ADDTIME(TIMESTAMP({date}), {time})"


class MySQLDumpSum(DumpSum):

    def __call__(self):
        if isinstance(self.phrase.domain, IntegerDomain):
            self.format("CAST(SUM({op}) AS SIGNED INTEGER)", self.arguments)
        else:
            self.format("SUM({op})", self.arguments)


