#
# Copyright (c) 2006-2011, Prometheus Research, LLC
# See `LICENSE` for license information, `AUTHORS` for the list of authors.
#


"""
:mod:`htsql.tr.fn.dump`
=======================
"""


from ...adapter import adapts, adapts_none
from ..dump import DumpBySignature
from .signature import (AddSig, ConcatenateSig, DateIncrementSig,
                        DateTimeIncrementSig, SubtractSig, DateDecrementSig,
                        DateTimeDecrementSig, DateDifferenceSig,
                        MultiplySig, DivideSig, IfSig, SwitchSig,
                        ReversePolaritySig, RoundSig, RoundToSig, TruncSig,
                        TruncToSig, LengthSig, LikeSig, ReplaceSig,
                        SubstringSig, UpperSig, LowerSig, TrimSig, TodaySig,
                        NowSig, MakeDateSig, MakeDateTimeSig,
                        CombineDateTimeSig, ExtractYearSig, ExtractMonthSig,
                        ExtractDaySig, ExtractHourSig, ExtractMinuteSig,
                        ExtractSecondSig, ExistsSig, CountSig, MinMaxSig,
                        SumSig, AvgSig)


class DumpFunction(DumpBySignature):

    adapts_none()
    template = None

    def __call__(self):
        if self.template is None:
            super(DumpFunction, self).__call__()
        else:
            self.format(self.template, self.arguments, self.signature)


class DumpAdd(DumpFunction):

    adapts(AddSig)
    template = "({lop} + {rop})"


class DumpSubtract(DumpFunction):

    adapts(SubtractSig)
    template = "({lop} - {rop})"


class DumpMultiply(DumpFunction):

    adapts(MultiplySig)
    template = "({lop} * {rop})"


class DumpDivide(DumpFunction):

    adapts(DivideSig)
    template = "({lop} / {rop})"


class DumpDateIncrement(DumpFunction):

    adapts(DateIncrementSig)
    template = "CAST({lop} + {rop} * INTERVAL '1' DAY AS DATE)"


class DumpDateTimeIncrement(DumpFunction):

    adapts(DateTimeIncrementSig)
    template = "({lop} + {rop} * INTERVAL '1' DAY)"


class DumpDateDecrement(DumpFunction):

    adapts(DateDecrementSig)
    template = "CAST({lop} - {rop} * INTERVAL '1' DAY AS DATE)"


class DumpDateTimeDecrement(DumpFunction):

    adapts(DateTimeDecrementSig)
    template = "({lop} - {rop} * INTERVAL '1' DAY)"


class DumpDateDifference(DumpFunction):

    adapts(DateDifferenceSig)
    template = "EXTRACT(DAY FROM {lop} - {rop})"


class DumpConcatenate(DumpFunction):

    adapts(ConcatenateSig)
    template = "({lop} || {rop})"


class DumpIf(DumpFunction):

    adapts(IfSig)

    def __call__(self):
        self.format("(CASE")
        for predicate, consequent in zip(self.phrase.predicates,
                                         self.phrase.consequents):
            self.format(" WHEN {predicate} THEN {consequent}",
                        predicate=predicate, consequent=consequent)
        if self.phrase.alternative is not None:
            self.format(" ELSE {alternative}",
                        alternative=self.phrase.alternative)
        self.format(" END)")


class DumpSwitch(DumpFunction):

    adapts(SwitchSig)

    def __call__(self):
        self.format("(CASE {variable}",
                    variable=self.phrase.variable)
        for variant, consequent in zip(self.phrase.variants,
                                       self.phrase.consequents):
            self.format(" WHEN {variant} THEN {consequent}",
                        variant=variant, consequent=consequent)
        if self.phrase.alternative is not None:
            self.format(" ELSE {alternative}",
                        alternative=self.phrase.alternative)
        self.format(" END)")


class DumpReversePolarity(DumpFunction):

    adapts(ReversePolaritySig)
    template = "(- {op})"


class DumpRound(DumpFunction):

    adapts(RoundSig)
    template = "ROUND({op})"


class DumpRoundTo(DumpFunction):

    adapts(RoundToSig)
    template = "ROUND({op}, {precision})"


class DumpTrunc(DumpFunction):

    adapts(TruncSig)
    template = "TRUNC({op})"


class DumpTruncTo(DumpFunction):

    adapts(TruncToSig)
    template = "TRUNC({op}, {precision})"


class DumpLength(DumpFunction):

    adapts(LengthSig)
    template = "CHARACTER_LENGTH({op})"


class DumpLike(DumpFunction):

    adapts(LikeSig)

    def __call__(self):
        self.format("({lop} {polarity:not}LIKE {rop} ESCAPE {escape:literal})",
                    self.arguments, self.signature, escape="\\")


class DumpReplace(DumpFunction):

    adapts(ReplaceSig)
    template = "REPLACE({op}, {old}, {new})"


class DumpSubstring(DumpFunction):

    adapts(SubstringSig)

    def __call__(self):
        if self.phrase.length is not None:
            self.format("SUBSTRING({op} FROM {start} FOR {length})",
                        self.phrase)
        else:
            self.format("SUBSTRING({op} FROM {start})", self.arguments)


class DumpUpper(DumpFunction):

    adapts(UpperSig)
    template = "UPPER({op})"


class DumpLower(DumpFunction):

    adapts(LowerSig)
    template = "LOWER({op})"


class DumpTrim(DumpFunction):

    adapts(TrimSig)

    def __call__(self):
        if self.signature.is_left and not self.signature.is_right:
            self.format("TRIM(LEADING FROM {op})", self.arguments)
        elif not self.signature.is_left and self.signature.is_right:
            self.format("TRIM(TRAILING FROM {op})", self.arguments)
        else:
            self.format("TRIM({op})", self.arguments)


class DumpToday(DumpFunction):

    adapts(TodaySig)
    template = "CURRENT_DATE"


class DumpNow(DumpFunction):

    adapts(NowSig)
    template = "LOCALTIMESTAMP"


class DumpMakeDate(DumpFunction):

    adapts(MakeDateSig)
    template = ("CAST(DATE '2001-01-01' + ({year} - 2001) * INTERVAL '1' YEAR"
                " + ({month} - 1) * INTERVAL '1' MONTH"
                " + ({day} - 1) * INTERVAL '1' DAY AS DATE)")


class DumpMakeDateTime(DumpFunction):

    adapts(MakeDateTimeSig)

    def __call__(self):
        template = ("(TIMESTAMP '2001-01-01 00:00:00'"
                    " + ({year} - 2001) * INTERVAL '1' YEAR"
                    " + ({month} - 1) * INTERVAL '1' MONTH"
                    " + ({day} - 1) * INTERVAL '1' DAY")
        if self.phrase.hour is not None:
            template += " + {hour} * INTERVAL '1' HOUR"
        if self.phrase.minute is not None:
            template += " + {minute} * INTERVAL '1' MINUTE"
        if self.phrase.second is not None:
            template += " + {second} * INTERVAL '1' SECOND"
        template += ")"
        self.format(template, self.arguments)


class DumpCombineDateTime(DumpFunction):

    adapts(CombineDateTimeSig)
    template = "({date} + {time})"


class DumpExtractYear(DumpFunction):

    adapts(ExtractYearSig)
    template = "EXTRACT(YEAR FROM {op})"


class DumpExtractMonth(DumpFunction):

    adapts(ExtractMonthSig)
    template = "EXTRACT(MONTH FROM {op})"


class DumpExtractDay(DumpFunction):

    adapts(ExtractDaySig)
    template = "EXTRACT(DAY FROM {op})"


class DumpExtractHour(DumpFunction):

    adapts(ExtractHourSig)
    template = "EXTRACT(HOUR FROM {op})"


class DumpExtractMinute(DumpFunction):

    adapts(ExtractMinuteSig)
    template = "EXTRACT(MINUTE FROM {op})"


class DumpExtractSecond(DumpFunction):

    adapts(ExtractSecondSig)
    template = "EXTRACT(SECOND FROM {op})"


class DumpExists(DumpFunction):

    adapts(ExistsSig)
    template = "EXISTS{op}"


class DumpCount(DumpFunction):

    adapts(CountSig)
    template = "COUNT({op})"


class DumpMinMax(DumpFunction):

    adapts(MinMaxSig)

    def __call__(self):
        if self.signature.polarity > 0:
            self.format("MIN({op})", self.arguments)
        else:
            self.format("MAX({op})", self.arguments)


class DumpSum(DumpFunction):

    adapts(SumSig)
    template = "SUM({op})"


class DumpAvg(DumpFunction):

    adapts(AvgSig)
    template = "AVG({op})"


