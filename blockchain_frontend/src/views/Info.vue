<template>
  <section id="info" class="container is-max-desktop">
    <div class="infoContainer">
      <Info
          :title="info.Info.Title"
          :options="info.Info.Options"
      />
      <div @click="resetSystem">
        <ITSButton text="Reset system" :buttonColor="'rgba(76, 212, 176, 0.2)'">
          <template v-slot:beforeIcon>
            <ResetSystemIcon/>
          </template>
        </ITSButton>
      </div>
    </div>
  </section>
</template>

<script>
import Info from "@/components/info/Info.vue";
import ITSButton from "@/components/ui/ITSButton.vue";
import DataInfo from "@/data/info.json";
import ResetSystemIcon from "@/assets/icons/iconmonstr-synchronization-23.svg?component";
import {useNotificationStore} from "@/hooks/useNotificationStore";
export default {
    components: {
        Info,
        ITSButton,
        ResetSystemIcon
    },
    setup() {
        const {notification} = useNotificationStore();
        return {
            notification
        };
    },
    data() {
        return {
            info: DataInfo
        };
    },
    methods: {
        async resetSystem() {
            this.fetching = true;
            await fetch("/api/reset_system", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    if (data.error !== null) {
                        console.log(data.error);
                        this.notification.notify(data.error, false);
                        return;
                    }
                    this.notification.notify("Success", true);
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