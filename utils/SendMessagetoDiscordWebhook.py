URI = 'https://discordapp.com/...'# your webhook url string 
alert = 'Testing'  ####WHAT TO ALERT
report = "username=" + Player.Name + "&content=" + alert
PARAMETERS=report
from System.Net import WebRequest
request = WebRequest.Create(URI)
request.ContentType = "application/x-www-form-urlencoded"
request.Method = "POST"
from System.Text import Encoding
bytes = Encoding.ASCII.GetBytes(PARAMETERS)
request.ContentLength = bytes.Length
reqStream = request.GetRequestStream()
reqStream.Write(bytes, 0, bytes.Length)
reqStream.Close()
response = request.GetResponse()
from System.IO import StreamReader
result = StreamReader(response.GetResponseStream()).ReadToEnd().replace('\r', '\n')
