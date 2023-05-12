<template>
  <main>
    <h1>
      Ausstellung <cite>{{ exhibition?.title }}</cite>
    </h1>

    <b-card v-if="currentImageId">
      <b-row no-gutters class="card-row">
        <b-col md="6" class="height-full-column d-flex align-items-center justify-content-start">
          <img :src="imageService.getImageUrl(currentImageId, 1000)" class="rounded-0 image-fit" />
        </b-col>
        <b-col md="6" class="height-full-column d-flex align-items-center justify-content-start">
          <div class="actions position-absolute top-0 end-0" aria-hidden="true">
            <button class="btn btn-outline-primary m-4" @click="speakCurrentImageDescription">
              <i-mdi-speak class="icon" :class="{ 'is-speaking': isSpeaking }" />
            </button>
          </div>
          <blockquote class="blockquote fs-3">
            <p class="image-description">{{ currentImageDescription }}</p>
          </blockquote>
        </b-col>
      </b-row>
    </b-card>
  </main>
</template>

<script lang="ts">
import { ImageService } from "@/services/image-service";
import { DescriptionService } from "@/services/description-service";
import { ref } from "vue";
import type { ExhibitionModel } from "@/models/exhibition-model";

export default {
  name: "HomeView",
  data() {
    const imageService = new ImageService();
    const descriptionService = new DescriptionService();

    const currentImageId = ref<string | null>(null);
    const currentImageDescription = ref<string | null>(null);
    const exhibition = ref<ExhibitionModel | null>(null);
    const isSpeaking = ref(false);

    return {
      imageService,
      descriptionService,

      currentImageId,
      currentImageDescription,
      exhibition,
      isSpeaking,
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
      if (this.exhibition === null) {
        this.exhibition = await this.imageService.getExhibition();
      }

      if (this.currentImageId === null || this.currentImageId.length === 0) {
        this.currentImageId = this.exhibition.imageIds[0];
      }

      this.currentImageDescription = (await this.loadDescription(this.currentImageId)).description;
    },
    async loadDescription(imageId: string) {
      return this.descriptionService.get(imageId);
    },
    speakCurrentImageDescription() {
      if (this.currentImageDescription) {
        if (!this.isSpeaking) {
          const u = new SpeechSynthesisUtterance(this.currentImageDescription);
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

.text-justified {
  text-align: justify;
  text-justify: inter-word;
}

.height-full-column {
  height: calc(100vh - 2.5rem - 214px);
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
