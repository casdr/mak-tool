# Remaining MAK tool
# By casdr / cas.reuver.co

from lxml import etree
import hmac
import hashlib
import base64
import requests
import sys

BPrivateKey = bytes([
    0xfe, 0x31, 0x98, 0x75, 0xfb, 0x48, 0x84, 0x86, 0x9c, 0xf3, 0xf1, 0xce, 0x99, 0xa8, 0x90, 0x64,
    0xab, 0x57, 0x1f, 0xca, 0x47, 0x04, 0x50, 0x58, 0x30, 0x24, 0xe2, 0x14, 0x62, 0x87, 0x79, 0xa0
])

def build_xml(serial):
    uri = "http://www.microsoft.com/DRM/SL/BatchActivationRequest/1.0"
    root = etree.Element("ActivationRequest", xmlns=uri)

    versionNumber = etree.Element("VersionNumber")
    versionNumber.text = "2.0"
    root.append(versionNumber)

    requestType = etree.Element("RequestType")
    requestType.text = "2"
    root.append(requestType)

    requestsGroup = etree.Element("Requests")
    requestElement = etree.Element("Request")
    pidEntry = etree.Element("PID")
    pidEntry.text = str(serial)

    requestElement.append(pidEntry)
    requestsGroup.append(requestElement)
    root.append(requestsGroup)

    byte_xml = bytes(etree.tostring(root).decode("utf-8"), "utf-16-le")
    base64_xml = base64.b64encode(byte_xml)

    digest = base64.b64encode(hmac.new(BPrivateKey, byte_xml, digestmod=hashlib.sha256).digest())

    form = "<?xml version=\"1.0\" encoding=\"utf-8\"?><soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\"><soap:Body><BatchActivate xmlns=\"http://www.microsoft.com/BatchActivationService\"><request><Digest>{0}</Digest><RequestXml>{1}</RequestXml></request></BatchActivate></soap:Body></soap:Envelope>";
    form = form.format(digest.decode('utf-8'), base64_xml.decode('utf-8'))

    return form

def do_request(xmldata):
    url ="https://activation.sls.microsoft.com/BatchActivation/BatchActivation.asmx"
    headers = {
        "SOAPAction": "http://www.microsoft.com/BatchActivationService/BatchActivate",
        "Content-Type": "text/xml; charset=\"utf-8\"",
        "Host": "activation.sls.microsoft.com"
    }
    result = requests.post(url, xmldata, headers=headers, verify=False)

    return result

def parse_xml(result):
    try:
        root = etree.fromstring(result)
        response = root.find(".//{http://www.microsoft.com/BatchActivationService}ResponseXml")
        parsed = etree.fromstring(bytes(response.text.encode('utf-16')))
        activations = parsed.find(".//{http://www.microsoft.com/DRM/SL/BatchActivationResponse/1.0}ActivationRemaining")

        return int(activations.text)
    except:
        return None

if __name__ == '__main__':
    args = sys.argv
    if len(sys.argv) < 3:
        print("python3 check_mak.py [key_id] [warning_limit]")
        sys.exit(3)

    xmldata = build_xml(sys.argv[1])
    result = do_request(xmldata).content
    activations = parse_xml(result)
    if activations != None:
        if activations >= int(sys.argv[2]):
            print("OK - {0} activations left".format(activations))
            sys.exit(0)
        elif activations < 1:
            print("CRITICAL - {0} activations left".format(activations))
            sys.exit(2)
        elif activations < int(sys.argv[2]):
            print("WARNING - {0} activations left".format(activations))
            sys.exit(1)
    print("UKNOWN - Could not get activation count.")
    sys.exit(3)
