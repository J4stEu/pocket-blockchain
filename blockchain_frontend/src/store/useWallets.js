import {defineStore} from "pinia";

export const useWallets = defineStore("wallets", {
    state: () => ({
        wallets: [],
        addresses: [],
        fetching: false,
    }),
    actions: {
        reset() {
            this.wallets = [];
            this.addresses = [];
            this.fetching = false;
        },
        async getWallets() {
            this.fetching = true;
            await fetch("/api/get_wallets", {
                method: "GET"
            })
                .then(response => response.json())
                .then(data => {
                    // console.log(data);
                    if (data.error !== null) {
                        console.log(data.err);
                        return;
                    }
                    this.wallets = data.data;
                    this.addresses = [];
                    data.data.forEach(wallet => {
                        this.addresses.push(wallet.address);
                    });
                })
                .finally(() => {
                    this.fetching = false;
                })
                .catch(err => {
                    console.log(err);
                    this.fetching = false;
                });
        },
    }
});