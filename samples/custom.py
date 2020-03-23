from fasjsonclient import ClientBuilder

#custom principal and baseurl
cb = ClientBuilder(principal_name='user@DOMAIN.COM', baseurl='http://apisomething.com')
cb.principal_name = 'user2@DOMAIN.ORG' #princpal_name and baseurl can be changed as props
client = cb.build()

print(client.whoami())