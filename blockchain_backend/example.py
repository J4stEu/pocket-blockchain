from app.blockchain_app.blockchain import BlockChain
from app.app import db

print('\n')
print('Example: ')
print('\n')
# create blockchain_app instance
bc = BlockChain(db)
print('\n')
# create wallets
address1 = bc.new_wallet()
address2 = bc.new_wallet()
address3 = bc.new_wallet()
address4 = bc.new_wallet()
address5 = bc.new_wallet()
address6 = bc.new_wallet()
address7 = bc.new_wallet()
address8 = bc.new_wallet()
print('\n')
# init blockchain_app system, 10 sign unit - reward
print('Init blockchain_app system by address1 ({}):'.format(address1))
bc.init_system(address1)
bc.get_balance(address1)
print('\n')
# we can send sign units that we have. That is how transactions are created and added to pool.
# once a new transaction is created and added to pool, you can not use your wallet to
# create new transactions until it verified(added to a new block)
bc.send(address1, address2, 3)
bc.mine_block(address1)
bc.get_balance(address1)
print('\n')
bc.send(address1, address3, 2)
bc.mine_block(address1)
bc.get_balance(address1)
print('\n')
bc.send(address1, address4, 1)
bc.mine_block(address1)
bc.get_balance(address1)
print('\n')
bc.send(address1, address5, 1)
bc.mine_block(address1)
bc.get_balance(address1)
print('\n')
bc.send(address1, address6, 1)
bc.mine_block(address1)
bc.get_balance(address1)
print('\n')
bc.send(address1, address7, 1)
bc.mine_block(address1)
bc.get_balance(address1)
print('\n')
bc.send(address1, address8, 1)
bc.mine_block(address1)
bc.get_balance(address1)
print('\n')
bc.send(address2, address1, 1)
bc.send(address3, address1, 1)
bc.send(address4, address1, 1)
bc.send(address5, address1, 1)
bc.send(address6, address1, 1)
bc.send(address7, address1, 1)
bc.send(address8, address1, 1)
# we have 7 transactions in pool from 7 different wallets
# we can create two blocks: one with 2 transactions, one with 3 transactions in a block (5 - default)
# there will be 2 transactions in a pool (not verified)
bc.mine_block(address2, 2)
bc.mine_block(address2, 3)
print('Balances: ')
bc.get_balance(address1)
bc.get_balance(address2)
bc.get_balance(address3)
bc.get_balance(address4)
bc.get_balance(address5)
bc.get_balance(address6)
bc.get_balance(address7)
bc.get_balance(address8)
print('\n')
# blockchain_app system information
bc.show_blocks()