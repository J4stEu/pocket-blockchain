<template>
  <section id="preview">
    <div class="bottomPreview">
      <div class="bottomPreviewContainer">
        <div class="previewImage" />
      </div>
      <div class="bottomPreviewContainer">
        <div>
          <transition appear name="me-button">
            <div class="nameContainer">
              <ITSButton
                  text="Eugene Nikonov"
                  src="https://j4steu.github.io/"
                  :isSrc="true"
                  :buttonColor="'rgba(76, 212, 176, 0.2)'"
              >
                <template v-slot:afterIcon>
                  <ShareIcon/>
                </template>
              </ITSButton>
            </div>
          </transition>
          <transition appear name="me-intro">
            <p>Digital Artificer (Developer / Designer)</p>
          </transition>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import ITSButton from "@/components/ui/ITSButton.vue";
import ShareIcon from "@/assets/icons/iconmonstr-share-8.svg?component";
export default {
    components: {
        ITSButton,
        ShareIcon
    },
};
</script>

<style lang="scss" scoped>
  .me-button-enter-from, .me-intro-enter-from {
    transform: translateY(#{$offsetVal + px});
  }
  .me-button-enter-to, .me-intro-enter-to {
    transform: translateY(0);
  }
  .me-button-enter-active {
    transition: transform 0.2s ease-in-out;
  }
  .me-intro-enter-active {
    transition: transform 0.4s ease-in-out;
  }
  #preview {
    padding: 0 $offsetVal + px;
    margin-top: $offsetVal + px;
  }
  .bottomPreview {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;

    div {

      &:last-child {

        h1, p {
          text-align: center;
          margin: calc($offsetVal / 4) + px 0;
          white-space: nowrap;
        }
      }
    }

    h1 {
      font-size: 2em;
      font-weight: bold;
    }
  }
  .bottomPreviewContainer {
    display: flex;
    justify-content: center;
    width: 50%;

    @media screen and (min-width:0px) and (max-width:768px) {
      width: auto;
    }

    div {
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    .nameContainer {
      display: flex;
      flex-direction: row;
    }

    &:last-child {
      margin-top: calc($offsetVal / 4) + px;
    }
  }
  .previewImage {
    width: $offsetVal * 8 + px;
    height: $offsetVal * 8 + px;
    border: 2px solid $lightGreen;
    border-radius: 50%;
    background: url("@/assets/img/j4steu.jpeg") center;
    background-size: cover;

    @media screen and (min-width:0px) and (max-width:768px) {
      margin-top: $offsetVal + px;
    }
  }
</style>>
