from glob import glob
import npyscreen as np

mp3_list = glob('/mnt/0b6b53eb-f83a-4f34-9224-da2310643534/Music/*.mp3')

class CommandLine(np.ActionControllerSimple):
    def create(self):
        self.add_action('^:q', self.exit_app, live=False)

    def exit_app(self, command_line, widget_proxy, live):
        exit()


class ClidInterface(np.FormMuttActiveTraditional):
    def create(self):
        self.action_controller = CommandLine
        self.wStatus1.value = 'clid'
        self.wStatus2.value = 'Status Bar'


class ClidApp(np.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', ClidInterface, name='clid')


if __name__ == '__main__':
    ClidApp().run()