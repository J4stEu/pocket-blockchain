import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";

export function useNavigation(items) {
    const router = useRouter();
    const route = useRoute();

    const navItems = ref(items);
    const selectedItem = ref({});
    const currentRouteName = () => {
        return route.path;
    };
    const setCurrentItem = (item) => {
        selectedItem.value = item;
        router.push(item.path);
    };

    return {
        navItems,
        selectedItem,
        currentRouteName,
        setCurrentItem,
    };
}