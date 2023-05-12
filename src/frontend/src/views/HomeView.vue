<template>
  <main>
    <div>
      <h1>
        Ausstellung <cite>{{ exhibition?.title }}</cite>
      </h1>

      <b-card>
        <b-card-title class="text-center">
          <span class="fs-2">
            &laquo;{{ currentImageDescription?.title }}&raquo; ({{ currentImageDescription?.year }})
          </span>
        </b-card-title>
        <div class="loader" v-if="isLoading">
          <b-spinner v-if="isLoading" label="Loading..." />
        </div>
        <b-row no-gutters class="card-row">
          <b-col md="6" class="height-full-column d-flex align-items-center justify-content-start">
            <img
              v-if="currentImageId"
              :src="imageService.getImageUrl(currentImageId, 1000)"
              class="rounded-0 image-fit"
              @load="isImageLoading = false"
            />
          </b-col>
          <b-col md="6" class="height-full-column d-flex flex-column">
            <div class="actions d-flex flex-row justify-content-between w-100" aria-hidden="true">
              <div class="ms-4">
                <button
                  class="btn btn-outline-primary my-4 me-2"
                  @click="previousImage"
                  aria-label="Vorheriges Kunstwerk"
                  title="Vorheriges Kunstwerk"
                >
                  <i-mdi-arrow-left-bold class="icon" />
                </button>
                <button class="btn btn-outline-primary my-4 me-2" @click="goToArchive">
                  <i-mdi-archive class="icon" /> <span class="fs-5">im Archiv stöbern</span>
                </button>
                <button
                  class="btn btn-outline-primary my-4 me-2"
                  @click="nextImage"
                  aria-label="Nächstes Kunstwerk"
                  title="Nächstes Kunstwerk"
                >
                  <i-mdi-arrow-right-bold class="icon" />
                </button>
              </div>
              <button
                class="btn btn-outline-primary my-4 me-2"
                @click="speakCurrentImageDescription"
                aria-label="Beschreibung vorlesen"
                title="Beschreibung vorlesen"
              >
                <i-mdi-speak class="icon" :class="{ 'is-speaking': isSpeaking }" />
              </button>
            </div>
            <div class="d-flex flex-column align-items-center justify-content-center flex-fill">
              <blockquote class="blockquote fs-3 ms-4">
                <p class="image-description">{{ currentImageDescription?.description }}</p>
              </blockquote>
            </div>
          </b-col>
        </b-row>
      </b-card>
    </div>
  </main>
</template>

<script lang="ts">
import { ImageService } from "@/services/image-service";
import { DescriptionService } from "@/services/description-service";
import { computed, ref } from "vue";
import type { ExhibitionModel } from "@/models/exhibition-model";
import type { ImageDescriptionModel } from "@/models/image-description-model";
import { useRoute } from "vue-router";

export default {
  name: "HomeView",
  data() {
    const router = useRoute();
    const imageId = router.query.imageid; // Access the query parameter

    const imageService = new ImageService();
    const descriptionService = new DescriptionService();

    const currentImageId = ref<string | null>(null);
    const currentImageDescription = ref<ImageDescriptionModel | null>(null);
    const exhibition = ref<ExhibitionModel | null>(null);
    const isSpeaking = ref(false);
    const isServiceLoading = ref(true);
    const isImageLoading = ref(true);
    const isLoading = computed(() => isServiceLoading.value || isImageLoading.value);

    if (imageId) {
      currentImageId.value = imageId as string;
    }

    return {
      router,
      imageService,
      descriptionService,

      currentImageId,
      currentImageDescription,
      exhibition,
      isSpeaking,
      isServiceLoading,
      isImageLoading,
      isLoading,
    };
  },
  async mounted() {
    await this.loadMainImage();
  },
  unmounted() {
    speechSynthesis.cancel();
  },
  methods: {
    async loadMainImage() {
      this.isServiceLoading = true;
      if (this.exhibition === null) {
        this.exhibition = await this.imageService.getExhibition(this.currentImageId);
      }

      if (this.currentImageId === null || this.currentImageId.length === 0) {
        this.currentImageId = this.exhibition.imageIds[0];
        this.updateCurrentImageQuery();
      }

      this.currentImageDescription = await this.loadDescription(this.currentImageId);

      this.isServiceLoading = false;
    },
    async loadDescription(imageId: string) {
      return this.descriptionService.get(imageId);
    },
    async previousImage() {
      const currentIndex = this.exhibition?.imageIds.indexOf(this.currentImageId ?? "");

      if (this.exhibition !== null && currentIndex !== undefined && currentIndex !== null) {
        speechSynthesis.cancel();
        this.isImageLoading = true;

        const nextIndex =
          (currentIndex - 1 + this.exhibition.imageIds.length) % this.exhibition.imageIds.length;

        this.isServiceLoading = true;
        this.currentImageId = this.exhibition?.imageIds[nextIndex];

        this.updateCurrentImageQuery();

        this.currentImageDescription = await this.loadDescription(this.currentImageId);

        this.isServiceLoading = false;
      }
    },
    async nextImage() {
      const currentIndex = this.exhibition?.imageIds.indexOf(this.currentImageId ?? "");

      if (this.exhibition !== null && currentIndex !== undefined && currentIndex !== null) {
        speechSynthesis.cancel();
        this.isImageLoading = true;

        const nextIndex = (currentIndex + 1) % this.exhibition.imageIds.length;

        this.isServiceLoading = true;
        this.currentImageId = this.exhibition?.imageIds[nextIndex];

        this.updateCurrentImageQuery();

        this.currentImageDescription = await this.loadDescription(this.currentImageId);

        this.isServiceLoading = false;
      }
    },
    goToArchive() {
      this.$router.push({ name: "archive", query: { imageid: this.currentImageId } });
    },
    updateCurrentImageQuery() {
      const currentQueryParams = { ...this.router.query };
      currentQueryParams.imageid = this.currentImageId;
      this.$router.replace({ query: currentQueryParams });
    },
    speakCurrentImageDescription() {
      if (this.currentImageDescription) {
        if (!this.isSpeaking) {
          const u = new SpeechSynthesisUtterance(this.currentImageDescription.description);
          u.rate = 1.3;
          u.lang = "de-DE";

          u.onend = () => {
            this.isSpeaking = false;
          };
          u.onerror = () => {
            this.isSpeaking = false;
          };

          speechSynthesis.speak(u);

          this.isSpeaking = true;
        } else {
          speechSynthesis.cancel();
          this.isSpeaking = false;
        }
      }
    },
  },
};
</script>

<style lang="scss">
@import "@/scss/variables.scss";

.loader {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.5);

  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;

  .spinner-border {
    width: 3rem;
    height: 3rem;
  }
}

.text-justified {
  text-align: justify;
  text-justify: inter-word;
}

.height-full-column {
  height: calc(100vh - 2.5rem - 214px - 39px);
}

.image-fit {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
}
.actions {
  .icon {
    font-size: 3rem;
    cursor: pointer;

    &.is-speaking {
      animation: colorAnimation 2s linear infinite;
    }
  }
}

.image-description {
  height: 100%;
}

@keyframes colorAnimation {
  0% {
    color: #ea583d;
  }
  50% {
    color: #f9a17b;
  }
  100% {
    color: #ea583d;
  }
}
</style>
