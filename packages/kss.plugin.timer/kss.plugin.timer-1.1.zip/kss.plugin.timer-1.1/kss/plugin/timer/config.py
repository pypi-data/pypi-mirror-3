import os

from kssplugintimer.commands import KssplugintimerCommands

package_dir = os.path.dirname(os.path.abspath(__file__))
javascript_dir = os.path.join(package_dir, 'javascript')

class Timer(Plugin):

    javascripts = [os.path.join(javascript_dir, 'plugin.js')]

    extra_javascripts = []

    # if you need extra 3rd party Javascript files put them in the 3rd
    #  party directory and use the line below
    #
    # extra_javascripts = [] javascripts_from(os.path.join(package_dir, '3rd_party'))

    commandsets = {
    }

    selectors = []

