from dm.migrate import DomainModelLoader

class DomainModelLoader(DomainModelLoader):

    def migrateDataDump(self):
        if self.getDumpVersion() == '0.1':
           self.migrateDataDump__0_1__to__0_2()
        if self.getDumpVersion() == '0.2':
           self.migrateDataDump__0_2__to__0_3()
        if self.getDumpVersion() == '0.3':
           self.migrateDataDump__0_3__to__0_4()
        if self.getDumpVersion() == '0.4':
           self.migrateDataDump__0_4__to__0_5()
        if self.getDumpVersion() == '0.5':
           self.migrateDataDump__0_5__to__0_6()

    def migrateDataDump__0_1__to__0_2(self):
        self.setDumpVersion('0.2')

    def migrateDataDump__0_2__to__0_3(self):
        self.setDumpVersion('0.3')

    def migrateDataDump__0_3__to__0_4(self):
        self.setDumpVersion('0.4')
        # Rename 'scheduleStart' attribute of Assembly objects to 'starts'.
        for (assemblyId, assembly) in self.dataDump['Assembly'].items():
            if assemblyId == 'metaData':
                continue
            assembly['starts'] = assembly.pop('scheduledStart')

    def migrateDataDump__0_4__to__0_5(self):
        self.setDumpVersion('0.5')

    def migrateDataDump__0_5__to__0_6(self):
        self.setDumpVersion('0.6')

