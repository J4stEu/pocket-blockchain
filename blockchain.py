import hashlib
from fastecdsa import curve, ecdsa, keys
from base58 import b58encode, b58decode
from datetime import datetime
#from app import db
#from models import *

class Wallet(object):
    def __init__(self, privateKey, publicKey, publicKeyBytes):
        self.privateKey = privateKey
        self.publicKey = publicKey
        self.publicKeyBytes = publicKeyBytes

class Transaction(object):
    def __init__(self, id, vIn, vOut):
        self.id = id
        self.vIn = vIn
        self.vOut = vOut

    def __repr__(self):
        vInRepresentation = []
        for vIn in self.vIn:
            vInRepresentation.append(vIn.__repr__)
        vOutRepresentation = []
        for vOut in self.vOut:
            vOutRepresentation.append(vOut.__repr__)
        return "Transaction: id = {}, vIn = {}, vOut = {}".format(self.id, vInRepresentation, vOutRepresentation)

class TransactionOutput(object):
    def __init__(self, val, pubKeyHash):
        self.val = val
        self.pubKeyHash = pubKeyHash

    def __repr__(self):
        return "TransactionOutput: val = {}, pubKeyHash = {}".format(self.val, self.pubKeyHash)

    def lock(self, address, version, addrCheckSumLen):
        pubKeyHash = b58decode(address)
        pubKeyHash = pubKeyHash[len(version) : len(pubKeyHash) - addrCheckSumLen]
        return pubKeyHash

    def isLockedWithKey(self, pubKeyHash):
        return pubKeyHash == self.pubKeyHash

class TransactionInput(object):
    def __init__(self, id, vOut, sig, pubKey, pubKeyBytes):
        self.id = id
        self.vOut = vOut
        self.sig = sig
        self.pubKey = pubKey
        self.pubKeyBytes = pubKeyBytes

    def __repr__(self):
        return "TransactionInput: id = {}, vOut = {}, sig = {}, pubKey = {}, pubKeyBytes = {}".format(self.id, self.vOut, self.sig, self.pubKey, self.pubKeyBytes)

    def usesKey(self, pubKey, pubKeyHash):
        return pubKey == pubKeyHash

class Block(object):
    def __init__(self, timeStamp, transactions, prevHash, hash, nonce):
        self.timeStamp = timeStamp
        self.transactions = transactions
        self.prevHash = prevHash
        self.hash = hash
        self.nonce = nonce

class Chain(object):
    def __init__(self):
        self.blocks = []
        self.wallets = {}
        # We can change target bits due to control complexity of making new blocks
        #self.targetBits = int(24)
        self.targetBits = int(12)
        # Value to get for mining
        self.signUnit = 10
        self.addrCheckSumLen = 4
        self.version = bytes(0x00)

    def newWallet(self):
        prKey, pubKey, pubKeyBytes = self.newKeyPair()
        wallet = Wallet(prKey, pubKey, pubKeyBytes)
        address = str(self.getAddress(wallet), 'utf-8')
        self.wallets[address] = wallet
        print('Your new address: ' + address)
        return address

    def newKeyPair(self):
        # generate a private key for curve P256
        prKey = keys.gen_private_key(curve.P256)
        # get the public key corresponding to the private key we just generated
        pubKey = keys.get_public_key(prKey, curve.P256)
        # public key to bytes
        pubKeyBytes = pubKey.x.to_bytes(32, "big") + pubKey.y.to_bytes(32, "big")
        return prKey, pubKey, pubKeyBytes

    def pubKeyHash(self, pubKeyBytes):
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(hashlib.sha256(pubKeyBytes).digest())
        return ripemd160.digest()

    def getAddress(self, wallet):
        pubKeyHash = self.pubKeyHash(self.version + wallet.publicKeyBytes)
        # first 4 bytes - checksum
        checksum = hashlib.sha256(hashlib.sha256(pubKeyHash).digest()).digest()[:self.addrCheckSumLen]
        address = b58encode(pubKeyHash + checksum)
        return address

    def signTransaction(self, transaction, privateKey):
        if self.isCoinBase(transaction):
            return
        prevTransactions = {}
        for vIn in transaction.vIn:
            prevTransaction = self.findTransaction(vIn.id)
            if prevTransaction == None:
                print('Failed to find previous transaction')
                return
            prevTransactions[prevTransaction.id] = prevTransaction
        return self.sign(transaction, prevTransactions, privateKey)

    def sign(self, transaction, prevTransactions, privateKey):
        for vIn in transaction.vIn:
            if not (vIn.id in prevTransactions and prevTransactions[vIn.id].id):
                print('Previous transaction is not correct')
                return
        txTrimmedCopy = self.txTrimmedCopy(transaction)
        for index, vIn in enumerate(txTrimmedCopy.vIn):
            prevTransaction = prevTransactions[vIn.id]
            vIn.sig = None
            vIn.pubKeyBytes = prevTransaction.vOut[vIn.vOut].pubKeyHash
            dataToSign = txTrimmedCopy.__repr__()
            r, s = ecdsa.sign(dataToSign, privateKey)
            transaction.vIn[index].sig = {'r': r, 's': s}
            vIn.pubKey = None
        return transaction

    def verifyTransaction(self, transaction):
        if self.isCoinBase(transaction):
            return
        prevTransactions = {}
        for vIn in transaction.vIn:
            prevTransaction = self.findTransaction(vIn.id)
            if prevTransaction == None:
                print('Failed to find previous transaction')
                return
            prevTransactions[prevTransaction.id] = prevTransaction
        return self.verify(transaction, prevTransactions)

    def verify(self, transaction, prevTransactions):
        for vIn in transaction.vIn:
            if not (vIn.id in prevTransactions and prevTransactions[vIn.id].id):
                print('Previous transaction is not correct')
                return
        txTrimmedCopy = self.txTrimmedCopy(transaction)
        for index, vIn in enumerate(transaction.vIn):
            prevTransaction = prevTransactions[vIn.id]
            txTrimmedCopy.vIn[index].sig = None
            txTrimmedCopy.vIn[index].pubKeyBytes = prevTransaction.vOut[vIn.vOut].pubKeyHash
            if vIn.sig == None:
                return False
            r, s = vIn.sig['r'], vIn.sig['s']
            dataToVerify = txTrimmedCopy.__repr__()
            verify = ecdsa.verify((r, s), dataToVerify, vIn.pubKey)
            if verify == False:
                return False
        return True

    def txTrimmedCopy(self, transaction):
        inputs = []
        outputs = []
        for vIn in transaction.vIn:
            inputs.append(TransactionInput(vIn.id, vIn.vOut, None, None, None))
        for vOut in transaction.vOut:
            outputs.append(TransactionOutput(vOut.val, vOut.pubKeyHash))
        return Transaction(transaction.id, inputs, outputs)

    # def isAddressValid(self, address):
    #     pubKeyHash = b58decode(address)
    #     # pub key
    #     pubKey = pubKeyHash[: len(pubKeyHash) - self.addrCheckSumLen]
    #     # check sum
    #     checkSum = pubKeyHash[len(pubKeyHash) - self.addrCheckSumLen:]
    #     pass

    # hash - 256 bits
    # target bits - 25 bits -> target instance that is smaller than the hash (not valid proof of work)
    # we need to calculate new hash(for new block) with (nonce + new block info) to be smaller than target instance
    def proofOfWork(self, block):
        target = int(str(int(10**round((256 - self.targetBits)/4))), 16) # target bits -> target instance
        maxInt64 = int(9223372036854775807) # 64 bits (8 bytes). To prevent overflow
        nonce = 0
        allIdsTxsInOne = ''
        for tx in block.transactions:
            allIdsTxsInOne += tx.id
        txHash = hashlib.sha256(allIdsTxsInOne.encode('utf-8')).hexdigest()
        while nonce < maxInt64:
            allInOne = str(block.timeStamp) + str(txHash) + str(block.prevHash) + '{:x}'.format(int(nonce))
            dataHash = hashlib.sha256(allInOne.encode('utf-8')).hexdigest()
            # cmp
            if ((int(dataHash, 16) > target) - (int(dataHash, 16) < target)) == -1:
                break
            else:
                nonce += 1
        return dataHash, nonce

    def testProofOfWork(self, data, nonceToCheck = None):
        target = int(str(int(10**round((256 - self.targetBits)/4))), 16) # target bits -> target instance
        maxInt64 = int(9223372036854775807) # 64 bits (8 bytes). To prevent overflow
        nonce = 0
        origHash = hashlib.sha256((data + '{:x}'.format(int(nonceToCheck)) if nonceToCheck != None else "").encode('utf-8')).hexdigest()
        while nonce < maxInt64:
            allInOne = data +'{:x}'.format(int(nonce)) if nonce != 0 else ""
            dataHash = hashlib.sha256(allInOne.encode('utf-8')).hexdigest()
            # cmp
            if ((int(dataHash, 16) > target) - (int(dataHash, 16) < target)) == -1:
                break
            else:
                nonce += 1
        print("Original hash: {}, Hash with nonce: {}, Nonce: {}, Nonce(hex): {}".format(origHash, dataHash, nonce, '{:x}'.format(int(nonce))))

    # check if proof of work is valid for a single block
    def blockProofCheck(self, block):
        target = int(str(int(10**round((256 - self.targetBits)/4))), 16)
        allInOne = str(block.timeStamp) + str(block.data) + str(block.prevHash) + '{:x}'.format(int(block.nonce))
        dataHash = hashlib.sha256(allInOne.encode('utf-8')).hexdigest()
        return ((int(dataHash, 16) > target) - (int(dataHash, 16) < target)) == -1

    def proofCheck(self):
        for block in self.blocks:
            print('Data: ' + block.data)
            print('Hash: ' + block.hash)
            print('Pr.hash: ' + block.prevHash)
            print('Proof of work: ' + 'valid' if self.blockProofCheck(Block(block.timeStamp, block.data, block.prevHash, block.hash, block.nonce)) else 'invalid')
            print('\n')

    def setHash(self, block):
        allIdsTxsInOne = ''
        for tx in block.transactions:
            allIdsTxsInOne += tx.id
        txHash = hashlib.sha256(allIdsTxsInOne.encode('utf-8')).hexdigest()
        allInOne = str(block.timeStamp) + str(txHash) + str(block.prevHash) + '{:x}'.format(int(block.nonce))
        return hashlib.sha256(allInOne.encode('utf-8')).hexdigest()

    def newBlock(self, transactions, prevHash):
        block = Block(datetime.now(), transactions, prevHash, '', '')
        block.hash, block.nonce = self.proofOfWork(block)
        return block

    def transactionHash(self, transaction):
        allInOne = ''
        for txIn in transaction.vIn:
            allInOne += str(txIn.id) + str(txIn.vOut) + str(txIn.sig) + str(txIn.pubKey)
        for txOut in transaction.vOut:
            allInOne += str(txOut.val) + str(txOut.pubKeyHash)
        txHash = hashlib.sha256(allInOne.encode('utf-8')).hexdigest()
        return txHash

    def coinBaseTx(self, to, data):
        tIn = TransactionInput(None, -1, None, None, data)
        tOut = TransactionOutput(self.signUnit, None)
        tOut.pubKeyHash = tOut.lock(to, self.version, self.addrCheckSumLen)
        tr = Transaction(0, [tIn], [tOut])
        tr.id = self.transactionHash(tr)
        return tr

    def isCoinBase(self, transaction):
        return len(transaction.vIn) == 1 and transaction.vIn[0].id == None and transaction.vIn[0].vOut == -1

    def unspentTxs(self, pubKeyHash):
        unspentTxs = []
        unlockingInputs = []
        unspentValidTxs = []
        for block in self.blocks:
            for tx in block.transactions:
                for index, vOut in enumerate(tx.vOut):
                    move = True
                    for vIn in tx.vIn:
                        # if an input have any reference to the output -> tx was spent
                        if (index == vIn.vOut) and (vIn.id == tx.id):
                            move = False
                            break
                    if move == False: continue
                    # check if provided public key hash was used to lock the output
                    if vOut.isLockedWithKey(pubKeyHash):
                        # set tx itself, index of the vOut and vOut itself
                        unspentTxs.append([tx, index, vOut])
                for vIn in tx.vIn:
                    if vIn.vOut == -1: break # first transaction
                    if vIn.usesKey(self.pubKeyHash(vIn.pubKeyBytes), pubKeyHash):
                        unlockingInputs.append(vIn)
        # we have unlocking inputs and unspent transactions -> get valid unspent transactions
        if len(unlockingInputs) == 0:
            unspentValidTxs = unspentTxs
        else:
            for vOutput in unspentTxs:
                for vInput in unlockingInputs:
                    equals = False
                    for vInput in unlockingInputs:
                        if (vInput.id == vOutput[0].id) and (vInput.vOut == vOutput[1]):
                            equals = True
                            break
                    if equals == False:
                        unspentValidTxs.append(vOutput)
                        break
        return unspentValidTxs

    def accVer(self, pubKeyHash, amount):
        unspentTxs = self.unspentTxs(pubKeyHash)
        unspentAddressTxs = []
        acc = 0
        for tx in unspentTxs:
            if tx[0].vOut[tx[1]].isLockedWithKey(pubKeyHash) and (acc < amount):
                acc += tx[2].val
                unspentAddressTxs.append(tx)
                if (acc >= amount): break
        return acc, unspentAddressTxs

    def newTransaction(self, fr, to, amount):
        inputs = []
        outputs = []

        fromWallet = self.wallets.get(fr, False)
        if not fromWallet:
            print("There is no such an address: " + fr)
            return

        acc, unspentAddressTxs = self.accVer(self.pubKeyHash(fromWallet.publicKeyBytes), amount)

        if acc < amount:
            print('Not enough units...')
            return

        for tx in unspentAddressTxs:
            inputs.append(TransactionInput(tx[0].id, tx[1], None, fromWallet.publicKey, fromWallet.publicKeyBytes))

        output = TransactionOutput(amount, None)
        output.pubKeyHash = output.lock(to, self.version, self.addrCheckSumLen)
        outputs.append(output)

        if acc > amount:
            output = TransactionOutput(acc - amount, None)
            output.pubKeyHash = output.lock(fr, self.version, self.addrCheckSumLen)
            outputs.append(output)

        # reward
        output = TransactionOutput(self.signUnit, None)
        output.pubKeyHash = output.lock(fr, self.version, self.addrCheckSumLen)
        outputs.append(output)

        tx = Transaction(None, inputs, outputs)
        tx.id = self.transactionHash(tx)
        tx = self.signTransaction(tx, fromWallet.privateKey)
        return tx

    def findTransaction(self, id):
        for block in self.blocks:
            for tx in block.transactions:
                if tx.id == id:
                    return tx
        return None

    def initBlockChain(self, to):
        print('Mining the Genesis Block with data "Genesis Block"...')
        transactions = [self.coinBaseTx(to, "Genesis block")]
        self.blocks.append(self.newBlock(transactions, ''))
        print('Sucess.')

    def addBlock(self, transactions):
        print('Mining the block...')
        for tx in transactions:
            if self.verifyTransaction(tx) == False:
                print('Invalid transaction')
                return False
        prevBlock = self.blocks[len(self.blocks) - 1]
        newBlock = self.newBlock(transactions, self.setHash(Block(prevBlock.timeStamp, prevBlock.transactions, prevBlock.prevHash, prevBlock.hash, prevBlock.nonce)))
        self.blocks.append(newBlock)
        return True

    def send(self, fr, to, amount):
        print('Sending data=' + str(amount) + ' from ' + fr + ' to ' + to)
        # here should be all new transactions.
        transaction = self.newTransaction(fr, to, amount)
        if transaction:
            blockIsAdded = self.addBlock([transaction])
            if blockIsAdded:
                print('Success.')
            else:
                print('Error.')

    def getBalance(self, address):
        wallet = self.wallets.get(address, False)
        if not wallet:
            print("There is no such an address: " + address)
            return
        balance = 0
        for tx in self.unspentTxs(self.pubKeyHash(wallet.publicKeyBytes)):
            balance += int(tx[2].val)
        print('Balance of ' + address + ': ' + str(balance))

    def showBlocks(self):
        print('All blocks:')
        print('\n')
        for index, block in enumerate(self.blocks):
            print('Block Id: ' + str(index))
            print('Hash: ' + block.hash)
            print('Nonce: ' + str(block.nonce))
            print('Pr.hash: %s' % (block.prevHash if block.prevHash else 'none'))
            print('Time: ' + str(block.timeStamp))
            print('Transactions(count): ' + str(len(block.transactions)))
            for index, transaction in enumerate(block.transactions):
                print(' - Transaction ' + str(index + 1) + '(coin base transaction)' if self.isCoinBase(transaction) else '')
                print(' - Transaction id:' + str(transaction.id))
                print(' - Inputs (count):' + str(len(transaction.vIn)))
                print(' - Outputs (count):' + str(len(transaction.vOut)))
                print(' ---')
                for vInIndex, vIn in enumerate(transaction.vIn):
                    print(' -> Input ' + str(vInIndex))
                    print(' -> Input id:' + str(vIn.id))
                    print(' -> Input sig:' + str(vIn.sig))
                    print(' -> Relative id of output:' + str(vIn.vOut))
                    if not self.isCoinBase(transaction):
                        print(' -> Input pub key (elliptic curve):' + 'X: {}, Y: {}'.format(str(vIn.pubKey.x), str(vIn.pubKey.y)))
                        print(' -> Input pub key(bytes):' + str(vIn.pubKeyBytes))
                    print(' ---')
                for vOutIndex, vOut in enumerate(transaction.vOut):
                    print(' -> Output ' + str(vOutIndex))
                    print(' -> Output value:' + str(vOut.val))
                    print(' -> Output public key(bytes):' + str(vOut.pubKeyHash))
            print('\n')

class BlockChain(Chain):
    def __init__(self):
        super(BlockChain, self).__init__()
        print('BlockChain instance is created.')
        print('There is no BlockChain initialization yet.')

print('\n')
print('Example: ')
print('\n')
bc = BlockChain()
print('\n')
# Eugene
print('Create wallet for Eugene:')
addressEugene = bc.newWallet()
# bc.testProofOfWork("Data")
# Ivan
print('Create wallet for Ivan:')
addressIvan = bc.newWallet()
# Alena
print('Create wallet for Alena:')
addressAlena = bc.newWallet()
print('\n')
print('Init blockchain by Eugene ({}):'.format(addressEugene))
bc.initBlockChain(addressEugene)
bc.getBalance(addressEugene)
print('\n')
print('Sending data from Eugene({}) to Ivan({}):'.format(addressEugene, addressIvan))
bc.send(addressEugene, addressIvan, 4)
bc.getBalance(addressEugene)
bc.getBalance(addressIvan)
print('\n')
print('Sending data from Ivan({}) to Alena({}):'.format(addressIvan, addressAlena))
bc.send(addressIvan, addressAlena, 2)
bc.getBalance(addressIvan)
bc.getBalance(addressAlena)
print('\n')
print('Sending data from Ivan({}) to Eugene({}):'.format(addressIvan, addressEugene))
bc.send(addressIvan, addressEugene, 4)
print('\n')
print('Sending data from Eugene({}) to Alena({}):'.format(addressEugene, addressAlena))
bc.send(addressEugene, addressAlena, 1)
bc.getBalance(addressEugene)
bc.getBalance(addressAlena)
print('\n')
print('Balance of all members:')
bc.getBalance(addressEugene)
bc.getBalance(addressIvan)
bc.getBalance(addressAlena)
print('\n')
bc.showBlocks()
