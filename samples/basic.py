from fasjsonclient import ClientBuilder

cb = ClientBuilder()
client = cb.build()

print(client.get_group_members('admins'))