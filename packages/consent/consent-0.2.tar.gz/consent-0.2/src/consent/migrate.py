from dm.migrate import DomainModelLoader

class DomainModelLoader(DomainModelLoader):

    def migrateDataDump(self):
        # Migrate from 0.1 to 0.2.
        if self.getDumpVersion() == '0.1':
           self.migrateDataDump__0_1__to__0_2()

    def migrateDataDump__0_1__to__0_2(self):
        # Update the version.
        self.setDumpVersion('0.2')



