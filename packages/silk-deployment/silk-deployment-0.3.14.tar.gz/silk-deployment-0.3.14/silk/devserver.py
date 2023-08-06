import os
import sys
import cherrypy

import silk.lib

role = silk.lib.get_role()
root = silk.lib.get_site_root(os.getcwd())
config = silk.lib.get_config(root, role)

if config.get('static_dirs'):
    for static_dir in config['static_dirs']:
        # Mount each of our static dirs as its own app in the cherrypy tree.
        # Each static_dir is a dict with url_path and system_path keys
        url_path = static_dir['url_path'].rstrip('/')
        sys_path = os.path.join(root, static_dir['system_path'])
        cherry_conf = {'/': {'tools.staticdir.on': True,
                             'tools.staticdir.dir': sys_path,}}
        cherrypy.tree.mount(None, script_name=url_path, config=cherry_conf)

#mount the wsgi app
wsgi_app = cherrypy.lib.attributes(config['wsgi_app'].replace(':', '.'))
cherrypy.tree.graft(wsgi_app, '')

sys.path.append(root)
os.chdir(root)
app = cherrypy.tree
