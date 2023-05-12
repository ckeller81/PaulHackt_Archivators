<template>
  <main>
    <div class="archive">
      <div class="actions-container position-absolute top-0 right-0 m-5">
        <button
          class="btn btn-outline-primary my-4 me-2"
          @click="backToExhibition"
          aria-label="Zurück zur Ausstellung"
          title="Zurück zur Ausstellung"
        >
          <i-mdi-arrow-left-bold class="icon" />
        </button>
      </div>
      <div ref="graphContainer" class="graph-container z-0" />
    </div>
  </main>
</template>

<script lang="ts">
import { ImageService } from "@/services/image-service";
import ForceGraph from "force-graph";
import { ref } from "vue";
import { useRoute } from "vue-router";

export default {
  setup() {
    const router = useRoute();

    const imageService = new ImageService();

    const imageId = router.query.imageid as string; // Access the query parameter

    const graphContainer = ref<any>(null);

    return {
      imageService,

      graphContainer,
      imageId,
    };
  },
  mounted() {
    this.loadGraph();
  },
  methods: {
    backToExhibition() {
      this.$router.push({
        name: "home",
        query: { imageid: this.imageId },
      });
    },
    async loadGraph() {
      const graph = ForceGraph()(this.graphContainer);

      const imageUrl = this.imageService.getImageUrl(this.imageId);
      const data = {
        nodes: [{ id: this.imageId, url: imageUrl, img: this.loadImage(imageUrl) }],
        links: [],
      };

      const containerWidth = this.graphContainer.offsetWidth;
      const containerHeight = this.graphContainer.offsetHeight;

      graph
        .nodeCanvasObject(({ img, x, y }, ctx) => {
          const size = 128;
          ctx.drawImage(img, x - size / 2, y - size / 2, size, size);
        })
        .nodePointerAreaPaint((node, color, ctx) => {
          const size = 12;
          ctx.fillStyle = color;
          ctx.fillRect(node.x - size / 2, node.y - size / 2, size, size); // draw square as pointer trap
        })
        .width(containerWidth)
        .height(containerHeight)
        .enableNodeDrag(false)
        .graphData(data);
    },
    loadImage(imageUrl: string) {
      const img = new Image();
      img.src = imageUrl;

      return img;
    },
  },
};
</script>

<style lang="scss">
.archive {
  width: 100%;
  height: 100%;
  position: relative;

  .actions-container {
    z-index: 1;
  }

  .graph-container {
    z-index: 0;

    width: 100%;
    height: calc(100vh - 151px);
  }
}
</style>
