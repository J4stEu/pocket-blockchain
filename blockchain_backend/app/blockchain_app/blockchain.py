from .chain import Chain
from .errors import BcSystemError


class BlockChain(Chain):
    def __init__(self, bc, wallets_store="./app/blockchain_app/wallets.bcw"):
        super().__init__(bc, wallets_store)
        print('BlockChain instance is created.')
        if self.is_system_initialized():
            print("Blockchain system is already initialized.")
            blocks = self.get_blocks()
            if blocks is None:
                print("Failed reindex.")
            self.chain_state.reindex(blocks, self.de_serialize_block)
        else:
            print('Blockchain system is not initialized yet.')
        store = self.create_wallets_store()
        if store is False:
            raise BcSystemError("Wallets", "Failed to configure wallets store")
