<template>
  <section id="info" class="container is-max-desktop">
    <div class="infoContainer">
      <Info
          :title="info.Info.Title"
          :options="info.Info.Options"
      />
      <transition appear name="reset-system-button">
        <div @click="resetSystem" v-show="!fetching">
          <ITSButton text="Reset system" :buttonColor="'rgba(76, 212, 176, 0.2)'">
            <template v-slot:beforeIcon>
              <ResetSystemIcon/>
            </template>
          </ITSButton>
        </div>
      </transition>
    </div>
  </section>
</template>

<script>
import Info from "@/components/info/Info.vue";
import ITSButton from "@/components/ui/ITSButton.vue";
import DataInfo from "@/data/info.json";
import ResetSystemIcon from "@/assets/icons/iconmonstr-synchronization-23.svg?component";
import {useNotificationStore} from "@/hooks/useNotificationStore";
import {useWalletsStore} from "@/hooks/useWalletsStore";
import {ref} from "vue";
export default {
    components: {
        Info,
        ITSButton,
        ResetSystemIcon
    },
    setup() {
        const {notification} = useNotificationStore();
        const { walletsStore } = useWalletsStore();
        const info = ref(DataInfo);
        const fetching = ref(false);
        return {
            notification,
            walletsStore,
            info,
            fetching
        };
    },
    methods: {
        async resetSystem() {
            if (this.fetching) {
                return;
            }
            this.fetching = true;
            this.notification.notify("Resetting...", true);
            await fetch("/api/reset_system", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
            })
                .then(response => response.json())
                .then(data => {
                    // console.log(data);
                    if (data.error !== null) {
                        console.log(data.error);
                        this.notification.notify(data.error, false);
                        return;
                    }
                    this.notification.notify("Reset system: success", true);
                })
                .finally(() => {
                    this.fetching = false;
                    this.walletsStore.getWallets();
                })
                .catch(err => {
                    console.log(err);
                    this.notification.notify("Error", false);
                });
        },
    }
};
</script>

<style lang="scss" scoped>
  .reset-system-button-enter-from, .reset-system-button-leave-tp {
    transform: translateY(#{$offsetVal + px});
  }
  .reset-system-button-enter-to, .reset-system-button-leave-from {
    transform: translateY(0);
  }
  .reset-system-button-enter-active, .reset-system-button-leave-active {
    transition: transform 0.4s ease-in-out;
  }
  #info {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    height: 100%;
    padding: 0 $offsetVal + px;
    margin-top: $offsetVal * 2 + px;
  }
  .infoContainer {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    div {
      margin-top: $offsetVal + px;
    }
  }
</style>