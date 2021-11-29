import sys
import os
sys.path.append('classes')
sys.path.append('classes/migrations')
sys.path.append('config')

from stargate_address_book_migration import StargateAddressBookMigration
            
migration = StargateAddressBookMigration("/home/sg1/sg1/")