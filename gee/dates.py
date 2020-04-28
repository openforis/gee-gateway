import ee

ORIGIN = 1721423

MS_TO_DAYS = 86400000

EPOCH_DAYS = ee.Number(719163)


def msToDays(ms):
    return ee.Number(ms).divide(MS_TO_DAYS)


def dateToJdays(str_date):
    if (str_date is None):
        return ('Required parameter [str_date] missing')
    date = ee.Date(str_date)
    return msToDays(date.millis()).add(EPOCH_DAYS)


def jdaysToms(jdays):
    daysSinceEpoch = ee.Number(jdays).subtract(EPOCH_DAYS)
    return daysSinceEpoch.multiply(MS_TO_DAYS)


def jdaysToDate(jdays):
    return ee.Date(jdaysToms(jdays))


def msToJdays(ms):
    return ee.Number(msToDays(ms)).add(EPOCH_DAYS)


def msToFrac(ms):
    year = (ee.Date(ms).get('year'))
    frac = (ee.Date(ms).getFraction('year'))
    return year.add(frac)


def fracToms(frac):
    fyear = ee.Number(frac)
    year = fyear.floor()
    d = fyear.subtract(year).multiply(365)
    day_one = ee.Date.fromYMD(year, 1, 1)
    return day_one.advance(d, 'day').millis()


def fracToDate(frac):
    ms = fracToms(frac)
    return msToDate(ms)


def msToDate(ms):
    return jdaysToDate(msToJdays(ms))


def convertDate(options):
    if options is None:
        return ('Required parameter [options] missing')
    print(options)
    if 'inputFormat' in options:
        inputFormat = options['inputFormat']
    else:
        inputFormat = 0
    if options['inputDate'] is None:
        inputDate = {}
    else:
        inputDate = options['inputDate']
    if options['outputFormat'] is None:
        outputFormat = 0
    else:
        outputFormat = options['outputFormat']
    if inputDate is None:
        return ('Required parameter [inputDate] missing')
    if inputFormat == 0:
        milli = jdaysToms(inputDate)
    elif inputFormat == 1:
        milli = fracToms(inputDate)
    elif inputFormat == 2:
        milli = inputDate
    elif inputFormat == 3:
        milli = jdaysToms(dateToJdays(inputDate))
    if outputFormat == 0:
        output = msToJdays(milli)
    elif outputFormat == 1:
        output = msToFrac(milli)
    elif outputFormat == 2:
        output = milli
    elif outputFormat == 4:
        output = jdaysToDate(msToJdays(milli))
    return output


exports = {
    msToDays: msToDays,
    dateToJdays: dateToJdays,
    jdaysToms: jdaysToms,
    jdaysToDate: jdaysToDate,
    msToJdays: msToJdays,
    msToFrac: msToFrac,
    msToDate: msToDate,
    fracToms: fracToms,
    convertDate: convertDate
}
# need to use .getInof() to get the actual string, maybe add to the functions if needed
# print(convertDate({inputFormat: 3, inputDate: '2019-10-01', outputFormat: 2}))

# print(msToDays(86400000)) # 86400000
#ms = 1
#day \
    # print(dateToJdays('0001-01-01')) # 1 \
# print(dateToJdays('2019-10-01')) # 737333 \
# print(jdaysToms(737333)) # 1569888000000 \
# print(ee.Date(1569888000000)) # 2019 - 10 - 01 \
# print(jdaysToDate(737333)) # 2019 - 10 - 01 \
# print(msToJdays(1569888000000)) # 737333 \
# print(msToFrac(1569888000000)) # 2019.7479452054795 \
# print(fracToms(2019.7479452054795)) # 1569888000000 \
# print(ee.Date(1569888000000)) # 2019 - 10 - 01 \
# 737333, 2019.7479452054795, 1569888000000 \
# print(fracToDate(2019.7479452054795))
