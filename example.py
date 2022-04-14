from blockchain import BlockChain

print('\n')
print('Example: ')
print('\n')
bc = BlockChain()
print('\n')
# Eugene
print('Create wallet for Eugene:')
addressEugene = bc.new_wallet()
# bc.testPoW("Data")
# Ivan
print('Create wallet for Ivan:')
addressIvan = bc.new_wallet()
# Alena
print('Create wallet for Alena:')
addressAlena = bc.new_wallet()
print('\n')
print('Init blockchain by Eugene ({}):'.format(addressEugene))
bc.init_system(addressEugene)
bc.get_balance(addressEugene)
print('\n')
print('Sending data from Eugene({}) to Ivan({}):'.format(addressEugene, addressIvan))
bc.send(addressEugene, addressIvan, 4)
bc.get_balance(addressEugene)
bc.get_balance(addressIvan)
print('\n')
print('Sending data from Ivan({}) to Alena({}):'.format(addressIvan, addressAlena))
bc.send(addressIvan, addressAlena, 2)
bc.get_balance(addressIvan)
bc.get_balance(addressAlena)
print('\n')
print('Sending data from Ivan({}) to Eugene({}):'.format(addressIvan, addressEugene))
bc.send(addressIvan, addressEugene, 4)
print('\n')
print('Sending data from Eugene({}) to Alena({}):'.format(addressEugene, addressAlena))
bc.send(addressEugene, addressAlena, 1)
bc.get_balance(addressEugene)
bc.get_balance(addressAlena)
print('\n')
print('Balance of all members:')
bc.get_balance(addressEugene)
bc.get_balance(addressIvan)
bc.get_balance(addressAlena)
print('\n')
bc.show_blocks()