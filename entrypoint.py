import config


##################################################
# project main entrypoint
##################################################

import config
from context import app
from rest import AppJSONEncoder

# NOTE: Add your swagger namespace here
from route import hello, paper, user

if __name__ == "__main__":
    # run Flask App
    app.json_encoder = AppJSONEncoder
    app.run(debug=True, port=config.server_port, host="0.0.0.0", use_reloader=True)
