from fasjsonclient import ClientBuilder

cb = ClientBuilder()
client = cb.build()

print(client.whoami())