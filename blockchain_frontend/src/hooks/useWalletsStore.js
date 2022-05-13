import {useWallets} from "@/store/useWallets.js";
import {storeToRefs} from "pinia/dist/pinia";

export function useWalletsStore() {
    const walletsStore = useWallets();
    const { wallets, addresses } = storeToRefs(walletsStore);
    return {
        walletsStore,
        wallets,
        addresses,
    };
}