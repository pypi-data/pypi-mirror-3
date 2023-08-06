from kss.base.commands import KSSCommandSet

class KssplugintimerCommands(KSSCommandSet):

    # Add your own actions here, you can use the following code as
    #  a starting point
    def yourAction(self, selector, value):
        self.commands.add('yourAction', selector, parameter=value)
