from dm.migrate import DomainModelLoader

class DomainModelLoader(DomainModelLoader):

    def migrateDataDump(self):
        if self.getDumpVersion() == '0.1':
           self.migrateDataDump__0_1__to__0_2()
        if self.getDumpVersion() == '0.2':
           self.migrateDataDump__0_2__to__0_3()

    def migrateDataDump__0_1__to__0_2(self):
        self.setDumpVersion('0.2')

    def migrateDataDump__0_2__to__0_3(self):
        self.setDumpVersion('0.3')

