import xml.etree.ElementTree as ET
from urllib.request import urlopen

ns = {"q": "http://quakeml.org/xmlns/bed/1.2"}


def get_xitem_as_text(item, key):
    anItem = item.find(key, ns)
    if (anItem != None):
        return anItem.text
    else:
        return 'None'

def get_xitem_value_as_text(item, key, valuekey):
    anItem = item.find(key, ns)
    if (anItem == None):
        return 'None'
    else:
        value = anItem.find(valuekey, ns)
        if (value != None):
            return value.text
        else:
            return 'None'


def parse_event(xevent):
    ev = {}
    ev["publicID"] = xevent.attrib["publicID"]
    ev["preferredOriginID"] = xevent.find("q:preferredOriginID", ns).text
    ev["type"] = xevent.find("q:type", ns).text
    return ev


def parse_origin(xevent):
    xorigin = xevent.findall('q:origin', ns)[0]

    origin = xorigin.attrib.copy()
    origin.update({'dataid': origin['{http://anss.org/xmlns/catalog/0.1}dataid']})
    origin.update({'datasource': origin['{http://anss.org/xmlns/catalog/0.1}datasource']})
    origin.update({'time': get_xitem_value_as_text(xorigin, 'q:time', 'q:value')})

    origin.update({'timeUncertainty': get_xitem_value_as_text(xorigin, 'q:time', 'q:uncertainty')})
    value = get_xitem_as_text(xorigin, 'q:evaluationMode')
    if (value != 'NA'):
        origin.update({"evaluationMode": value})
    origin.update({'latitude': get_xitem_value_as_text(xorigin, 'q:latitude', 'q:value')})
    origin.update({'longitude': get_xitem_value_as_text(xorigin, 'q:longitude', 'q:value')})
    origin.update({'depth': get_xitem_value_as_text(xorigin, 'q:depth', 'q:value')})
    origin.update({'depthError': get_xitem_value_as_text(xorigin, 'q:depth', 'q:uncertainty')})
    origin.update({'usedPhaseCount': get_xitem_value_as_text(xorigin, 'q:quality', 'q:usedPhaseCount')})
    origin.update({'usedStationCount': get_xitem_value_as_text(xorigin, 'q:quality', 'q:usedStationCount')})
    origin.update({'standardError': get_xitem_value_as_text(xorigin, 'q:quality', 'q:standardError')})
    origin.update({'azimuthalGap': get_xitem_value_as_text(xorigin, 'q:quality', 'q:azimuthalGap')})
    origin.update({'minimumDistance': get_xitem_value_as_text(xorigin, 'q:quality', 'q:minimumDistance')})

    origin.update({'creationInfo': get_xitem_value_as_text(xorigin, 'q:creationInfo', 'q:author')})

    origin.update(
        {'horizontalUncertainty': get_xitem_value_as_text(xorigin, 'q:originUncertainty', 'q:horizontalUncertainty')})
# print(origin)
    return origin


def parse_magnitudes(xevent):
    xmags = xevent.findall('q:magnitude', ns)
    # print(xmags)
    mags_default = [{'{http://anss.org/xmlns/catalog/0.1}datasource': 'us', '{http://anss.org/xmlns/catalog/0.1}dataid': 'N/A', '{http://anss.org/xmlns/catalog/0.1}eventsource': 'iscgem', '{http://anss.org/xmlns/catalog/0.1}eventid': 'N/A', 'publicID': 'N/A', 'mag': 'None', 'magError': 'None', 'magType': 'None', 'stationCount': 'None', 'originID': 'N/A', 'creationTime': 'N/A'}]

    mags = []
    for xmag in xmags:
        mdict = xmag.attrib.copy()
        mdict.update({'mag': get_xitem_value_as_text(xmag, 'q:mag', 'q:value')})
        mdict.update({'magError': get_xitem_value_as_text(xmag, 'q:mag', 'q:uncertainty')})
        mdict.update({'magType': get_xitem_as_text(xmag, 'q:type')})
        value = get_xitem_as_text(xmag, 'q:stationCount')
        if (value != 'NA'):
            mdict.update({"stationCount": value})

        value = get_xitem_as_text(xmag, 'q:originID')
        if (value != 'NA'):
            mdict.update({"originID": value})

        mdict.update({'creationTime': get_xitem_value_as_text(xmag, 'q:creationInfo', 'q:creationTime')})
        # if (value != 'NA'):
        #     mdict.update({"creationTime": value})

        # value = get_xitem_as_text(xmag, 'q:phaseCount')
        # if (value != 'NA'):
        #     mdict.update({"phaseCount": value})

        mags.append(mdict)

    # print(mags)
    if mags == []:
        return mags_default
    else:
        return mags

def convert_earthquakeType(type):
    if type == "earthquake":
        return "V"
    else:
        return "E"


def convert_time(time):
    return time[:10] + " " + time[11:19]

def convert_time_Csec(time):
    return "0" + time[19:22]

def evaluation_mode(mode):
    # print(mode)
    if mode == 'manual':
        return 'H'
    else:
        return 'A'

def convert_time_pubdate(time):
    month = time[5:7]
    day = time[8:10]
    if month == "01" and day =='31':
        return time[:5] + "02-01 00:00:00"
    elif month == "03" and day =='31':
        return time[:5] + "04-01 00:00:00"
    elif month == "05" and day =='31':
        return time[:5] + "06-01 00:00:00"
    elif month == "07" and day =='31':
        return time[:5] + "08-01 00:00:00"
    elif month == "08" and day =='31':
        return time[:5] + "09-01 00:00:00"
    elif month == "10" and day =='31':
        return time[:5] + "11-01 00:00:00"
    elif month == "12" and day =='31':
        return str(int(time[:4])+1) + "-01-01 00:00:00"
    elif month == "04" and day =='30':
        return time[:5] + "05-01 00:00:00"
    elif month == "06" and day =='30':
        return time[:5] + "07-01 00:00:00"
    elif month == "09" and day =='30':
        return time[:5] + "10-01 00:00:00"
    elif month == "11" and day =='30':
        return time[:5] + "12-01 00:00:00"
    else:
        return time[:8] + str(int(time[8:10])+1) + " 00:00:00"

def convert_network_code(time, datasource):
    return "ANSS_" + datasource + "_" + time[:4] + time[5:7]+ time[8:10] + time[11:13] + time[14:16] + time[17:19] + time[20:22]

def convert_depth(depth):
    if depth == 'None':
        return '0'
    else:
        return str(float(depth) / 1000)

def convert_depthErr(depth):
    if depth == 'None':
        return '0'
    else:
        return str(float(depth) / 1000)

def convert_magError(error):
    if error == 'None':
        return '0'
    else:
        return "%.5f" %float(error)

def parse_xml(filepath):
    xtree = ET.parse(filepath)
    xroot = xtree.getroot()

    xeventParameters = xroot.findall('q:eventParameters', ns)


    for ep in xeventParameters:
        xevents = ep.findall('q:event', ns)
        print("Found " + str(len(xevents)) + " events.")

    events = []

    # i = 0

    for xev in xevents:
        ev = parse_event(xev)
        origin = parse_origin(xev)
        # focal = parse_focalparse_focal_mechanism(xev)
        mags = parse_magnitudes(xev)
        # info = parse_creationInfo(xev)

        events.append({'eventInfo': ev, 'origin': origin, 'mags': mags})

    # print(events)
    return events


def convert_to_WOVOdat_format(events):
    wovoml = ET.Element('wovoml')
    wovoml.attrib = {'xmlns': "http://www.wovodat.org", 'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                     'version': "1.1.0", 'xsi:schemaLocation': "http://www.wovodat.org/WOVOdatV1.xsd", 'pubDate': "2008-01-01 00:00:00"}
    data = ET.SubElement(wovoml, 'Data')
    seismic = ET.SubElement(data, 'Seismic')
    networkEventDataset = ET.SubElement(seismic, 'NetworkEventDataset')


    for event in events:
        root = ET.Element('root') #where is root?
        networkEventDataset.extend(root)
        networkEvent = ET.SubElement(networkEventDataset, 'NetworkEvent')
        seismoArchive = ET.SubElement(networkEvent, 'seismoArchive')
        originTime = ET.SubElement(networkEvent, 'originTime')
        originTimeCsec = ET.SubElement(networkEvent, 'originTimeCsec')
        picksDetermination = ET.SubElement(networkEvent, 'picksDetermination')
        # locaTechnique = ET.SubElement(networkEvent, 'locaTechnique')
        if (event['origin']['latitude'] != 'None'):
            lat = ET.SubElement(networkEvent, 'lat')
        if (event['origin']['longitude'] != 'None'):
            lon = ET.SubElement(networkEvent, 'lon')
        if (event['origin']['depth'] != 'None'):
            depth = ET.SubElement(networkEvent, 'depth')
        # fixedDepth = ET.SubElement(networkEvent, 'fixedDepth')
        if (event['origin']['usedStationCount'] != 'None'):
            numberOfStations = ET.SubElement(networkEvent, 'numberOfStations')
        if (event['origin']['usedPhaseCount'] != 'None'):
            numberOfPhases = ET.SubElement(networkEvent, 'numberOfPhases')
        if (event['origin']['azimuthalGap'] != 'None'):
            largestAzimuthGap = ET.SubElement(networkEvent, 'largestAzimuthGap')
        if (event['origin']['minimumDistance'] != 'None'):
            distClosestStation = ET.SubElement(networkEvent, 'distClosestStation')
        if (event['origin']['standardError'] != 'None'):
            travelTimeRMS = ET.SubElement(networkEvent, 'travelTimeRMS')
        if (event['origin']['horizontalUncertainty'] != 'None'):
            horizLocaErr = ET.SubElement(networkEvent, 'horizLocaErr')
        # maxLonErr = ET.SubElement(networkEvent, 'maxLonErr')
        # maxLatErr = ET.SubElement(networkEvent, 'maxLatErr')
        if (event['origin']['depthError'] != 'None'):
            depthErr = ET.SubElement(networkEvent, 'depthErr')
        if (event['mags'][0]['mag'] != 'None'):
            if (event['mags'][0]['mag'] != 'N/A'):
                primMagnitude = ET.SubElement(networkEvent, 'primMagnitude')
        if (event['mags'][0]['magType'] != 'None'):
            if (event['mags'][0]['magType'] != 'N/A'):
                primMagnitudeType = ET.SubElement(networkEvent, 'primMagnitudeType')
        # secMagnitude = ET.SubElement(networkEvent, 'secMagnitude')
        # secMagnitudeType = ET.SubElement(networkEvent, 'secMagnitudeType')
        earthquakeType = ET.SubElement(networkEvent, 'earthquakeType')
        orgDigitize = ET.SubElement(networkEvent, 'orgDigitize')
        comments = ET.SubElement(networkEvent, 'comments')


        seismoArchive.text = 'ANSS'
        originTime.text = convert_time(event['origin']['time'])
        originTimeCsec.text = convert_time_Csec(event['origin']['time'])
        picksDetermination.text = evaluation_mode(event['origin']['evaluationMode'])
        if (event['origin']['latitude'] != 'None'):
            lat.text = "%.5f" %float(event['origin']['latitude'])
        if (event['origin']['longitude'] != 'None'):
            lon.text = "%.5f" %float(event['origin']['longitude'])
        if (event['origin']['depth'] != 'None'):
            depth.text = convert_depth(event['origin']['depth'])
        if (event['origin']['usedStationCount'] != 'None'):
            numberOfStations.text = event['origin']['usedStationCount']
        if (event['origin']['usedPhaseCount'] != 'None'):
            numberOfPhases.text = event['origin']['usedPhaseCount']
        if (event['origin']['azimuthalGap'] != 'None'):
            largestAzimuthGap.text= event['origin']['azimuthalGap']
        if (event['origin']['minimumDistance'] != 'None'):
            distClosestStation.text = event['origin']['minimumDistance']
        if (event['origin']['standardError'] != 'None'):
            travelTimeRMS.text = event['origin']['standardError']
        if (event['origin']['horizontalUncertainty'] != 'None'):
            horizLocaErr.text = str(float(event['origin']['horizontalUncertainty'])/1000)
        if (event['origin']['depthError'] != 'None'):
            depthErr.text = convert_depthErr(event['origin']['depthError'])
        if (event['mags'][0]['mag'] != 'None'):
            if (event['mags'][0]['mag'] != 'N/A'):
                primMagnitude.text = event['mags'][0]['mag']
        if (event['mags'][0]['magType'] != 'None'):
            if (event['mags'][0]['magType'] != 'N/A'):
                primMagnitudeType.text = event['mags'][0]['magType']
        earthquakeType.text = convert_earthquakeType(event['eventInfo']['type'])
        orgDigitize.text = 'O'
        comments.text = "datasource=" + event['origin']['datasource'] + '; dataid=' + event['origin']['dataid'] + "; updated=" + event['mags'][0][
                            'creationTime'] + "; MagError=" + convert_magError(event['mags'][0]['magError'])

        networkEventDataset.attrib = {'netwok': 'ANSS_US_regional_seisnet', 'owner1': 'ANSS', 'owner2': 'USGS',
                                      'owner3': 'PNSN',
                                      'pubDate': convert_time_pubdate(event['origin']['time'])}
        networkEvent.attrib = {'network': 'ANSS_US_regional_seisnet', 'owner1': 'ANSS', 'owner2': 'USGS',
                               'owner3': 'PNSN',
                               'pubDate': convert_time_pubdate(event['origin']['time']),
                               'code': convert_network_code(event['origin']['time'], event['origin']['datasource'] )}
    tree = ET.ElementTree(wovoml)

    return tree
    #tree.write("Event 2002_1stQuarter.xml", encoding='utf-8')
print("Download Started!")
cur_year = 2005
end_year = 2005
ET.register_namespace("", "http://quakeml.org/xmlns/quakeml/bed/1.2")
while cur_year <= end_year:
    url = urlopen(
        'https://earthquake.usgs.gov/fdsnws/event/1/query?format=quakeml&minlatitude=38&minlongitude=-128.7&maxlatitude=38.5&maxlongitude=-104.84&eventtype=earthquake&endtime=' + str(
            cur_year) + '-03-01&starttime=' + str(cur_year) + '-01-01')
    try:
        ori_tree = ET.parse(url)

        root = ori_tree.getroot()
        filename = 'C:\\Users\\hungd\\output\\' + str(
            cur_year) + '_Jan_data.xml'
        ori_tree.write(filename)
        events = parse_xml(filename)

        chunks = [events[x:x + 1000] for x in range(0, len(events), 1000)]
        # print(len(chunks))
        for i in range(len(chunks)):
            tree = convert_to_WOVOdat_format(chunks[i])
            converted_file = 'Event ' + 'test.xml'
            tree.write(converted_file, encoding='utf-8')
            print("Write successful!")
    except:
        pass
    cur_year += 1
print("Download Done!")

# try:


# events = parse_xml("C:\\Users\\hungdp1999\\PycharmProjects\\Convert_xml\\Before_convert_2.xml")
# # print(events)
# convert_to_WOVOdat_format(events)


# start_year = 2018
# end_year = 2020
# cur_year = start_year
# ET.register_namespace("", "http://quakeml.org/xmlns/quakeml/bed/1.2")
#
# print("Download Started!")
# while cur_year < end_year:
#     url = urlopen(
#         'https://earthquake.usgs.gov/fdsnws/event/1/query?format=quakeml&minlatitude=42&minlongitude=-123.5&maxlatitude=49.7&maxlongitude=-119.5&eventtype=earthquake&endtime=' + str(cur_year+1) '-01-01&starttime=' str(cur_year) +'-01-01')
#     try:
#         ori_tree = ET.parse(url)
#         root = ori_tree.getroot()
#         filename = 'C:\\Users\\hungdp1999\\PycharmProjects\\Convert_xml\\output\\downloaded_' + cur_year '_data.xml'
#
#         ori_tree.write(filename)
#         events = parse_xml(filename)
#         tree = convert_to_WOVOdat_format(events)
#         converted_file = 'Event ' + cur_year + '.xml'
#         tree.write(converted_file, encoding='utf-8')
#     except:
#         pass
#
#     cur_year += 1
#
# print("Download Done!")
#


# def parse_creationInfo(xevent):
#     # xorigin = xevent.findall('q:origin', ns)[0]
#     # origin = xorigin.attrib.copy()
#     #
#     # origin.update({'time': get_xitem_value_as_text(xorigin, 'q:time', 'q:value')})
#     # origin.update({'timeUncertainty': get_xitem_value_as_text(xorigin, 'q:time', 'q:uncertainty')})
#
#     xinfo = xevent.findall('q:creationInfo', ns)[0]
#     info = xinfo.attrib.copy()
#     info.update({'agencyID': get_xitem_value_as_text(xinfo, 'q:creationInfo', 'q:agencyID')})
#     info.update({'creationTime': get_xitem_value_as_text(xinfo, 'q:creationInfo', 'q:creationTime')})
#     # infos = []
#     # for xinfo in xinfos:
#     #     info_dict = xinfos.attrib.copy()
#     #     info_dict.update({'agencyID': get_xitem_value_as_text(xmag, 'q:creationInfo', 'q:agencyID')})
#     #     info_dict.update({'creationTime': get_xitem_value_as_text(xmag, 'q:creationInfo', 'q:creationTime')})
#
#     return info