c.JupyterHub.ip = "0.0.0.0"
c.JupyterHub.port = 8000
c.JupyterHub.hub_ip = "0.0.0.0"

c.JupyterHub.authenticator_class = "dummy"
c.DummyAuthenticator.password = "admin"
c.Authenticator.admin_users = {"admin"}
c.Authenticator.allow_all = True

c.Spawner.default_url = "/lab"
c.Spawner.notebook_dir = "/home/admin"