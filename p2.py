raw = '''"https://" +
"ev-h.phn" +
    "cdn.com" + "/" +
	"hls/vide" +
    "os/20" + "230" + 
    "4/27/" + "430" + 
	"418901/" + "1" +
    "080P_400" + 
    "0K_43041" +
	"8901.mp4" +
    "/mast" + "er." + 
    "m3u8?va" + "l" +
	"idfrom=1" +
    "6850344" + "1" +
    "2&validt" +
	"o=168504" +
    "1612&" + "ipa" +
    "=82.64.2" +
	"32.157&" + "h" +
    "dl=-1&ha" +
    "sh=wY" + "8F7" +
	"GttDx" + "Aey" +
    "mt7vC" + "Geq" +
    "Wu9oZI%" + "3" +
	"D";'''

url = ''.join(raw.replace('"', '').replace('+', '').replace(';', '') .split())

print(url)