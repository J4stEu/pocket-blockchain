import {defineStore} from "pinia";

export const useNotification = defineStore("notification", {
    state: () => ({
        text: "",
        show: false,
        success: true
    }),
    actions: {
        reset() {
            this.text = "";
            this.show = false;
            this.success = true;
        },
        notify(text, success) {
            this.text = text;
            this.show = true;
            this.success = success;
            setTimeout(() => {
                this.reset();
            }, 3000);
        }
    }
});