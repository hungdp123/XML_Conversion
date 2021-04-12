import re
import xml.etree.ElementTree as ET
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from urllib.request import urlopen

# Access ISC website and get the data
import xml.etree.ElementTree as ET
import math
from datetime import datetime
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ns = {"q": "http://quakeml.org/xmlns/quakeml/1.2"}


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
    ev["preferredOriginID"] = get_xitem_as_text(xevent, "q:preferredOriginID")
    ev["type"] = get_xitem_as_text(xevent, "q:type")
    ev["typeCertainty"] = get_xitem_as_text(xevent, "q:typeCertainty")
    ev['description'] = {
        get_xitem_value_as_text(xevent, 'q:description', 'q:type'): get_xitem_value_as_text(xevent, 'q:description',
                                                                                            'q:text')}

    #print(ev)
    return ev


def parse_origin(xevent):
    xorigin = xevent.findall('q:origin', ns)[0]
    origin = xorigin.attrib.copy()

    origin.update({'time': get_xitem_value_as_text(xorigin, 'q:time', 'q:value')})
    origin.update({'timeUncertainty': get_xitem_value_as_text(xorigin, 'q:time', 'q:uncertainty')})
    origin.update({'latitude': get_xitem_value_as_text(xorigin, 'q:latitude', 'q:value')})
    origin.update({'longitude': get_xitem_value_as_text(xorigin, 'q:longitude', 'q:value')})
    origin.update({'depth': get_xitem_value_as_text(xorigin, 'q:depth', 'q:value')})
    origin.update({'depthType': get_xitem_as_text(xorigin, 'q:depthType')})
    origin.update({'usedPhaseCount': get_xitem_value_as_text(xorigin, 'q:quality', 'q:usedPhaseCount')})
    origin.update({'usedStationCount': get_xitem_value_as_text(xorigin, 'q:quality', 'q:associatedStationCount')})
    origin.update({'standardError': get_xitem_value_as_text(xorigin, 'q:quality', 'q:standardError')})
    origin.update({'azimuthalGap': get_xitem_value_as_text(xorigin, 'q:quality', 'q:azimuthalGap')})
    origin.update({'minimumDistance': get_xitem_value_as_text(xorigin, 'q:quality', 'q:minimumDistance')})

    origin.update({'creationInfo': get_xitem_value_as_text(xorigin, 'q:creationInfo', 'q:author')})

    origin.update(
        {'horizontalUncertainty': get_xitem_value_as_text(xorigin, 'q:originUncertainty', 'q:horizontalUncertainty')})

    #print(origin)
    return origin


def parse_focal_mechanism(xevent):
    focal = {}
    #focal_def = {}
    if len(xevent.findall('q:focalMechanism', ns)) > 0:
        xfocal = xevent.findall('q:focalMechanism', ns)[0]
        focal = xfocal.attrib.copy()
        if len(xevent.findall('q:nodalPlanes', ns)) > 0:
            xnodalplane = xfocal.findall('q:nodalPlanes', ns)[0]
            if len(xevent.findall('q:nodalPlane1', ns)) > 0:
                xnodalplane1 = xnodalplane.findall('q:nodalPlane1', ns)[0]
                focal.update({'strike1': get_xitem_value_as_text(xnodalplane1, 'q:strike', 'q:value')})
                focal.update({'dip1': get_xitem_value_as_text(xnodalplane1, 'q:dip', 'q:value')})
                focal.update({'rake1': get_xitem_value_as_text(xnodalplane1, 'q:rake', 'q:value')})
            if len(xevent.findall('q:nodalPlane2', ns)) > 0:
                xnodalplane2 = xnodalplane.findall('q:nodalPlane2', ns)[0]
                focal.update({'strike2': get_xitem_value_as_text(xnodalplane2, 'q:strike', 'q:value')})
                focal.update({'dip2': get_xitem_value_as_text(xnodalplane2, 'q:dip', 'q:value')})
                focal.update({'rake2': get_xitem_value_as_text(xnodalplane2, 'q:rake', 'q:value')})
        focal.update({'author': get_xitem_value_as_text(xfocal, 'q:creationInfo', 'q:author')})
    return focal

    # else:
    #     return focal_def
    #print(focal)


def parse_magnitudes(xevent):
    # print(xevent)
    xmags = xevent.findall('q:magnitude', ns)
    # print(xmags)
    mags_default = [{'publicID': 'None', 'mag': 'None', 'magType': 'None', 'stationCount': 'None', 'originID': 'None', 'author': 'None'}]

    mags = []

    for xmag in xmags:
        mdict = xmag.attrib.copy()
        #print(mdict)
        mdict.update({'mag': get_xitem_value_as_text(xmag, 'q:mag', 'q:value')})
        mdict.update({'magType': get_xitem_as_text(xmag, 'q:type')})
        value = get_xitem_as_text(xmag, 'q:stationCount')
        if (value != 'NA'):
            mdict.update({"stationCount": value})

        value = get_xitem_as_text(xmag, 'q:originID')
        if (value != 'NA'):
            mdict.update({"originID": value})

        value = get_xitem_value_as_text(xmag, 'q:creationInfo', 'q:author')
        if (value != 'NA'):
            mdict.update({"author": value})

        mags.append(mdict)
    if mags == []:
        return mags_default
    else:
        return mags


def parse_xml(filepath):
    xtree = ET.parse(filepath)
    xroot = xtree.getroot()

    xeventParameters = xroot.findall('q:eventParameters', ns)

    for ep in xeventParameters:
        xevents = ep.findall('q:event', ns)
        print("Found " + str(len(xevents)) + " events.")

    events = []

    for xev in xevents:
        ev = parse_event(xev)
        # print(ev)
        origin = parse_origin(xev)
        #print(origin)
        focal = parse_focal_mechanism(xev)
        #print(focal)
        mags = parse_magnitudes(xev)
        #print(mags)

        events.append({'eventInfo': ev, 'origin': origin, 'focalMechanism': focal, 'mags': mags})

    #print(events)
    return events


def get_author(origin, focal, mags):
    authorList = set()
    for mag in mags:
        if (mag['author'] != 'ISC' and mag['author'] != 'None'):
            authorList.add(mag['author'])
    if focal != {}:
        if (focal['author'] != 'ISC' and focal['author'] != 'None'):
            authorList.add(focal['author'])
    if (origin['creationInfo'] != 'ISC' and origin['creationInfo'] != 'None'):
        authorList.add(origin['creationInfo'])
    #print(authorList)
    return authorList


def get_comment(event, mags, focal, authorList):
    res = ""
    for key in event['description']:
        res += key + ': ' + event['description'][key] + ' '
    res += event['preferredOriginID']
    if mags != 'None':
        res += '; ' + mags
    if focal != {}:
        res += '; ' + focal['publicID']
    #count = 2
    # if authorList != '':
    #     for author in authorList:
    #         res += '; ' + 'owner' + str(count) +': ' + author
    #         count+=1
    if authorList != set():
        if len(authorList) ==1:
            for author in authorList:
                res += "; owner:" + author
        else:
            res += "; owners:"
            for author in authorList:
                res += author + "; "
    return res


def convert_time(time):
    return time[:10] + " " + time[11:19]

def convert_time_to_code(time):
    return time[:4] + time[5:7] + time[8:10] + time [11:13] + time[14:16] + time[17:19] + time[20:22]



def convert_timeCsec(time):
    if (isinstance(time, int)):
        return "0." + time[20:22]
    return "0.00"


# def convert_depth(depth):
#     if depth != 'None':
#         return str(float(depth) / 1000)
#     return 'None'


# def convert_azimuthGap(gap):
#     if gap != 'None':
#         return str(round(float(gap), 1))
#     return 'None'


def convert_distClosestStation(dist, lat):
    if dist != 'None' and lat != 'None':
        radLatitude = float(lat) * math.pi / 180
        return str(round(float(dist) * math.cos(radLatitude) * 111.321, 3))
    return 'None'


# def convert_horizLocaErr(err):
#     if err != 'None':
#         return str(float(err) / 1000)
#     return 'None'


def get_earthquake_type(typeE):
    if typeE == 'earthquake':
        return 'R'
    return 'None'


def check_rake(rake):
    if rake != '9999999999.00':
        return rake
    return 'None'

def convert_depthType(depthType):
    if depthType == 'operator assigned':
        return 'Y'
    return 'N'

def getID(publicID):
    numList = re.findall(r'[0-9]+', publicID)
    if numList != []:
        return numList[0];
    else:
        return "N/A"


def convert_to_WOVOdat_format(events):
    # if len(events) > 0:
    #     startDate = events[0]

    wovoml = ET.Element('wovoml')
    wovoml.attrib = {'xmlns': "http://www.wovodat.org", 'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                     'version': "1.1.0", 'xsi:schemaLocation': "http://www.wovodat.org/WOVOdatV1.xsd"}
    data = ET.SubElement(wovoml, 'Data')
    seismic = ET.SubElement(data, 'Seismic')
    networkEventDataset = ET.SubElement(seismic, 'NetworkEventDataset')

    for event in events:
        root = ET.Element('root')
        networkEvent = ET.SubElement(root, 'NetworkEvent')
        seismoArchive = ET.SubElement(networkEvent, 'seismoArchive')
        if (event['origin']['time'] != 'None'):
            originTime = ET.SubElement(networkEvent, 'originTime')
            originTimeCsec = ET.SubElement(networkEvent, 'originTimeCsec')
        if (event['origin']['timeUncertainty'] != 'None'):
            originTimeCsecUnc = ET.SubElement(networkEvent, 'originTimeCsecUnc')
        locaTechnique = ET.SubElement(networkEvent, 'locaTechnique')
        if (event['origin']['latitude'] != 'None'):
            lat = ET.SubElement(networkEvent, 'lat')
        if (event['origin']['longitude'] != 'None'):
            lon = ET.SubElement(networkEvent, 'lon')
        if (event['origin']['depth'] != 'None'):
            depth = ET.SubElement(networkEvent, 'depth')
        fixedDepth = ET.SubElement(networkEvent, 'fixedDepth')
        if (event['origin']['usedStationCount'] != 'None'):
            numberOfStations = ET.SubElement(networkEvent, 'numberOfStations')
        if (event['origin']['usedPhaseCount'] != 'None'):
            numberOfPhases = ET.SubElement(networkEvent, 'numberOfPhases')
        if (event['origin']['azimuthalGap'] != 'None'):
            largestAzimuthGap = ET.SubElement(networkEvent, 'largestAzimuthGap')
        if (event['origin']['minimumDistance'] != 'None' and event['origin']['latitude'] != 'None'):
            distClosestStation = ET.SubElement(networkEvent, 'distClosestStation')
        if (event['origin']['standardError'] != 'None'):
            travelTimeRMS = ET.SubElement(networkEvent, 'travelTimeRMS')
        if (event['origin']['horizontalUncertainty'] != 'None'):
            horizLocaErr = ET.SubElement(networkEvent, 'horizLocaErr')
        # maxLonErr = ET.SubElement(networkEvent, 'maxLonErr')
        # maxLatErr = ET.SubElement(networkEvent, 'maxLatErr')
        # depthErr = ET.SubElement(networkEvent, 'depthErr')
        locaQuality = ET.SubElement(networkEvent, 'locaQuality')
        if (event['mags'][0]['mag'] != 'None'):
            if (event['mags'][0]['mag'] != 'N/A'):
                primMagnitude = ET.SubElement(networkEvent, 'primMagnitude')
        if (event['mags'][0]['magType'] != 'None'):
            if (event['mags'][0]['magType'] != 'N/A'):
                primMagnitudeType = ET.SubElement(networkEvent, 'primMagnitudeType')
        if len(event['mags']) > 1:
            secMagnitude = ET.SubElement(networkEvent, 'secMagnitude')
            secMagnitudeType = ET.SubElement(networkEvent, 'secMagnitudeType')
        if (get_earthquake_type(event['eventInfo']['type']) != "None"):
            earthquakeType = ET.SubElement(networkEvent, 'earthquakeType')
        # momentTensorScale = ET.SubElement(networkEvent, 'momentTensorScale')
        # momentTensorXX = ET.SubElement(networkEvent, 'momentTensorXX')
        # momentTensorXY = ET.SubElement(networkEvent, 'momentTensorXY')
        # momentTensorXZ = ET.SubElement(networkEvent, 'momentTensorXZ')
        # momentTensorYY = ET.SubElement(networkEvent, 'momentTensorYY')
        # momentTensorYZ = ET.SubElement(networkEvent, 'momentTensorYZ')
        # momentTensorZZ = ET.SubElement(networkEvent, 'momentTensorZZ')

        if event['focalMechanism'] != {}:
            if (event['focalMechanism'].get('strike1') != None):
                strike1 = ET.SubElement(networkEvent, 'strike1')
            if (event['focalMechanism'].get('dip1') != None):
                dip1 = ET.SubElement(networkEvent, 'dip1')
            if (event['focalMechanism'].get('rake1') != None):
                if (check_rake(event['focalMechanism'].get('rake1')) != "None"):
                    rake1 = ET.SubElement(networkEvent, 'rake1')
            if (event['focalMechanism'].get('strike2') != None):
                strike2 = ET.SubElement(networkEvent, 'strike2')
            if (event['focalMechanism'].get('dip2') != None):
                dip2 = ET.SubElement(networkEvent, 'dip2')
            if (event['focalMechanism'].get('rake2') != None):
                if (check_rake(event['focalMechanism'].get('rake2')) != "None"):
                    rake2 = ET.SubElement(networkEvent, 'rake2')
        orgDigitize = ET.SubElement(networkEvent, 'orgDigitize')
        comments = ET.SubElement(networkEvent, 'comments')


        authorList = get_author(event['origin'], event['focalMechanism'], event['mags'])
        networkEvent.attrib = {'code': "ISC_" + getID(event['eventInfo']['publicID']) + "_" + convert_time_to_code(event['origin']['time']), 'network': "ISC_seisnet",
                               'owner1': 'ISC', 'pubDate': current_time}

        seismoArchive.text = 'ISC'
        if (event['origin']['time'] != "None"):
            originTime.text = convert_time(event['origin']['time'])
            originTimeCsec.text = convert_timeCsec(event['origin']['time'])
        if (event['origin']['timeUncertainty'] != "None"):
            originTimeCsecUnc.text = event['origin']['timeUncertainty']
        locaTechnique.text = 'Event reviewed by ISC analysts following procedure described in http://www.isc.ac.uk/iscbulletin/review/'
        if (event['origin']['latitude'] != "None"):
            lat.text = "%.5f" % float(event['origin']['latitude'])
        if (event['origin']['longitude'] != "None"):
            lon.text = "%.5f" % float(event['origin']['longitude'])
        if (event['origin']['depth'] != "None"):
            depth.text = str(float(event['origin']['depth']) / 1000)
        if (event['origin']['usedStationCount'] != "None"):
            numberOfStations.text = event['origin']['usedStationCount']
        if (event['origin']['usedPhaseCount'] != "None"):
            numberOfPhases.text = event['origin']['usedPhaseCount']
        if (event['origin']['azimuthalGap'] != "None"):
            largestAzimuthGap.text = event['origin']['azimuthalGap']
        if (event['origin']['minimumDistance'] != "None"):
            distClosestStation.text = convert_distClosestStation(event['origin']['minimumDistance'], event['origin']['latitude'])
        if (event['origin']['standardError'] != "None"):
            travelTimeRMS.text = event['origin']['standardError']
        if (event['origin']['horizontalUncertainty'] != "None"):
            horizLocaErr.text = str(float(event['origin']['horizontalUncertainty']) / 1000)
        locaQuality.text = 'ISC automatic programs to check for inconsistencies and errors ref: http://www.isc.ac.uk/iscbulletin/review/'
        if (event['mags'][0]['mag'] != "None" and event['mags'][0]['mag'] != 'N/A'):
            primMagnitude.text = event['mags'][0]['mag']
        if (event['mags'][0]['magType'] != "None" and event['mags'][0]['magType'] != 'N/A'):
            primMagnitudeType.text = event['mags'][0]['magType']
        if len(event['mags']) > 1:
            if (event['mags'][1]['mag'] != "None" and event['mags'][1]['mag'] != 'N/A'):
                secMagnitude.text = event['mags'][1]['mag']
            if (event['mags'][1]['magType'] != "None" and event['mags'][1]['magType'] != 'N/A'):
                secMagnitudeType.text = event['mags'][1]['magType']
        if (get_earthquake_type(event['eventInfo']['type']) != "None"):
            earthquakeType.text = get_earthquake_type(event['eventInfo']['type'])
        fixedDepth.text = convert_depthType(event['origin']['depthType'])
        # momentTensorScale.text =
        # momentTensorXX.text =
        # momentTensorXY.text =
        # momentTensorXZ.text =
        # momentTensorYY.text =
        # momentTensorYZ.text =
        # momentTensorZZ.text =
        #print(event['focalMechanism'])
        if event['focalMechanism'] != {}:
            if (event['focalMechanism'].get('strike1') != None):
                strike1.text = event['focalMechanism']['strike1']
            if (event['focalMechanism'].get('dip1') != None):
                dip1.text = event['focalMechanism']['dip1']
            if (event['focalMechanism'].get('rake1') != None):
                if (check_rake(event['focalMechanism'].get('rake1')) != "None"):
                    rake1.text = event['focalMechanism']['rake1']
            if (event['focalMechanism'].get('strike2') != None):
                strike2.text = event['focalMechanism']['strike2']
            if (event['focalMechanism'].get('dip2') != None):
                dip2.text = event['focalMechanism']['dip2']
            if (event['focalMechanism'].get('rake2') != None):
                if (check_rake(event['focalMechanism'].get('rake2')) != "None"):
                    rake2.text = check_rake(event['focalMechanism']['rake2'])
            # continue
        orgDigitize.text = 'O'
        comments.text = get_comment(event['eventInfo'], event['mags'][0]['publicID'], event['focalMechanism'], authorList)

        networkEventDataset.extend(root)
    tree = ET.ElementTree(wovoml)

    # tree.write("C:\\Users\\anhdu\\OneDrive\\Desktop\\EOS\\output_st_helens_01-01-1964_01-01-1980.xml")
    return tree


print("Download Started!")
bot_lat = -10
top_lat = 26.8
left_lon = 92.7
right_lon = 131.24
start_year = 2014
increment = 1
end_year = 2020
start_month = 1
end_month = 1
ET.register_namespace("", "http://quakeml.org/xmlns/quakeml/1.2")

while start_year <= end_year:
    url = urlopen('http://www.isc.ac.uk/cgi-bin/web-db-v4?request=COMPREHENSIVE&out_format=QuakeML&searchshape=RECT&bot_lat=' + str(bot_lat) + '&top_lat=' + str(top_lat) + '&left_lon=' + str(left_lon) + '&right_lon=' + str(right_lon) + '&start_year='+ str(start_year) + '&start_month=' + str(start_month) +'&start_day=01&start_time=00%3A00%3A00&end_year='+ str(start_year+increment) + '&end_month=' + str(end_month) + '&end_day=1&end_time=00%3A00%3A00&null_dep=on&null_mag=on&req_mag_type=Any&req_mag_agcy=Any&null_phs=on&prime_only=on&include_magnitudes=on')
    # url = urlopen('http://www.isc.ac.uk/cgi-bin/web-db-v4?out_format=QuakeML&request=REVIEWED&searchshape=GLOBAL&start_year=2009&start_month=2&start_day=22&start_time=00%3A00%3A00&end_year=2009&end_month=3&end_day=22&end_time=00%3A00%3A00&null_dep=on&req_mag_agcy=Any&null_mag=on&req_mag_type=Any&req_mag_agcy=Any&null_phs=on&prime_only=on&include_magnitudes=on')
    try:
        ori_tree = ET.parse(url)
        root = ori_tree.getroot()
        filename = 'C:\\Users\\hungd\\output\\' + str(
            start_year) + '_Jan_data.xml'
        ori_tree.write(filename)
        events = parse_xml(filename)
        print("Parse Successful year" + str(start_year))
        chunks = [events[x:x + 900] for x in range(0, len(events), 900)]
        for i in range(len(chunks)):
            tree = convert_to_WOVOdat_format(chunks[i])
            print("Convert successful")
            #converted_file = 'Test event.xml'
            converted_file = 'ISC_Event ' + str(start_month) + str(start_year) + '-' + str(end_month) + str(start_year+increment) + '(' + str(i) + ')' + '_' + str(bot_lat) + str(top_lat) + str(left_lon) + str(right_lon) +  '.xml'
            tree.write(converted_file, encoding='utf-8')
            print("Write successful!")
    except Exception as e:
        print(e)

    start_year += increment

print("Download Done!")

'''
driver.get('https://wovodat.org:8080/index.php')
username = driver.find_element_by_id("input_username")
password = driver.find_element_by_id("input_password")

username.send_keys('wovodat_view')
password.send_keys('+00World')
driver.find_element_by_id("input_go").click()
driver.find_element_by_title("input_go")
'''