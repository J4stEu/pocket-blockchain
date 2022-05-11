import {useNotification} from "@/store/useNotification.js";
import {storeToRefs} from "pinia/dist/pinia";

export function useNotificationStore() {
    const notification = useNotification();
    const {text, show, success} = storeToRefs(notification);
    return {
        notification,
        text,
        show,
        success
    };
}