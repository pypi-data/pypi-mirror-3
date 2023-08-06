import livestreamer

channel = livestreamer.resolve_url("http://www.twitch.tv/TiltGaming")
streams = channel.get_streams()

stream = streams["live"]

stream.open()

while True:
    data = stream.read(1024)
    if len(data) == 0:
        break

    print(len(data))

stream.close()
